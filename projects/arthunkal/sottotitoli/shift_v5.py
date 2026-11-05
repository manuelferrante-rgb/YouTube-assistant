# Copy, 5/11: sposta i sottotitoli it/en sui lunghi nuovi di Montaggio (arthunkal v5 6:21, te v8 6:26).
#   arthunkal: fino a 34.533 invariati; 34.533-69.300 tolto; dopo 69.300 -28.267 s
#   te: fino a 15.333 invariati; dopo +2.000 s
#   python3 projects/arthunkal/sottotitoli/shift_v5.py
import re
def ts(s):
    h, m, r = s.split(':'); sec, ms = r.split(','); return int(h)*3600 + int(m)*60 + int(sec) + int(ms)/1000
def fm(t):
    t = max(0, t); ms = int(round(t*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
def shift(path, f):
    blocks = re.split(r'\n\s*\n', open(path, encoding='utf-8').read().strip()); out = []
    for b in blocks:
        L = b.splitlines(); a, z = [ts(x.strip()) for x in L[1].split('-->')]
        r = f(a, z)
        if r: out.append((r, L[2:]))
    s = '\n\n'.join(f"{i}\n{fm(a)} --> {fm(z)}\n" + '\n'.join(t) for i, ((a, z), t) in enumerate(out, 1)) + '\n'
    open(path, 'w', encoding='utf-8').write(s); print(path, len(blocks), '->', len(out))
def arth(a, z):
    A, B, D = 34.533, 69.300, 28.267
    if z <= A: return a, z
    if a >= B: return a - D, z - D
    if a < A: return a, A                      # taglia la coda prima del tratto tolto
    if z > B: return B - D, z - D              # ne resta solo la parte dopo
    return None                                # dentro il tratto tolto
def te(a, z):
    A, D = 15.333, 2.0
    if z <= A: return a, z
    if a >= A: return a + D, z + D
    return a, z + D
for l in ('it', 'en'):
    shift(f'projects/arthunkal/sottotitoli/VociVere_arthunkal_long.{l}.srt', arth)
    shift(f'projects/te/sottotitoli/VociVere_te_long.{l}.srt', te)
