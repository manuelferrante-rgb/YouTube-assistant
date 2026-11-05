# Scrive in volti_scelti.json la scelta fatta sul provino: python3 copioni/caroselli/volti_set.py <video> <cover_id> <id> <id> ...
# Ordine: copertina (volto forte, non il più forte), poi il più forte, poi gli altri; ogni persona una volta.
# (id del provino di volti_review.py; "id:zoom" per un ritaglio più largo o stretto, es. 2_0:2.8)
import json, sys
v, ids = sys.argv[1], sys.argv[2:]; R = json.load(open(f'work/volti/review_{v}.json'))
def e(s):
    i, *z = s.split(':'); d = dict(R[i]); d['id'] = i
    if z: d['zoom'] = float(z[0])
    return d
S = json.load(open('copioni/caroselli/volti_scelti.json')); old = S.get(v, {})
S[v] = {'cover': e(ids[0]), 'faces': [e(i) for i in ids[1:]]}
if 'closing' in old: S[v]['closing'] = old['closing']
json.dump(S, open('copioni/caroselli/volti_scelti.json', 'w'), indent=1)
