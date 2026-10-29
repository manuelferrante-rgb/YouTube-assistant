# Formato dei reel Voci Vere (Manuel, 29/10, approvato sul reel meenakshi)

Modello: `projects/meenakshi/build.py` → `montati/meenakshi/VociVere_meenakshi_reel_1080x1920.mp4` (cartella Drive
1Gov2PE4EU32BZPdJW3miH3oYPc68Iv8v). Manuel: "mi piace proprio questo reel fatto così, per i prossimi reel".
Vale per ogni verticale (teaser e reel dopo il lungo, reel singoli). Il contenuto cambia, il formato resta questo.
Prevale sulle note più vecchie sui verticali in `regole/montaggio_documentario.md` e in CLAUDE.md dove sono diverse
(scritte Anton, sottotitoli con il contorno, logo sul nero).

## Struttura e ritmo
- Durata: circa 20 s finali (meenakshi 19.3 s). Voiceover di Manuel sul copione di Copy, una frase dopo l'altra.
- Gancio forte da 0 s: la persona più forte già nel momento migliore (meenakshi: il signore col segno sulla fronte
  già zoomato), solo ~1 s, poi subito il luogo. Titolo di gancio grande dal primo fotogramma (es. "Saccheggiato nel 1310").
- La rivelazione: un movimento di camera vero (meenakshi: la rotazione, solo il pezzo del giro, accelerato 1.6x) che
  finisce sulla frase forte ("Guardatelo oggi").
- Immagini brevi (1-2 s) che seguono le parole: la cosa si vede mentre si dice. Una vista dall'alto/panoramica breve
  (~1.3 s) dopo la rivelazione funziona.
- NESSUNA pausa tra le frasi del VO: niente respiri, niente silenzi (pad 0.03/0.06 s, `gap=0`).
- Tutto il video finito accelerato a 1.1x alla fine (immagini, voce, musica, titoli, logo): `faster()` in
  `projects/meenakshi/build.py`, codifica crf 16 slow. Mai in CapCut (perde qualità).

## Titoli (fatti, nomi, luoghi)
- Su una riga, il più grandi possibile senza uscire dallo schermo: Poppins ExtraBold ORO (#B68A4B) su riquadro
  BIANCO (opzione E). Stile `Tag` di `tools/reel_kit.py`: `r.title(a, b, "Testo", "Tag", 400)`.
- Font `assets/fonts/VVTitolo-PoppinsExtraBold.ttf` (famiglia "VV Titolo", copiato in `models/` dall'hook di avvio:
  rinominato perché il Poppins ExtraBold vero cambierebbe il grassetto dei sottotitoli).
- Entrano di colpo ("bam": scala 107% → 100% in 0.11 s, niente dissolvenza), nel momento in cui la parola si dice
  (nome del tempio su "Tempio di Meenakshi", luogo su "Madurai, Tamil Nadu"), in alto (y 400), mai sul viso.

## Sottotitoli
- Su tutto il parlato, parola per parola, una riga, tutti alla STESSA altezza (anche all'inizio, sotto il titolo).
- Poppins bianco su UNA fascia scura semitrasparente per tutta la riga (opzione 3), la parola che si sta dicendo in
  oro: `Reel(..., cap_box=True)`. La fascia è un solo blocco, senza stacchi tra le parole.
- Spariscono al taglio dopo l'ultima frase (`r.cap_stop`): sulle immagini finali niente sottotitoli.

## Audio
- Solo la voce di Manuel pulita (RNNoise, `tools/voice_clean.py`), clip mute.
- Musica della chat Audio bassissima e costante sotto la voce (`MUS_LEVEL = 0.08`, `duck=False, norm=False`),
  un po' più su (0.17) sul finale senza voce. Segni di Audio (gancio, rivelazione, chiusura) ~12 dB sotto la voce
  (gain 0.24); `cue_chiusura` e musica arrivano fino all'ultimo fotogramma del logo. Mix -14 LUFS.
  Il livello si potrà ritoccare video per video.

## Chiusura (sempre uguale)
1. Subito dopo l'ultima frase: 1 immagine breve del luogo (~0.9 s), poi l'ultima persona ~2 s (non di più: la
   persona dopo un po' è imbarazzata).
2. Nel fotogramma in cui sparisce l'ultimo sottotitolo entra la frase **Ascolta altre voci, su** nello stesso stile
   dei titoli (oro su bianco, in alto), e resta fino alla fine.
3. La persona continua sotto un velo nero LEGGERO (35%, entra in 0.5 s, non deve sembrare "l'uomo nero"); il logo
   `assets/brand/logo_vocivere_trasparente_chiaro.png` (con il payoff) sfuma in 0.6 s, centrato in verticale e
   orizzontale, largo il 70%. 2 s, poi fine. Codice: `logo_card()` in `projects/meenakshi/build.py`.
   Attenzione alle clip orizzontali (es. 3840x2160): ritaglio 9:16 al centro come nel reel, mai schiacciate.

## Copy (modello: `copioni/meenakshi_testi.md`)
- Un solo fatto forte, niente lista. Copione VO di ~50 parole in 6 frasi brevi, registrato da Manuel una frase per
  riga (anche una sola presa basta); voce calma, poi il video va a 1.1x.
- Schema delle frasi: 1) gancio col fatto forte (se le fonti non concordano: "si racconta"); 2) la rivelazione breve
  ("Guardatelo oggi."); 3) nome e luogo ("Tempio di Meenakshi, Madurai, nel Tamil Nadu, in India."); 4-5) il fatto
  spiegato in concreto (chi, quando, cosa si vede); 6) una frase umana sul presente ("Secoli dopo, qui si viene ancora
  a pregare."). Poi la chiusura fissa.
- Titoli a schermo: 3 (gancio col fatto, nome, luogo), max ~22 caratteri, una riga, legati alla parola detta.
- Didascalie e titolo dello Short ripetono il gancio ("Saccheggiato nel 1310. Guardatelo oggi").

## Controlli prima di consegnare (come sempre)
Fotogrammi a ogni titolo e sottotitolo e dei primi 5 s, trascrizione del montato (nessuna parola tagliata o
ripetuta; i dubbi si riascoltano a pezzi), `tools/audio_check.py`, ffprobe sul file finito. Se si cambia un pezzo
generato (logo, scheda), cancellare `work/<video>/out/reel_*_work`: la cache è per nome di file.
Dove mandare le versioni (Manuel, 29/10): lunghi, teaser e reel dei lunghi vanno direttamente su Drive (cartella del
video), le modifiche si fanno da lì. In chat (SendUserFile) solo i verticali che sono una storia a sé (tipo meenakshi),
che Manuel approva prima che si sostituisca il file su Drive.
