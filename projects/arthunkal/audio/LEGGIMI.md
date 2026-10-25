# Suoni per Arthunkal (chat Audio) - PROPOSTE in attesa dell'ok di Manuel (25/10)

Tutti i file sono anche su Drive: cartella del video -> montati/arthunkal/audio/ (wav 48 kHz 24 bit).
- `transizione_zoom_nero.wav` (0.95 s): onda vera che monta per 0.75 s, poi taglio secco e 0.2 s di silenzio.
  Allineare il TAGLIO (0.75 s) al primo fotogramma nero. Volume indicativo -5 dB sotto il dialogo.
- `uscita_nero.wav` (1.8 s): parte insieme al nero (0.2 s prima dell'immagine nuova), con l'audio della
  scena nuova in dissolvenza da 0.45 s (J-cut). Volume indicativo -7 dB.
- `mappa_sfx_v3.wav` (8 s): traccia completa della mappa con whoosh, 13 tick veri alternati e ding
  (tempi di map_sfx.py, --t-a 4.1 --t-b 6.0). Rigenerabile con `audio/kit/mix_mappa.py --t-a .. --t-b ..`
  se cambiano i tempi (il 13 deve cadere su "Tredici").
- Il ding è PROVVISORIO (nel girato non ci sono campane): verrà sostituito.
Anteprime per Manuel: anteprima_mappa_suoni_veri.mp4, anteprima_transizione_zoom_nero.mp4 (stessa cartella Drive).

Musica originale (bozza 25/10, `audio/musica/compose.py`), su Drive in montati/arthunkal/audio/:
- `musica_bozza_cammino.wav` (2:00): cammino, interviste, cibo. Ci sono le corde pizzicate che danno il passo.
- `musica_bozza_storia.wav` (1:04): mappa e linea del tempo, piano rado.
- `musica_bozza_arrivo.wav` (1:04): arrivo alla basilica e finale.
Sono bozze: appena c'è il montato le taglio a misura sulle scene e faccio il mix. Se nel frattempo le metti nel montato,
tienile basse (circa -22/-26 dB sotto la voce) e mai sotto le interviste con voci nel girato.
