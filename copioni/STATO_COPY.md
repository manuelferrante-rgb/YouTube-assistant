# Copy: stato e passaggio di consegne (aggiornato 9/11)
Da leggere all'avvio di ogni nuova chat Copy, dopo CLAUDE.md. Regole complete in `regole/copy.md` (in fondo le note più nuove),
`regole/formato_reel.md`, `copioni/caroselli/testi_caroselli.md` (regole dei caroselli), `copioni/stories/storie_testi.md`.

## Video e stato del pacchetto Copy
- mercato: pubblicati teaser, lungo, 2 reel, carosello "fatto" (7/11, musica IG "Art of Life" di Lesfm, 8 immagini su YT).
  Reel 3 A "alle 3 di notte" pubblicato il 9/11 (commento fissato unico YT+IG). Restano: storie set 1 (10/11), set 2 (11/11),
  carosello "I volti" + set 3 (12/11). 9/11: titolo e miniature v3 del lungo rifatti e approvati (Insights + Manuel):
  "UN PESCE DA 50 CHILI IN INDIA 🇮🇳 il mercato del pesce sulla spiaggia", M1 signora "ALL'ASTA / SULLA SABBIA" (principale),
  M2, M3, it/en, Drive montati/mercato/miniatura/ (vecchie in vecchie/), generatore copioni/miniature_v3/mercato_v3.py.
  Niente sfocature sulle miniature (Manuel 9/11: "bruttissimo"). Link lungo: https://youtu.be/LW4zO_0oSgQ
- arthunkal (lungo dom 15/11): pacchetto in `copioni/arthunkal_pacchetto.md`. Titolo e miniature v3 approvati l'8/11
  (titolo "LA PREGHIERA CHE NON SI FERMA MAI..."; Test e confronto A2, A3, A1 su Drive miniatura/). Verticali v3 (8/11).
  Sottotitoli it/en spostati sul lungo v5 (6:21) il 5/11.
- te (lungo dom 29/11): pacchetto in `copioni/te_pacchetto.md`. Titolo e miniature v3 approvati 8/11 (T1, T5, T3).
  Verticali v3. Sottotitoli sul lungo v8 (6:26).
- coir (lungo A dom 20/12): APPROVATO 8/11, lungo finale v4 6:45 (9/11: sottotitoli it/en spostati con shift() in make_srt.py,
  capitoli 0:00, 0:18, 1:20, 2:48, 4:24, 5:12, 6:08, sostituiti su Drive), pacchetto completo in `copioni/coir_pacchetto.md` e su Drive cartella "Coir"
  (19zCOBK_aJ6a4SFwGffbZvDKUr-IXR8UA) montati/coir: miniature C1, C2, C3, sottotitoli it/en (`projects/coir/sottotitoli/make_srt.py`),
  descrizione e capitoli it/en, 5 verticali (teaser + 4 reel), carosello "fatto" (`copioni/caroselli/carosello_coir.py`),
  "I volti", storie 3x6 (`copioni/stories/stories_coir.py`). Script, VO e note per Montaggio/Audio in `copioni/coir_testi.md`.
  Da fare: inserire il link del lungo nei post YouTube quando esce (lo mette Manuel).
- Tracce audio inglesi dei lunghi te e coir (Manuel 10/11): copioni in `copioni/te_audio_en.md` e `copioni/coir_audio_en.md`
  (anche su Drive montati/<video>/TESTI_audio_inglese.txt). Manuel le registra una settimana prima dell'uscita (te ~22/11,
  coir ~13/12) con Copy, poi Montaggio fa la traccia (istruzioni nel file del te). Arthunkal niente traccia inglese.
- erosione: domande e parti in camera in `copioni/erosione_testi.md`; girato forse dal 9/11.
- meenakshi: carosello "I volti" pronto (Drive cartella meenakshi). comorin: copy completo in `copioni/comorin_testi.md`.

## Decisioni recenti di Manuel e Insights (6-8/11), già nelle regole
- Miniature v3 (generatore `copioni/miniature_v3/miniature_v3.py`): persona del posto grande, colore cinematografico, testo
  enorme Anton, volto SEMPRE libero dalla scritta; versioni it ed en; 3 in "Test e confronto", un solo titolo.
- Titolo: gancio in MAIUSCOLO + spiegazione + bandiera, sempre anche in inglese.
- Titolo degli Short: fatto concreto con un numero o un oggetto, tutto in italiano.
- Testi dei verticali e dei caroselli: fatto, contesto, domanda su una riga, una frase con cosa si scopre solo nel lungo
  (anche come commento fissato su YT), "Video completo sul canale YouTube Voci Vere, link in bio." Hashtag in italiano:
  #india #kerala #viaggio #VociVere + uno sul tema. Tutto in italiano anche su IG, niente sottotitoli inglesi sui reel.
- Verticali: la PRIMA frase del VO è la più forte; "Kerala, India" non si ripete (né detto né a schermo) se non serve.
- Storie: escono SEMPRE dopo il lungo, mai "domenica" o conto alla rovescia.
- Carosello "I volti": ritratti in posa, filtro caldo naturale, ogni persona una volta, niente microfoni, copertina con un
  volto forte (non il più forte), il più forte nella 2, ultima slide foto del luogo sfocata + logo.
- Lunghi: tema "dare voce a chi ne ha più bisogno", persone al centro, Manuel poco; voiceover che dà valore al lavoro.

## Strumenti (computer della chat, work/ non è nel repo)
rclone con GDRIVE_RCLONE_TOKEN (come `tools/drive_upload.sh`, RCLONE_CONFIG_GDRIVE_ROOT_FOLDER_ID = cartella del video):
mercato 1X3qkOWu91EZUWqKoVu0pZ3Dd1ipXlGeB, arthunkal 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX, te 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw,
coir 19zCOBK_aJ6a4SFwGffbZvDKUr-IXR8UA, comorin 1z5BA2MoG69ExGT6ivPb9VAcbxV25VVmI, meenakshi 1Gov2PE4EU32BZPdJW3miH3oYPc68Iv8v.
Modelli: volti in work/volti/model (YuNet, SFace da media.githubusercontent.com/media/opencv/opencv_zoo/...), scontorno
work/models/u2net_human_seg.onnx (github.com/danielgatis/rembg/releases/download/v0.0.0/). Trascrizione: `tools/transcribe_segments.py`.
Il lavoro di Montaggio sta sul branch claude/montaggio-prossimo (capitoli in projects/<video>/capitoli.md).
