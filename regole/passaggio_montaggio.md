# Passaggio alla nuova chat Montaggio (aggiornato 29/10 sera)

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
Dove mandare (Manuel, 29/10): lunghi, teaser e reel dei lunghi direttamente su Drive, le modifiche si fanno da lì.
In chat solo i verticali che sono una storia a sé (tipo meenakshi).
`GDRIVE_FOLDER_ID=<cartella del video> tools/drive_upload.sh <video> <file>` (al posto dei vecchi; se si blocca,
`timeout 290` e riprova). Poi `piano/calendario.md`, commit, PR su master e merge.
