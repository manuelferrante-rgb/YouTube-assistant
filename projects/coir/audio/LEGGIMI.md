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
