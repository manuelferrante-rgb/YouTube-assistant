# coir (lungo): musica (chat Audio, 6/11)

Brief: `copioni/coir_audio_brief.md`, posizioni in `copioni/coir_testi.md` ("PER AUDIO"). Solo musica originale
(`audio/musica/coir.py`, autore Voci Vere), fa minore, nessun suono del girato, niente pulizia voce. 48 kHz, -20 LUFS,
tutti controllati con `audio/kit/bande.py`: niente sotto 150 Hz, OK.
Scelte di Manuel (6/11) tra tre bozze: intro C dinamica, strada C dinamica, laguna A, macchine C, finale A dinamica.

## Regola di Manuel per questo video
SOLO SOTTOFONDO, e solo dove serve. Mai sotto le interviste, il salario (`0002`-`0006`) e la frase degli 80 centesimi
(`0094`). Se in un punto la musica non aggiunge niente, si toglie: meglio meno.

## File e posizioni
| File | Durata | Dove | Note |
|---|---|---|---|
| `coir_intro.flac` | 10 s | da 0:00 sotto VO0, fino alla sigla | contiene il motivo di tre note (fa-lab-sol) a ~2.5 s, che resta aperto; sfuma da solo in 2 s, tagliare sull'attacco della sigla |
| `coir_strada.flac` | 30 s | VO1-VO3, le donne che non lo fanno più e la strada (tuk-tuk muti) | cresce; tagliare dove finisce VO3 con dissolvenza 1 s |
| `coir_laguna.flac` | 30 s | VO5-VO6, laguna e uomo in barca | il motivo torna a ~15 s: farlo cadere, se possibile, su VO6 o su un'immagine della barca |
| `coir_macchine.flac` | 12 s | VO9, la fibra nelle macchine, passaggio alla fabbrica | finisce in 1.5 s; tagliare prima della prima voce in fabbrica |
| `coir_finale.flac` | 35 s | VO12 fino alla frase di chiusura di Manuel, prima della sigla finale | sale fino a ~26 s, poi il motivo si chiude sul fa e resta un accordo lungo: allineare la fine del VO ("la voce è stata la loro") a 27-32 s |

Se un tratto è più lungo del file: rifarlo con la durata giusta (`BRANI` in `coir.py`), non loopare. Se è più corto:
tagliare con dissolvenza di 1 s.

## Livelli (sottofondo)
- Sotto il voiceover: circa 25 dB sotto la voce. Con la voce a -14 LUFS e il file a -20 LUFS, gain ~ -19 dB (0.11).
- Su B-roll senza voce (raro): fino a -8 dB dal file (gain 0.4), solo se il momento lo chiede.
- Entrate e uscite: dissolvenza di 1 s; la musica è già fuori 1 s prima di ogni intervista.
- Mix finale come sempre: -14 LUFS integrati, picchi sotto -1 dBTP.

## Rifare i file
`python3 audio/musica/coir.py <brano> <stile> <out.wav> [--dinamica]`, poi guadagno fisso a -20 LUFS e
`python3 audio/kit/bande.py <file>`. Brani e scelte: intro C --dinamica, strada C --dinamica, laguna A, macchine C,
finale A --dinamica.

# Verticali di coir: musica e segni (chat Audio, 9/11)
Codice: `audio/musica/coir_verticali.py` (stessa famiglia del lungo, fa minore). Scelte tra tre bozze A/B/C fatte da
Insights su richiesta di Manuel (9/11). Tutti controllati con `bande.py` (sotto 150 Hz da -57 a -70 dB: OK).
Livelli e posizioni come `regole/formato_reel.md` (musica 0.08-0.11 costante sotto la voce, segni gain 0.24, chiusura e
musica fino all'ultimo fotogramma del logo).

## teaser
| File | Durata | Livello | Dove |
|---|---|---|---|
| `teaser_musica.flac` | 25 s | -18 LUFS | da 0:00 a fine logo; archi brevi a passo (92 bpm) + archi tenuti, cresce verso la fine (bozza A) |
| `teaser_cue_gancio.flac` | 3.5 s | -18 LUFS | prima immagine; quattro note di piano che restano sospese (B) |
| `teaser_cue_rivelazione.flac` | 4.5 s | -18 LUFS | prima nota sui gusci che galleggiano (`0021`), musica -6 dB mentre suona (B, arpeggio di piano) |
| `teaser_cue_chiusura.flac` | 5.5 s | -18 LUFS | sulla fine della voce fino al logo: motivo del lungo fa-lab-sol-fa (A, piano e archi) |
Rifare: `python3 audio/musica/coir_verticali.py teaser musica A out.wav` (gancio B, rivelazione B, chiusura A), poi
loudnorm a -20 (musica) / -18 (segni) come in `flac()`.

## made in india, indietro, premilla, 1975 (scelte di Insights, 9/11)
| Reel | Musica | Gancio | Rivelazione (immagine) | Chiusura |
|---|---|---|---|---|
| teaser | A archi a passo | B piano | B arpeggio di piano (`0021`) | A piano + archi |
| madeinindia | A archi a passo, armonia ferma | B piano | A archi + piano, la bemolle (`0542`) | A piano + archi |
| indietro | C pizzicato regolare | B piano | B arpeggio, mi bemolle (`0074`) | A piano + archi |
| premilla | A archi caldi (re bemolle) | B piano | A archi + piano (`0016`) | B solo piano |
| 1975 | A accordi lunghi | B piano | A archi + piano, la bemolle (`0527`) | B solo piano |
File: `<reel>_musica.flac` (25 s, bozza scelta) e `<reel>_cue_gancio|rivelazione|chiusura.flac`.

## Montati con questo audio (Manuel 9/11: "ci pensi tu", senza Montaggio)
`python3 projects/coir/audio/verticali.py teaser madeinindia indietro premilla 1975`: prende il video APPROVATO da Drive
(montati/coir, in `work/coir/drive/`, copiato senza ricodifica: immagini, testi e sottotitoli identici, verificato) e ci
mette sopra l'audio rifatto con `projects/coir/build.py` (voce negli stessi tempi: scarto 0 ms con l'approvato).
Musica ricomposta della durata esatta del reel (crescendo sul finale). Livelli (Manuel 9/11: "molto più bassi, accompagnamento
leggero"): 0.025 sotto la voce, -6 dB mentre suona la
rivelazione, 0.055 dopo la voce; segni a 0.08 (chiusura 0.14, dalla fine della voce all'ultimo fotogramma del logo).
La musica resta sotto il livello dei verticali approvati prima, anche sul logo.
Limitatore a -2 dB con sovracampionamento: -14.7/-15.2 LUFS, picchi sotto -1.8 dBTP.
