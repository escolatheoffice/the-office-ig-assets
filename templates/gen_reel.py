"""Gerador de REEL animado The Office — motion design proprio (Playwright, sem IA externa),
no mesmo padrao visual dos posts estaticos (gen_post.py): fundo preto/verde-limao, Offi 3D,
frase gigante com palavra-chave em destaque.

Beats (13.5s, 1080x1920, 30fps):
  0.0-1.15s  Offi entra com "overshoot" (bounce) + glow de fundo cresce
  1.0-1.4s   tag (rotulo do tema) desliza da esquerda
  1.4-...    cada linha da frase sobe + aparece, staggered; Offi flutua (bob) continuo
  ...+0.5s   palavra-chave pulsa (scale) pra chamar atencao
  9.0-9.8s   Offi encolhe pro canto, frase sai, transicao pro encerramento
  9.3-10.2s  logo "THE OFFICE" + CTA (pill) entram
  10.2-13.0s respiro do CTA (pulsar leve) pra prender o olhar
  13.0-13.5s fade pro preto

Uso:
  python3 templates/gen_reel.py --texto "Enquanto voce pensa|a IA ja fez|o *site.*" \
      --tag "Sites com IA" --out reels/AAAA-MM-DD-slot [--cta "Chama no direct ->"] \
      [--duration 13.5] [--fps 30]
Gera reel.mp4 (+ frames/ temporario, removido no final) na pasta --out.
"""
import os, sys, html, argparse, subprocess, shutil, math
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
OFFI = os.path.join(os.path.dirname(BASE), "mascote", "offi.png")

W, H = 1080, 1920
DEFAULT_DURATION = 13.5
DEFAULT_FPS = 30

def fmt(text):
    # *palavra* -> <em> (destaque lima); | -> quebra de linha
    out, on = [], False
    for part in html.escape(text).split("*"):
        out.append(f"<em>{part}</em>" if on else part); on = not on
    return "".join(out).replace("|", "<br>")

def lines_html(text):
    # cada linha vira um <div class="ln"> proprio (pra animar staggered)
    raw = text.split("|")
    out = []
    for ln in raw:
        out.append(f"<div class='ln'>{fmt(ln)}</div>")
    return "".join(out), len(raw)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;position:relative;background:#060706;color:#fff}
#bg{position:absolute;inset:0;background:#060706}
#glow{position:absolute;left:50%%;top:38%%;width:1400px;height:1400px;margin-left:-700px;margin-top:-700px;
  border-radius:50%%;background:radial-gradient(circle,rgba(212,255,31,.30) 0%%,rgba(212,255,31,.10) 35%%,rgba(212,255,31,0) 70%%);
  filter:blur(10px);opacity:0;transform:translate(-50%%,-50%%) scale(1)}
#offiWrap{position:absolute;left:50%%;top:23%%;width:460px;margin-left:-230px;margin-top:-230px;opacity:0;
  transform:translate(0,0) scale(.7)}
#offiWrap img{width:100%%;display:block;filter:drop-shadow(0 0 90px rgba(212,255,31,.35))}
#tag{position:absolute;left:96px;top:250px;font-weight:800;font-size:30px;letter-spacing:3px;
  text-transform:uppercase;opacity:0;color:#fff}
#hook{position:absolute;left:96px;right:96px;top:1080px}
#hook .ln{font-weight:900;letter-spacing:-.035em;line-height:.98;font-size:%(hsize)dpx;opacity:0;transform:translateY(50px)}
#hook em{font-style:normal;color:#D4FF1F;display:inline-block}
#logo{position:absolute;left:0;right:0;top:44%%;text-align:center;font-weight:900;font-size:108px;
  letter-spacing:-.03em;opacity:0;transform:translateY(40px)}
#logo span{color:#D4FF1F}
#ctaWrap{position:absolute;left:0;right:0;bottom:300px;display:flex;justify-content:center;opacity:0;transform:scale(.9)}
#ctaPill{display:inline-flex;align-items:center;padding:26px 48px;border-radius:999px;
  background:rgba(212,255,31,.10);border:2px solid #D4FF1F;font-weight:800;font-size:34px;color:#fff}
#mark{position:absolute;left:96px;bottom:300px;font-weight:900;font-size:36px;letter-spacing:-.5px;opacity:0}
#mark span{color:#D4FF1F}
#blackout{position:absolute;inset:0;background:#060706;opacity:0;pointer-events:none}
"""

JS = r"""
function clamp01(x){return Math.max(0,Math.min(1,x));}
function easeOutCubic(p){return 1-Math.pow(1-p,3);}
function easeInCubic(p){return p*p*p;}
function easeInOutCubic(p){return p<0.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2;}
function easeOutBack(p){const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(p-1,3)+c1*Math.pow(p-1,2);}
function mix(t,t0,t1,v0,v1,ease){
  ease = ease || (x=>x);
  if(t<=t0) return v0;
  if(t>=t1) return v1;
  const p = ease(clamp01((t-t0)/(t1-t0)));
  return v0+(v1-v0)*p;
}
const NLINES = window.__NLINES__;
const LINE_START = window.__LINE_START__; // s
const LINE_STEP = window.__LINE_STEP__;
const LINE_DUR = window.__LINE_DUR__;
const OUTRO_T = window.__OUTRO_T__;

function renderFrame(t){
  // --- glow de fundo ---
  const glow = document.getElementById('glow');
  const glowOp = mix(t,0,1.2,0,1,easeOutCubic);
  const glowS = 1+0.04*Math.sin(t*0.7);
  glow.style.opacity = glowOp;
  glow.style.transform = `translate(-50%,-50%) scale(${glowS})`;

  // --- Offi ---
  const offi = document.getElementById('offiWrap');
  let ty, s, tx=0, op;
  if (t < 0.9){
    ty = mix(t,0,0.9,300,-20,easeOutBack);
    s  = mix(t,0,0.9,0.7,1.08,easeOutBack);
    op = mix(t,0,0.5,0,1,easeOutCubic);
  } else if (t < 1.15){
    ty = mix(t,0.9,1.15,-20,0,easeOutCubic);
    s  = mix(t,0.9,1.15,1.08,1.0,easeOutCubic);
    op = 1;
  } else if (t < OUTRO_T){
    ty = Math.sin((t-1.15)*1.3)*14;
    s = 1.0; op = 1;
  } else if (t < OUTRO_T+0.8){
    const p = (t-OUTRO_T)/0.8;
    ty = mix(t,OUTRO_T,OUTRO_T+0.8,0,-650,easeInOutCubic) + Math.sin(t*1.3)*14*(1-p);
    tx = mix(t,OUTRO_T,OUTRO_T+0.8,0,300,easeInOutCubic);
    s  = mix(t,OUTRO_T,OUTRO_T+0.8,1.0,0.45,easeInOutCubic);
    op = 1;
  } else {
    tx = 300; s = 0.45;
    ty = -650 + Math.sin((t-OUTRO_T-0.8)*1.3)*6;
    op = 1;
  }
  offi.style.opacity = op;
  offi.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`;

  // --- tag ---
  const tag = document.getElementById('tag');
  let tagOp = mix(t,1.0,1.4,0,1,easeOutCubic);
  let tagTx = mix(t,1.0,1.4,-40,0,easeOutCubic);
  if (t > OUTRO_T) tagOp = tagOp * mix(t,OUTRO_T,OUTRO_T+0.4,1,0,easeInCubic);
  tag.style.opacity = tagOp;
  tag.style.transform = `translateX(${tagTx}px)`;

  // --- linhas da frase ---
  const lns = document.querySelectorAll('#hook .ln');
  let lastEnd = LINE_START;
  for (let i=0;i<lns.length;i++){
    const s0 = LINE_START + i*LINE_STEP;
    const s1 = s0 + LINE_DUR;
    lastEnd = Math.max(lastEnd, s1);
    let lop = mix(t,s0,s1,0,1,easeOutCubic);
    let lty = mix(t,s0,s1,50,0,easeOutCubic);
    let lsc = 1;
    if (t > OUTRO_T){
      const oOp = mix(t,OUTRO_T,OUTRO_T+0.4,1,0,easeInCubic);
      const oTy = mix(t,OUTRO_T,OUTRO_T+0.4,0,-40,easeInCubic);
      const oSc = mix(t,OUTRO_T,OUTRO_T+0.4,1,0.95,easeInCubic);
      lop = lop*oOp; lty = lty+oTy; lsc = oSc;
    }
    lns[i].style.opacity = lop;
    lns[i].style.transform = `translateY(${lty}px) scale(${lsc})`;
  }
  // --- pulso da palavra-chave ---
  const kw = document.querySelectorAll('#hook em');
  const pStart = lastEnd + 0.2, pMid = pStart+0.25, pEnd = pStart+0.5;
  let kScale = 1;
  if (t < pMid) kScale = mix(t,pStart,pMid,1,1.18,easeOutCubic);
  else kScale = mix(t,pMid,pEnd,1.18,1,easeOutCubic);
  kw.forEach(e=>{ e.style.transform = `scale(${kScale})`; });

  // --- logo de encerramento ---
  const logo = document.getElementById('logo');
  logo.style.opacity = mix(t,OUTRO_T+0.3,OUTRO_T+0.9,0,1,easeOutCubic);
  logo.style.transform = `translateY(${mix(t,OUTRO_T+0.3,OUTRO_T+0.9,40,0,easeOutCubic)}px)`;

  // --- CTA pill ---
  const cta = document.getElementById('ctaWrap');
  const ctaInEnd = OUTRO_T+1.2;
  let ctaOp = mix(t,OUTRO_T+0.6,OUTRO_T+1.0,0,1,easeOutCubic);
  let ctaScale;
  if (t < ctaInEnd) ctaScale = mix(t,OUTRO_T+0.6,ctaInEnd,0.9,1,easeOutCubic);
  else ctaScale = 1+0.03*Math.sin((t-ctaInEnd)*(2*Math.PI/1.2));
  cta.style.opacity = ctaOp;
  cta.style.transform = `scale(${ctaScale})`;

  // --- marca THE OFFICE (sutil, junto com a frase, antes do outro) ---
  const mark = document.getElementById('mark');
  mark.style.opacity = mix(t,1.4,1.8,0,0.9,easeOutCubic) * mix(t,OUTRO_T,OUTRO_T+0.3,1,0,easeInCubic);

  // --- blackout final ---
  const bo = document.getElementById('blackout');
  bo.style.opacity = mix(t,window.__FADE_T0__,window.__FADE_T1__,0,1);
}
window.renderFrame = renderFrame;
"""

def timings(duration):
    """(outro_t, fade_t0, fade_t1) para uma duracao — usado no render e na previa do Reel Studio."""
    return duration - 4.5, duration - 0.5, duration


def build_html(texto, tag, cta, hsize, outro_t, fade_t0, fade_t1, offi_src=None):
    hook, n = lines_html(texto)
    offi_src = offi_src or f"file://{OFFI}"
    line_step = 0.25
    line_dur = 0.5
    line_start = 1.4
    css = CSS % dict(w=W, h=H, hsize=hsize)
    body = (
        f"<div id='bg'></div><div id='glow'></div>"
        f"<div id='offiWrap'><img src='{offi_src}'></div>"
        f"<div id='tag'>{html.escape(tag)}</div>"
        f"<div id='hook'>{hook}</div>"
        f"<div id='mark'>THE <span>OFFICE</span></div>"
        f"<div id='logo'>THE <span>OFFICE</span></div>"
        f"<div id='ctaWrap'><div id='ctaPill'>{html.escape(cta)}</div></div>"
        f"<div id='blackout'></div>"
    )
    js = (JS
          .replace("window.__NLINES__", str(n))
          .replace("window.__LINE_START__", str(line_start))
          .replace("window.__LINE_STEP__", str(line_step))
          .replace("window.__LINE_DUR__", str(line_dur))
          .replace("window.__OUTRO_T__", str(outro_t))
          .replace("window.__FADE_T0__", str(fade_t0))
          .replace("window.__FADE_T1__", str(fade_t1)))
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}<script>{js}</script></body></html>"


def render(texto, tag, out_dir, cta="Chama no direct →", duration=DEFAULT_DURATION, fps=DEFAULT_FPS,
           hsize=104, sample_times=None, progress=None):
    """progress: callback opcional progress(etapa, feito, total) — usado pelo Reel Studio."""
    os.makedirs(out_dir, exist_ok=True)
    frames_dir = os.path.join(out_dir, "_frames")
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)

    outro_t, fade_t0, fade_t1 = timings(duration)   # outro ~9.0s quando duration=13.5

    html_path = os.path.join(out_dir, "_reel.html")
    open(html_path, "w").write(build_html(texto, tag, cta, hsize, outro_t, fade_t0, fade_t1))

    total_frames = int(round(duration * fps))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto("file://" + html_path)
        pg.wait_for_timeout(100)
        for i in range(total_frames):
            t = i / fps
            pg.evaluate(f"renderFrame({t})")
            pg.screenshot(path=os.path.join(frames_dir, f"f_{i:05d}.png"))
            if progress:
                progress("frames", i + 1, total_frames)
        # amostras pra conferencia visual, se pedido
        samples = {}
        if sample_times:
            for st in sample_times:
                pg.evaluate(f"renderFrame({st})")
                sp = os.path.join(out_dir, f"sample_{st}s.png")
                pg.screenshot(path=sp)
                samples[st] = sp
        pg.close(); b.close()
    os.remove(html_path)

    mp4 = os.path.join(out_dir, "reel.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps), "-i", os.path.join(frames_dir, "f_%05d.png"),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest",
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        mp4,
    ]
    if progress:
        progress("encode", 0, 1)
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(frames_dir)
    return mp4, samples


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--texto", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--cta", default="Chama no direct →")
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, default=DEFAULT_DURATION)
    ap.add_argument("--fps", type=int, default=DEFAULT_FPS)
    ap.add_argument("--hsize", type=int, default=104)
    ap.add_argument("--samples", default="")  # ex: "0.2,1.5,5,9.5,11,13.4"
    a = ap.parse_args()
    samples = [float(x) for x in a.samples.split(",") if x.strip()] if a.samples else None
    mp4, samples_out = render(a.texto, a.tag, a.out, a.cta, a.duration, a.fps, a.hsize, samples)
    print("ok:", mp4)
    for st, sp in (samples_out or {}).items():
        print("sample", st, sp)
