#!/usr/bin/env python3
"""Sigla fissa Voci Vere (~5.8 s), identica in ogni video, lungo e verticali.

Frase di Manuel "Il mondo, raccontato da chi lo vive. Questo è Voci Vere." sopra lampi di viaggio
(assets/sigla/0N_*.mp4), poi il logo animato (tools/logo_anim.py) che parte sulla parola "Voci".
Niente musica: solo effetti brevi (tools/sfx.py).
    from sigla import sigla
    sigla(tl, workdir)      # da chiamare subito dopo l'intro del video
"""
import glob, os
from logo_anim import build as logo_build, EVENTS
from sfx import sfx_file

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
S = f"{ROOT}/assets/sigla"
FRASE = f"{S}/frase_sigla_manuel.m4a"
FRASE_A, FRASE_B, VOCI = 1.70, 5.75, 4.63   # inizio/fine del parlato e attacco di "Voci" nel file
# pezzi: (file, posizione orizzontale nel verticale, posizione verticale nel 16:9)
PIECES = [("01_strada_tuktuk.mp4", 0.5, 0.5), ("02_marari_pescatori.mp4", 0.42, 0.5),
          ("03_marari_spiaggia.mp4", 0.5, 0.5), ("04_kerala_chai.mp4", 0.5, 0.45),
          ("05_marari_laguna.mp4", 0.5, 0.55), ("06_marari_mare.mp4", 0.5, 0.5)]
FRAMES = [15, 15, 15, 15, 14, 14]            # 88 fotogrammi: il logo entra su "Voci"
LOGO_DUR = 2.9


def sigla(tl, workdir):
    t_s = tl.t
    tl.sfx(max(0, t_s - 0.6), sfx_file("whoosh_rev"), 0.45)        # ingresso dall'intro
    for i, ((f, cx, cy), nf) in enumerate(zip(PIECES, FRAMES)):
        t = tl.t
        tl._add(f"{S}/{f}", 0.05, nf / 30, cx=cx, cy=cy, grade="null", audio=False,
                fx=dict(flash=0.1 if i else 0.15, zoom=(1.10, 1.0, 0.3)))
        tl.sfx(t, sfx_file("flash"), 0.5 if i == 0 else 0.32)
    t_logo = tl.t
    # frase: "Voci" cade sul primo colpo della V
    tl.vos.append(dict(file=FRASE, a=FRASE_A, b=FRASE_B, speed=1.0, t=t_logo + 0.03 - (VOCI - FRASE_A)))
    tl.sfx(max(0, t_logo - 2.6), sfx_file("riser_long"), 0.3)
    os.makedirs(workdir, exist_ok=True)
    card = f"{workdir}/logo_anim_{tl.W}x{tl.H}.mp4"
    if not os.path.exists(card):
        logo_build(card, f"{S}/logo_sfondo.jpg", tl.W, tl.H, LOGO_DUR)
    tl.clip(card)
    gains = {"stamp": 0.42, "tick": 0.35, "shimmer": 0.45}
    for t, name in EVENTS:
        tl.sfx(t_logo + t, sfx_file(name), gains[name])
    return t_s
