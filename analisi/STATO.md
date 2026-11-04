# Insights: stato e passaggio di consegne (aggiornato 4/11/2026)

Da leggere all'avvio di ogni nuova chat Insights, dopo CLAUDE.md e analisi/README.md.

## Cosa è stato fatto (27/10-4/11, chat Insights session_01HtfbgyzAxUCZDsgATkknE1)
- MERCATO, dati a 48 ore (YT lungo, YT Shorts, IG teaser e reel 1): `mercato.md`. Punti chiave: durata media
  1:43 (28%), 46 spettatori unici, 87% non iscritti, italiani 81%; buco tra 0:30 e 1:30 ("Il giorno prima"),
  risalita a ~3:15-3:45 (probabile pesce da 50 kg promesso dalla miniatura); CTR 3,7%; teaser-trailer scorso via
  61% IG / ~84% YT contro 25,6% IG / ~64% YT del reel aperto sul pescatore; 0 follower IG da 16 visite al profilo;
  invii e commenti quasi zero; teaser YT collegato al lungo solo dopo l'uscita.
- Regola passata a Montaggio: primo fotogramma dei reel = persona o gesto più forte (nota in
  `regole/formato_reel.md`). Modifiche ad arthunkal e te prima dell'uscita: note del 4/11 in
  `projects/arthunkal/brief.md` e `projects/te/brief.md` (Manuel le manda a Montaggio, file sostituiti su Drive).
- Miniature meno da blogger, persone del posto al centro, 2-3 versioni in "Test e confronto": `miniature.md` +
  nota in `regole/copy.md` (Manuel la manda a Copy, con rifacimento miniature di arthunkal, te e mercato).
- Kanyakumari (`comorin`): ricerca e brief di 4 reel in `comorin_reel.md`; i reel sono già fatti (Manuel, 4/11).
- Messaggi a Montaggio e Copy dati a Manuel il 4/11 sera (non ancora inviati quando si è chiusa la chat).

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
- Promemoria programmati (spostati sulla nuova chat Insights il 4/11): dati mercato a 7 giorni (dom 8/11, mattina
  in India: analisi principale, completa `analisi/mercato.md` e decidi cosa diventa regola), revisione strumenti
  (9/11). Per ogni nuovo lungo uscito programmare 48 h e 7 giorni (arthunkal: lungo dom 15/11 -> 17/11 e 22/11).
- In arrivo da Manuel: insights del reel B del mercato (appena pubblicato), stories set 1, reel 2 e 3 IG.
  A 7 giorni: confermare o smentire le lezioni di `mercato.md` (primo minuto, miniatura, primo fotogramma).
- Da seguire: risultato del "Test e confronto" della nuova miniatura del mercato; dati dei 4 reel comorin quando
  escono (skip rate e invii per primi).
