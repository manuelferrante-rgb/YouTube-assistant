# Regole del copy (titoli, descrizioni, didascalie)

Valgono insieme ai limiti di `CLAUDE.md` (niente retorica, niente salvatore bianco, mai il trattino lungo,
"paesi a basso/medio reddito" o il nome del paese).

- Titolo YouTube: frase concreta + luogo, es. «Un posto in pace»: alle 3 di notte in mare | Kerala, India.
  Sempre anche la versione inglese (traduzioni YouTube).
- Capitoli: minutaggi esatti dati dal montaggio, 0:00 il primo, almeno 3, ognuno di almeno 10 s, solo il titolo
  (niente "Parte 1"), in italiano e inglese.
- Verticali dopo il lungo: nessuna scritta di rimando nel video, solo un rimando breve nel testo ("video fuori",
  proporre varianti). Link e "video correlato" li mette Manuel.
- Numeri e fatti solo se verificati o detti dalle persone nel video (allora si attribuiscono).
- Ogni video sta in piedi da solo: niente richiami ai video precedenti.
- Testi di un video in `copioni/<video>_testi.md`: titolo it/en, descrizione it/en, capitoli it/en, didascalie
  dei 4 verticali (teaser + 3 dopo il lungo), idee di miniatura, giorni di uscita.
- Chiusura della descrizione YouTube (scelta di Manuel, 25/10): "Voci Vere racconta le persone e i luoghi lontani
  dalle cartoline, dando voce a chi ne ha più bisogno." EN: "Voci Vere tells the stories of people and places far
  from the postcards, giving a voice to those who need it most." Niente formula sul consenso nella descrizione.
- Titolo YouTube (regola di Manuel, 25/10, vale sopra gli schemi dei competitor): nelle anteprime si leggono solo
  le prime parole (mercato: si leggeva fino a "sulla", ~45 caratteri). Quindi gancio + paese ("India") nei primi
  ~40 caratteri; località e dettagli dopo. Gli schemi di Insights ("DENTRO + luogo", bandiera alla fine) si usano
  solo se rispettano questo. Riferimento: il titolo del mercato messo da Manuel, "Sveglia alle 3 in India 🇮🇳 ...".

Nota da Insights, 25/10 (decisione di Manuel + analisi dei competitor, `analisi/competitor/pattern.md`).
TESTI DEI VERTICALI (4 per lungo: 1 teaser prima, 3 dopo). Per ognuno Copy consegna:
- Scritta di gancio nel video (la monta Montaggio nei primi 2 s): 4-7 parole, un fatto concreto che incuriosisce.
  Es. "Scolpita a Milano. Nel 1647." Niente frasi astratte o filosofiche: nei competitor sono gli Short peggiori.
- Titolo dello Short (YT) e prima riga della didascalia IG: la curiosità stessa in max ~50 caratteri, più la
  bandiera alla fine (🇮🇳). Es. "La statua di Milano sulla costa del Kerala 🇮🇳". Il titolo deve reggere da solo,
  senza il video (schema dei migliori Shorts di Balini e Binsky).
- Didascalia IG: riga 1 il gancio; 2-4 righe brevi di contesto (luogo preciso, fatto, numeri attribuiti); per i
  3 dopo il lungo, l'ultima riga è il rimando breve (varianti: "Il video completo è sul canale", "Tutta la storia
  su YouTube, link in bio"); per il teaser "Domenica il video completo" o simile. 3-5 hashtag specifici
  (#kerala #india #vocivere + luogo/tema), niente raffiche.
- Descrizione dello Short YT: 1-2 righe che raccontano la storia e chiudono su una domanda (schema di Harald Baldr).
- Angoli che rendono: un "come funziona" spiegato da dentro, una persona del posto protagonista, il legame con
  l'Italia. Da evitare: "il più povero/pericoloso/sporco", il tono da beneficenza, i superlativi non verificabili.

Ruolo di Copy allargato (Manuel, 25/10):
- Testi a schermo per Montaggio, nella sezione "PER MONTAGGIO" di `copioni/<video>_testi.md`: etichette sui B-roll
  del lungo (luogo/ora), testi delle grafiche, e per ogni verticale gancio dei primi 2 s + scritte sulle immagini +
  quale audio già registrato usare. Si scrivono sul girato e sul VO che ci sono, non su cose da girare.
- Per i prossimi video, prima delle riprese: le domande da fare alle persone e la parte di storia da dire in camera
  (fatti con fonti dalla chat Pianificazione), nella sezione "DA DIRE E DA CHIEDERE" dello stesso file.

Consegna di Copy per ogni lungo, appena Montaggio chiude il montato (Manuel, 25/10), in quest'ordine:
1. Trascrivere il lungo finito (parakeet, `models/`) e scrivere i due file di sottotitoli per YouTube, italiano e
   inglese (`.srt` con tempi, tutto il parlato: Manuel, voiceover e interviste tradotte fedeli), in
   `projects/<video>/sottotitoli/` e caricati su Drive nella cartella del video (`montati/<video>`).
2. Titolo it/en (gancio + paese nei primi ~40 caratteri), descrizione it/en con i capitoli da
   `projects/<video>/capitoli.md`, miniatura (prove + scelta di Manuel).

Carosello di ogni lungo (Manuel, 25/10): 7-8 immagini 4:5 (1080x1350) dal girato vero, logo Voci Vere piccolo in
alto a sinistra, testo e logo dentro il quadrato centrale 1080x1080 (YouTube ritaglia a quadrato). Slide 1: foto
forte + gancio di 3-7 parole + "Scorri"; slide 2 che regge da sola; slide interne: un fatto per slide (titolo 2-5
parole + una riga, max ~15 parole); ultima: domanda specifica da commentare + "il video completo è uscito sul canale".
Didascalia IG + testo del post YouTube + posizione (luogo) in `copioni/caroselli/testi_caroselli.md`. Immagini su
Drive in `montati/<video>/carosello/`. Generatore: `copioni/caroselli/carosello.py`. Schemi dei competitor:
`analisi/competitor/caroselli.md`.
