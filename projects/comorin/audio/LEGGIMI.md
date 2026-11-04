# Comorin (4 reel, Kanyakumari): audio (chat Audio, 4/11)

Cartella Drive del video: 1z5BA2MoG69ExGT6ivPb9VAcbxV25VVmI. Indicazioni di Copy: "PER AUDIO" in
`copioni/comorin_testi.md`. Solo musica originale (`audio/musica/comorin.py`, autore Voci Vere): niente suoni del
girato, niente ambienti, niente pulizia voce (regola di Manuel 27-28/10, confermata 29/10). L'audio delle clip lo
gestisce Montaggio. Tutti i file a 48 kHz, controllati con `audio/kit/bande.py`: niente sotto 150 Hz, tutti OK.
I TEMPI QUI SOTTO SONO PRIMA DEL 1.1x: si monta sulla musica così com'è, poi `faster()` accelera tutto insieme.

## File
| File | Durata | Livello | Reel |
|---|---|---|---|
| `musica_cocco.flac` | 20 s | -16 LUFS | 1 cocco: la musica porta tutto, la dorico, 120 bpm, legno intonato sui colpi + pizzicato + piano |
| `musica_canna.flac` | 30 s | -20 LUFS | 2 canna: re maggiore, 76 bpm, leggera e calda |
| `cue_canna_gancio/rivelazione/chiusura.flac` | 3.5 / 4.5 / 5 s | -18 LUFS | 2 canna: i tre segni, in re |
| `musica_statua.flac` | 36 s | -20 LUFS | 3 statua: mi maggiore, 66 bpm, ampia (archi alti larghi, pizzicato rado, campanella) |
| `cue_statua_gancio/rivelazione/chiusura.flac` | 3.5 / 4.5 / 5 s | -18 LUFS | 3 statua: i tre segni, in mi |
| `musica_mari_loop_8s8.flac` | 8.80 s esatti | -16 LUFS | 4 tre mari: loop perfetto. Con il 1.1x diventa 8.0 s |
| `musica_mari_loop_8s0.flac` | 8.00 s esatti | -16 LUFS | 4 tre mari: stesso loop già a 8.0 s, se il reel 4 NON passa dal 1.1x |

## Reel 1, cocco: si monta sulla griglia della musica (battuta = 2 s, colpo = 0.5 s)
Nessuna voce: musica a livello pieno (non quello sotto la voce), mix finale -14 LUFS. I colpi sono già nella musica
(note di legno, non rumori): mettere un colpo di machete del venditore su ogni accento.
| Tempo (prima del 1.1x) | Musica | Immagine (PER MONTAGGIO di Copy) |
|---|---|---|
| 0.0 | GANCIO: accordo di legno + campanella | il colpo più netto di `135736` |
| 1.0-2.0 | levata di pizzicato | `135652` la pila di cocchi |
| 2.0-10.0 | groove: colpi a 2.0, 2.5, 3.0 / 4.0, 4.5, 5.0 / 6.0, 6.5, 7.0 / 8.0, 8.5, 9.0 (prendi, taglia, taglia, porgi) | il taglio ripetuto; il cocco passato al cliente sul quarto tempo (es. 9.5) |
| 10.0-12.0 | PASSAGGIO ALLA POLPA: si apre in do, arpeggio di piano che sale; colpi a 10.0 e 11.0 | `140138` le mani della signora che spaccano il cocco |
| 12.0-14.0 | si svuota, colpo a 12.0 | `140346` la montagna di gusci |
| 14.0-16.0 | colpo a 14.0 | il venditore prende il cocco successivo |
| 16.0-20.0 | CHIUSURA: tre note che scendono, legno e campanella a 17.5 che restano | chiusura fissa "Ascolta altre voci, su" + logo; la musica arriva fino all'ultimo fotogramma |
Con il 1.1x: 20 s diventano 18.2 s. Se il reel deve essere più corto, togliere una battuta intera tra 4.0 e 10.0
(un ciclo di 2 s), tagliando sul colpo con dissolvenza di 20 ms: la griglia resta a tempo.

## Reel 2, canna e reel 3, statua (come meenakshi, `regole/formato_reel.md`)
- Musica da 0:00 del file, bassissima e costante sotto la voce (`MUS_LEVEL = 0.08`), più su (0.17) sul finale senza
  voce, fino all'ultimo fotogramma del logo. Sfumare 1 s in uscita dove finisce il reel.
- Segni a gain 0.24 (~12 dB sotto la voce):
| Reel | Gancio | Rivelazione | Chiusura |
|---|---|---|---|
| 2 canna | `cue_canna_gancio` dal primo fotogramma (la ruota) | `cue_canna_rivelazione`, prima nota quando lui piega la canna spremuta e la ripassa (frase 3) | `cue_canna_chiusura` sull'ultima immagine di lui, fino al logo |
| 3 statua | `cue_statua_gancio` dal primo fotogramma (statua dal basso) | `cue_statua_rivelazione`, prima nota su "Poi lui", quando la camera di `130308` trova la statua | `cue_statua_chiusura` sulla gente ai piedi della statua, fino al logo |
Mentre suona la rivelazione la musica può scendere di 6 dB. Se un segno cade su un vuoto di voce sotto 1.5 s va bene
comunque a quel livello: è sotto la voce.

## Reel 4, tre mari: loop
È l'unico suono del video. Il video deve durare ESATTAMENTE quanto il file (8.80 s prima del 1.1x, o 8.00 s se il
reel non viene accelerato): la musica ripiega su se stessa (le code e il riverbero della fine sono già sommati
all'inizio), quindi niente dissolvenze né in entrata né in uscita, e niente chiusura con logo. Misurato: al giunto
il salto è più piccolo di quelli interni al brano (nessun clic). Mix: portare a -14 LUFS con un guadagno fisso
(non loudnorm dinamico, che romperebbe il loop).

## Rifare i file
`python3 audio/musica/comorin.py <brano> <out.wav>` (brani: cocco, canna, canna_gancio, canna_rivelazione,
canna_chiusura, statua, statua_gancio, statua_rivelazione, statua_chiusura, mari_8.8, mari_8.0), poi guadagno fisso
(musiche -20, segni -18, cocco e mari -16 LUFS) e `python3 audio/kit/bande.py <file>`.
