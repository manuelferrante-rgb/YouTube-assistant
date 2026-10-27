# Insights: stato e passaggio di consegne (27/10/2026)

Da leggere all'avvio di ogni nuova chat Insights, dopo CLAUDE.md e analisi/README.md.

## Cosa è stato fatto (25-26/10)
- Analisi dei competitor YouTube (11 canali, ultimi 60 lunghi e 60 Shorts): `competitor/elenco.md`,
  `competitor/pattern.md` (schemi dei lunghi, dei titoli e degli Shorts, consigli di ritenzione per lunghi di 7-9 min).
- Caroselli (post YouTube dei competitor, immagini viste): `competitor/caroselli.md`.
- Instagram: cosa conta (Mosseri: tempo di visione, like, invii): `competitor/instagram.md`.
- B-roll IA per "te": ricerca su strumenti e stile, alternative gratuite: `broll_ia_te.md`. Per "te" Manuel ha
  RINUNCIATO (linea del tempo + panorami veri + Pixabay).
- Inventario strumenti: `strumenti.md`.
- Regole già passate alle altre aree (note datate Insights 25/10): formato dei 4 verticali in
  `regole/montaggio_documentario.md`, testi dei verticali in `regole/copy.md`, angoli dei verticali di arthunkal
  in `projects/arthunkal/brief.md`.

## Decisioni di Manuel da ricordare
- 4 verticali per ogni lungo: 1 teaser prima + 3 reel dopo. Formato virale ma naturale: hook nei primi 2 s,
  sottotitoli centrali su tutto il parlato, un po' di B-roll e suoni, semplice.
- Titoli: gancio + paese nei primi ~40 caratteri (regola di Copy).
- Metodo: YouTube dei competitor online (yt-dlp funziona, il dominio è sbloccato); Instagram non si vede senza login,
  quindi ricerca web + screenshot di Manuel.
- Dati dei nostri video: si chiedono a 48 ore e a 7 giorni dall'uscita del lungo. A 28 giorni NO.
- Le chat non si mandano messaggi (risparmio, CLAUDE.md): tutto passa dai file. Solo se lo chiede Manuel.

## Cosa chiedere a Manuel quando arrivano i dati (screenshot)
- Lungo YouTube: Panoramica (visualizzazioni, durata media, iscritti), Coinvolgimento (grafico di fidelizzazione),
  Copertura (impressioni, CTR, sorgenti di traffico), Pubblico (paesi, nuovi/ricorrenti).
- Shorts YouTube (teaser e reel): visualizzazioni, % "visualizzati" vs "scorsi via", durata media, iscritti,
  visualizzazioni generate sul lungo dal "video correlato".
- Reel e carosello IG: copertura, visualizzazioni, tempo medio, like, commenti, salvataggi, condivisioni (invii),
  follower ottenuti, % non follower. Numero chiave per la crescita: invii/copertura.

## Aperto
- Cloudflare Workers AI per immagini IA gratuite: Manuel deve creare account e token, poi aggiungere i segreti
  `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` e il dominio `api.cloudflare.com`. Quando ci sono: prova
  con una scena storica del tè (prompt in `broll_ia_te.md`), animata con zoom lento.
- Chiave AWS nell'ambiente non usata da nessun file: chiedere a Manuel se toglierla. Freesound: verificare se
  Audio la usa.
- Promemoria programmati (nella chat Insights attiva): dati mercato 48 h (3/11), 7 giorni (8/11, poi scrivere
  `analisi/mercato.md`), revisione strumenti (9/11). Per ogni nuovo lungo uscito programmare 48 h e 7 giorni.
