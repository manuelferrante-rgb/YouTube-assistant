import sys, textwrap
sys.path.insert(0, sys.argv[1]); from cues import C
def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def wrap(t):
    if len(t) <= 42: return t
    best = None
    for i, ch in enumerate(t):
        if ch == " ":
            score = abs(len(t[:i]) - len(t[i+1:]))
            if best is None or score < best[0]: best = (score, i)
    return t[:best[1]] + "\n" + t[best[1]+1:]
prev = 0
for a, b, it, en in C:
    assert b - a >= 0.6, (a, it or en); assert a >= prev - 1e-6, (a, prev); prev = b
    for x in (it, en):
        if x: assert "—" not in x and "–" not in x
for lang, k in (("it", 2), ("en", 3)):
    rows = [(a, b, c[k]) for c in C for a, b in [(c[0], c[1])] if c[k]]
    with open(f"{sys.argv[1]}/VociVere_mercato_long_v4.{lang}.srt", "w") as f:
        for i, (a, b, t) in enumerate(rows, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{wrap(t)}\n\n")
    print(lang, len(rows), "max line", max(len(l) for _, _, t in rows for l in wrap(t).split("\n")))
