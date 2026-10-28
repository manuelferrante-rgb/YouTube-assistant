# Regole dell'audio (sound design, musica, mix)

- REGOLA PRINCIPALE (Manuel, 27/10 sera, dopo il rumore di camion nel tè; vale per tutti i video da ora e prevale
  sulle regole più vecchie qui sotto):
  1. niente suoni presi dal girato e niente ambienti (vento, aria, onde, strada, motori, letti, J-cut d'ambiente);
  2. solo musica e segni melodici a tema del video, composti dalla chat Audio, autore Voci Vere;
  3. solo nei momenti di solo B-roll, senza nessuno che parla, e non forzati: se un momento non ne ha bisogno, niente.
     Sotto chi parla (Manuel, interviste, voiceover) niente, o al massimo la musica molto bassa;
  4. musica leggera e melodica, senza tappeto basso continuo; passa-alto deciso (160 Hz, ripido) su tutto;
  5. prima di consegnare, `python3 audio/kit/bande.py <file>`: niente rombo sotto 150 Hz (deve dire OK).
  Precisazione di Manuel (28/10): un po' di rumore naturale nella clip di chi parla può restare, fa capire dove siamo
  (lo gestisce Montaggio con la pulizia della voce). La chat Audio invece non prende MAI rumori esterni o del girato:
  crea solo musiche e suoni melodici originali, a tema del video, autore Voci Vere.
  Le regole sotto su suoni veri, letti, ambienti e J-cut restano solo come storia (Arthunkal): non si applicano più.

- Suoni NATURALI e professionali, mai "forzati" (Manuel, 24/10). Ordine delle fonti:
  1. suoni veri del girato di Manuel (onde, vento, passi, voci, campane, pentole) e registrazioni "wild" che
     Manuel fa apposta (20-30 s di ambiente o di un gesto, senza parlare);
  2. librerie con licenza CC0 o libera da attribuzione (Freesound filtrato CC0, Internet Archive/SSE Library,
     dal 25/10 niente YouTube Audio Library);
  3. sintesi solo per suoni astratti (tick di un contatore), e rifinita perché suoni vera.
- Ogni file nel kit ha una riga in `audio/catalogo.md`: nome, fonte, autore, licenza, link, uso.
- Pochi effetti e mirati: sulla mappa un whoosh verso l'India, i tick dei km, un ding leggero (approvati 23/10).
  Transizioni: J-cut (il suono della scena nuova entra prima dell'immagine) come base; effetto vero solo nei
  cambi forti (zoom nel nero).
- Musica (decisione di Manuel, 25/10): ORIGINALE, composta dalla chat Audio per ogni video, diritti tutti di Voci
  Vere (niente Content ID, vale anche su Instagram). Niente più YouTube Audio Library. Fondali calmi da documentario,
  bassi sotto la voce; niente brani "etnici" da cartolina; canti e preghiere del girato restano ambiente, mai
  trasformati in musica. Solo se serve un brano preciso: CC0 o pubblico dominio da fonte affidabile, nel catalogo.
- Flusso (Manuel, 25/10): Manuel giudica sul lungo orizzontale finito, non sulle singole proposte. La chat Audio
  parte dal montato della chat Montaggio e consegna musica + effetti (+ mix) su Drive in montati/<video>/audio/.
- Mix: voce e interviste sempre sopra tutto; finale a -14 LUFS integrati, picchi sotto -1 dBTP; mai due voci
  insieme (B-roll della stessa clip della voce a volume zero).
- Scambio con il montaggio: il montaggio scrive `projects/<video>/audio_cue.md` (tempo nel montato, cosa succede,
  che suono serve); la chat Audio risponde con i file in `projects/<video>/audio/` (wav 48 kHz) o su Drive e
  compila la colonna "file" del cue.
- Gancio (Manuel, 26/10, dopo aver visto il lungo di Arthunkal): primi 30 s calmi, solo suono vero, niente colpi né
  whoosh né cambi rumorosi. Li tiene insieme un letto naturale continuo (onde, canto o folla lontani, dal girato).
- Ambienti di riempimento (J-cut, buchi): solo da clip SENZA parlato (controllare con la trascrizione): sotto la
  mappa di Arthunkal si sentiva una voce presa da un ambiente con Manuel che parlava.
- Internet Archive (verificato 26/10): molte raccolte di effetti marcate "CC0" o "public domain" sono librerie commerciali
  ricaricate da utenti (Sound Ideas, Disney, Warner, Lucasfilm): licenza falsa, rischio Content ID. Da lì solo
  registrazioni con autore e provenienza chiari; per gli effetti, prima il girato e le registrazioni "wild" di Manuel.
- Audio generato insieme ai B-roll IA (Veo): non si usa mai; i suoni delle scene IA li fa la chat Audio (Insights, 26/10).

Nota da Montaggio, 27/10 (decisione di Manuel dopo la v2 del tè, vale per ogni video):
- Voce pulita prima di tutto. Niente letti d'ambiente sotto tutto il video: `ambiente_colline` (molto basso sotto i
  200 Hz) steso sotto tutto il lungo del tè suonava come un camion in sottofondo. Gli ambienti servono solo per i momenti
  vuoti senza parlato, con un contesto, e vanno consegnati già senza rombo (passa-alto almeno 90-120 Hz).
- Niente fruscii (carta, penna) sulle grafiche della linea del tempo, niente ronzii o ticchettii sotto il voiceover.
- Gli effetti si usano solo dove l'immagine li giustifica (es. il chai tirato mentre si vede il chai).
