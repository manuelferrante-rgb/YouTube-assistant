#!/usr/bin/env python3
"""Mercato del pesce di Marari: lungo 16:9 (con teaser e sigla), teaser 9:16, 2 Short 9:16.

    python3 projects/mercato/build.py [long|teaser|short2|short3|all] [--preview]
--preview: 960x540 / 540x960 veloce per controllare la struttura.
"""
import os, subprocess, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import Timeline, run, dur_of

R = f"{ROOT}/work/raw"
VO = f"{ROOT}/work/vo"
MU = f"{ROOT}/work/musica"
OUT = f"{ROOT}/work/mercato"
LOGO_W = f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png"
os.makedirs(OUT, exist_ok=True)


def raw(n):
    return f"{R}/DJI_{n}.MP4"


def mimo(t):
    return f"{R}/dji_{t}.mp4"


TENT = "colorbalance=rs=0.08:bs=-0.10:rm=0.06:bm=-0.08:rh=0.03:bh=-0.04,eq=saturation=0.95"

M_FLIGHT = f"{MU}/taking_flight_blue_deer_studio.mp3"   # energica: teaser, mercato
M_HOME = f"{MU}/way_back_home_simon_herody.mp3"          # morbida: il giorno prima
M_YOGA = f"{MU}/yoga_style_chris_haugen.mp3"             # calma: Kerala, colazione
M_HERE = f"{MU}/from_here_on_in_everet_almond.mp3"       # cresce: sigla, chiusura


# ---------- voiceover: punti di taglio ----------
def quiet_point(path, lo, hi):
    raw_ = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                          capture_output=True).stdout
    x = np.frombuffer(raw_, np.float32); hop = 160
    e = [np.sqrt(np.mean(x[int(t * 16000):int(t * 16000) + hop] ** 2)) for t in np.arange(lo, hi, 0.01)]
    return lo + 0.01 * int(np.argmin(np.convolve(e, np.ones(9) / 9, mode="same")))


T, P, K, MK, C, S = (f"{VO}/1_teaser.m4a", f"{VO}/3_persone.m4a", f"{VO}/4_kerala.m4a", f"{VO}/5_mercato.m4a",
                     f"{VO}/6_chiusura.m4a", f"{VO}/7_shorts.m4a")
G = f"{VO}/2_giorno_prima.m4a"
sp_t = quiet_point(T, 12.3, 13.3)
sp_m1 = quiet_point(MK, 7.35, 8.3)
sp_m2 = quiet_point(MK, 9.1, 10.1)
VOS = {
    "vo_01": (T, 4.36, 9.05), "vo_02": (T, 9.79, sp_t), "vo_03": (T, sp_t, 16.2),
    "vo_04": (G, 4.55, 12.2),
    "vo_05": (P, 2.23, 4.75), "vo_06": (P, 5.24, 9.95), "vo_07": (P, 10.78, 16.15),
    "vo_08": (K, 0.93, 4.85), "vo_09": (K, 8.59, 13.9),
    "vo_10": (MK, 4.56, sp_m1), "vo_11": (MK, sp_m2, 15.45), "vo_12": (MK, 16.6, 19.65), "vo_13": (MK, 20.0, 25.75),
    "vo_14": (C, 1.75, 7.9), "vo_15": (C, 8.27, 11.95),
    "vo_s2": (S, 1.36, 4.72), "vo_s3": (S, 6.0, 10.8),
}


def prep_vo(key):
    """Blocco di voiceover pronto: tagliato, a 1.1x, pause interne ridotte a ~0.2 s. Ritorna (file, durata)."""
    f, a, b = VOS[key]
    out = f"{OUT}/{key}.wav"
    if not os.path.exists(out):
        run(["ffmpeg", "-v", "error", "-y", "-i", f, "-af",
             f"atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,atempo=1.1,aresample=48000,"
             "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08:"
             "stop_periods=-1:stop_duration=0.25:stop_threshold=-45dB:stop_silence=0.2",
             "-ar", "48000", "-ac", "1", out])
    return out, dur_of(out)


import json
_SEG = json.load(open(f"{ROOT}/work/out/seg_speech.json"))


def has_voice(src, a, b):
    segs = _SEG.get(os.path.basename(src), [])
    return any(sg["start"] < b and sg["end"] > a for sg in segs)


def vo(tl, key, shots, **kw):
    tl.voice_check = has_voice
    f, d = prep_vo(key)
    return tl.vo(f, 0, d, shots, speed=1.0, **kw)


def vo_at(tl, key, t):
    f, d = prep_vo(key)
    tl.vos.append(dict(file=f, a=0, b=d, speed=1.0, t=t))


# ---------- clip grafiche ----------
def logo_card(src, t, dur, W, H, out, cx=0.5):
    """Fermo immagine sfocato e scurito con il logo che entra (stile presentazione)."""
    if os.path.exists(out):
        return out
    crop = f"crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{cx}-ih*9/32))':0," if H > W else ""
    lw = int(W * (0.62 if H > W else 0.42))
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src, "-loop", "1", "-t", f"{dur}", "-i", LOGO_W,
         "-filter_complex",
         f"[0:v]{crop}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},trim=end_frame=1,"
         f"tpad=stop_mode=clone:stop_duration={dur},fps=30,trim=duration={dur},setpts=PTS-STARTPTS,split[a][b];"
         f"[b]gblur=sigma={int(28 * W / 1920)},eq=brightness=-0.24:saturation=0.65[bl];"
         f"[a][bl]xfade=transition=fade:duration=0.6:offset=0.05[v];"
         f"[1:v]scale={lw}:-1,format=rgba,fade=t=in:st=0.35:d=0.6:alpha=1[lg];"
         f"[v][lg]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[o]",
         "-map", "[o]", "-t", f"{dur}", "-c:v", "libx264", "-crf", "15", "-preset", "veryfast", out])
    return out


def sigla(W, H, tag=None):
    tag = f"{W}x{H}"
    """Sigla cumulativa: un pezzo per ogni video pubblicato (qui il primo: Marari) + logo."""
    out = f"{OUT}/sigla_{tag}.mp4"
    if os.path.exists(out):
        return out
    tl = Timeline(W, H, f"{OUT}/sigla_{tag}_work")
    pieces = [(raw("0122"), 1.0, 0.5), (raw("0076"), 40.0, 0.42), (raw("0117"), 15.0, 0.5),
              (raw("0119"), 0.8, 0.45), (raw("0143"), 3.0, 0.5)]
    for src, a, cx in pieces:
        tl.broll(src, a, 0.8, gain=0.0, cx=cx)
    tl.clip(logo_card(raw("0117"), 15.8, 2.4, W, H, f"{OUT}/sigla_logo_{tag}.mp4"))
    tl.music(0, tl.t, M_HERE, offset=118.0, level=0.9, fin=0.3, fout=0.9)
    tl.render(out, reuse=True, crf=16, preset="veryfast")
    return out


def maps(W, H):
    return f"{ROOT}/work/map_marari_4k.mp4" if W > H else f"{ROOT}/work/map_marari_9x16.mp4"


# ---------- teaser (uguale all'inizio del lungo e nel teaser verticale) ----------
def teaser(tl):
    tl.broll(raw("0117"), 3.0, 2.2, gain=0.6, cx=0.5)
    t0 = vo(tl, "vo_01", [(raw("0121"), 0.5, 0.5), (raw("0119"), 0.3, 0.45), (raw("0093"), 20.0, 0.5)])
    tl.music(0, t0 + 13, M_FLIGHT, offset=12.0, level=0.45, fin=0.4, fout=1.2)
    tl.speech(raw("0076"), [(26.45, 28.35)], subs=[(26.45, 28.35, "Di notte. Alle tre si comincia.")], cx=0.45)
    tm = tl.t
    tl.clip(maps(tl.W, tl.H))
    vo_at(tl, "vo_02", tm + 0.9)
    vo(tl, "vo_03", [(raw("0118"), 19.5, 0.62), (raw("0124"), 1.6, 0.42), (raw("0086"), 20.0, 0.5)], tail=0.5)
    tl.clip(sigla(tl.W, tl.H, "16x9" if tl.W > tl.H else "9x16"), audio=True)


def long_video(tl):
    trailer(tl)

    # ---- il giorno prima ----
    t0 = vo(tl, "vo_04", [(mimo("143640"), 0.0), (mimo("142648"), 12.0), (mimo("142648"), 3.0)  # TODO: dji_143748 non piu su Drive (21/10): sostituito con altro tratto di 142648
                          ,
                          (mimo("143050"), 1.0)])
    tl.broll(mimo("144938"), 0.5, 2.2, gain=0.35)
    tl.broll(mimo("145004"), 3.0, 2.4, gain=0.35)
    tl.broll(mimo("151316"), 0.5, 2.4, gain=0.45)
    tl.broll(mimo("155220"), 0.2, 2.6, gain=0.4)
    tl.broll(mimo("155336"), 0.5, 2.2, gain=0.35)
    tl.speech(mimo("143504"), [(0.95, 4.25), (4.8, 7.9), (8.65, 9.65), (10.8, 12.8)], speed=1.1)
    tl.music(t0, tl.t - 6.5, M_HOME, offset=20.0, level=0.42, fin=0.8, fout=1.5)
    t_people = tl.t

    # ---- le persone: il pescatore delle reti ----
    vo(tl, "vo_05", [(raw("0081"), 49.0), (raw("0081"), 55.0)])
    tl.speech(raw("0081"), [(19.25, 20.9), (21.9, 24.7), (32.8, 36.5), (40.3, 42.3), (45.2, 46.9)],
              subs=[(19.25, 20.9, "Lo fai tutti i giorni?"), (21.9, 24.7, "Tutti i giorni, a pescare."),
                    (32.8, 34.6, "Alle quattro. Alle quattro, di mattina."), (34.6, 36.5, "La mattina, alle otto."),
                    (40.3, 42.3, "A volte, a preparare."), (45.2, 46.9, "Posso vedere la rete?")])
    tl.broll(raw("0081"), 50.0, 3.2, gain=0.6)
    tl.speech(raw("0081"), [(62.45, 65.0), (70.65, 75.25), (75.75, 76.95), (77.3, 80.75), (93.8, 98.95)],
              subs=[(19.25, 20.9, "Lo fai tutti i giorni?"), (21.9, 24.7, "Tutti i giorni, a pescare."),
                    (32.8, 34.6, "Alle quattro. Alle quattro, di mattina."), (34.6, 36.5, "La mattina, alle otto."),
                    (40.3, 42.3, "A volte, a preparare."), (62.45, 65.0, "Questa serve per prepararsi a pescare."),
                    (70.65, 73.0, "Incredibile."), (73.0, 75.25, "La fai a mano?"), (75.75, 76.95, "Sì."),
                    (77.3, 80.75, "E la usi per andare... nell'oceano."),
                    (93.8, 96.3, "Arabico. Mar Arabico."), (96.3, 98.95, "Ah, lo chiamate Mar Arabico. Sì.")])

    # ---- il pescatore sulla barca ----
    vo(tl, "vo_06", [(raw("0076"), 223.0, 0.45), (mimo("145004"), 2.0)])
    tl.speech(raw("0076"), [(3.25, 6.0)], cx=0.45, subs=[(3.25, 5.2, "Sei un pescatore?"), (5.2, 6.0, "Sì, sono un pescatore.")])
    tl.speech(raw("0076"), [(24.2, 28.35), (36.85, 43.05), (57.55, 58.65), (63.8, 66.8)], cx=0.45,
              subs=[(24.2, 26.5, "No, no, di notte."), (26.5, 28.35, "Di notte. Alle tre si comincia."),
                    (36.85, 40.9, "Alle otto e mezza, alle otto, si torna col pesce."),
                    (41.1, 42.4, "Poi vai al mercato?"), (42.4, 43.05, "Mercato, mercato."),
                    (57.55, 58.65, "E da quanti anni?"), (63.8, 65.6, "Trent'anni di pesca."),
                    (65.6, 66.8, "Tre, zero. Sì.")])
    vo(tl, "vo_07", [(mimo("151316"), 1.0), (raw("0081"), 58.0)])
    tl.speech(raw("0076"), [(250.7, 255.55), (260.5, 262.7), (267.75, 271.95)], cx=0.45,
              subs=[(250.7, 251.6, "Kayak."), (251.8, 254.3, "Ah, ok. Fai la guida?"), (254.4, 255.55, "Sì, la guida."),
                    (260.5, 262.7, "E questo ti piace di più? Sì."), (267.75, 269.4, "Un'ora, due ore."),
                    (270.3, 271.95, "Canali stretti, strettissimi.")])

    # ---- il Kerala di cui ci parla ----
    vo(tl, "vo_08", [(raw("0076"), 229.0, 0.45), (mimo("145004"), 8.0)])
    tl.speech(raw("0076"), [(275.45, 278.35), (284.5, 287.45)], cx=0.45,
              subs=[(275.45, 278.35, "Com'è la vita qui in Kerala?"), (284.5, 287.45, "Solo pesca. È buona, è buona.")])
    tl.speech(raw("0076"), [(309.7, 312.3), (316.0, 319.1), (322.05, 325.8), (343.3, 347.0)], cx=0.45,
              subs=[(309.7, 312.3, "In Kerala tante religioni."), (316.0, 319.1, "Cristiani, induisti, musulmani."),
                    (322.05, 325.8, "Vanno molto d'accordo. Amici."),
                    (343.3, 347.0, "È un posto in pace. Un posto in pace.")])
    t0 = vo(tl, "vo_09", [(mimo("145004"), 1.0), (raw("0076"), 235.0, 0.45)])
    tl.speech(raw("0076"), [(146.05, 150.35)], cx=0.45,
              subs=[(146.05, 147.2, "Vengono mille persone."), (147.4, 150.35, "Per tutti c'è il cibo gratis.")])
    tl.music(t0, tl.t + 0.8, M_YOGA, offset=30.0, level=0.4, fin=0.8, fout=1.0)
    # letto musicale morbido sotto le interviste: riempie i passaggi, sotto la voce sparisce (ducking)
    tl.music(t_people - 1.0, t0 + 0.5, M_HOME, offset=70.0, level=0.22, fin=1.5, fout=1.0)

    # ---- il mercato ----
    t0 = vo(tl, "vo_10", [(raw("0085"), 0.2), (raw("0094"), 3.0)])
    tl.speech(raw("0083"), [(0.0, 5.5), (6.1, 7.45), (9.4, 13.85)], speed=1.1)
    tl.speech(raw("0085"), [(2.3, 7.4), (11.75, 18.0), (22.4, 31.3)], speed=1.1)
    for src, a, d, cx in [(raw("0093"), 3.0, 2.2, 0.5), (raw("0123"), 0.5, 2.0, 0.4), (raw("0117"), 8.0, 2.2, 0.5),
                          (raw("0118"), 12.0, 2.0, 0.62), (raw("0124"), 1.4, 2.0, 0.45), (raw("0126"), 10.0, 2.2, 0.5)]:
        tl.broll(src, a, d, gain=0.55, cx=cx)
    vo(tl, "vo_11", [(raw("0093"), 25.0), (raw("0119"), 0.5, 0.45), (raw("0121"), 0.5), (raw("0120"), 2.0)])
    tl.speech(raw("0089"), [(0.65, 2.9), (4.85, 6.6)], speed=1.1)
    tl.speech(raw("0087"), [(1.45, 5.05)], speed=1.1)
    tl.broll(raw("0116"), 0.5, 1.6, gain=0.5)
    tl.speech(raw("0086"), [(0.6, 2.95), (5.85, 8.3), (16.15, 20.1)], speed=1.1)
    tl.broll(raw("0086"), 27.0, 2.6, gain=0.5)
    tl.speech(raw("0091"), [(0.45, 7.8)], speed=1.1)
    tl.speech(raw("0092"), [(2.2, 6.75), (7.05, 10.3), (12.95, 14.35), (15.6, 17.2)], cx=0.55,
              subs=[(2.2, 6.75, "Questo è il mercato di Mararikulam. È molto famoso."),
                    (7.05, 10.3, "E ogni giorno, la mattina, si fa la stessa cosa."),
                    (12.95, 14.35, "Da tanto tempo."), (15.6, 17.2, "Da tantissimo tempo. Sì, sì.")])
    tl.speech(raw("0093"), [(6.0, 9.65), (11.4, 14.2), (15.3, 16.7), (18.0, 21.75), (27.8, 29.2), (31.55, 33.45)], speed=1.1)
    tl.speech(raw("0094"), [(0.7, 5.55), (6.7, 8.4), (9.1, 11.9), (12.35, 15.1), (15.65, 17.15), (17.8, 19.9),
                            (23.3, 27.1), (27.95, 30.1)], speed=1.1)
    tl.broll(raw("0120"), 3.0, 2.2, gain=0.5)
    tl.broll(raw("0118"), 3.0, 2.2, gain=0.5, cx=0.55)
    tl.broll(raw("0125"), 1.0, 2.0, gain=0.5, cx=0.45)
    tl.broll(raw("0127"), 0.3, 1.5, gain=0.5)
    tl.speech(raw("0122"), [(0.0, 3.5)], speed=1.1)
    tl.speech(raw("0109"), [(2.45, 4.95)], speed=1.1)
    t1 = vo(tl, "vo_12", [(raw("0109"), 5.0), (raw("0095"), 3.0), (raw("0110"), 1.0), (raw("0135"), 0.0)])
    for src, a, d in [(raw("0134"), 1.0, 2.2), (raw("0136"), 0.5, 2.0), (raw("0112"), 0.5, 2.2), (raw("0114"), 0.3, 1.8)]:
        tl.broll(src, a, d, gain=0.45)
    tl.music(t0, tl.t + 0.6, M_FLIGHT, offset=40.0, level=0.38, fin=0.8, fout=1.0)

    # ---- colazione ----
    t2 = tl.t
    tl.speech(raw("0096"), [(1.15, 2.6)], speed=1.1, grade=TENT)
    tl.speech(raw("0097"), [(0.0, 2.95), (3.4, 4.35)], speed=1.1, grade=TENT)
    tl.broll(raw("0097"), 12.0, 3.0, gain=0.4, grade=TENT)
    tl.broll(raw("0097"), 30.0, 3.0, gain=0.4, grade=TENT)
    tl.speech(raw("0099"), [(0.0, 2.65), (4.1, 5.25)], speed=1.1, grade=TENT)
    tl.broll(raw("0099"), 15.0, 3.0, gain=0.4, grade=TENT)
    tl.broll(raw("0099"), 26.0, 2.5, gain=0.4, grade=TENT)
    tl.speech(raw("0100"), [(1.2, 4.9)], speed=1.1, grade=TENT)
    tl.broll(raw("0101"), 0.2, 2.4, gain=0.4, grade=TENT)
    tl.speech(raw("0107"), [(1.15, 1.95), (4.45, 5.9)], speed=1.1, grade=TENT)
    tl.broll(raw("0108"), 1.0, 2.2, gain=0.4, grade=TENT)
    vo(tl, "vo_13", [(raw("0117"), 10.0), (raw("0126"), 6.0), (raw("0118"), 20.0, 0.62)])
    tl.music(t2, tl.t + 0.6, M_YOGA, offset=60.0, level=0.38, fin=0.6, fout=1.0)

    # ---- chiusura ----
    t3 = tl.t
    tl.broll(raw("0137"), 0.5, 2.6, gain=0.3)
    tl.broll(raw("0138"), 1.0, 3.0, gain=0.3)
    vo(tl, "vo_14", [(mimo("142648"), 10.0), (mimo("151316"), 2.0)])
    vo(tl, "vo_15", [(raw("0094"), 20.0), (raw("0108"), 4.0)], tail=0.6)
    tl.speech(raw("0143"), [(0.0, 9.0)], speed=1.1)
    tl.clip(logo_card(raw("0143"), 8.0, 3.5, tl.W, tl.H, f"{OUT}/fine_logo_{tl.W}x{tl.H}.mp4"))
    tl.music(t3, tl.t, M_FLIGHT, offset=60.0, level=0.42, fin=1.0, fout=2.0)  # niente "chitarrina"


def short2(tl):
    tl.speech(raw("0076"), [(24.2, 28.35)], cx=0.45,
              subs=[(24.2, 26.5, "No, no, di notte."), (26.5, 28.35, "Di notte. Alle tre si comincia.")])
    t0 = vo(tl, "vo_s2", [(raw("0094"), 3.0), (raw("0093"), 20.0)])
    tl.speech(raw("0076"), [(63.8, 66.8)], cx=0.45, subs=[(63.8, 65.6, "Trent'anni di pesca."), (65.6, 66.8, "Tre, zero. Sì.")])
    tl.speech(raw("0081"), [(21.9, 24.7)], cx=0.5, subs=[(21.9, 24.7, "Tutti i giorni, a pescare.")])
    tl.broll(raw("0121"), 0.5, 1.6, gain=0.4)
    tl.music(t0, tl.t, M_HOME, offset=40.0, level=0.4)
    tl.clip(sigla(tl.W, tl.H, "9x16"), audio=True)


def short3(tl):
    t0 = vo(tl, "vo_s3", [(raw("0117"), 3.0), (raw("0126"), 6.0)])
    tl.speech(raw("0086"), [(0.6, 2.95), (16.15, 20.1)], speed=1.1)
    tl.speech(raw("0091"), [(3.3, 7.8)], speed=1.1)
    tl.speech(raw("0122"), [(0.0, 3.5)], speed=1.1)
    tl.music(0, tl.t, M_FLIGHT, offset=12.0, level=0.4)
    tl.clip(sigla(tl.W, tl.H, "9x16"), audio=True)


# ---------- trailer (teaser in stile film: v2 dopo il feedback di Manuel) ----------
BEAT = 0.4528          # Taking Flight, 132.5 bpm
M_OFF = 3.414          # attacco del brano su un battere, prima della crescita
SIGLA_VO = f"{ROOT}/assets/sigla/frase_sigla_manuel.m4a"


def _to_beat(tl, nbeats):
    """Durata che porta il prossimo taglio su un battito (almeno ~nbeats battiti)."""
    import math
    target = math.ceil((tl.t + nbeats * BEAT - 0.2 * BEAT) / BEAT) * BEAT
    return target - tl.t


def montage(tl, shots, beats):
    for (src, a, cx), nb in zip(shots, beats):
        tl.broll(src, a, _to_beat(tl, nb), gain=0.0, cx=cx)


def trailer(tl):
    """Un solo suono per volta: musica sui montaggi, una voce per volta, poi sigla con la frase di Manuel."""
    montage(tl, [(raw("0117"), 3.0, .5), (raw("0119"), 0.3, .45), (raw("0086"), 20.0, .5), (raw("0121"), 0.5, .5)],
            [2, 2, 2, 2])
    tl.speech(raw("0076"), [(26.45, 28.35)], subs=[(26.45, 28.35, "Di notte. Alle tre si comincia.")], cx=0.45)
    montage(tl, [(raw("0085"), 0.3, .5), (raw("0093"), 25.0, .5), (raw("0123"), 0.5, .4), (raw("0109"), 5.0, .5)],
            [2, 2, 1, 1])
    tl.speech(raw("0076"), [(316.0, 319.1), (343.3, 345.1)], cx=0.45,
              subs=[(316.0, 319.1, "Cristiani, induisti, musulmani."), (343.3, 345.1, "È un posto in pace.")])
    montage(tl, [(raw("0086"), 27.0, .5), (raw("0089"), 3.5, .5), (raw("0120"), 3.0, .5), (raw("0118"), 12.0, .62),
                 (raw("0124"), 1.6, .42), (raw("0126"), 10.0, .5)], [1, 1, 1, 1, 1, 1])
    tl.speech(raw("0091"), [(3.3, 7.8)], speed=1.1)
    tl._add(maps(tl.W, tl.H), 0, 4.5, speed=1.8, audio=False, grade="null")
    # sigla: lampi sotto "Il mondo, raccontato da chi lo vive", logo su "Questo è Voci Vere"
    t_s = tl.t
    tl.vos.append(dict(file=SIGLA_VO, a=1.70, b=5.75, speed=1.0, t=t_s + 0.05))
    montage(tl, [(raw("0122"), 1.0, .5), (raw("0076"), 40.0, .42), (raw("0081"), 95.0, .5), (raw("0117"), 15.0, .5),
                 (raw("0143"), 3.0, .5)], [1, 1, 1, 1, 1])
    tl.clip(logo_card(raw("0143"), 3.4, 2.9, tl.W, tl.H, f"{OUT}/sigla_logo2_{tl.W}x{tl.H}.mp4"))
    tl.music(0, tl.t, M_FLIGHT, offset=M_OFF, level=0.8, fin=0.05, fout=1.2)



def reel_A(tl):
    """Alle tre di notte: la giornata del pescatore."""
    tl.speech(raw("0076"), [(24.2, 28.35)], cx=0.45,
              subs=[(24.2, 26.5, "No, no, di notte."), (26.5, 28.35, "Di notte. Alle tre si comincia.")])
    montage(tl, [(raw("0085"), 0.3, .5), (raw("0093"), 3.0, .5), (raw("0094"), 3.0, .5), (raw("0123"), 0.5, .4)],
            [2, 2, 2, 2])
    tl.speech(raw("0076"), [(63.8, 66.8)], cx=0.45, subs=[(63.8, 65.6, "Trent'anni di pesca."), (65.6, 66.8, "Tre, zero. Sì.")])
    montage(tl, [(raw("0081"), 50.0, .5), (mimo("142648"), 3.0, .5), (raw("0121"), 0.5, .5), (raw("0119"), 0.3, .45)],
            [1, 1, 1, 1])
    tl.speech(raw("0081"), [(21.9, 24.7)], cx=0.5, subs=[(21.9, 24.7, "Tutti i giorni, a pescare.")])
    montage(tl, [(raw("0117"), 3.0, .5), (raw("0126"), 10.0, .5)], [2, 3])
    tl.music(0, tl.t, M_FLIGHT, offset=M_OFF + 8 * BEAT * 4, level=0.8, fin=0.05, fout=1.5)


def reel_B(tl):
    """Il pesce da 50 chili: il mercato."""
    tl.speech(raw("0086"), [(0.6, 4.5)], speed=1.1)
    montage(tl, [(raw("0117"), 8.0, .5), (raw("0126"), 6.0, .5), (raw("0119"), 0.3, .45), (raw("0086"), 27.0, .5),
                 (raw("0089"), 3.5, .5), (raw("0120"), 3.0, .5)], [1, 1, 1, 1, 1, 1])
    tl.speech(raw("0091"), [(0.45, 7.8)], speed=1.1)
    montage(tl, [(raw("0121"), 0.5, .5), (raw("0095"), 3.0, .5), (raw("0109"), 5.0, .5), (raw("0110"), 1.0, .5)],
            [1, 1, 2, 2])
    tl.speech(raw("0122"), [(0.0, 3.5)], speed=1.1)
    tl.music(0, tl.t, M_FLIGHT, offset=M_OFF + 8 * BEAT * 8, level=0.8, fin=0.05, fout=1.2)


def reel_C(tl):
    """Un posto in pace: la convivenza tra religioni."""
    tl.speech(raw("0076"), [(316.0, 319.1)], cx=0.45, subs=[(316.0, 319.1, "Cristiani, induisti, musulmani.")])
    montage(tl, [(raw("0118"), 12.0, .62), (raw("0124"), 1.6, .42), (raw("0125"), 1.0, .45), (raw("0120"), 3.0, .5)],
            [2, 2, 2, 2])
    tl.speech(raw("0076"), [(322.05, 325.8)], cx=0.45, subs=[(322.05, 325.8, "Vanno molto d'accordo. Amici.")])
    montage(tl, [(raw("0117"), 15.0, .5), (raw("0126"), 10.0, .5), (raw("0119"), 0.3, .45), (raw("0093"), 25.0, .5)],
            [1, 1, 1, 1])
    tl.speech(raw("0076"), [(343.3, 347.0)], cx=0.45, subs=[(343.3, 347.0, "È un posto in pace. Un posto in pace.")])
    montage(tl, [(mimo("145004"), 1.0, .5), (mimo("151316"), 0.5, .5)], [2, 2])
    tl.speech(raw("0076"), [(146.05, 150.35)], cx=0.45,
              subs=[(146.05, 147.2, "Vengono mille persone."), (147.4, 150.35, "Per tutti c'è il cibo gratis.")])
    montage(tl, [(raw("0117"), 3.0, .5)], [3])
    tl.music(0, tl.t, M_FLIGHT, offset=M_OFF + 8 * BEAT * 12, level=0.8, fin=0.05, fout=1.5)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    prev = "--preview" in sys.argv
    jobs = {"long": (long_video, False), "teaser": (teaser, True), "trailer": (trailer, True),
            "reelA": (reel_A, True), "reelB": (reel_B, True), "reelC": (reel_C, True), "short2": (short2, True), "short3": (short3, True)}
    for name, (fn, vert) in jobs.items():
        if what != name and not (what == "all" and name != "trailer"):
            continue
        W, H = ((540, 960) if vert else (960, 540)) if prev else ((1080, 1920) if vert else (3840, 2160))
        tag = f"{name}_{W}x{H}"
        tl = Timeline(W, H, f"{OUT}/{tag}_work")
        fn(tl)
        print(f"== {name}: {len(tl.shots)} inquadrature, {tl.t:.1f} s")
        tl.render(f"{OUT}/VociVere_mercato_{tag}.mp4", crf=18 if not prev else 23, preset="medium" if not prev else "veryfast")
