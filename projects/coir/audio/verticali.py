#!/usr/bin/env python3
"""Verticali di coir con la musica e i segni della chat Audio (Manuel 9/11: "ci pensi tu", senza passare da Montaggio).

    python3 projects/coir/audio/verticali.py teaser|madeinindia|indietro|premilla|1975 [--preview]
Il video resta QUELLO APPROVATO su Drive (montati/coir, copiato senza ricodifica: immagini, testi e sottotitoli
identici); da projects/coir/build.py (non toccato) si rifà solo l'audio, con la voce negli stessi tempi, e lo si mette
sul video approvato. Audio come da regole/formato_reel.md:
- musica del verticale (<video>_musica.flac) costante e bassissima sotto la voce, un po' più su sul finale senza voce;
- mentre suona la rivelazione la musica scende di 6 dB, poi torna;
- cue_gancio da 0:00, cue_rivelazione sulla prima immagine della rivelazione (brief di Copy), cue_chiusura subito
  sulla fine della voce fino all'ultimo fotogramma del logo.
Girato in work/coir/raw (solo le clip dei verticali + voiceoververticali.m4a), parole in work/coir/words.json.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
if "--preview" not in sys.argv:          # il video si rende piccolo: serve solo il suo audio
    sys.argv.append("--preview")
sys.path.insert(0, os.path.join(HERE, ".."))
import build as B  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "audio", "musica"))
import coir_verticali as CV  # noqa: E402

AUD = HERE
RIV = {"teaser": "0021", "made_in_india": "0542", "indietro": "0074", "premilla": "0016", "1975": "0527"}
PREF = {"made_in_india": "madeinindia"}
MUS, MUS_UP, DIP = 0.08, 0.17, 0.5          # sotto la voce, finale senza voce, -6 dB durante la rivelazione
CUE, CUE_END = 0.24, 0.45
D_RIV = 4.0
STILE = {"teaser": "A", "madeinindia": "A", "indietro": "A", "premilla": "A", "1975": "A"}   # bozze scelte
APPROVATI = f"{B.WORK}/drive"         # verticali approvati scaricati da Drive montati/coir


def musica_su_misura(p, dur):
    """La musica scelta, ricomposta lunga quanto il reel: il crescendo arriva sul finale, la coda sul logo."""
    wav = f"{B.OUT}/audio_{p}_musica_{dur:.2f}.wav"
    out = wav[:-4] + ".flac"
    CV.scrivi(CV.musica(p, STILE[p], dur), wav)
    CV.flac(wav, out, -20)
    return out


def cue_wav(name, d, fout):
    out = f"{B.OUT}/audio_{name}_{d:.2f}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{AUD}/{name}.flac", "-t", f"{d:.3f}", "-af",
                    f"apad,atrim=0:{d:.3f},afade=t=out:st={max(0, d - fout):.3f}:d={fout}", "-ac", "2", "-ar", "48000",
                    out], check=True)
    return out


def vfinish(r, name, track, t_b, end, offset=0.0):
    tl = r.tl; p = PREF.get(name, name)
    mus = musica_su_misura(p, end + 0.5)
    key = RIV[name]
    t_r = next(s["t"] for s in tl.shots if f"_{key}_" in os.path.basename(s["src"]))
    t_r2 = min(t_r + D_RIV, t_b)
    # musica: tre tratti allineati allo stesso tempo del file (nessun salto), livello costante a gradini morbidi
    tl.music(0.0, t_r + 0.15, mus, offset=0.0, level=MUS, fin=0.05, fout=0.3, duck=False, norm=False)
    tl.music(t_r, t_r2 + 0.15, mus, offset=t_r, level=MUS * DIP, fin=0.3, fout=0.3, duck=False, norm=False)
    tl.music(t_r2, t_b + 0.3, mus, offset=t_r2, level=MUS, fin=0.4, fout=0.3, duck=False, norm=False)
    tl.music(t_b, end, mus, offset=t_b, level=MUS_UP, fin=0.3, fout=1.0, duck=False, norm=False)
    tl.sfx(0.0, cue_wav(f"{p}_cue_gancio", 3.5, 0.5), CUE)
    tl.sfx(t_r, cue_wav(f"{p}_cue_rivelazione", D_RIV, 0.8), CUE)
    tl.sfx(t_b - 0.05, cue_wav(f"{p}_cue_chiusura", end - t_b + 0.05, 1.0), CUE_END)
    print(f"{name}: rivelazione {t_r:.2f} s, fine voce {t_b:.2f} s, fine {end:.2f} s", flush=True)
    tl.audio_map = {B.VOV: B.cleaned(B.VOV, B.VOCE)}
    tl.nat_af = "highpass=f=90"
    W, H = r.W, r.H
    tmp = r.render(f"{B.OUT}/audio_{name}_{W}x{H}.mp4", crf=30, preset="veryfast")
    app = f"{APPROVATI}/VociVere_coir_{name}_1080x1920.mp4"
    out = f"{B.OUT}/VociVere_coir_{name}_1080x1920.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", app, "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "alimiter=limit=0.84:level=false", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
    return out


B.vfinish = vfinish

if __name__ == "__main__":
    what = [a for a in sys.argv[1:] if not a.startswith("--")]
    for w in what:
        print({"teaser": B.teaser, "madeinindia": B.madeinindia, "indietro": B.indietro, "premilla": B.premilla,
               "1975": B.r1975}[w]())
