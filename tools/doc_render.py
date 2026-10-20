#!/usr/bin/env python3
"""Motore di montaggio per i documentari Voci Vere.

Uso da uno script di progetto:
    from doc_render import Timeline
    tl = Timeline(w=3840, h=2160, workdir=...)
    tl.speech(src, [(a, b), ...], speed=1.1, subs=[(a, b, "testo"), ...])   # parlato con audio originale
    tl.broll(src, a, dur, gain=0.3)                                          # immagini con suono d'ambiente
    tl.vo(vofile, a, b, shots=[(src, a), ...])                               # voiceover sopra immagini
    tl.music(t0, t1, track, offset, level)                                   # musica (si abbassa sotto la voce)
    tl.render(out)

Regole applicate: tagli a fotogramma esatto con audio e video della stessa durata (sincronia verificata),
parlato di Manuel a 1.1x, sottotitoli su una riga fissa sopra il video finale, musica in ducking sotto
voiceover e parlato, loudness finale -14 LUFS.
"""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FPS = 30
GRADE_DEFAULT = "eq=contrast=1.03:saturation=1.05"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(map(str, cmd))[:2000]); print(r.stderr[-3000:]); sys.exit(1)
    return r.stdout


def dur_of(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def ts(t):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


class Timeline:
    def __init__(self, w, h, workdir, sub_size=None, sub_margin=None):
        self.W, self.H, self.dir = w, h, workdir
        os.makedirs(workdir, exist_ok=True)
        self.shots, self.vos, self.musics, self.subs = [], [], [], []
        self.t = 0.0
        self.vertical = h > w
        k = h / 1080 if not self.vertical else w / 1080
        self.sub_size = sub_size or int(52 * k)
        self.sub_margin = sub_margin or (int(110 * k) if not self.vertical else int(560 * w / 1080))

    # ---------- elementi ----------
    def _add(self, src, a, dur_src, speed=1.0, gain=1.0, cx=0.5, zoom=1.0, grade=GRADE_DEFAULT, norm=False,
             fade=0.02, audio=True, still=False):
        n = max(1, round(dur_src / speed * FPS))
        d = n / FPS
        self.shots.append(dict(src=src, a=a, dur_src=dur_src, speed=speed, gain=gain, cx=cx, zoom=zoom, grade=grade,
                               norm=norm, fade=fade, audio=audio, n=n, d=d, t=self.t, still=still))
        self.t += d
        return self.t - d

    def speech(self, src, ranges, speed=1.0, subs=(), cx=0.5, zoom=1.0, grade=GRADE_DEFAULT, gain=1.0):
        """Parlato con audio originale; ogni range è un taglio. subs: (a, b, testo) in tempi della sorgente."""
        for a, b in ranges:
            t0 = self._add(src, a, b - a, speed=speed, gain=gain, cx=cx, zoom=zoom, grade=grade, norm=True)
            for sa, sb, txt in subs:
                lo, hi = max(sa, a), min(sb, b)
                if hi - lo > 0.15:
                    self.subs.append((t0 + (lo - a) / speed, t0 + (hi - a) / speed, txt))

    def broll(self, src, a, dur, gain=0.3, cx=0.5, zoom=1.0, grade=GRADE_DEFAULT, speed=1.0):
        self._add(src, a, dur * speed, speed=speed, gain=gain, cx=cx, zoom=zoom, grade=grade, fade=0.25)

    def clip(self, path, cx=0.5, audio=False, grade="null"):
        """Clip già pronta (mappa, sigla, cartello finale)."""
        self._add(path, 0, dur_of(path), gain=1.0, cx=cx, grade=grade, audio=audio)

    def vo(self, vofile, a, b, shots, speed=1.1, lead=0.25, tail=0.35, nat=0.22, weights=None):
        """Voiceover sopra una sequenza di immagini che ne coprono la durata (più un piccolo respiro)."""
        dvo = (b - a) / speed
        total = lead + dvo + tail
        weights = weights or [1] * len(shots)
        start = self.t
        for (sh, w) in zip(shots, weights):
            src, sa = sh[0], sh[1]
            cx = sh[2] if len(sh) > 2 else 0.5
            grade = sh[3] if len(sh) > 3 else GRADE_DEFAULT
            self._add(src, sa, total * w / sum(weights), gain=nat, cx=cx, grade=grade, fade=0.25)
        self.vos.append(dict(file=vofile, a=a, b=b, speed=speed, t=start + lead))
        return start

    def music(self, t0, t1, track, offset=0.0, level=0.35, fin=1.0, fout=1.5):
        self.musics.append(dict(t0=t0, t1=t1, track=track, offset=offset, level=level, fin=fin, fout=fout))

    # ---------- render ----------
    def _vf(self, s):
        W, H = self.W, self.H
        f = []
        if self.vertical:
            # ricomposizione verticale: ritaglio 9:16 centrato sul soggetto (cx = frazione orizzontale)
            f.append(f"crop=ih*9/16:ih:'max(0,min(iw-ih*9/16,iw*{s['cx']}-ih*9/32))':0")
        elif s["zoom"] != 1.0:
            z = s["zoom"]
            f.append(f"crop=iw/{z}:ih/{z}:'max(0,min(iw-iw/{z},iw*{s['cx']}-iw/{z}/2))':'(ih-ih/{z})*0.4'")
        f.append(f"scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=increase,crop={W}:{H}")
        if s["grade"] and s["grade"] != "null":
            f.append(s["grade"])
        f.append(f"setpts=(PTS-STARTPTS)/{s['speed']}")
        f.append(f"fps={FPS},tpad=stop_mode=clone:stop_duration=2,trim=end_frame={s['n']},setpts=PTS-STARTPTS")
        f.append("format=yuv420p")
        return ",".join(f)

    def _af(self, s):
        d = s["d"]
        f = []
        if s["speed"] != 1.0:
            f.append(f"atempo={s['speed']}")
        f.append("aresample=48000")
        if s["norm"]:
            f.append("highpass=f=80,afftdn=nf=-28,loudnorm=I=-17:TP=-2:LRA=7,aresample=48000")
        f.append(f"volume={s['gain']}")
        fd = min(s["fade"], d / 3)
        f.append(f"apad,atrim=end={d:.4f},afade=t=in:d={fd:.3f},afade=t=out:st={d - fd:.4f}:d={fd:.3f}")
        return ",".join(f)

    def render(self, out, reuse=True, crf=19, preset="medium"):
        parts = []
        for i, s in enumerate(self.shots):
            p = f"{self.dir}/shot_{i:03d}.mkv"
            key = json.dumps({k: v for k, v in s.items() if k != "t"}, sort_keys=True) + f"{self.W}x{self.H}"
            kp = p + ".key"
            if not (reuse and os.path.exists(p) and os.path.exists(kp) and open(kp).read() == key):
                cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{s['dur_src'] + 1:.3f}", "-i", s["src"]]
                if s["audio"]:
                    cmd += ["-map", "0:v:0", "-map", "0:a:0", "-af", self._af(s)]
                else:
                    cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v:0", "-map", "1:a:0"]
                cmd += ["-vf", self._vf(s), "-t", f"{s['d']:.4f}", "-c:v", "libx264", "-crf", "15", "-preset", "veryfast",
                        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", p]
                run(cmd)
                open(kp, "w").write(key)
            parts.append(p)
            print(f"  shot {i:03d} t={s['t']:7.2f} d={s['d']:5.2f}  {os.path.basename(s['src'])} @{s['a']:.2f} x{s['speed']}", flush=True)
        lst = f"{self.dir}/list.txt"
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        cut = f"{self.dir}/cut.mkv"
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cut])
        total = self.t

        # ---- audio: ambiente/parlato + voiceover + musica in ducking ----
        inputs = ["-i", cut]
        fc, vo_labels = [], []
        for j, v in enumerate(self.vos):
            inputs += ["-i", v["file"]]
            k = len(inputs) // 2 - 1
            dvo = (v["b"] - v["a"]) / v["speed"]
            fc.append(f"[{k}:a]atrim={v['a']:.3f}:{v['b']:.3f},asetpts=PTS-STARTPTS,atempo={v['speed']},aresample=48000,"
                      f"highpass=f=80,afftdn=nf=-30,loudnorm=I=-16:TP=-2:LRA=6,aresample=48000,"
                      f"afade=t=in:d=0.04,afade=t=out:st={dvo - 0.08:.3f}:d=0.08,"
                      f"adelay={int(v['t'] * 1000)}:all=1,apad,atrim=end={total:.3f}[vo{j}]")
            vo_labels.append(f"[vo{j}]")
        mu_labels = []
        for j, m in enumerate(self.musics):
            inputs += ["-i", m["track"]]
            k = len(inputs) // 2 - 1
            d = m["t1"] - m["t0"]
            fc.append(f"[{k}:a]atrim={m['offset']:.3f}:{m['offset'] + d:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
                      f"loudnorm=I=-18:TP=-2,aresample=48000,volume={m['level']},"
                      f"afade=t=in:d={m['fin']},afade=t=out:st={max(0, d - m['fout']):.3f}:d={m['fout']},"
                      f"adelay={int(m['t0'] * 1000)}:all=1,apad,atrim=end={total:.3f}[mu{j}]")
            mu_labels.append(f"[mu{j}]")
        fc.append(f"[0:a]asplit=2[nat][natk]")
        if vo_labels:
            fc.append(f"{''.join(vo_labels)}amix=inputs={len(vo_labels)}:normalize=0,asplit=2[vo][vok]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=end={total:.3f}[vo];anullsrc=r=48000:cl=stereo,atrim=end={total:.3f}[vok]")
        if mu_labels:
            fc.append(f"{''.join(mu_labels)}amix=inputs={len(mu_labels)}:normalize=0[mus]")
            fc.append(f"[vok][natk]amix=inputs=2:normalize=0[key]")
            fc.append(f"[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400:makeup=1[musd]")
            fc.append(f"[nat][vo][musd]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1:LRA=9,aresample=48000[a]")
        else:
            fc.append(f"[nat][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=9,aresample=48000[a]")
        mix = f"{self.dir}/mix.wav"
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[a]",
             "-c:a", "pcm_s16le", "-ar", "48000", "-t", f"{total:.3f}", mix])

        # ---- sottotitoli ----
        ass = f"{self.dir}/subs.ass"
        PALE_GOLD = "&H0098D8F2"
        with open(ass, "w") as f:
            f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {self.W}\nPlayResY: {self.H}\nWrapStyle: 0\n\n"
                    "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
                    "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                    "Alignment, MarginL, MarginR, MarginV, Encoding\n"
                    f"Style: Sub,Poppins Medium,{self.sub_size},{PALE_GOLD},{PALE_GOLD},&H00000000,&H90000000,0,0,0,0,100,100,"
                    f"0.5,0,1,{self.sub_size / 32:.1f},{self.sub_size / 36:.1f},2,{int(self.W * 0.08)},{int(self.W * 0.08)},"
                    f"{self.sub_margin},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            for a, b, t in sorted(self.subs):
                f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{t}\n")

        run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-i", mix, "-vf", f"ass={ass}:fontsdir={ROOT}/models",
             "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-profile:v", "high",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "-t", f"{total:.3f}", out])
        self.check(out)
        return out

    def check(self, out):
        """Controlli finali: durata audio = video, nessun silenzio lungo."""
        v = float(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", out]))
        a = float(run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration", "-of", "csv=p=0", out]))
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", out, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32); hop = 80; n = len(x) // hop
        db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
        quiet = db < -50
        holes, run_s = [], None
        for i, q in enumerate(quiet):
            if q and run_s is None:
                run_s = i
            if not q and run_s is not None:
                if (i - run_s) * 0.01 > 0.4:
                    holes.append((round(run_s * 0.01, 2), round((i - run_s) * 0.01, 2)))
                run_s = None
        print(f"CHECK {os.path.basename(out)}: video {v:.2f}s audio {a:.2f}s, silenzi >0.4s: {holes}")
