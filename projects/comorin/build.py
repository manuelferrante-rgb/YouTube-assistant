#!/usr/bin/env python3
"""Capo Comorin, Kanyakumari (4/11): 4 reel verticali 9:16 nel formato meenakshi (regole/formato_reel.md).

    python3 projects/comorin/build.py cocco|canna|statua|mari [--preview]
Girato e VO in work/comorin/raw (cartella Drive 1z5BA2MoG69ExGT6ivPb9VAcbxV25VVmI, rclone). Sequenze e testi di
Copy in copioni/comorin_testi.md ("PER MONTAGGIO"), musica e segni di Audio in projects/comorin/audio/ (LEGGIMI),
girato e scelte in projects/comorin/girato.md.
Cocco e tre mari sono eccezioni (Manuel 4/11): senza voce e senza sottotitoli, una sola scritta fissa; il tre mari
dura 8 s, gira in loop e non ha il logo finale.
Manuel 4/11: in cocco e canna solo le persone che lavorano, mai Manuel né la sua ragazza (fuori 135850, 140944,
140244 e in 135906 tutto dopo 4.4 s tranne 7.9-11.0; 140138 solo da 3.5 a 26; 140346 da 2 s; 140828 fino a 4.8;
122458 solo da 12 s).
"""
import glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, f"{ROOT}/tools")
from doc_render import run
from reel_kit import Reel
from voice_clean import cleaned
import reel_close as RC

PREVIEW = "--preview" in sys.argv
WORK = f"{ROOT}/work/comorin"
R = f"{WORK}/raw"
OUT = f"{WORK}/out"
AUD = f"{ROOT}/projects/comorin/audio"
VO_CANNA = f"{R}/SH 179.m4a"         # Manuel ha mandato due file: canna e statua
VO_STATUA = f"{R}/SH 179 2.m4a"
os.makedirs(OUT, exist_ok=True)

MUS_LEVEL = 0.08                     # bassissima e costante sotto il VO (come meenakshi)
MUS_UP = 0.17                        # sul finale senza voce
CTA = "Ascolta altre voci, su"
FLIP = "hflip,vflip,eq=contrast=1.03:saturation=1.05"   # 122458 girata capovolta
PAD = (0.03, 0.06)                   # niente respiri tra le frasi (formato reel)


def C(tag):
    """Clip DJI del 4/11 per ora di ripresa HHMMSS, o clip iPhone (IMG_xxxx)."""
    m = glob.glob(f"{R}/dji_mimo_20261104_{tag}_*") if tag[0].isdigit() else glob.glob(f"{R}/{tag}.MOV")
    assert len(m) == 1, (tag, m)
    return m[0]


def cue(tl, t, name, d, gain, fout=0.5):
    """Segno melodico della chat Audio, lungo d secondi con coda sfumata."""
    out = f"{OUT}/{name}_{d:.2f}.wav"
    if not os.path.exists(out):
        run(["ffmpeg", "-v", "error", "-y", "-i", f"{AUD}/{name}.flac", "-t", f"{d:.3f}", "-af",
             f"afade=t=out:st={d - fout:.3f}:d={fout}", "-ac", "2", "-ar", "48000", out])
    tl.sfx(t, out, gain)


def phrase(a, b, text, times, cut=()):
    """Frase del VO (tratto di voce misurato a 10 ms sulla voce pulita) con le parole del copione: tempi dalla
    trascrizione, la prima parola non prima dell'inizio del tratto."""
    ws = list(zip(text.split(), times))
    ws[0] = (ws[0][0], max(ws[0][1], a))
    return (a, b, ws, list(cut))   # cut: tratti tolti dentro la frase (pause, parole ripetute), misurati a 10 ms


# CANNA (SH 179.m4a): frasi riascoltate a pezzi sulla voce pulita, testo uguale alla registrazione
C1 = phrase(2.58, 5.47, "I greci di Alessandro Magno la chiamavano miele senza api.",
            [2.42, 2.58, 2.9, 2.98, 3.46, 3.86, 3.94, 4.42, 4.9, 5.22])
C2 = phrase(5.75, 8.33, "È la canna da zucchero, e qui la spremono al momento.",
            [5.62, 5.78, 5.86, 6.18, 6.34, 6.98, 7.06, 7.14, 7.3, 7.86, 8.02], cut=[(6.76, 6.92)])
C3 = phrase(8.71, 11.41, "Passa nei rulli, si piega, si ripassa, finché non resta secca.",
            [8.5, 8.82, 8.98, 9.38, 9.46, 9.86, 9.94, 10.34, 10.66, 10.74, 11.06])
C4 = phrase(11.73, 14.53, "E la parola zucchero viene dal sanscrito, sharkara.",
            [11.62, 11.78, 11.86, 12.26, 12.82, 13.06, 13.22, 13.86])
C5 = phrase(14.96, 19.31, "Perché lo zucchero in cristalli l'hanno inventato qui, in India, più di 1500 anni fa.",
            [14.74, 15.06, 15.22, 15.62, 15.7, 16.18, 16.5, 16.9, 17.14, 17.3, 17.62, 17.78, 17.94, 18.9, 19.14])

# STATUA (SH 179 2.m4a): "Poi lui" ripetuto tre volte con "Ripeto": si usa l'ultima presa intera (28.07)
S1 = phrase(3.14, 6.15, "Alta 133 piedi, uno per ogni capitolo del suo libro.",
            [2.98, 3.54, 4.26, 4.66, 4.82, 4.98, 5.22, 5.62, 5.7, 5.86])
S2 = phrase(6.45, 9.03, "Per arrivarci si prende la barca, la punta più a sud dell'India.",
            [6.26, 6.5, 6.98, 7.06, 7.3, 7.38, 7.86, 7.94, 8.18, 8.34, 8.42, 8.66])
S3 = phrase(9.34, 14.09, "Prima c'è lo scoglio di Vivekananda. Si racconta che nel 1892 ci arrivò a nuoto.",
            [9.22, 9.54, 9.7, 9.86, 10.18, 10.26, 11.22, 11.38, 11.7, 11.86, 12.02, 13.06, 13.22, 13.54, 13.7], cut=[(11.04, 11.21)])
S4 = phrase(28.07, 33.18, "Poi lui. Thiruvalluvar, poeta tamil. Visse si racconta, quasi duemila anni fa.",
            [27.91, 28.23, 28.96, 29.91, 30.31, 30.87, 31.35, 31.51, 32.07, 32.31, 32.87, 33.03], cut=[(28.56, 28.93), (31.23, 32.05)])
S5 = phrase(33.66, 39.41, "Scrisse il Thirukkural: 1330 versi su come si vive. La virtù, la ricchezza, l'amore.",
            [33.71, 34.27, 34.35, 35.47, 36.35, 36.75, 36.91, 37.07, 37.23, 37.71, 37.87, 38.35, 38.51, 38.99], cut=[(35.32, 35.49), (37.52, 37.73)])
S6 = phrase(40.18, 45.77, "Il piedistallo è alto 38 piedi, come i capitoli sulla virtù. Sopra, la ricchezza e l'amore.",
            [40.03, 40.19, 40.91, 41.07, 41.47, 41.95, 42.27, 42.43, 42.51, 43.07, 43.39, 44.11, 44.51, 44.67, 45.15, 45.31], cut=[(43.70, 44.08)])
S7 = phrase(47.54, 49.17, "E tutto intorno, solo oceano.", [47.54, 47.56, 47.88, 48.36, 48.6])


def word_t(line, w):
    return next(t for x, t in line[2] if x.startswith(w))


def at(t0, line, t_src):
    """Tempo nel montato di un istante della frase (titoli sulla parola), tolti i tratti tagliati prima."""
    gone = sum(min(cb, t_src) - ca for ca, cb in line[3] if t_src > ca)
    return t0 + (t_src - (line[0] - PAD[0])) - gone


def narr_cuts(line):
    """narr() allarga di suo i tagli (+0.12 s all'inizio, -0.06 s alla fine): qui si compensa, così si toglie
    esattamente il tratto misurato."""
    return [(ca - 0.12, cb + 0.06) for ca, cb in line[3]]


def logo_card(W, H, d, src, a, grade="eq=contrast=1.03:saturation=1.05", cx=0.5, speed=1.0):
    """Logo chiaro (70%) che sfuma sopra l'ultima persona, che continua sotto un velo nero leggero (35%)."""
    out = f"{OUT}/logo_card_{os.path.basename(src)[:26]}_{a:.2f}_{d:.2f}_{speed:.2f}_{W}x{H}.mp4"
    lw = int(W * 0.7) // 2 * 2
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d * speed + 0.5:.3f}", "-i", src, "-loop", "1", "-t", f"{d:.3f}",
         "-i", f"{ROOT}/assets/brand/logo_vocivere_trasparente_chiaro.png", "-filter_complex",
         f"[0:v:0]crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{cx}-ih*9/32))':0,scale={W}:{H}:flags=lanczos,setpts=(PTS-STARTPTS)/{speed},fps=30,{grade},"
         "tpad=stop_mode=clone:stop_duration=2[v0];"
         f"color=c=black@0.35:s={W}x{H}:r=30:d={d:.3f},format=rgba,fade=t=in:st=0:d=0.5:alpha=1[k];"
         "[v0][k]overlay=shortest=1[bg];"
         f"[1]scale={lw}:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[l];[bg][l]overlay=(W-w)/2:(H-h)/2:shortest=1,"
         "format=yuv420p", "-an", "-t", f"{d:.3f}", "-r", "30", "-c:v", "libx264", "-crf", "16", out])
    return out


def faster(src, out, k):
    """Tutto il video accelerato di k (formato reel: 1.1x qui, mai in CapCut)."""
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", f"[0:v]setpts=PTS/{k},fps=30[v];[0:a]atempo={k}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out])
    return out


def size():
    return (540, 960) if PREVIEW else (1080, 1920)


def finish(r, name):
    W, H = r.W, r.H
    out = f"{OUT}/VociVere_comorin_{name}_{W}x{H}.mp4"
    one = r.render(out.replace(".mp4", "_1x.mp4"), crf=16 if W == 1080 else 24, preset="medium" if W == 1080 else "veryfast")
    if os.environ.get("PLAN"):
        return one
    return faster(one, out, 1.1)


# ---------------------------------------------------------------- reel 1: cocco (senza voce, a tempo di musica)
def cocco():
    """Montato sulla griglia della musica di Audio (battuta 2 s, colpi ogni 0.5 s, tempi prima del 1.1x).
    I tagli col machete a 1.35x: un colpo ogni ~0.5 s, come i colpi della musica."""
    W, H = size()
    r = Reel(f"{OUT}/reel_cocco_{W}_work", W, H, speed=1.0, gap=0.0, amb=0.0, cap_box=True)
    tl = r.tl
    V = 0.58                                                    # in 135736 il venditore sta a destra del centro
    # v4 (Manuel 4/11): ~10 s. Lui taglia tanto, lo dà, taglia ancora, la signora seduta che lo apre, di nuovo lui
    # che taglia SENZA scritta, poi la chiusura. Tagli sui battere della musica (battuta 2 s, colpi ogni 0.5 s)
    r.own(C("135736"), 3.62, cx=V)(1.0)                         # 0-1 GANCIO: machete già alzato, il colpo a 0.2 s
    r.own(C("135906"), 7.9, speed=1.35)(2.0)                    # 1-3 prende il cocco e taglia (solo lui, fino a 10.6)
    r.own(C("135906"), 2.3)(1.0)                                # 3-4 lo dà al cliente
    r.own(C("135736"), 8.95, cx=V, speed=1.35)(1.0)             # 4-5 taglia di nuovo
    r.own(C("140138"), 11.0)(1.5)                               # 5-6.5 la signora seduta che lo apre (solo mani)
    t_v = r.t
    r.own(C("135906"), 0.0, speed=1.35)(1.5)                    # 6.5-8 di nuovo lui che taglia, senza scritta
    t_b = r.t
    # chiusura stabile (Manuel 5/11): scritta subito, logo 0.8 s dopo; lui continua sotto il velo, mai oltre 4.4 s del clip
    r.own(C("135906"), 1.5 * 1.35, speed=1.35)(RC.LOGO_DELAY)
    r.gen(RC.logo_card(OUT, W, H, 2.4, C("135906"), (1.5 + RC.LOGO_DELAY) * 1.35, speed=0.55, variant="A"))(2.4)
    end = r.t
    r.title(0.0, t_v, "Prendi, taglia, porgi. Ricomincia", "Tag", 400)
    r.title(t_b, end, RC.CTA, RC.VARIANTS["A"]["style"], 400)
    # musica: il groove fino alla battuta 8.0, poi il finale del brano (da 16.0, anche lui inizio di battuta)
    tl.music(0.0, t_b + 0.02, f"{AUD}/musica_cocco.flac", offset=0.0, level=1.0, fin=0.01, fout=0.02, duck=False, norm=False)
    tl.music(t_b, end, f"{AUD}/musica_cocco.flac", offset=16.0, level=1.0, fin=0.02, fout=0.6, duck=False, norm=False)
    tl.nat_af = "highpass=f=90"
    return finish(r, "reel1_cocco")


# ---------------------------------------------------------------- reel 2: canna
def canna():
    W, H = size()
    r = Reel(f"{OUT}/reel_canna_{W}_work", W, H, speed=1.0, gap=0.0, amb=0.0, cap_box=True)
    tl = r.tl
    say = lambda line, vis: r.narr(VO_CANNA, line[0], line[1], vis, words=line[2], pad=PAD, cuts=narr_cuts(line))
    # 1. GANCIO: la ruota che gira e le canne che entrano, poi le canne intere
    say(C1, [(r.own(C("140516"), 14.2), 1.1), (r.own(C("140434"), 1.7), None)])
    r.title(0.0, r.t, "Miele senza api", "Tag", 400)
    cue(tl, 0.0, "cue_canna_gancio", 3.5, 0.24)
    # 2. lui spinge la canna nei rulli, il succo nel colino
    say(C2, [(r.own(C("140434"), 14.0), 1.5), (r.own(C("140434"), 34.5), None)])
    # 3. RIVELAZIONE: piega la canna spremuta e la ripassa (gesto intero, 1.5x)
    t3 = say(C3, [(r.own(C("140516"), 4.0, speed=1.5), None)])
    cue(tl, t3, "cue_canna_rivelazione", 4.5, 0.24, fout=0.8)
    # 4. il succo versato dal colino; titolo sulla parola
    t4 = say(C4, [(r.own(C("140808"), 1.0), None)])
    t_sk = at(t4, C4, word_t(C4, "sharkara"))
    # 5. la signora che riempie i bicchieri, poi le canne nei rulli da vicino
    t5 = say(C5, [(r.own(C("140828"), 0.3, cx=0.3), 2.2), (r.own(C("140434"), 28.2), None)])
    r.title(t_sk, t5 + 1.2, "Sanscrito: śarkarā", "Tag", 400)     # resta un po' anche sulla signora
    r.title(at(t5, C5, word_t(C5, "più")), r.t, "Più di 1500 anni fa", "Tag", 400)
    t_b = r.t
    r.cap_stop.append(t_b)
    _, end = RC.close(r, OUT, C("140622"), 0.3, variant="B")       # lui ai rulli; logo 0.8 s dopo la scritta (5/11)
    cue(tl, t_b - 0.05, "cue_canna_chiusura", end - t_b + 0.05, 0.45, fout=1.0)   # subito sulla fine della voce: niente buco
    music(tl, "musica_canna", t_b, end)
    tl.audio_map = {VO_CANNA: cleaned(VO_CANNA, f"{WORK}/voce")}
    tl.nat_af = "highpass=f=90"
    return finish(r, "reel2_canna")


def music(tl, name, t_b, end):
    tl.music(0.0, t_b + 0.3, f"{AUD}/{name}.flac", offset=0.0, level=MUS_LEVEL, fin=0.05, fout=0.3, duck=False, norm=False)
    tl.music(t_b, end, f"{AUD}/{name}.flac", offset=t_b, level=MUS_UP, fin=0.1, fout=1.0, duck=False, norm=False)


# ---------------------------------------------------------------- reel 3: statua
def statua():
    W, H = size()
    r = Reel(f"{OUT}/reel_statua_{W}_work", W, H, speed=1.0, gap=0.0, amb=0.0, cap_box=True)
    tl = r.tl
    say = lambda line, vis: r.narr(VO_STATUA, line[0], line[1], vis, words=line[2], pad=PAD, cuts=narr_cuts(line))
    # 1. GANCIO: la statua dal basso, enorme, poi statua e piedistallo
    say(S1, [(r.own(C("130140"), 0.0), 1.3), (r.own(C("132340"), 0.0), None)])
    r.title(0.0, r.t, "133 piedi, 133 capitoli", "Tag", 400)
    cue(tl, 0.0, "cue_statua_gancio", 3.5, 0.24)
    # 2. la barca: la grata del molo, dentro il traghetto (122458 raddrizzata; da 2 a 11 s c'è una ragazza che può essere
    # quella di Manuel: si usa solo da 12 s, panche e finestrini)
    t2 = say(S2, [(r.own(C("121640"), 0.5), 0.9), (r.own(C("122458"), 17.2, grade=FLIP), None)])
    r.title(at(t2, S2, word_t(S2, "punta")) - 0.1, r.t, "La punta dell'India", "Tag", 400)
    # 3. lo scoglio di Vivekananda che si avvicina, i piedi nudi sulla pietra
    say(S3, [(r.own(C("123010"), 0.0), 2.6), (r.own(C("132602"), 0.0), None)])
    # 4. RIVELAZIONE: dal panorama la camera gira e trova la statua su "Poi lui"
    t4 = say(S4, [(r.own(C("130308"), 1.0), 2.6), (r.own(C("132332"), 0.0), None)])
    cue(tl, t4, "cue_statua_rivelazione", 4.5, 0.24, fout=0.8)
    r.title(at(t4, S4, word_t(S4, "Thiruvalluvar")), at(t4, S4, word_t(S4, "Visse")), "Thiruvalluvar", "Tag", 400)
    # 5. il muro con i versi, le scale di pietra
    say(S5, [(r.own(C("132230"), 0.0), 3.8), (r.own(C("130034"), 0.0), None)])
    # 6. il piedistallo e la statua che sale
    # Manuel 4/11: la statua una volta sola, poi da lontano (statua e piedistallo sul memoriale), poi l'oceano
    say(S6, [(r.own(C("130308"), 4.5), 3.0), (r.own(C("132340"), 0.0, speed=0.75), None)])
    # 7. la costa e il mare dalla roccia, le onde
    say(S7, [(r.own(C("130308"), 0.0), 0.8), (r.own(C("125410"), 0.2), None)])
    t_b = r.t
    r.cap_stop.append(t_b)
    # chiusura (Manuel 4/11): ferma sulla statua, nel tratto più stabile di 130308 (6.0-8.2 s, misurato con la
    # correlazione di fase: <0.3 px a fotogramma), rallentato a 0.45x; il logo sfuma sullo stesso tratto
    _, end = RC.close(r, OUT, C("130308"), 6.0, variant="A", speed=0.45,      # muta (atempo non va sotto 0.5)
                      own=r.gen(C("130308"), 6.0, speed=0.45, grade="eq=contrast=1.03:saturation=1.05"))
    cue(tl, t_b - 0.05, "cue_statua_chiusura", end - t_b + 0.05, 0.45, fout=1.0)   # subito sulla fine della voce: niente buco
    music(tl, "musica_statua", t_b, end)
    tl.audio_map = {VO_STATUA: cleaned(VO_STATUA, f"{WORK}/voce")}
    tl.nat_af = "highpass=f=90"
    return finish(r, "reel3_statua")


# ---------------------------------------------------------------- reel 4: tre mari (loop, 8.8 s prima del 1.1x)
def mari():
    """Arrivo veloce (~3.4 s), poi si resta sul mare. Dopo il 1.1x il video dura 8.00 s esatti (240
    fotogrammi) come la musica in loop di Audio (file da 8.00 s, messo DOPO il 1.1x con guadagno fisso a -14 LUFS e
    senza dissolvenze, così il giunto resta intatto). Loop senza stacco: si monta 0.3 s in più e gli ultimi 0.3 s
    sfumano nei primi 0.3 s del video, che poi parte da 0.3 s: l'ultimo fotogramma si attacca al primo."""
    W, H = size()
    X = 9                                                       # fotogrammi della dissolvenza del loop (0.3 s)
    r = Reel(f"{OUT}/reel_mari_{W}_work", W, H, speed=1.0, gap=0.0, amb=0.0, cap_box=True)
    # Manuel 4/11: solo le clip dell'iPhone del 3/11 (niente DJI): il sentiero verso il mare, il prato fino alla
    # scogliera, le onde sulla spiaggia, poi una sola inquadratura lunga sulle onde
    r.own(C("IMG_8759"), 0.3, speed=1.3)(1.1)                   # la strada che scende verso il mare
    r.own(C("IMG_8761"), 0.5, speed=1.3)(1.2)                   # il sentiero nel prato fino alla scogliera
    r.own(C("IMG_8762"), 2.0, speed=1.3)(1.1)                   # le onde sulla spiaggia
    t_sea = r.t
    r.own(C("IMG_8765"), 0.0, speed=0.9)((240 + X) * 1.1 / 30 - r.t)   # le onde, una sola inquadratura lunga
    r.title(0.0, t_sea, "Qui si incontrano 3 mari", "Tag", 400)
    # Manuel 4/11: sulle onde i tre mari, uno dopo l'altro (l'ultimo resta fino alla fine, dentro la dissolvenza del loop)
    seas = ["Golfo del Bengala", "Mar Arabico", "Oceano Indiano"]
    step = (r.t - X * 1.1 / 30 - t_sea) / 3
    for i, name in enumerate(seas):
        r.title(t_sea + i * step, t_sea + (i + 1) * step if i < 2 else r.t, name, "Tag", 400)
    one = finish(r, "reel4_tre_mari_video")
    if os.environ.get("PLAN"):
        return one
    out = f"{OUT}/VociVere_comorin_reel4_tre_mari_{W}x{H}.mp4"
    mus = f"{AUD}/musica_mari_loop_8s0.flac"
    m = json.loads(subprocess.run(["ffmpeg", "-hide_banner", "-i", mus, "-af", "loudnorm=I=-14:TP=-1:print_format=json",
                                   "-f", "null", "-"], capture_output=True, text=True).stderr.split("[Parsed_loudnorm")[-1].split("\n", 1)[1])
    g = min(-14 - float(m["input_i"]), -1 - float(m["input_tp"]))   # guadagno fisso, senza superare -1 dBTP
    run(["ffmpeg", "-v", "error", "-y", "-i", one, "-i", mus, "-filter_complex",
         f"[0:v]split[a][b];[a]trim=start_frame={X}:end_frame={240 + X},setpts=PTS-STARTPTS[body];"
         f"[b]trim=end_frame={X},setpts=PTS-STARTPTS[head];"
         f"[body][head]xfade=transition=fade:duration={X / 30:.4f}:offset={(240 - X) / 30:.4f},format=yuv420p[v];"
         f"[1:a]volume={g:.2f}dB[aud]", "-map", "[v]", "-map", "[aud]", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
         "-c:a", "aac", "-b:a", "256k", "-frames:v", "240", "-t", "8.0", "-movflags", "+faststart", out])
    return out


if __name__ == "__main__":
    print({"cocco": cocco, "canna": canna, "statua": statua, "mari": mari}[sys.argv[1]]())
