#!/usr/bin/env python3
"""Musiche e segni dei 5 verticali di coir (teaser, madeinindia, indietro, premilla, 1975), autore Voci Vere.
Stessa famiglia sonora del lungo (audio/musica/coir.py: fa minore, archi, spiccato, pizzicato, piano, motivo
fa-lab-sol), niente sotto 150 Hz, voci raddoppiate in alto per il telefono. Brief di Copy: copioni/coir_testi.md,
"PER AUDIO (verticali)".

    python3 audio/musica/coir_verticali.py <video> musica|gancio|rivelazione|chiusura <A|B|C> <out.wav>
    python3 audio/musica/coir_verticali.py <video> bozze <outdir>     # tutte le bozze + un mp4 nero per brano
"""
import argparse, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import SR, Track, pluck, hp_fft  # noqa: E402
import coir  # noqa: E402
from coir import CH, archi, spiccato, onda, piano_m  # noqa: E402

# carattere di ogni verticale (Copy, 6/11) -> brano del lungo riadattato: durata 25 s, crescendo dentro il brano
VIDEO = {
    "teaser": dict(prog=["Fm", "Db", "Fsus", "Fm", "Db", "Ab", "Eb", "Fsus"], bars=1,
                   bpm={"A": 92, "B": 88, "C": 96}, nota="acqua, attesa"),
    # sobria: armonia ferma (due accordi per giro), meno note; la rivelazione (sorriso in camera) si apre in la bemolle
    "madeinindia": dict(prog=["Fm", "Fm", "Db", "Eb", "Fm", "Cm", "Db", "Eb"], bars=1,
                        bpm={"A": 88, "B": 84, "C": 92}, nota="sobria", aperto="Fm", riv="Ab"),
    # passi lenti, regolare: un accordo ogni due battute, passo fermo; la rivelazione (la fila) si apre in mi bemolle
    "indietro": dict(prog=["Fm", "Eb", "Db", "Eb"], bars=2, bpm={"A": 84, "B": 80, "C": 88}, nota="passi lenti",
                     aperto="Fsus", riv="Eb"),
    # calda, intima: armonia che gira sul maggiore (re bemolle, la bemolle); rivelazione su Premilla in re bemolle
    "premilla": dict(prog=["Db", "Ab", "Fm", "Eb", "Db", "Ab", "Bbm", "Fsus"], bars=1,
                     bpm={"A": 80, "B": 76, "C": 84}, nota="calda, intima", aperto="Db", riv="Db"),
    # la più spoglia, niente tristezza: accordi lunghi, si apre in la bemolle (luce) sulle donne sedute
    "1975": dict(prog=["Fm", "Db", "Ab", "Eb"], bars=2, bpm={"A": 84, "B": 80, "C": 88}, nota="spoglia",
                 aperto="Fm", riv="Ab"),
}
CUE_DUR = {"gancio": 3.5, "rivelazione": 4.5, "chiusura": 5.5}


def musica(video, stile, dur=25.0):
    v = VIDEO[video]
    coir.BRANI["_v"] = dict(dur=dur, prog=v["prog"], bars=v["bars"], motivo=None, chiude=False)
    coir.STILI[stile] = v["bpm"][stile]
    return coir.brano("_v", stile, din=True)


def cue(kind, stile, bpm=92, aperto="Fsus", riv="Db"):
    """Segni brevi in fa minore. A archi + spiccato, B piano, C pizzicato + archi a ondate."""
    beat = 60 / bpm; T = Track(CUE_DUR[kind])
    if kind == "gancio":                # calmo, niente colpi: si apre e resta sospeso (Fsus)
        ch = CH[aperto]
        for j, n in enumerate(ch[2:]):
            T.add(archi(n + 12, 3.2, 3200, att=0.9, rel=1.0), 0.0, 0.05, pan=-0.4 + j * 0.4)
        if stile == "A":
            for s_, n in enumerate([ch[1], ch[3], ch[2] + 12, ch[3] + 12, ch[4] + 12, ch[3] + 12]):
                T.add(spiccato(n, 0.45 + 0.08 * s_), 0.05 + s_ * beat / 2, 0.1, pan=0.2 if s_ % 2 else -0.2)
        elif stile == "B":
            for s_, n in enumerate([65, 72, 77, 79]):
                T.add(piano_m(n, beat * (2.5 if s_ == 3 else 0.8), 0.45), 0.05 + s_ * beat * 0.6, 0.16, pan=0.1)
        else:
            for s_, n in enumerate([65, 72, 77, 79, 84, 79]):
                T.add(pluck(n, beat * 1.2, 0.994, 0.55), 0.05 + s_ * beat / 2, 0.09, pan=0.35 if s_ % 2 else -0.3)
            for j, n in enumerate(ch[2:]):
                T.add(onda(n + 12, beat * 2, 3200), 0.05 + beat, 0.05, pan=-0.3 + j * 0.3)
        return hp_fft(T.render(fade_in=0.02, fade_out=1.2, rev=0.4))
    if kind == "rivelazione":           # il fatto: sospensione che si apre su re bemolle maggiore
        for j, n in enumerate(CH["Fsus"][2:]):
            T.add(archi(n + 12, 1.6, 3000, att=0.4, rel=0.3), 0.0, 0.045, pan=-0.4 + j * 0.4)
        for j, n in enumerate(CH[riv][1:]):
            T.add(archi(n + 12, 3.0, 3400, att=0.3, rel=1.5), 1.3, 0.05, pan=-0.45 + j * 0.3)
        if stile == "A":
            for s_ in range(8):
                n = [68, 72, 77, 72][s_ % 4]
                T.add(spiccato(n, 0.5 + 0.05 * s_), 0.05 + s_ * beat / 2, 0.1, pan=0.2 if s_ % 2 else -0.2)
            T.add(piano_m(80, beat * 3, 0.5), 1.3, 0.14, pan=0.1)
        elif stile == "B":
            for s_, n in enumerate([68, 72, 73, 77, 80]):
                T.add(piano_m(n, beat * (3.0 if s_ == 4 else 0.7), 0.48), 0.05 + s_ * beat * 0.45, 0.15, pan=0.1)
                T.add(piano_m(n - 12, beat * 0.7, 0.3), 0.05 + s_ * beat * 0.45, 0.05)
        else:
            for s_ in range(12):
                n = [72, 77, 79, 77][s_ % 4] + (1 if s_ >= 6 and s_ % 4 == 2 else 0)
                T.add(pluck(n, beat * 0.6, 0.99, 0.6), 0.05 + s_ * beat / 4, 0.08, pan=0.35 if s_ % 2 else -0.3)
            T.add(piano_m(85, beat * 3, 0.45), 1.3, 0.11, pan=0.1); T.add(piano_m(77, beat * 3, 0.35), 1.3, 0.06)
        return hp_fft(T.render(fade_in=0.02, fade_out=1.5, rev=0.42))
    if kind == "chiusura":              # il motivo del lungo che si chiude sul fa (fa-lab-sol-fa), accordo che resta
        p = beat * 1.2
        for j, n in enumerate(CH["Fm"]):
            T.add(archi(n + 12 if j >= 2 else n, 5.0, 3000, att=0.8, rel=2.0), 0.0, 0.035, pan=-0.45 + j * 0.22)
        for i, n in enumerate([77, 80, 79, 77]):
            lunga = i == 3
            if stile == "C":
                T.add(pluck(n, p * (3 if lunga else 1.2), 0.995, 0.55), 0.1 + i * p, 0.13, pan=0.1)
                T.add(pluck(n - 12, p, 0.995, 0.4), 0.1 + i * p, 0.05)
            else:
                T.add(piano_m(n, p * (3.0 if lunga else 1.1), 0.5), 0.1 + i * p, 0.17, pan=0.1)
                T.add(piano_m(n - 12, p * (2.8 if lunga else 1.0), 0.35), 0.1 + i * p, 0.07, pan=0.1)
            if stile == "A":
                T.add(spiccato(n - 12, 0.55), 0.1 + i * p, 0.08, pan=-0.2)
        return hp_fft(T.render(fade_in=0.02, fade_out=1.8, rev=0.45))
    raise ValueError(kind)


def scrivi(x, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", out], input=x.astype("<f8").tobytes(), check=True)


def flac(wav, out, lufs):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", f"loudnorm=I={lufs}:TP=-2:linear=true",
                    "-ar", str(SR), "-c:a", "flac", out], check=True)


def mp4_bozze(files, titolo, out):
    """Un mp4 a schermo nero: le tre bozze una dopo l'altra (1.5 s di silenzio tra l'una e l'altra), lettera a
    schermo, ogni bozza a -14 LUFS (regola delle tre bozze, Manuel 6/11)."""
    inp, flt, parti, t, testo = [], [], [], 0.0, []
    for i, (lett, f) in enumerate(files):
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                 capture_output=True, text=True).stdout)
        inp += ["-i", f]
        flt.append(f"[{i}:a]loudnorm=I=-14:TP=-1.5:linear=true,aresample={SR},apad=pad_dur=1.5[a{i}]")
        parti.append(f"[a{i}]")
        testo.append(f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{lett}':fontsize=420:"
                     f"fontcolor=0xB68A4B:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t:.2f},{t + d + 1.5:.2f})'")
        t += d + 1.5
    flt.append("".join(parti) + f"concat=n={len(files)}:v=0:a=1[a]")
    titolo_f = (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{titolo}':fontsize=54:"
                f"fontcolor=white:x=(w-tw)/2:y=h*0.78")
    flt.append(f"color=black:s=1080x1920:r=25:d={t:.2f}," + ",".join(testo) + "," + titolo_f + "[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(flt), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", choices=list(VIDEO)); ap.add_argument("cosa"); ap.add_argument("a"); ap.add_argument("b", nargs="?")
    a = ap.parse_args()
    v = VIDEO[a.video]; bpm = v["bpm"]
    kw = dict(aperto=v.get("aperto", "Fsus"), riv=v.get("riv", "Db"))
    if a.cosa != "bozze":
        x = musica(a.video, a.a) if a.cosa == "musica" else cue(a.cosa, a.a, bpm[a.a], **kw)
        return scrivi(x, a.b)
    os.makedirs(a.a, exist_ok=True)
    for cosa in ("musica", "gancio", "rivelazione", "chiusura"):
        files = []
        for s in "ABC":
            w = f"{a.a}/{a.video}_{cosa}_{s}.wav"
            scrivi(musica(a.video, s) if cosa == "musica" else cue(cosa, s, bpm[s], **kw), w)
            flac(w, w[:-4] + ".flac", -20 if cosa == "musica" else -18)
            files.append((s, w[:-4] + ".flac"))
        mp4_bozze(files, f"coir {a.video} - {cosa}", f"{a.a}/BOZZE_{a.video}_{cosa}.mp4")
        print("ok", cosa, flush=True)


if __name__ == "__main__":
    main()
