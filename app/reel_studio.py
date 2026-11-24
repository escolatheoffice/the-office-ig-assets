"""Reel Studio The Office — interface visual (no navegador) para o templates/gen_reel.py.

Preencha frase, tag e CTA, veja a previa animada em 9:16 (com zona segura do TikTok),
gere o MP4 1080x1920 e baixe pronto pra postar no TikTok / Reels.

Uso:
  python3 app/reel_studio.py            # abre em http://127.0.0.1:8765
  python3 app/reel_studio.py --port 9000 --host 0.0.0.0

Requisitos: os mesmos do gen_reel.py (playwright + chromium, ffmpeg). Sem dependencias extras.
Os videos sao salvos em reels/<pasta>/reel.mp4 (+ legenda.txt), igual ao fluxo atual.
"""
import os, sys, re, json, html, argparse, threading, uuid, time, datetime, mimetypes, traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "templates"))
import gen_reel  # noqa: E402

APP_DIR = os.path.dirname(os.path.abspath(__file__))
REELS_DIR = os.path.join(ROOT, "reels")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")

JOBS = {}                       # id -> dict(status, stage, done, total, folder, error)
JOBS_LOCK = threading.Lock()
RENDER_LOCK = threading.Lock()  # um render por vez (Chromium + ffmpeg sao pesados)


def clean_params(d):
    """Valida e normaliza os parametros vindos do formulario."""
    texto = str(d.get("texto", "")).strip()
    if not texto:
        raise ValueError("Escreva a frase do reel.")
    if len(texto) > 300:
        raise ValueError("Frase muito longa (max. 300 caracteres).")
    tag = str(d.get("tag", "")).strip()[:60]
    cta = str(d.get("cta", "")).strip()[:60] or "Chama no direct →"
    try:
        duration = float(d.get("duration", gen_reel.DEFAULT_DURATION))
        fps = int(d.get("fps", gen_reel.DEFAULT_FPS))
        hsize = int(d.get("hsize", 104))
    except (TypeError, ValueError):
        raise ValueError("Duracao, FPS e tamanho precisam ser numeros.")
    if not 8 <= duration <= 60:
        raise ValueError("Duracao deve ficar entre 8 e 60 segundos.")
    if fps not in (24, 30, 60):
        raise ValueError("FPS deve ser 24, 30 ou 60.")
    if not 60 <= hsize <= 160:
        raise ValueError("Tamanho da frase deve ficar entre 60 e 160 px.")
    return dict(texto=texto, tag=tag, cta=cta, duration=duration, fps=fps, hsize=hsize)


def preview_html(p):
    outro_t, fade_t0, fade_t1 = gen_reel.timings(p["duration"])
    page = gen_reel.build_html(p["texto"], p["tag"], p["cta"], p["hsize"],
                               outro_t, fade_t0, fade_t1, offi_src="/offi.png")
    return page.replace("</body>", "<script>renderFrame(0)</script></body>")


def list_reels():
    out = []
    if os.path.isdir(REELS_DIR):
        for name in sorted(os.listdir(REELS_DIR), reverse=True):
            mp4 = os.path.join(REELS_DIR, name, "reel.mp4")
            if os.path.isfile(mp4):
                cap = os.path.join(REELS_DIR, name, "legenda.txt")
                out.append(dict(
                    folder=name,
                    url=f"/reels/{name}/reel.mp4",
                    size_mb=round(os.path.getsize(mp4) / 1e6, 1),
                    legenda=open(cap, encoding="utf-8").read() if os.path.isfile(cap) else "",
                ))
    return out


def run_job(job_id, p, folder, legenda):
    def progress(stage, done, total):
        with JOBS_LOCK:
            JOBS[job_id].update(stage=stage, done=done, total=total)
    try:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "na fila"
        with RENDER_LOCK:
            with JOBS_LOCK:
                JOBS[job_id]["status"] = "gerando"
            out_dir = os.path.join(REELS_DIR, folder)
            gen_reel.render(p["texto"], p["tag"], out_dir, p["cta"], p["duration"], p["fps"],
                            p["hsize"], progress=progress)
            if legenda:
                with open(os.path.join(out_dir, "legenda.txt"), "w", encoding="utf-8") as f:
                    f.write(legenda.strip() + "\n")
        with JOBS_LOCK:
            JOBS[job_id].update(status="pronto", url=f"/reels/{folder}/reel.mp4")
    except Exception as e:  # mostra o erro na interface em vez de travar
        traceback.print_exc()
        with JOBS_LOCK:
            JOBS[job_id].update(status="erro", error=str(e) or e.__class__.__name__)


class Handler(BaseHTTPRequestHandler):
    server_version = "ReelStudio/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("[reel-studio] " + (fmt % args) + "\n")

    # --- helpers ---
    def send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def json(self, code, obj):
        self.send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def send_file(self, path, download_name=None):
        if not os.path.isfile(path):
            return self.send(404, "nao encontrado", "text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        size = os.path.getsize(path)
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        m = re.match(r"bytes=(\d*)-(\d*)$", rng or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416); self.send_header("Content-Range", f"bytes */{size}"); self.end_headers()
                return
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if download_name:
            self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)

    # --- rotas ---
    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        path = u.path

        if path in ("/", "/index.html"):
            return self.send_file(os.path.join(APP_DIR, "index.html"))
        if path == "/offi.png":
            return self.send_file(gen_reel.OFFI)
        if path == "/preview":
            try:
                p = clean_params(q)
            except ValueError as e:
                return self.send(400, f"<body style='background:#060706;color:#fff;font:40px sans-serif;padding:80px'>{html.escape(str(e))}</body>")
            return self.send(200, preview_html(p))
        if path == "/api/reels":
            return self.json(200, list_reels())
        m = re.match(r"^/api/jobs/([0-9a-f]{32})$", path)
        if m:
            with JOBS_LOCK:
                job = JOBS.get(m.group(1))
                return self.json(200, dict(job)) if job else self.json(404, {"error": "job nao encontrado"})
        m = re.match(r"^/reels/([a-z0-9][a-z0-9-]*)/reel\.mp4$", path)
        if m:
            name = m.group(1)
            dl = f"{name}.mp4" if q.get("download") else None
            return self.send_file(os.path.join(REELS_DIR, name, "reel.mp4"), dl)
        return self.send(404, "nao encontrado", "text/plain; charset=utf-8")

    def do_POST(self):
        if urlparse(self.path).path != "/api/render":
            return self.send(404, "nao encontrado", "text/plain; charset=utf-8")
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n > 100_000:
                raise ValueError("Requisicao muito grande.")
            data = json.loads(self.rfile.read(n) or b"{}")
            p = clean_params(data)
            folder = str(data.get("folder", "")).strip().lower()
            if not SLUG_RE.match(folder):
                raise ValueError("Nome da pasta invalido: use so letras minusculas, numeros e hifen.")
            if os.path.exists(os.path.join(REELS_DIR, folder, "reel.mp4")) and not data.get("overwrite"):
                return self.json(409, {"error": f"Ja existe reels/{folder}/reel.mp4. Marque 'sobrescrever' ou troque o nome."})
            legenda = str(data.get("legenda", ""))[:2200]  # limite de legenda do TikTok
        except (ValueError, json.JSONDecodeError) as e:
            return self.json(400, {"error": str(e)})
        job_id = uuid.uuid4().hex
        with JOBS_LOCK:
            JOBS[job_id] = dict(status="na fila", stage="", done=0, total=0, folder=folder,
                                created=time.time())
        threading.Thread(target=run_job, args=(job_id, p, folder, legenda), daemon=True).start()
        return self.json(202, {"job": job_id})


def main():
    ap = argparse.ArgumentParser(description="Reel Studio The Office")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    os.makedirs(REELS_DIR, exist_ok=True)
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"Reel Studio rodando em http://{a.host}:{a.port}  (Ctrl+C para sair)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
