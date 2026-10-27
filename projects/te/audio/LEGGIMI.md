# Tè di Munnar: audio (chat Audio, 27/10 sera, sostituisce tutto quello di prima)

Cartella Drive del video: 1D0vC10Ej5Uo8cns93a8aeiYJi-kU-JMw, file in montati/te/audio/.

## Regole nuove di Manuel (27/10 sera, per questo video e per i prossimi)
- Niente suoni presi dal girato e niente ambienti (vento, aria, strada, motori). Solo musica e segni melodici composti
  dalla chat Audio (autore Voci Vere).
- Solo nei momenti di solo B-roll, senza nessuno che parla, e solo se servono. Sotto chi parla (Manuel, interviste,
  voiceover) niente, o al massimo la musica molto bassa.
- Nessun file di Audio ha energia sotto i 150 Hz: tutti misurati con `audio/kit/bande.py` (sotto 150 Hz più di 55 dB
  sotto il totale; la vecchia musica_colline aveva il 28% dell'energia sotto 150 Hz).

## Cosa NON usare più (spostati in `dismessi/`, non cancellati)
`ambiente_colline`, `chai_tirato`, `motore_camion`, `carta`, `penna`, `orologio_lontano`, `fabbrica_provvisorio`
e la vecchia `musica_voiceover_lungo` (tempi v1, musica scura). Su Drive le due musiche vecchie sono in
`montati/te/audio/vecchi/`.
ATTENZIONE in build.py: `aud("ambiente_colline", QUIET[0])` ora non trova il file e ripiega su 114701 (suono del
girato). Va tolto `tl.fill` (lungo e `vfinish`) e il ripiego, non sostituito con un altro ambiente.

## File (48 kHz, nessuno contiene rumori)
| File | Durata | Livello | Cos'è |
|---|---|---|---|
| Drive `musica_colline.wav` = qui `musica_te_luce.flac` | 4:00 | -20 LUFS | musica nuova, leggera e melodica (sol maggiore, 72 bpm): piano che canta, pizzicato leggero, archi alti solo a respiri. Niente tappeto basso, passa-alto a 160 Hz |
| `cue_domanda.flac` (Drive `.wav`) | 5.5 s | -18 LUFS | quattro note di piano che salgono e restano sospese: domanda aperta |
| `cue_storia.flac` | 5.0 s | -18 LUFS | tre note che scendono, in mi minore: si entra nella storia |
| `cue_citta.flac` | 5.0 s | -18 LUFS | arpeggio pizzicato che sale, più luminoso: arrivo in città |
| `cue_chai.flac` | 8.0 s | -18 LUFS | pizzicato veloce (il tè tirato che scende e risale) con una piccola melodia, chiude sulla tonica |

Su Drive la musica nuova ha lo STESSO NOME di prima (`musica_colline.wav`): riscaricandola in work/te/musica/,
build.py la usa senza modifiche, con gli stessi offset (0, 11, 20, 27, 35, 47, 54, 62, 66, 76, 90, 100).

## Dove vanno (tempi della v3, 6:43: cambiano un po' con la nuova parte del chai, si seguono le scene)
### Lungo
| Circa | Scena (build.py) | Suono | Livello |
|---|---|---|---|
| 0:20 | `e.b(114701)` con il titolo "E oggi, di chi sono queste colline?", prima della sigla | `cue_domanda`, dall'inizio del B-roll; la coda si spegne sotto l'inizio della sigla | pieno |
| 3:34 | dopo il nero, `e.b(134442)` + `from_black`, inizio "La storia e chi ci lavora" | `cue_storia`, la prima nota sul primo fotogramma dopo il nero; sfumarlo quando parla Sadish (133946) | pieno, poi via sotto la voce |
| 5:49 | dopo il nero forte, `e.b(141843)` + `e.b(141109)` con l'etichetta "Munnar" | `cue_citta`, dall'inizio del B-roll; finisce prima di Manuel (141707) | pieno |
| ~5:58 | B-roll del chai `142433` + `142447` (e `142545` se resta) | `cue_chai`, dall'inizio del primo B-roll; tagliarlo con dissolvenza di 0.4 s dove riparte il parlato | pieno |
| sotto i VO 2-12 | dove `vo_over(..., music=...)` | musica nuova, se Manuel la vuole: MOLTO bassa, `level` da 0.42 a 0.25 | molto basso |
| 6:33-fine | VO 14 e logo | musica nuova (offset 100) sotto il VO a 0.25; sul logo (solo immagine) può salire a 0.42 | basso, poi pieno |
Il gancio (0:00-0:20) resta senza niente: solo le voci. Nessun segno sotto Sadish, Shaharon, Manuel o il voiceover.
Se un momento senza voci è più corto di 1.5 s, meglio niente.

### Verticali
| Verticale | Dove | Suono |
|---|---|---|
| v1_teaser | gli ultimi 2 s su 114701 con "E oggi, di chi sono?", prima della mini sigla | `cue_domanda`. Togliere la musica sotto tutto il teaser (`r.tl.music(0, ...)`) o lasciarla molto bassa (0.15) |
| v4_chai | i primi 1.8 s sul gesto del chai (142447), prima che parli Manuel | primi 2 s di `cue_chai` con dissolvenza di 0.3 s, al posto del suono vero |
| v4_chai | sotto la voce (narr di 143318) | niente (via `chai_tirato`) |
| v2_raccolta, v3_giornata | coda di 0.7 s su un B-roll | niente: troppo corta |

## Controllo prima di consegnare
`python3 audio/kit/bande.py <file>`: LUFS, picco, energia per banda, livello sotto 150 Hz (deve dire OK).
Rifare i file: `python3 audio/musica/compose.py te_luce|cue_domanda|cue_storia|cue_citta|cue_chai <out.wav>`, poi
livello come sopra (musica -20 LUFS, segni -18 LUFS).
