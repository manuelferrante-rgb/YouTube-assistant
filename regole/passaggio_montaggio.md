# Passaggio alla nuova chat Montaggio (aggiornato 9/11)

## STATO AL 9/11 (leggere prima di tutto)
- coir: FINITO e approvato. Lungo v5 4K 6:45 + 5 verticali (teaser, made_in_india, indietro, premilla, 1975, a 1x) su Drive
  cartella "Coir" (19zCOBK_aJ6a4SFwGffbZvDKUr-IXR8UA), montati/coir. Codice: `projects/coir/build.py` (long, verticali),
  `v4_finale.py` (ultimi 15 s senza volti), `v5_chiusura.py` (voce di chiusura registrata). Girato e scelte in
  `projects/coir/girato.md`, capitoli in `projects/coir/capitoli.md`. Copy ha già il pacchetto. Non toccarlo salvo richiesta.
- te: v9 su Drive (stessi tempi del v8, immagini a metà video con persone): `projects/te/v9_modifiche.py`. Approvato.
- arthunkal: lungo invariato; verticali v1-v4 rifatti l'8-9/11 (`projects/arthunkal/reels.py`): v2 apre sull'anziano
  col telo bianco (090951) e poi Manuel. Approvati.
- Diwali annullato (vedi calendario). Prossimi lunghi: B (migranti o erosione, 10/1) e bilancio (24/1, `piano/bilancio.md`).

## AGGIORNAMENTO 9-10/11 (chat Montaggio session_01Htfbgygqfq2ApmZ8QQUNmP, chiusa)
- Terzo banner fisso nei lunghi: "instagram" (vocivere, Segui -> Segui già), approvato da Manuel il 9/11. Già messo in
  coir (2:50.8), te (5:37.0), arthunkal (5:01.8), file sostituiti su Drive. Codice: `tools/subscribe_banner.py instagram`,
  `tools/apply_banners.py ... --instagram T`. Dove metterlo: su una dissolvenza, con una frase leggera di voiceover o senza
  parlato, immagini tranquille, mai su interviste con sottotitoli (regola in `regole/montaggio_documentario.md`).
- Nessun altro lavoro aperto: si aspetta il prossimo video di Manuel (girato su Drive).

## FATTO 11/11: coir v6, intro nuova (su Drive; `projects/coir/v6_intro.py`, capitoli in `projects/coir/capitoli.md`)
- Persone delle miniature: miniatura 2 = 0063 7.8-10.6, miniatura 3 = 0063 13.8-17.9, miniatura 1 = 0052 2.0-5.0.
- Metodo: v5 copiato senza ricodifica prima (0-7.6) e dopo la sigla (fotogrammi chiave), solo 10 s nuovi codificati;
  flussi H.264 grezzi uniti, niente -shortest nel mux (tagliava l'audio). Voce nuova con limitatore (picchi alti).
- Copy avvisata per i sottotitoli (Manuel 11/11).

Richiesta originale:
- coir lungo, nuova intro: le 3 promesse delle miniature (uomo nella laguna, "Made in India", "80 centesimi a tappeto")
  nei primi ~20 s. Al posto di VO0 un VO nuovo che Manuel deve registrare: "Su quei tappeti c'è scritto Made in India.
  Non c'è scritto chi li ha fatti. Né che a loro per ogni tappeto vanno ottanta centesimi. Quattro euro al
  giorno. Da oggi, ogni volta che ne vedi uno, saprai da dove viene." (testo DEFINITIVO 11/11, senza "ci dicono"; VO0 passa da ~5 a ~12-13 s).
- Immagini: "Made in India" -> signora seduta tra la fibra che guarda in camera (0063); "ottanta centesimi" -> donna
  davanti al mucchio di gusci col fazzoletto; "quattro euro" -> donne al lavoro. 0544 resta al primo fotogramma, 0034/0038
  restano. Resto invariato. Poi capitoli nuovi in projects/coir/capitoli.md e piano/calendario.md.
- Titolo nuovo (deciso): "CHI C'È DIETRO I NOSTRI TAPPETI: le donne del coir in Kerala, India 🇮🇳".
- Manuel 11/11: sotto le parole nuove del VO SOLO video delle persone delle miniature (le 3 del test, su Drive
  montati/coir/miniatura), sempre coerenti con quello che si dice in quel momento. Trovare le clip confrontando i
  fotogrammi con le miniature (candidate: 0063 4-7 s, 0540, 0549, 0544).
- Si parte quando Manuel lo chiede e ha caricato la registrazione del VO.
- A montaggio finito (Manuel 11/11): avvisare Copy (session_01HtfbgysqTrKE7hBx3kQeSA) che deve rifare i sottotitoli
  it/en del lungo coir sui nuovi tempi, con i capitoli nuovi.

## LEZIONI DI COIR (6-9/11), valgono per i prossimi
- Velocità: lunghi e verticali a 1x quando il VO è registrato sciolto (Manuel). Pause d'enfasi brevi (~0.45 s) nei
  verticali solo dove servono (`say(..., pause=PAUSE)`).
- Voce delle clip: `leveled()` in `projects/coir/build.py` (voce RNNoise a -18 LUFS + fondo della clip sempre a -56 dB,
  gate dolce nelle pause); interviste lontane dal microfono: `lift=True`. Chi parla piano e lontano: RNNoise lo cancella,
  usare `voice_clean.light()`; folla dietro: `voice_clean.gated(..., double=True)`.
- Taglio delle pause nelle frasi: solo pause >= 0.3 s, altrimenti si mangiano consonanti ("persone" -> "pedone").
- Frase di chiusura dei lunghi: SEMPRE `assets/voce/chiusura_vocivere.m4a` (0.88-6.80 s), mai l'audio della ripresa.
  Mentre la si dice non si vede Manuel: persone al lavoro, poi immagini senza volti (schermata finale negli ultimi 15 s).
  Scritta finale animata: `tools/scritta_finale.py` (font DM Serif Display, riquadro con luce a cometa), approvata.
- Insights 8/11: promessa di titolo e miniatura nel primo minuto; a metà video niente campi larghi senza persone;
  ultimi 10-15 s senza volti; verticali: primo fotogramma = persona del posto o gesto, mai Manuel per primo.
- Titoli dei reel: uno sparisce quando entra il successivo (niente sovrapposizioni); controllare che le scritte in
  alto non coprano i volti (se serve: zoom dal bordo alto, vedi `premilla()` in coir).
- Modifiche a un lungo già consegnato senza rifare il 4K: sovrapporre le parti nuove e ricodificare una volta (`te/v9`,
  `coir/v4`), o solo l'audio con il video copiato (`coir/v5`). Disco: liberare `work/` (girato già consegnato, shot_*)
  prima dei render 4K; `direct_concat` in doc_render evita il cut.mkv da 11 GB.
- Upload grandi su Drive: `rclone copyto ... --drive-chunk-size 128M --timeout 2m` (senza, si blocca alla fine).


PRIMA DI TUTTO, PER OGNI REEL: `regole/formato_reel.md` (formato approvato da Manuel sul reel meenakshi: gancio forte,
nessuna pausa, tutto a 1.1x, titoli Poppins ExtraBold oro su bianco, sottotitoli su fascia scura, chiusura "Ascolta
altre voci, su" + logo su velo leggero). Modello pronto: `projects/meenakshi/build.py`.

Leggi prima CLAUDE.md, poi `regole/montaggio_documentario.md` (soprattutto le regole in fondo dal 26/10 in poi), poi questo file.
Si risponde sempre in italiano a Manuel, risposte brevi e concrete.

## Stato
- te (tè di Munnar): FINITO e approvato. Su Drive (cartella 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw, montati/te) lungo 4K 6:24
  e 4 verticali; Copy ha già fatto il pacchetto. Non toccarlo salvo richiesta di Manuel.
- meenakshi (tempio di Madurai): FINITO e approvato 29/10, verticale 19.3 s in montati/meenakshi (cartella Drive
  1Gov2PE4EU32BZPdJW3miH3oYPc68Iv8v). Non toccarlo salvo richiesta di Manuel.
- arthunkal, mercato: finiti (vedi `piano/calendario.md`).
- comorin (Kanyakumari, 4 reel: cocco, canna, statua di Thiruvalluvar, tre mari in loop): consegnato 4/11 sera (v4)
  in montati/comorin (cartella Drive 1z5BA2MoG69ExGT6ivPb9VAcbxV25VVmI). Manuel ha chiesto le ultime modifiche e le
  ha avute; se ne chiede altre: `python3 projects/comorin/build.py cocco|canna|statua|mari`, scelte e clip escluse in
  `projects/comorin/girato.md` (la sua ragazza non deve comparire mai; in cocco e canna niente Manuel).
- Lezioni di comorin (valgono per tutti i reel): titoli oro su bianco più piccoli (`TAG_SIZE, TAG_PAD, TAG_SIDE` in
  `tools/reel_kit.py`); "Ascolta altre voci, su" entra in dissolvenza (stile `TagIn`); il segno di chiusura parte sulla
  fine della voce (niente buco); pause lunghe dentro le frasi del VO e parole ripetute si tagliano (`cut=` nelle frasi,
  `narr_cuts` in `projects/comorin/build.py`); voce registrata a 0 dBFS: `voice_clean.py` ora abbassa prima di RNNoise
  (prima crepitava). Controllare lo spettrogramma della voce e il livello a 50 ms nelle chiusure (buchi o colpi).
- Manuel vuole i video direttamente su Drive (lunghi, teaser, reel), niente anteprime in chat salvo verticali a sé.
- Prossimo video: lo dice Manuel. Quando carica il girato su Drive, il flusso è quello di CLAUDE.md.

## Come lavorare (lezioni del tè, Manuel ci tiene moltissimo)
1. Audio
   - Sotto chi parla (Manuel, interviste, voiceover) solo la sua voce. B-roll sempre muti: mai suoni presi dal girato,
     mai letti d'ambiente, mai ambienti di transizione.
   - Il "rumore da camion" può stare nella clip stessa di chi parla (vento, motori): ogni clip parlata passa da
     `tools/voice_clean.py` (RNNoise, ritardo compensato) tramite `tl.audio_map` (vedi `clean_voices` in
     `projects/te/build.py`). Anche i tagli automatici (`voiced`) leggono la voce pulita.
   - Musica: solo quella consegnata dalla chat Audio nell'ultima versione (mai i file in `dismessi/` o `vecchi/`),
     e solo dove la vuole Manuel: bassissima e costante (`Timeline.music(..., duck=False, norm=False)`, circa 23 dB
     sotto la voce), mai sotto le interviste. Segni melodici di Audio solo sui B-roll senza parlato.
   - Una registrazione con più bassi: filtro solo su quella voce (`af=` in `vo_over`).
   - Normalizzazione finale lineare (già in `tools/doc_render.py`).
2. Intro e teaser (Manuel, 27/10): ~20 s, uguali tra lungo e teaser. Si parte da Manuel in camera con solo le sue
   parole (niente scritte, musica o voiceover sotto), poi la frase forte su un'immagine muta della persona, il voiceover
   sulle colline/il luogo, frasi attaccate senza nessuna pausa, la domanda aperta con il segno di Audio, la sigla.
   I tagli delicati si misurano a 10 ms sulla voce pulita e si riascoltano con la trascrizione (`say(..., exact=True)`).
3. Chiusura di ogni lungo (28/10): dopo la riflessione finale e prima del logo, la frase di Manuel "Il viaggio di Voci
   Vere, per dar voce a chi ne ha più bisogno, continua. Seguimi per scoprire le prossime storie"
   (`projects/te/vo/rajmala_3.m4a`) su B-roll suo a tema viaggio. Così la chiusura supera i 10 s ed è il capitolo
   "Chiusura".
4. Labiale: mai mostrare la clip di chi parla mentre si sente un altro istante della stessa clip.
   `PLAN=plan.json python3 projects/<video>/build.py <pezzo>` e `python3 tools/sync_check.py plan.json` -> 0 problemi.
5. Verticali: sottotitoli sempre su una riga, pezzi brevi che scorrono col parlato (`tools/reel_kit.py` misura la
   larghezza); controllare i fotogrammi a ogni sottotitolo. Punto dopo l'ultima parola di una frase, così un pezzo
   non mescola due frasi.
6. Controlli obbligatori prima di ogni consegna: `tools/audio_check.py` (ogni finestra segnalata spiegata o corretta),
   trascrizione del montato (nessuna parola tagliata o ripetuta, nessun vuoto), fotogrammi dei punti cambiati e dei
   primi 5 s, labiale. Manuel non deve trovare lui gli errori.

## Velocità (Manuel vuole tempi brevi)
- Il 4K completo richiede ~2 ore. Se cambia solo un tratto, si rende in 4K solo quel tratto e si attacca al file già
  consegnato con il concat di ffmpeg sul fotogramma esatto, con il mix completo nuovo fatto in anteprima
  (`MIXONLY=1 ... --preview`: stessi tempi del 4K). Se cambia solo l'audio, si rimonta il mix sul video con `-c:v copy`.
  Esempi: `projects/te/MODIFICHE_27-10_sera.md` (v6 e v7).
- Teaser e verticali prima: si mandano subito a Manuel (anche in chat) mentre il lungo codifica.
- Tenere il turno attivo con attese in primo piano finché i render non finiscono.
- Mai `pkill -f` con un testo che compare nello stesso comando (uccide la shell): usare il PID.

## Consegna
`GDRIVE_FOLDER_ID=<cartella del video> tools/drive_upload.sh <video> <file>` (al posto dei vecchi; se si blocca,
`timeout 290` e riprova). Poi `piano/calendario.md`, commit, PR su master e merge.

Nota Montaggio 4/11 (comorin): voce da un file registrato a 0 dBFS (tipo i memo di Manuel): `tools/voice_clean.py` ora
abbassa di 6 dB prima di RNNoise, altrimenti satura e crepita. Controllare sempre lo spettrogramma della voce pulita
contro l'originale (righe verticali larghe = crepitio).

Nota Montaggio 4/11 sera: arthunkal v5 e te v8 (richieste di Manuel dai dati del mercato, vedi `piano/calendario.md`).
- Modifiche fatte sul lungo già consegnato, senza rifare il 4K: tagli sui fotogrammi chiave e copia del resto
  (`projects/arthunkal/v5_modifiche.sh`, `projects/te/v8_modifiche.sh`). Metodo veloce (3 minuti invece di 2 ore):
  stessi parametri x264 del file (crf 20, maxrate 38M, bufsize 76M, high 5.1, GOP chiuso), concat con -c copy.
- I verticali di arthunkal ora sono in `projects/arthunkal/reels.py` (formato reel 29/10, usa build.py per clip e
  grafiche). Il voiceover vo_take1 di arthunkal non c'è più su Drive: se servisse, chiederlo a Manuel.
- Tabella W_BASILICA in build.py: i tempi a inizio clip erano anticipati di ~0.4 s (corretti in reels.py dalla
  trascrizione della voce pulita).
- Mai `pkill -f` dentro un comando che contiene lo stesso testo: è successo di nuovo il 4/11 (uccide la shell).

## REEL EXTRA "spazio Munnar" (11/11, Manuel, in approvazione)
- Riferimento in Drive "Reel voiceover spazio/Riferimenti" (cartella 1V_kn3DJO61loXNLeUWLz6G4oq9jVRDlC). Discesa dallo
  spazio con immagini satellitari vere (`tools/space_zoom.py`: Blue Marble NASA + Sentinel-2 cloudless 2016 di EOX, CC BY 4.0,
  da citare in descrizione) fino al 2nd Mile View Point (22RQ+HP7 = 10.0417 N, 77.0393 E), poi il girato del tè.
- Manuel: breve; niente musica, solo il suono del movimento (sintetizzato in build.py); chiusura senza riquadro bianco:
  sfondo sfocato, "Video fuori sul canale" + logo. Codice: `projects/spazio_munnar/build.py` (girato da cartella te).
- Rete: aggiunti all'ambiente gli host eoimages.gsfc.nasa.gov e tiles.maps.eox.at (EOX funziona, NASA no).
