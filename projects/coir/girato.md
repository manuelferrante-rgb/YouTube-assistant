# coir: girato e scelte di Montaggio (6/11)

Girato: cartella Drive "Coir" (19zCOBK_aJ6a4SFwGffbZvDKUr-IXR8UA), 122 clip DJI 4K HEVC 29.97 fps del 6/11 + `voiceoverlungo.m4a`
e `voiceoververticali.m4a`. Scaricato con rclone in `work/coir/raw`. Trascrizione a parole in `work/coir/words.json`
(parakeet su tutta la clip con dynaudnorm: i tratti brevi a energia perdevano la chiusura `0102`), voce pulita in `work/coir/voce`.
Montaggio: `python3 projects/coir/build.py long|teaser|madeinindia|indietro|premilla|1975 [--preview]`.

## Parlato usato (tempi nella clip)
- `0034` 0.2-4.0 "Così viene raccolta la materia prima per produrre i nostri tappeti." / `0038` "Il cocco da cui viene estratta la fibra viene da qua."
- `0526` 5.2-15.3 Manuel: "Queste donne prima lavoravano con la fibra di cocco, la coir..." / `0527` 18.1-21.0 "1975" (detto in due pezzi, "nineteen... seventy five", audio sporco).
- `0538` 0.4-12.1 "non c'è un proprietario... comunità" / `0546` 9.4-30.4 Manuel spiega la barca e le donne.
- `0031`, `0044` (la barca), `0045` (il frutto velenoso), `0043` (privilegiato), `0064` 6.4-9.3 ("mi prendono in giro, posso andare in Italia con questa barca").
- `0542` 4.4-7.6 domanda "How many years did you do this?" + 9.4-10.4 "Forty years".
- `0549` Premilla: nome 1.9-2.4, "sixty" 7.1-8.7, "forty years" 12.1-13.1, "this society opened forty years" 13.4-15.9 (la domanda "What's your name?" 0-1.6 resta).
- Interprete: `0002` 0-1.6 domanda "How much is the salary?" + 35.7-36.8 "four hundred rupees per day"; `0003` 0.6-5.6 "due to this low salary new generation not coming". Sempre sotto le donne al lavoro, mai in video.
- `0006` 0-9.6 e 22.4-35.2 (salario, "nessuno vorrà farlo a stipendi così bassi") / `0062` 2.4-8.2 / `0076` 1.3-12.1 / `0091`, `0092` / `0547` 10.3-22.6 (Manuel + "mats for exporting to France, Germany") / `0094` / `0098`, `0099` / `0102` chiusura.

## Scartato e perché
- `0011` (madre che insegna): la risposta della donna non si capisce, c'è solo Manuel che la ripete. Non si usa (mai attribuire frasi).
- `0004` (domanda "chiuderete se non viene nessuno?"): la risposta non si capisce. Fuori.
- `0002` "forty rupees per piece/per day": nell'audio la stessa frase dice sia "per day" sia "per piece". Si tiene solo "400 al giorno".
- `0081`: ripete `0076` (280 pezzi, 8 ore) e i 4 euro di `0006`. `0083` (quante persone lavorano): numero non chiaro.
- `0537`, `0532`, `0023`: tolti dal check di Insights approvato da Manuel. `0001`: ripete i "quarant'anni" di Premilla e VO8.
- VO lungo: "ripeto" e prese sbagliate scartate (VO4 seconda presa 31.1, VO6 51.0, VO8 72.7, VO11 99.5, VO12 seconda presa 124.5).
- VO verticali: per "1975" Manuel ha registrato una versione nuova ("questo è quello finale", 177.9-191.5): si usa quella,
  nel suo ordine (prima "4 euro al giorno, il salario è 400 rupie", poi "per questo i giovani non vengono più", poi il resto).

## Audio
Ogni clip parlata: voce RNNoise portata a -18 LUFS con guadagno fisso + il suono originale abbassato finché il fondo sta a -56 dB
(`leveled()` in build.py). Voiceover: stessa voce pulita, stesso livello. B-roll muti. Musica di Audio a 0.11 solo sotto VO0,
VO1-VO3, VO5-VO6, VO9 (+ tagli della fabbrica), VO12 e la scritta finale. Verticali: estratti degli stessi brani (Audio non ha
ancora consegnato musiche e segni per i verticali di coir).
