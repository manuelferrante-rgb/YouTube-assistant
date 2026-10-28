# Chat Audio: stato e istruzioni per ripartire (passaggio del 27/10)

Leggi prima CLAUDE.md, poi questo file, `regole/audio.md` e `audio/catalogo.md`. Si risponde in italiano.

## REGOLA NUOVA (Manuel, 27/10 sera): prevale su tutto quello che segue
Niente suoni dal girato né ambienti; solo musica e segni melodici composti da noi, solo sui momenti di solo B-roll e se
servono; sotto chi parla niente o musica molto bassa; niente tappeto basso, passa-alto 160 Hz; controllo con
`audio/kit/bande.py` (niente sotto 150 Hz) prima di consegnare. Dettagli in `regole/audio.md`.

## Come lavora la chat Audio (decisioni di Manuel)
- Sound design naturale e professionale, mai forzato. Fonti in quest'ordine: suoni veri del girato di Manuel
  (cartella Drive del video); registrazioni "wild" di Manuel (20-30 s senza parlare); sintesi solo per suoni astratti,
  rifinita. Ogni file ha la sua riga in `audio/catalogo.md` (fonte, autore, licenza, uso).
- Freesound: chiave salvata nell'ambiente (`FREESOUND_API_KEY`), ma il server di Freesound rifiuta i computer cloud
  (HTTP 403 anche senza chiave, verificato due volte il 25/10). Non provare ad aggirarlo. Manuel NON fa ricerche di suoni.
- Internet Archive: raggiungibile, ma molte raccolte di effetti "CC0" sono librerie commerciali ricaricate (licenza
  falsa): non usarle per gli effetti (regola in `regole/audio.md`).
- MUSICA ORIGINALE composta da noi (dal 25/10): niente YouTube Audio Library. Codice in `audio/musica/compose.py`
  (brani: cammino, storia, arrivo, verticale, colline). Sul montato: `audio/musica/sul_montato.py <json> <out.wav>`
  produce un wav unico allineato a 0:00, musica solo sotto i voiceover o momenti senza voci, mai sotto le interviste.
  Il json dei tratti sta in `projects/<video>/audio/`. Livello indicativo: circa 23 dB sotto la voce (ducking del montaggio).
- Gancio sempre calmo (niente colpi né whoosh); ambienti di riempimento solo da clip senza parlato.
- Audio generato dai B-roll IA (Veo): mai usato; i suoni delle scene IA li fa la chat Audio.
- Manuel giudica sul lungo finito, non sulle singole proposte. La chat Audio consegna a Montaggio tramite i file:
  piccoli nel repo (`projects/<video>/audio/`, flac o wav 48 kHz) + istruzioni in `projects/<video>/audio/LEGGIMI.md`;
  grandi su Drive in `montati/<video>/audio/` (`GDRIVE_FOLDER_ID=<id> tools/drive_upload.sh <video>/audio <file>`;
  a volte il primo tentativo si blocca: usare `timeout 290` e riprovare).
- RISPARMIO (26/10): niente messaggi alle altre chat salvo richiesta di Manuel. I tempi dei voiceover li manda
  Montaggio (o li scrive in `projects/<video>/audio_cue.md` / `vo_tempi*.txt`); il girato lo mappa Montaggio in
  `projects/<video>/girato.md`: leggerlo invece di riscaricare tutto.
- Con Manuel: rispondere SUBITO alle sue domande, poi continuare il lavoro. Risposte brevi e concrete.
- Non si può ascoltare: si controlla con spettrogrammi e loudness (ebur128). Dirlo a Manuel quando serve.

## Strumenti
- `audio/kit/build_kit.py`: kit dai suoni veri (zoom nel nero, uscita dal nero, whoosh mappa, tick km, ding
  provvisorio) + file per Arthunkal. Sorgenti in `work/arthunkal/girato/wav/` (non nel repo: riscaricare l'audio
  delle clip citate da Drive, cartella 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX, con `tools/drive.sh` o rclone).
- `audio/kit/mix_mappa.py`: traccia effetti della mappa (`--t-a --t-b`).
- `audio/kit/letto_gancio.py`: onde + rosario lontano (Arthunkal).
- `audio/kit/te_suoni.py`: suoni del tè (sorgenti `work/te/wav/HHMMSS.wav` dalla cartella 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw).
- Trascrizione: `python3 tools/transcribe_segments.py out.json file.wav ...` (per trovare tratti senza parlato).

## Stato dei video (27/10)
- arthunkal: consegnato tutto. Musica sul lungo v4 (409.40 s) in `projects/arthunkal/audio/musica_voiceover_lungo.flac`
  (json: `musica_lungo_v4.json`), integrata da Montaggio. Kit, letto del gancio, transizioni in `projects/arthunkal/audio/`.
  In sospeso: il ding della mappa è PROVVISORIO (nessuna campana nel girato): sostituirlo se Manuel registra un bicchiere
  d'acciaio o una campana. Se Manuel segnala un punto della musica, spostarlo nel json e rigenerare.
- te: APPROVATO da Manuel (v7, 28/10). Il rumore "camion" era nelle clip di chi parla (115233, strada del chiosco),
  non nei file di Audio: Montaggio lo toglie con RNNoise (`tools/voice_clean.py`). Usati: musica_te_luce bassissima
  (dopo "Sono a Munnar" e sotto la storia), cue_domanda, cue_storia. Non usati: cue_citta, cue_chai.
- te, 27/10 sera: TUTTO RIFATTO con la regola nuova (vedi `projects/te/audio/LEGGIMI.md`): musica `te_luce` (su Drive
  con il vecchio nome musica_colline.wav), 4 segni melodici cue_*. I vecchi suoni sono in `projects/te/audio/dismessi/`.
  Storia precedente: suoni e voiceover ripulito consegnati (vedi `projects/te/audio/LEGGIMI.md`). Musica sul lungo v1
  (437.90 s) in `projects/te/audio/musica_voiceover_lungo.flac` (json `musica_lungo_v1.json`): Montaggio la integra dopo
  l'ok di Manuel sul montaggio; se i tempi cambiano, rigenerarla. `fabbrica_provvisorio` da sostituire se arriva una
  registrazione vera. Il reel del bucato (105047, 105115): suono vero dell'acqua, musica leggera mai triste se serve.
- Video nuovi: dal prossimo, Manuel apre chat nuove per video ("Audio - <video>").
