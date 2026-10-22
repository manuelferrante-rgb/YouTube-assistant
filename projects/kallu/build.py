#!/usr/bin/env python3
"""Reel "Birra di cocco" (kallu, il toddy del Kerala), 9:16, stesse regole del reel Comunismo (tools/reel_kit.py).

    python3 projects/kallu/build.py [--preview]
Girato in work/reel2/raw (cartella Drive 1hYw8CWZyiaxIKnldG86gatwfvmDE8Ll2).
"""
import glob, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from reel_kit import Reel
from sfx import sfx_file

W, H = (540, 960) if "--preview" in sys.argv else (1080, 1920)
R = f"{ROOT}/work/reel2/raw"
OUT = f"{ROOT}/work/reel2/out"
os.makedirs(OUT, exist_ok=True)


def clip(tag):
    m = glob.glob(f"{R}/dji_mimo_20261022_{tag}_*")
    assert len(m) == 1, (tag, m)
    return m[0]


r = Reel(f"{OUT}/reel_{W}_work", W, H, cx_cam=0.5)

# 1. gancio in camera
r.cam(clip("121212"), 0.0, 2.35, words=[("Hai", 0.0), ("mai", 0.48), ("assaggiato", 0.64), ("la", 1.20),
                                         ("birra", 1.36), ("di", 1.76), ("cocco?", 1.92)])
r.tl.sfx(0.0, sfx_file("boom"), 0.25)

# 2. come si fa: palme, insegna del locale (titolo), vaso che versa, bicchiere che si riempie
src = clip("121314")
a, b = 1.95, 11.55
sp = r.SP
t_dentro, t_dir, t_eda = ((t - a) / sp for t in (4.12, 5.72, 7.50))
t_ferm = (10.38 - a) / sp
# palme -> vaso su "dentro una ciotola" -> di nuovo la palma -> insegna (titolo) -> il vaso versa nel bicchiere
t0 = r.narr(src, a, b, [(r.own(src, 2.0, gain=0.15), t_dentro),
                        (r.own(clip("121448"), 0.05, gain=0.35), t_dir - t_dentro),
                        (r.own(src, 6.0, gain=0.15), t_eda - t_dir),
                        (r.own(src, 12.2, cx=0.28, speed=0.5, gain=0.15), 1.4),
                        (r.own(clip("121128"), 2.6, gain=0.35), None)],
            words=[("Raccolgono", 2.04), ("le", 2.76), ("gocce", 2.84), ("del", 3.32), ("cocco", 3.48), ("dentro", 4.12),
                   ("una", 4.68), ("ciotola", 4.92), ("direttamente", 5.72), ("sulla", 6.28), ("palma.", 6.52),
                   ("E", 7.50), ("da", 7.66), ("lì,", 7.82), ("con", 7.98), ("la", 8.14), ("fermentazione,", 8.22),
                   ("diventa", 8.94), ("naturalmente", 9.42), ("birra", 10.38), ("di", 10.94), ("cocco.", 11.10)])
r.title(t0 + t_eda, t0 + t_eda + 1.4, "KALLU", "Big", 560)
r.title(t0 + t_eda + 0.25, t0 + t_eda + 1.4, "il toddy del Kerala", "Small", 700)

# 3. il gestore conferma (inglese, velocità normale, sottotitolo tradotto)
r.cam(clip("121336"), 0.6, 2.75, speed=1.0, cx=0.55,
      block=[(0.7, 2.2, "Lo fate voi?"), (2.25, 2.75, "Sì.")])

# 4. bicchieri sul tavolo (suono vero)
r.own(clip("121118"), 0.1, gain=0.8)(1.3)

# 5-7. l'assaggio
r.cam(clip("121502"), 0.0, 3.4, words=[("Me", 0.0), ("l'ha", 0.16), ("riempito", 0.40), ("tutto,", 0.88),
                                        ("dicendo", 1.04), ("che", 1.36), ("è", 1.44), ("naturale.", 1.60),
                                        ("Magari", 2.08), ("mi", 2.32), ("ubriaco", 2.40), ("adesso.", 2.96)])
r.cam(clip("121356"), 0.55, 2.4, words=[("Cheers!", 0.86)])
r.cam(clip("121514"), 0.0, 1.3, words=[("Buonissimo,", 0.16), ("oh.", 0.88)])

# 8. "non è come le birre in vetro": inizio in camera, poi il locale
src = clip("121636")
t0 = r.cam(src, 0.0, 1.5, words=[("Beh,", 0.16), ("sicuramente", 0.48), ("non", 1.04), ("è", 1.20), ("come", 1.36)])
r.narr(src, 1.5, 3.85, [(r.own(clip("121212"), 1.9, gain=0.1, fx=dict(zoom=(1.0, 1.05, None))), None)],
       words=[("le", 1.60), ("birre", 1.76), ("in", 2.40), ("vetro", 2.56), ("che", 2.96), ("beviamo", 3.12),
              ("noi.", 3.52)])

# 9-10. il sapore, poi la domanda finale
r.cam(clip("121646"), 0.0, 3.35, words=[("Si", 0.0), ("sente", 0.32), ("tantissimo", 0.72), ("il", 1.36),
                                         ("sapore,", 1.52), ("l'odore", 2.0), ("del", 2.64), ("cocco.", 2.80)])
r.cam(clip("121702"), 0.3, 1.8, words=[("E", 0.41), ("tu", 0.57), ("l'hai", 0.73), ("mai", 0.97), ("provata?", 1.21)],
      fx=dict(zoom=(1.0, 1.04, None)))

r.render(f"{OUT}/VociVere_kallu_reel_{W}x{H}.mp4", crf=18 if W == 1080 else 23,
         preset="medium" if W == 1080 else "veryfast")
