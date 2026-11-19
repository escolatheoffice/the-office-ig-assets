"""Novo padrão visual The Office — peças diretas, legíveis na miniatura do perfil.

Layouts:
  frase  — fundo preto, frase gigante, 1 palavra-chave em verde
  bloco  — fundo verde-limão, frase gigante em preto (quebra o grid)
  offi   — Offi grande + frase curta
  turma  — CTA: TH1 / TH2 em destaque (dia + horário apenas)
Regras: frase com no máx. ~8 palavras; *palavra* = destaque; | = quebra de linha.
Uso:
  python3 templates/gen_post.py --layout frase --texto "Anúncio bonito|não é anúncio|que *vende.*" \
      --tag "Tráfego pago" --out posts/AAAA-MM-DD-slot [--feed-size 128 --story-size 150]
Gera feed.png, story.png, feed.jpg e story.jpg na pasta --out.
TikTok: acrescente --tiktok → gera só post.png (1080×1920) com a zona segura do TikTok
(sem texto atrás dos botões da direita nem da legenda embaixo) e sem "Chama no direct".
Sem argumentos: gera os 6 exemplos em templates/out.
"""
import os, sys, html, argparse
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
OFFI = os.path.join(os.path.dirname(BASE), "mascote", "offi.png")
OUT = os.path.join(BASE, "out")
# margens da peça vertical: story do Instagram (padrão) ou TikTok (--tiktok)
SAFE = dict(top=250, bot=300, padr=96, txt_bot=420)
SAFE_TIKTOK = dict(top=210, bot=470, padr=180, txt_bot=560)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:%(bg)s;color:%(fg)s}
.mark{position:absolute;left:%(pad)dpx;bottom:%(bot)dpx;font-weight:900;font-size:%(mk)dpx;letter-spacing:-.5px}
.mark span{color:%(acc)s}
.tag{position:absolute;left:%(pad)dpx;top:%(top)dpx;font-weight:800;font-size:%(tg)dpx;letter-spacing:3px;text-transform:uppercase;opacity:.55}
.h{position:absolute;left:%(pad)dpx;right:%(padr)dpx;font-weight:900;letter-spacing:-0.035em;line-height:.98}
.h em{font-style:normal;color:%(acc)s}
.cta{position:absolute;right:%(padr)dpx;bottom:%(bot)dpx;font-weight:800;font-size:%(mk)dpx;opacity:.6}
"""

def page(w, h, bg, fg, acc, body):
    pad = 80 if w == h else 96
    css = CSS % dict(w=w, h=h, bg=bg, fg=fg, acc=acc, pad=pad,
                     top=pad if w == h else SAFE["top"], bot=pad if w == h else SAFE["bot"],
                     padr=pad if w == h else SAFE["padr"],
                     mk=30 if w == h else 36, tg=22 if w == h else 26)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"

def fmt(text):
    # *palavra* vira destaque; | vira quebra de linha
    out, on = [], False
    for part in html.escape(text).split("*"):
        out.append(f"<em>{part}</em>" if on else part); on = not on
    return "".join(out).replace("|", "<br>")

MARK = "<div class='mark'>THE <span>OFFICE</span></div>"

def frase(fmtk, txt, tag, size, story_cta=None):
    w, h = fmtk
    body = f"<div class='tag'>{tag}</div>" if tag else ""
    body += f"<div class='h' style='font-size:{size}px;top:50%;transform:translateY(-55%)'>{fmt(txt)}</div>"
    body += MARK
    if story_cta: body += f"<div class='cta'>{story_cta}</div>"
    return page(w, h, "#060706", "#FFFFFF", "#D4FF1F", body)

def bloco(fmtk, txt, tag, size, story_cta=None):
    w, h = fmtk
    body = f"<div class='tag'>{tag}</div>" if tag else ""
    body += f"<div class='h' style='font-size:{size}px;top:50%;transform:translateY(-55%)'>{fmt(txt)}</div>"
    body += "<div class='mark'>THE OFFICE</div>"
    if story_cta: body += f"<div class='cta'>{story_cta}</div>"
    return page(w, h, "#D4FF1F", "#060706", "#060706;text-decoration:underline;text-decoration-thickness:.08em;text-underline-offset:.08em", body)

def offi(fmtk, txt, tag, size, story_cta=None):
    w, h = fmtk
    sq = w == h
    img = 470 if sq else 640
    body = f"<div class='tag'>{tag}</div>" if tag else ""
    body += (f"<img src='file://{OFFI}' style='position:absolute;right:{40 if sq else 60}px;"
             f"top:{40 if sq else 220}px;width:{img}px;filter:drop-shadow(0 0 80px rgba(212,255,31,.25))'>")
    body += f"<div class='h' style='font-size:{size}px;bottom:{170 if sq else SAFE['txt_bot']}px'>{fmt(txt)}</div>"
    body += MARK
    if story_cta: body += f"<div class='cta'>{story_cta}</div>"
    return page(w, h, "#060706", "#FFFFFF", "#D4FF1F", body)

def turma(fmtk, txt, tag, size, story_cta=None):
    w, h = fmtk
    sq = w == h
    body = f"<div class='tag'>{tag}</div>" if tag else ""
    body += f"<div class='h' style='font-size:{size}px;top:{150 if sq else 300}px'>{fmt(txt)}</div>"
    rows = [("TH1", "Segunda · 9h às 12h", "Início 11/01"), ("TH2", "Terça · 14h às 17h", "Início 12/01")]
    top = 560 if sq else 1000
    for i, (t, d, s) in enumerate(rows):
        y = top + i * (150 if sq else 190)
        body += (f"<div style='position:absolute;left:{80 if sq else 96}px;right:{80 if sq else SAFE['padr']}px;top:{y}px;"
                 f"display:flex;align-items:baseline;gap:28px;border-top:3px solid #262626;padding-top:26px'>"
                 f"<span style='font-weight:900;font-size:{64 if sq else 80}px;color:#D4FF1F'>{t}</span>"
                 f"<span style='font-weight:800;font-size:{40 if sq else 48}px'>{d}</span>"
                 f"<span style='margin-left:auto;font-weight:700;font-size:{28 if sq else 32}px;opacity:.5'>{s}</span></div>")
    body += MARK
    if story_cta: body += f"<div class='cta'>{story_cta}</div>"
    return page(w, h, "#060706", "#FFFFFF", "#D4FF1F", body)

LAYOUTS = dict(frase=frase, bloco=bloco, offi=offi, turma=turma)
FEED, STORY = (1080, 1080), (1080, 1920)

def render(jobs, out_dir=None, names=None, tiktok=False):
    out = out_dir or OUT
    os.makedirs(out, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, layout, txt, tag, fsize, ssize in jobs:
            targets = ([(STORY, ssize, "post", None)] if tiktok else
                       [(FEED, fsize, "feed", None), (STORY, ssize, "story", "Chama no direct →")])
            for fmtk, size, suf, cta in targets:
                fname = suf if names == "simple" else f"{name}_{suf}"
                path = os.path.join(out, f"{fname}.html")
                open(path, "w").write(LAYOUTS[layout](fmtk, txt, tag, size, cta))
                pg = b.new_page(viewport={"width": fmtk[0], "height": fmtk[1]}, device_scale_factor=1)
                pg.goto("file://" + path); pg.wait_for_timeout(150)
                png = os.path.join(out, f"{fname}.png")
                pg.screenshot(path=png); pg.close(); os.remove(path)
                if names == "simple" and not tiktok:
                    from PIL import Image
                    Image.open(png).convert("RGB").save(os.path.join(out, f"{fname}.jpg"), "JPEG", quality=92)
        b.close()

DEFAULT_SIZES = dict(frase=(128, 150), bloco=(128, 150), offi=(100, 128), turma=(118, 150))

if __name__ == "__main__" and len(sys.argv) > 1:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", required=True, choices=list(LAYOUTS))
    ap.add_argument("--texto", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--feed-size", type=int)
    ap.add_argument("--story-size", type=int)
    ap.add_argument("--tiktok", action="store_true")
    a = ap.parse_args()
    if a.tiktok:
        SAFE.update(SAFE_TIKTOK)
    fs, ss = DEFAULT_SIZES[a.layout]
    render([("post", a.layout, a.texto, a.tag, a.feed_size or fs, a.story_size or ss)], a.out, "simple", a.tiktok)
    print("ok:", a.out)
elif __name__ == "__main__":
    render([
        ("01_trafego", "frase", "Anúncio bonito|não é anúncio|que *vende.*", "Tráfego pago", 128, 150),
        ("02_presencial", "bloco", "Aqui o professor|sabe o seu|nome.", "Presencial", 136, 160),
        ("03_sites", "offi", "A IA faz o site.|Você faz ele|*vender.*", "Sites com IA", 100, 128),
        ("04_cta", "turma", "Turmas 2027|*abertas.*", "Matrículas", 118, 150),
        ("05_mercado", "frase", "Quem anuncia|*e* cria o site|vale o dobro.", "Mercado", 128, 150),
        ("06_bastidores", "bloco", "Sua dúvida não|vira ticket.|Vira resposta.", "Bastidores", 118, 140),
    ])
    print("ok")
