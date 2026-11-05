"""Chiusura dei reel Voci Vere (Manuel 5/11, regola stabile in regole/formato_reel.md).

Appena sparisce l'ultimo sottotitolo entra "Ascolta altre voci, su" (dissolvenza 0.6 s) sull'ultima persona; 0.8 s dopo
il logo chiaro (70%, con il payoff) sfuma sulla stessa persona, che continua sotto un velo (2 s), poi fine.
Due varianti, stesso stile, da alternare tra i reel così non finiscono tutti uguali:
  A: scritta oro su riquadro bianco, velo nero 35%;
  B: scritta bianca su riquadro oro, velo bruno caldo 42%.
"""
import os
from doc_render import run

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CTA = "Ascolta altre voci, su"
LOGO_DELAY = 0.8
LOGO_DUR = 2.0
VARIANTS = {"A": dict(style="TagIn", veil="black@0.35"), "B": dict(style="TagInB", veil="0x2b1a08@0.42")}


def logo_card(out_dir, W, H, d, src, a, grade="eq=contrast=1.03:saturation=1.05", cx=0.5, speed=1.0, variant="A"):
    """Logo che sfuma sull'ultima persona (ritaglio 9:16 su cx), che continua sotto il velo della variante."""
    veil = VARIANTS[variant]["veil"]
    out = f"{out_dir}/logo{variant}_{os.path.basename(src)[:26]}_{a:.2f}_{d:.2f}_{speed:.2f}_{cx}_{W}x{H}.mp4"
    if os.path.exists(out):
        return out
    lw = int(W * 0.7) // 2 * 2
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d * speed + 0.5:.3f}", "-i", src, "-loop", "1", "-t",
         f"{d:.3f}", "-i", f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png", "-filter_complex",
         f"[0:v:0]crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{cx}-ih*9/32))':0,scale={W}:{H}:flags=lanczos,"
         f"setpts=(PTS-STARTPTS)/{speed},fps=30,{grade},tpad=stop_mode=clone:stop_duration=2[v0];"
         f"color=c={veil}:s={W}x{H}:r=30:d={d:.3f},format=rgba,fade=t=in:st=0:d=0.5:alpha=1[k];"
         "[v0][k]overlay=shortest=1[bg];"
         f"[1]scale={lw}:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[l];[bg][l]overlay=(W-w)/2:(H-h)/2:shortest=1,"
         "format=yuv420p", "-an", "-t", f"{d:.3f}", "-r", "30", "-c:v", "libx264", "-crf", "16", out])
    return out


def close(r, out_dir, src, a, variant="A", grade="eq=contrast=1.03:saturation=1.05", cx=0.5, speed=1.0, own=None):
    """Aggiunge la chiusura al Reel r: l'ultima persona (src da a) per LOGO_DELAY s con la scritta, poi il logo.
    own: funzione che mette la clip (default r.own; per clip mute ad altra velocità passare r.gen). -> (t_cta, fine)."""
    t_c = r.t
    if own is None:
        r.own(src, a, cx=cx, grade=grade, speed=speed)(LOGO_DELAY)
    else:
        own(LOGO_DELAY)
    r.gen(logo_card(out_dir, r.W, r.H, LOGO_DUR, src, a + LOGO_DELAY * speed, grade=grade, cx=cx, speed=speed,
                    variant=variant))(LOGO_DUR)
    r.title(t_c, r.t, CTA, VARIANTS[variant]["style"], 400)
    return t_c, r.t
