#!/usr/bin/env python3
"""Controllo del labiale sul piano del montaggio (Manuel 27/10 sera: ritorni in camera con voce e bocca scollegate).

Per ogni inquadratura con il suono dello stesso file che si vede (parlato in camera o voce di una clip sopra la
stessa clip) controlla che l'istante dell'immagine e quello della voce coincidano. Segnala anche le inquadrature
di una clip mostrata mentre si sente un altro tratto della stessa clip (bocca che si muove su parole diverse).
    PLAN=plan.json python3 projects/<video>/build.py ...   poi   python3 tools/sync_check.py plan.json
"""
import json, sys

p = json.load(open(sys.argv[1]))
bad = 0
for sh in p["shots"]:
    if sh.get("norm"):
        continue                                   # parlato in camera: audio e video dallo stesso taglio
    t0, t1 = sh["t"], sh["t"] + sh["d"]
    for v in p["vos"]:
        if v["file"] != sh["src"]:
            continue
        vt0 = v["t"]; vt1 = vt0 + (v["b"] - v["a"]) / v["speed"]
        lo, hi = max(t0, vt0), min(t1, vt1)
        if hi - lo < 0.05:
            continue
        # istante della sorgente a metà del tratto in comune: immagine contro voce
        tm = (lo + hi) / 2
        img = sh["a"] + (tm - t0) * sh["speed"]
        voc = v["a"] + (tm - vt0) * v["speed"]
        off = img - voc
        flag = abs(off) > 0.04 or abs(sh["speed"] - v["speed"]) > 1e-3
        bad += flag
        print(f"{'ERRORE' if flag else 'ok    '} t={tm:7.2f} {sh['src'].split('/')[-1][:24]} immagine {img:6.2f} voce {voc:6.2f} "
              f"(scarto {off:+.2f} s, velocità {sh['speed']} / {v['speed']})")
print(f"labiale: {bad} problemi")
