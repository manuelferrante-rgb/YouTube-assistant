# Regole dell'audio (sound design, musica, mix)

- Suoni NATURALI e professionali, mai "forzati" (Manuel, 24/10). Ordine delle fonti:
  1. suoni veri del girato di Manuel (onde, vento, passi, voci, campane, pentole) e registrazioni "wild" che
     Manuel fa apposta (20-30 s di ambiente o di un gesto, senza parlare);
  2. librerie con licenza CC0 o libera da attribuzione (Freesound filtrato CC0, Internet Archive/SSE Library,
     YouTube Audio Library scaricata da Manuel);
  3. sintesi solo per suoni astratti (tick di un contatore), e rifinita perché suoni vera.
- Ogni file nel kit ha una riga in `audio/catalogo.md`: nome, fonte, autore, licenza, link, uso.
- Pochi effetti e mirati: sulla mappa un whoosh verso l'India, i tick dei km, un ding leggero (approvati 23/10).
  Transizioni: J-cut (il suono della scena nuova entra prima dell'immagine) come base; effetto vero solo nei
  cambi forti (zoom nel nero).
- Musica: brani calmi della YouTube Audio Library caricati da Manuel, bassa sotto la voce; niente brani "etnici"
  da cartolina.
- Mix: voce e interviste sempre sopra tutto; finale a -14 LUFS integrati, picchi sotto -1 dBTP; mai due voci
  insieme (B-roll della stessa clip della voce a volume zero).
- Scambio con il montaggio: il montaggio scrive `projects/<video>/audio_cue.md` (tempo nel montato, cosa succede,
  che suono serve); la chat Audio risponde con i file in `projects/<video>/audio/` (wav 48 kHz) o su Drive e
  compila la colonna "file" del cue.
