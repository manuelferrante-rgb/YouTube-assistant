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

## Consegna per la chat Montaggio (25/10, nomi richiesti), in questa cartella
- `transizione_nero_in.wav` (0.6 s): il taglio è l'ultimo campione, mettilo sul primo fotogramma nero.
- `transizione_nero_out.wav` (1.3 s): colpo basso morbido + onda, parte sul primo fotogramma dopo il nero; solo 2-3 cambi forti.
- `tick_km.wav` (0.1 s), `ding_arrivo.wav` (1.6 s, PROVVISORIO: nel girato non c'è una campana; lo sostituisco appena
  Manuel registra un bicchiere d'acciaio o la campana), `tick_data.wav` (0.1 s, penna leggera, -6 dB rispetto al tick_km).
- Per la mappa puoi anche usare direttamente `mappa_sfx_v3.wav` (8 s, tutto già a tempo, tick alternati).
- Musica ORIGINALE (niente più "Turn In The Sun" e "inner_outer", decisione di Manuel): su Drive montati/arthunkal/audio/
  `musica_voiceover.wav` (3:30, calma, piano rado e archi: sotto il voiceover a circa -24 dB rispetto alla voce) e
  `musica_verticali.wav` (60 s, con il passo delle corde dall'inizio). Mai sotto interviste o voci del girato.

## Montato v2 (25/10, 5:41)
- `musica_voiceover_lungo.flac` (qui, 8 MB) = `musica_voiceover_lungo.wav` su Drive (montati/arthunkal/audio/): 5:40.93,
  allineata a 0:00 del lungo, silenzio fuori dai tratti. Sostituisce i quattro pezzi di musica_voiceover.
  Tratti (da `musica_lungo.json`, rigenerabile con `audio/musica/sul_montato.py` se cambiano i tempi):
  0:21-0:34 vo_2 | 1:05-1:30 vo_1c + notte + vo_3 + vo_jb (ponte sulla notte, senza voci) | 2:07-2:13 vo_8b |
  2:56-3:12 vo_5 e Manuel su chi offre | 3:35-3:51 In strada (col passo delle corde, si chiude quando esplode la folla) |
  4:25-4:56 La storia (scende di 5 dB sotto Manuel tra la folla, 4:32-4:50) | 5:13-5:41 finale, apertura "arrivo" fino al saluto.
  Picco -6 dBFS: livello indicativo -22/-24 dB sotto la voce.
- Note sul mix dell'anteprima (misure di loudness a 3 s):
  1. Arrivo 3:52-3:58 a -12/-13 LUFS contro -17/-18 del resto: 5 dB sopra. Folla e altoparlanti devono colpire, ma
     abbassare di circa 3 dB (picchi verso -15) per non far saltare il volume sui telefoni.
  2. Interviste più basse della voce di Manuel (2:27-2:32 a -25, 2:41-2:45 a -27): alzarle di 3-4 dB.
  3. Buchi brevi di quasi silenzio (0:55, 1:53-1:55, 3:15, 3:29, 5:04 a -30/-36): coprire con l'ambiente della scena
     dopo che entra prima (J-cut) o con la coda della precedente. Sono i "momenti vuoti" da evitare.
  4. tick_data: d'accordo a non usarlo. Ding provvisorio: tenerlo basso, nessun altro effetto da aggiungere.

## Gancio calmo (26/10, dopo la visione di Manuel)
- `letto_onde.flac` (40 s): onde vere di Marari, continue, entrata 1.5 s e uscita 2.5 s. Base dei primi 30 s.
- `rosario_lontano.flac` (40 s): il rosario cantato sul cammino (0264) e il mormorio della notte (0234), lontani
  (passa-basso e riverbero). Tenerlo circa 14 dB sotto le onde e abbassarlo di altri 8-10 dB sotto la voce di Manuel e
  il voiceover della statua: si deve sentire nelle pause, non sopra le parole.
- `letto_gancio.flac` (40 s): i due già insieme, se preferisci un file solo (allora ducking sotto la voce).
- Wav uguali su Drive in montati/arthunkal/audio/. Niente colpi né whoosh nel gancio; il primo effetto è la mappa.

## Montato v3 (26/10, 6:46.40)
- `musica_voiceover_lungo.flac` rigenerata su `musica_lungo_v3.json` (tempi di vo_tempi_v3.txt), 406.40 s, allineata
  a 0:00. Tratti: 0:22-0:34 | 1:08-1:34 (ponte sulla notte) | 1:59-2:05 | 4:07-4:17 | 4:45-5:02 In strada |
  5:28-6:02 La storia (giù di 5 dB tra 5:36 e 5:56) | 6:22-6:45 finale fino al saluto.
  vo_7a (0:12) nel gancio resta senza musica: sotto c'è il letto_gancio. Senza anteprima v3, le code dopo i voiceover
  sono corte (0.4-0.7 s) per non finire sotto interviste nuove.
