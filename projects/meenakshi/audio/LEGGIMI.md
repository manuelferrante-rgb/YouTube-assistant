# Meenakshi (verticale 30-45 s): audio (chat Audio, 29/10)

Cartella Drive del video: 1Gov2PE4EU32BZPdJW3miH3oYPc68Iv8v. Il 29/10 è ancora vuota: questi file sono pronti PRIMA
del girato, i tempi esatti si fissano sul montato. Tutto originale (`audio/musica/compose.py`, autore Voci Vere),
niente musica di YouTube, niente campioni. Tutti i file a 48 kHz, controllati con `audio/kit/bande.py`
(sotto 150 Hz da -60 a -74 dB: OK).

## File
| File | Durata | Livello | Cos'è |
|---|---|---|---|
| `musica_meenakshi.flac` | 50 s | -20 LUFS | re dorico, 84 bpm: pizzicato leggero da subito (dà passo al verticale), archi alti a respiri, melodia di piano dal terzo giro (~11 s), campanella sintetica ogni 4 battute. Si taglia dove serve: sfumata in uscita di 1 s |
| `cue_gancio.flac` | 3.5 s | -18 LUFS | due campanelle e un arpeggio che sale e resta aperto. Calmo, nessun colpo |
| `cue_rivelazione.flac` | 4.5 s | -18 LUFS | accordo sospeso che si apre, quattro note di piano che salgono: sul fatto forte |
| `cue_chiusura.flac` | 5 s | -18 LUFS | tre note che scendono sulla tonica, la campanella resta: sull'ultima immagine |

## Dove vanno
| Momento | Suono | Livello |
|---|---|---|
| 0:00, prima immagine (torre o fila), sotto la prima frase in camera | `cue_gancio` dalla prima immagine; se Manuel parla da subito, solo le prime campanelle e via in 0.5 s quando entra la voce | pieno sul B-roll, -10 dB sotto la voce |
| dal gancio alla fine | `musica_meenakshi` da 0:00 del file (o da ~11 s se si vuole la melodia subito) | sotto Manuel e interviste MOLTO bassa (circa -23 dB sotto la voce, ducking); sui B-roll senza voce può salire di 6-8 dB |
| la frase con il fatto forte (rito della sera, o torri ridipinte) | `cue_rivelazione`, la prima nota sul B-roll subito DOPO la frase (fiori, fila, torre); abbassare la musica di 6 dB mentre suona | pieno |
| ultima riga in camera e ultima immagine | `cue_chiusura` sull'ultima immagine senza voce; la musica sfuma sotto e finisce con lui | pieno |
Se un momento senza voci è più corto di 1.5 s, meglio niente. Mix finale del verticale: -14 LUFS, picchi sotto -1 dBTP.

## Audio ambiente del tempio e pulizia voce (in attesa)
Manuel ha chiesto (29/10) di usare l'ambiente del tempio (campane, canti, folla) se lo registra (lista riprese,
punto 5 di `piano/meenakshi.md`) e la pulizia voce. In attesa del girato e della conferma di Manuel che vale come
eccezione alla regola del 27-28/10 (niente suoni del girato da Audio; pulizia voce di Montaggio con
`tools/voice_clean.py`). Fino ad allora: nessun file di ambiente da Audio.

## Rifare i file
`python3 audio/musica/compose.py meenakshi|cue_gancio|cue_rivelazione|cue_chiusura <out.wav>`, poi
`ffmpeg -i <out.wav> -af loudnorm=I=-20:TP=-2:linear=true -c:a flac <file>.flac` (-18 per i cue) e `bande.py`.
