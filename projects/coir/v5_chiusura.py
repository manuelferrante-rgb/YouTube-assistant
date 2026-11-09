#!/usr/bin/env python3
"""coir v5 (9/11, Manuel): la frase di chiusura "Il viaggio di Voci Vere... continua. Seguimi per scoprire le prossime
storie" non è più l'audio della ripresa 0102 (rumore di macchine, voce sgranata) ma la registrazione pulita di Manuel,
da usare d'ora in poi in tutti i lunghi: assets/voce/chiusura_vocivere.m4a (Drive "Coir", file "Chiusura").

Cambia solo l'audio: immagini, scritta animata e tempi del lungo v4 restano. Dal premix del v3/v4 (stesso audio) si
tolgono la vecchia voce e i due tratti della musica finale e si rimettono con la voce nuova (la musica sale un po' alla
fine della voce, come prima); poi stessa normalizzazione lineare e limitatore del montaggio. Video copiato.
    python3 projects/coir/v5_chiusura.py
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WK = f"{ROOT}/work/coir/out/long_work"
OUTD = f"{ROOT}/work/coir/out"
VIDEO = f"{OUTD}/VociVere_coir_long_4K_v4.mp4"
OUT = f"{OUTD}/VociVere_coir_long_4K_v5.mp4"
MUSIC = f"{ROOT}/projects/coir/audio/coir_finale.flac"
OLD_VOICE = f"{ROOT}/work/coir/voce/chiusura_DJI_20261106093350_0102_D_0.00_5.35.wav"
NEW_SRC = f"{ROOT}/assets/voce/chiusura_vocivere.m4a"
NEW_A, NEW_B = 0.88, 6.80               # la frase nel file di Manuel (misurata sull'energia a 10 ms)
SR = 48000
T_SIGLA = 398.7333                      # attacco della sigla finale (fine della chiusura)
T_VOICE = 390.4667 + 0.3                # inizio della voce di chiusura (scritta e voce insieme)
OLD_LEN = 5.35
MUS, MUS_UP = 0.11, 0.3                  # livelli della musica di build.py


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)
    return r


def render(src, chain, t0, total, out):
    """Una traccia come la fa doc_render (filtri, adelay, apad), stereo f32 per tutta la durata."""
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex",
         f"[0:a]{chain},adelay={int(t0 * 1000)}:all=1,apad=whole_dur={total:.3f}[a]", "-map", "[a]", "-ac", "2",
         "-ar", str(SR), "-c:a", "pcm_f32le", "-t", f"{total:.3f}", out])
    x, _ = sf.read(out, dtype="float64")
    return x


def voice_chain(L):
    return (f"atrim=0:{L:.3f},asetpts=PTS-STARTPTS,atempo=1.0,aresample=48000,afade=t=in:d=0.04,"
            f"afade=t=out:st={L - 0.08:.3f}:d=0.08")


def music_chain(offset, d, level, fin, fout):
    return (f"atrim={offset:.3f}:{offset + d:.3f},asetpts=PTS-STARTPTS,aresample=48000,volume={level},"
            f"afade=t=in:d={fin},afade=t=out:st={max(0, d - fout):.3f}:d={fout}")


def music_pair(L, t_e, total, tag):
    """I due tratti di coir_finale di build.py: sotto VO12 e la voce fino a 0.4 s dopo la sua fine, poi più su."""
    off = max(0.0, 34.6 - (T_SIGLA - t_e))
    end_v = T_VOICE + L
    a = render(MUSIC, music_chain(off, end_v + 0.4 - t_e, MUS, 1.0, 0.6), t_e, total, f"{WK}/_m1_{tag}.wav")
    b = render(MUSIC, music_chain(off + end_v - t_e, T_SIGLA - end_v, MUS_UP, 0.5, 1.0), end_v, total,
               f"{WK}/_m2_{tag}.wav")
    return a + b


def lufs(path):
    e = run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"]).stderr
    return float(json.loads(e.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])["input_i"])


def main():
    # voce nuova: passa-alto e riduzione leggera (la registrazione è già pulita), stesso livello della vecchia
    tmp = f"{WK}/_chiusura_new_raw.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", NEW_SRC, "-af",
         f"aformat=channel_layouts=mono,highpass=f=90,highpass=f=90,afftdn=nf=-40:nr=8,atrim=start_sample=1200,"
         f"asetpts=PTS-STARTPTS,atrim={NEW_A}:{NEW_B},asetpts=PTS-STARTPTS", "-ar", str(SR), tmp])
    old_l = lufs(OLD_VOICE)
    new_voice = f"{ROOT}/work/coir/voce/chiusura_vocivere_coir.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={old_l - lufs(tmp):.2f}dB,alimiter=limit=0.95:level=false",
         "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", new_voice])
    L = (NEW_B - NEW_A)
    total = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VIDEO]).stdout)
    t_e = json.load(open(f"{OUTD}/long_3840x2160.json"))["chapters"][-1][0]
    old = render(OLD_VOICE, voice_chain(OLD_LEN), T_VOICE, total, f"{WK}/_v_old.wav") + music_pair(OLD_LEN, t_e, total, "old")
    new = render(new_voice, voice_chain(L), T_VOICE, total, f"{WK}/_v_new.wav") + music_pair(L, t_e, total, "new")
    # il lungo consegnato ha già i click dei banner nell'audio: si corregge l'audio finale stesso, solo nel tratto della
    # chiusura, con lo stesso guadagno fisso che il montaggio ha dato al premix (lì il limitatore non lavora)
    m = json.loads(run(["ffmpeg", "-hide_banner", "-i", f"{WK}/premix.wav", "-af",
                        "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"]).stderr
                   .split("[Parsed_loudnorm")[-1].split("\n", 1)[1])
    G = 10 ** ((-14 - float(m["input_i"])) / 20)
    run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-map", "0:a:0", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_f32le",
         f"{WK}/_final_v4.wav"])
    fin, _ = sf.read(f"{WK}/_final_v4.wav", dtype="float64")
    n = min(len(fin), len(old), len(new))
    lo, hi = int((t_e - 1) * SR), n
    out = fin.copy()
    LAG = 95          # l'audio del file finale è 95 campioni (2 ms) dopo quello ricostruito (misurato: residuo -44 dB)
    out[lo:hi] += G * (new[lo - LAG:hi - LAG] - old[lo - LAG:hi - LAG])
    print(f"residuo della vecchia chiusura: {20 * np.log10(np.sqrt(((fin - 0)[lo:hi, 0] - G * old[lo - LAG:hi - LAG, 0])[int((T_VOICE - t_e + 1) * SR):int((T_SIGLA - t_e + 0.9) * SR)].std()) + 1e-9):.1f}")
    print(f"picco nel tratto: {20 * np.log10(np.abs(out[lo:hi]).max()):.1f} dBFS, guadagno {20 * np.log10(G):.2f} dB")
    out = np.clip(out, -0.98, 0.98)
    sf.write(f"{WK}/mix_v5.wav", out.astype(np.float32), SR, subtype="PCM_16")
    run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", f"{WK}/mix_v5.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-t", f"{total:.3f}", OUT])
    print(OUT)


if __name__ == "__main__":
    main()
