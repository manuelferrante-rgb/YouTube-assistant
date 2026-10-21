# Video di presentazione del canale (16:9, circa 1:30)

Girato da Manuel davanti al telefono, sfondo neutro. Circa 210 parole: a ritmo calmo con le pause sta in 1:30.
Le barre "/" sono pause brevi, "(pausa)" una pausa vera.

## 1. Hook (0:00-0:15)
C'è una frase di un libro che non riesco a togliermi dalla testa. /
"Ti guardi distrattamente in uno specchio, e la persona che vedi non sei tu." /
E allora ti chiedi: davvero desideravo questa vita? O è semplicemente capitata?
(pausa)
Ho 25 anni. E a quel punto non ci voglio arrivare.

## 2. Chi sono (0:15-0:35)
Mi chiamo Manuel. Per anni ho lavorato nel no-profit: fermavo le persone per strada e raccontavo storie che non
erano mie. Storie di persone che non avevo mai incontrato. /
Adesso voglio andarle ad ascoltare. Da chi le vive.

## 3. Il dubbio (0:35-0:50)
Non ho tutte le risposte. / Avere dubbi è normale. Sentirsi all'improvviso senza riferimenti, senza certezze,
capita. / Ma so che non troverò niente restando fermo.

## 4. Voci Vere (0:50-1:15)
Per questo è nato Voci Vere. / Per dare voce a chi ne ha più bisogno.
Viaggio nei posti lontani dalle cartoline, a partire dal Kerala, in India. Incontro chi lavora, chi tira
avanti, chi di solito non viene ascoltato. E lascio parlare loro. /
Senza filtri. Senza pietismo. Non per salvare nessuno: per ascoltare e raccontare.

## 5. Chiusura (1:15-1:30)
Forse, in giro per il mondo, un po' di senso lo troverò. Forse no. /
Ma almeno, quando mi guarderò allo specchio, saprò chi sono.
(pausa)
Se vuoi venire con me, iscriviti. / Una voce alla volta.

## Titoli (clickbait ma veri)
1. Non voglio guardarmi allo specchio e non riconoscermi
2. Ho 25 anni e non voglio diventare quella persona
3. Perché parto per ascoltare chi nessuno ascolta

## Copertina
Primo piano stretto, sguardo dritto in camera, serio ma non triste. Testo grande su 2 righe:
"NON VOGLIO / DIVENTARE COSÌ" (con titolo 2) oppure "NON SONO IO" (con titolo 1).
Variante più forte: il tuo riflesso in uno specchio, un po' sfocato, con te nitido in primo piano.

## Come girarlo
- Orizzontale, telefono all'altezza degli occhi, a circa un metro. Guarda l'obiettivo, non lo schermo.
- Luce da una finestra di lato o davanti, mai alle spalle. Sfondo neutro a 1-2 metri dietro di te.
- DJI Mic sul petto.
- Non leggere: impara un blocco alla volta e giralo 2-3 volte, anche con parole tue. Scelgo io le prese migliori
  e taglio le pause.
- Nel blocco 4 metto sotto il tuo girato del Kerala (mani, reti, strada) mentre parli.

---

# Sigla Voci Vere (6-8 secondi)

Si monta UNA volta sola, dal video di presentazione più qualche inquadratura del Kerala, e si riusa identica
dopo il teaser di 20 secondi di ogni video lungo e di ogni verticale.
Durante le riprese della presentazione Manuel gira anche 2-3 prese dedicate della frase della sigla, staccate
dal resto (pausa prima e dopo, sguardo in camera). Il volto e la voce vengono da lì.

## Inquadrature da girare (orizzontale, 4K)
1. (1 s) Mani al lavoro, in primo piano: reti, pesce, attrezzi.
2. (1 s) Una persona che guarda in camera, ferma, in silenzio. Niente sorriso forzato.
3. (1-2 s) IL GESTO: la tua mano che porge il DJI Mic a qualcuno, e la sua mano che lo prende.
   È il simbolo del canale: dare voce.
4. (1 s) Tu di spalle che cammini in una strada del posto.
5. (2 s) Nero o un'immagine ferma: scritta "VOCI VERE" e, più piccola, "Storie senza filtri".

## Voce (tua, una frase sola, sull'inquadratura 3 o 5)
"Voci Vere. Dare voce a chi ne ha più bisogno."
Alternativa: "Voci Vere. Storie di chi di solito non viene ascoltato."

## Musica
Una nota o un colpo di musica che sale dall'inquadratura 1 e chiude sulla scritta. La prendo dai brani che carichi.

---

# Intro + sigla: struttura standard (dal 21/10, v3, riferimento: cold open di Progetto Happiness)

Ogni video si apre con due blocchi attaccati. Niente musica: solo audio originale, voce e effetti brevi
(colpi, whoosh, lampi, riser) generati da `tools/sfx.py`.

## 1. Intro (VARIABILE, ~20-25 s, si riscrive per ogni video)
Copy fatto SOLO di parlato vero preso dal girato (Manuel e le persone), nei momenti di maggiore impatto.
- 0-3 s: raffica di 4-5 immagini forti e veloci (0.4-0.6 s), con zoom a scatto e qualche lampo. Mai
  un'inquadratura lenta come prima immagine. Colpo basso sul primo fotogramma.
- Gancio di Manuel (voce sopra immagini, avvicinamento lento): una frase che mette lo spettatore nei panni di chi
  vive lì.
- Risposta di una persona del posto (in camera, sottotitolata): conferma o ribalta il gancio.
- Seconda raffica breve, poi il dato più forte (detto in camera).
- Mappa animata (sola grafica ammessa).
- Ultima frase: una persona del posto che apre la domanda e passa la parola alla sigla.

Mercato di Marari:
  [raffica: pesce, ghiaccio, ceste in testa, ceste, il pesce grande]
  MANUEL: "Immagina di svegliarti alle tre del mattino, alle quattro dover già andare nell'oceano indiano a pescare."
  PESCATORE: "Di notte. Alle tre si comincia."
  [raffica sul mercato]
  MANUEL: "Quello enorme pesava 50-55 chili. Quindi veramente come una persona."
  [mappa: Marari]
  PESCATORE: "Cristiani, induisti, musulmani. ... È un posto in pace."

## 2. Sigla (FISSA, ~5.8 s, identica in ogni video, `tools/sigla.py`)
  MANUEL: "Il mondo, raccontato da chi lo vive. Questo è Voci Vere."
- Sotto "Il mondo, raccontato da chi lo vive": 6 lampi di viaggio da 0.5 s (assets/sigla/0N_*.mp4).
- Su "Voci": la V si stampa in due colpi, "OCI" battuto veloce; su "Vere": VERE si rivela in oro con una luce
  che la attraversa, poi linee, onda sonora e payoff (`tools/logo_anim.py`).
Collegamento: l'ultima frase dell'intro è sempre una voce del posto; la sigla risponde con "il mondo,
raccontato da chi lo vive".
