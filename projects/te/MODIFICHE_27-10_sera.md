# te: nuova chat Montaggio (27/10 sera), richieste di Manuel sulla v3

Leggi prima CLAUDE.md, `regole/montaggio_documentario.md` (in fondo: regole 26-27/10 e "Audio pulito e controllo prima
di consegnare") e `projects/te/MODIFICHE_27-10.md` (come si riscarica e si rifà tutto: girato, VO, musica, stock, build).

## Punto di partenza
- v3 su Drive, cartella 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw, montati/te: `VociVere_te_long_4K.mp4` (6:43) e i 4 verticali
  `VociVere_te_v1_teaser`, `v2_raccolta`, `v3_giornata`, `v4_chai` (_1080x1920.mp4). Il codice è `projects/te/build.py`.
- La v3 ha già tolto il letto `ambiente_colline` sotto tutto, carta/penna, orologio e fabbrica. MA Manuel sente ANCORA
  il rumore di un camion in sottofondo, anche nell'intro e nei verticali.

## 1. Togliere il rumore del camion (prima cosa, lungo e verticali)
Non è ancora stato trovato con certezza. Indizi misurati dalla chat precedente:
- `work/te/musica/musica_colline.wav` (Audio): il suo fondo è quasi tutto tra 60 e 250 Hz e quasi niente sopra 1 kHz,
  cioè un tappeto scuro e basso: può suonare come un motore. Sta sotto i voiceover.
- `projects/te/audio/ambiente_colline.flac`: stesso profilo (rombo 60-250 Hz). Nella v3 è ancora usato per riempire i
  buchi (`tl.fill` in build.py e in `vfinish`) e come ripiego di QUIET.
- Suono vero delle clip sotto il parlato: `Edit.b(gain)`, `vo_over` (clip a gain 0.14 sotto il VO), il letto da 135012 in
  `Edit.b` quando la clip ha voci, gli ambienti di `to_black`/`from_black` (135012), `reel_kit` (`AMB=0.12` di default).
- Zone con più bassi nelle pause (v3): 0:00-0:10 (gancio), 0:20 (sigla), 0:35-0:45 (VO 2 con musica), 3:30, 4:00-4:20
  (Sadish, 134136), 4:50, 5:15, 5:45-6:35 (chai, strada vera).
- Per trovarlo: `STEM=nat|vo|mus MIXONLY=1 python3 projects/te/build.py long --preview` (aggiunto in
  `tools/doc_render.py`: scrive `work/te/out/long_work/stem_<x>.wav` con una sola traccia). Ascolta/misura ogni stem
  nelle zone sopra, trova la fonte, toglila.
Regole nuove di Manuel (27/10 sera):
- Sotto chi parla (Manuel in camera, interviste, voiceover) solo la sua voce/il suo audio vero. Niente suoni del girato
  presi da altre clip, niente letti, niente ambienti di Audio. Il teaser va bene anche solo con il girato di chi parla e il
  voiceover.
- Nei momenti di solo B-roll (nessuno che parla), e solo se servono: musiche/suoni MELODICI a tema fatti dalla chat Audio
  (autore Voci Vere). Mai rumori presi dal girato. Non forzati: se non servono, niente.
- Togliere quindi `tl.fill` con ambiente_colline, il gain del suono vero dei B-roll sotto il parlato e gli ambienti di
  transizione. Se restano buchi di silenzio totale tra frasi, si accorciano i tagli (non si riempiono con rumori).
- Musica sotto il voiceover: solo quella nuova di Audio (vedi sotto); se suona ancora scura/bassa, chiederlo a Manuel.

## 2. Sottotitoli dei verticali
- Le battute in italiano (traduzioni delle interviste, `block=` in reel_kit) escono dallo schermo: spezzarle in più pezzi
  brevi, sempre su UNA riga, che scorrono a tempo con il parlato (come quelli parola per parola). Mai testo fuori dalla
  safe zone: controllare ogni fotogramma con un sottotitolo.

## 3. Il tè del chai master (lungo e v4)
- Manuel: "il video del master è bello". La prima parte va più veloce: tagliare e mostrare poche scene, così si arriva
  subito a quello che dice Manuel sul master che non vuole parlare e sull'India (143318).
- Quando si torna su Manuel in camera, labiale e audio sono scollegati: controllare ogni ritorno in camera (143138, 143318,
  141707 e anche gli altri del video) fotogramma per fotogramma, con i tagli audio e video identici.

## 4. Consegna
- Rifare lungo 4K e 4 verticali, controlli obbligatori (audio_check, stem, trascrizione, fotogrammi, labiale), caricare su
  Drive al posto dei vecchi, segnare in `piano/calendario.md`, commit, PR su master e merge. Riassunto breve a Manuel.
- I suoni nuovi di Audio arriveranno in `projects/te/audio/` (vedi `LEGGIMI.md`): se non ci sono ancora, consegnare senza
  (voce pulita e basta) e aggiungerli dopo.
