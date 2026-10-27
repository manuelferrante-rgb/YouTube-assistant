# te: passaggio a una nuova chat Montaggio (27/10)

Leggi prima CLAUDE.md e `regole/montaggio_documentario.md` (in fondo le regole nuove di Manuel del 26-27/10).

## Stato
- 27/10 mattina: TUTTE le 13 modifiche sotto applicate in `build.py` (v2). Lungo 4K 6:43 e 4 verticali ricaricati su
  Drive montati/te con gli stessi nomi (i vecchi sono sovrascritti). Capitoli in `capitoli.md`. In attesa dell'ok di Manuel.
  Note tecniche: `snap_w` limita i tagli alla parola dopo/prima della trascrizione; il "ne ne" del VO 12 si toglie
  con tagli fissi sulla forma d'onda (130.30-131.63 + 131.735-138.3, `exact=True`, senza respiro), verificato con
  parakeet ("colline ne produceva"). Musica: si usa ancora `musica_colline.wav` a tratti sotto i VO; il file
  `musica_voiceover_lungo` di Audio (tempi v1) non vale più per la v2.
- Pellegrinaggio (arthunkal): APPROVATO da Manuel il 27/10, file finali e capitoli in `piano/calendario.md`. Fatto.
- Tè (te): v1 consegnata su Drive (cartella 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw, montati/te): lungo 4K 7:18
  `VociVere_te_long_4K.mp4`, verticali `VociVere_te_v1_teaser`, `v2_raccolta`, `v3_giornata`, `v4_chai`
  (_1080x1920.mp4) e il reel `VociVere_te_bucato_1080x1920.mp4` (approvato: editing e durata vanno bene).
  Manuel ha guardato il lungo e chiede le modifiche sotto. Dopo: rifare lungo 4K e verticali, ricaricare su Drive
  al posto dei vecchi, segnare in `piano/calendario.md`. NON mandare messaggi alle altre chat salvo se Manuel lo dice.

## Come si rifà (il computer della nuova chat parte vuoto: work/ non è nel repo)
1. Girato: `rclone copy gdrive: work/te/raw --include "DJI_*.MP4"` con le variabili RCLONE_CONFIG_GDRIVE_*
   (vedi `tools/drive_upload.sh`, ROOT_FOLDER_ID = cartella del video). ~6 GB. Il viaggio iniziale (105322-114701,
   tranne 114701) non serve: si può escludere per risparmiare disco.
2. Voiceover: Drive montati/te/audio/vo_te_pulito.wav (ripulito da Audio, stessi tempi di Rajmala.m4a) in
   work/te/vo/; in build.py mettere VO1 = vo_te_pulito.wav. Trascrizione del VO: `tools/transcribe_segments.py`
   (serve per `vwords`); trascrizione del girato in work/te/trans.json con lo stesso strumento (~30 min).
   Le parole già controllate sono in `projects/te/girato.md`, `interviste.md`, `vo_tagli.md`.
3. Musica: Drive montati/te/audio/musica_colline.wav in work/te/musica/. Stock Pixabay (4 clip, `PIXABAY_API_KEY`):
   id 41146 (pennino), 349087 (archivio), 92994 (pioggia), 70333 (chai) in work/te/stock/px_<id>.mp4; due non hanno
   audio: aggiungere una traccia muta (anullsrc) sennò il render si ferma.
4. `python3 projects/te/build.py long --preview` (anteprima 960x540, ~15 min), controlla, poi
   `python3 projects/te/build.py long` (4K ~2 h 30, consegna diretta a ~35 Mbps) e `v1 v2 v3 v4`.
   Tenere il turno attivo con attese in primo piano (i processi in background si fermano quando la sessione dorme).
   Disco: il 4K occupa ~7 GB di cut.mkv + 2 GB finale; `drop_shots` cancella le inquadrature dopo l'unione.
5. Caricare: `GDRIVE_FOLDER_ID=1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw tools/drive_upload.sh te <file>`.
6. Musica su misura: Audio aveva fatto `projects/te/audio/musica_voiceover_lungo.flac` sui tempi della v1; con i
   tempi nuovi si rigenera con `audio/musica/sul_montato.py` e un json come `projects/te/audio/musica_lungo_v1.json`
   (tempi dei VO in work/te/out/voiceover_3840x2160.txt); va usata solo se la durata coincide col montato.

## Modifiche di Manuel al lungo del tè (27/10), in ordine di video (tempi della v1)
1. GANCIO: si parte da Manuel "Dietro di me una piantagione immensa di tè" (115233 36.5-39.6), poi mentre dice
   "Qui nel 1877 vennero affittate per 3.000 rupie a un britannico" (41.4-47.8) si vede Sadish (es. 133703, Sadish
   tra i filari che raccoglie). Togliere le mani che raccolgono messe prima della frase.
2. "Le foglie vengono ancora raccolte a mano. Scoprirò l'arte che c'è dietro questo lavoro, e la storia, nella
   raccolta del tè che consumiamo tutti i giorni" (120307 0.82-5.95 + 120356 1.97-6.6): togliere TUTTI i silenzi
   (anche tra "E la storia." e "nella raccolta", 2.7-3.8 in 120356) perché suoni un'unica frase.
3. MUNNAR: "Sono a Munnar, in Kerala, a oltre 1500 metri" (115233 12.0-15.3), poi solo un attimo di paesaggio
   (~1,5 s) e subito il voiceover 2 con la linea del tempo (1877). NIENTE MAPPA. Meno panorami verdi di fila.
4. SADISH all'inizio: togliere "Italy... Munnar... very very good" (133721 4.8-8.1): partire da "This is the tea
   plantation" (8.2) = "Questa è la piantagione di tè".
5. ACQUA PIOVANA: togliere Manuel che cammina prima (b-roll 115728 dopo il primo blocco di Sadish) e la pioggia
   messa da sola: Sadish dice "Rainwater only" (133721 55.4-56.6) e MENTRE lo dice si vede la pioggia Pixabay
   (cover). Poi Manuel "tutto organico..." (134852).
6. Togliere la domanda "after which year?" e la risposta "ogni quindici giorni" (133721 112.5-116.6): non c'entra.
7. Manuel con le foglie (135758): quando dice "in generale c'è un processo dietro" (18.3-20.4) si vede Sadish che
   cammina (135922) sopra la sua voce; poi, quando parla dell'orario di lavoro (134231), si torna su di lui.
   Togliere il b-roll di Sadish che cammina messo da solo dopo (vuoto).
8. ~4:50 (voiceover 6): via la scena dal bus con il vento (181247); mettere scene naturali coerenti (es. case
   delle tenute 132655, colline 115553).
9. Voiceover 9 (legge del 1971): la grafica dell'anno breve, appena si vede l'anno subito le carte/archivio
   (Pixabay 349087) mentre la voce continua. Nessun b-roll dopo che la voce è finita.
10. ~6:14 (voiceover 12): si sente "ne ne" ripetuto quando entra il b-roll del chai. Causa: `snap` ha allungato il
   primo pezzo dentro la ripetizione. Pezzi giusti: (130.40, 131.69) + (131.86, 138.3) senza allungare oltre la
   parola dopo. Controllare anche il VO 8: il pezzo (64.9, 70.6) non deve prendere "Solo l'appassimento..." (70.98).
   In generale: in `piece()` limitare `snap` all'inizio della parola successiva della trascrizione.
11. FINALE (voiceover 14): via il bus con lo specchietto (181123, 181247). Usare scene finali naturali e con poco
   suono, es. le mucche sulla strada (160612), i petali (152338), poi il logo.
12. SUONI DI AUDIO (projects/te/audio/, LEGGIMI.md): mettere ambiente_colline (letto sotto tutto, al posto del
   fondo preso dal girato), carta/penna sulla grafica 1877 e sul pennino e sulla legge 1971, orologio_lontano basso
   sul voiceover 4, fabbrica_provvisorio molto basso sul voiceover 8, chai_tirato sotto il chai del voiceover 12.
   Sempre insieme ai suoni originali, non al loro posto.
13. Stesse regole per i verticali (soprattutto il teaser, che usa 115233 e 120307): niente pause, niente vuoti.
