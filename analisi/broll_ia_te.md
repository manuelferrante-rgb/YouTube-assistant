# B-roll con IA per "te" (ricerca Insights, 26/10/2026)

Solo per questo video (decisione di Manuel, 26/10). Limiti di Copy in `copioni/te_testi.md`, sezione "B-roll IA":
valgono tutti. Blocchi del voiceover = VOICEOVER v3.

## Strumenti (stato a ottobre 2026)
- **Google Veo 3.1:** il più realistico per luce, acqua, materiali. Clip di ~8 s. Genera anche l'audio:
  quell'audio NON si usa, i suoni li fa Audio.
- **Kling 3.0:** clip fino a 15 s, 4K, costa meno. Buono per i movimenti.
- **Runway Gen-4.5:** più controllo della camera, ma 720p con upscale.
- **Sora:** chiuso da OpenAI nel 2026, non usarlo.
- Per le immagini fisse da animare (illustrazioni storiche): un generatore di immagini, poi movimento lento
  in montaggio (parallasse, zoom lento) oppure image-to-video con Veo/Kling. È più controllabile e lo stile resta
  uguale in tutte le scene.
- Come si generano: nessuna chiave API IA in questo ambiente. Due strade:
  1. Manuel genera dall'app (Gemini/Flow per Veo, Kling) con i prompt qui sotto e carica i file nella cartella Drive
     del video, sottocartella `broll_ia/`, con il numero del blocco nel nome (es. `b05_foresta_a.mp4`).
  2. Una chiave API nei segreti dell'ambiente: `GEMINI_API_KEY` per Veo, oppure `FAL_KEY` (fal.ai, un'unica
     chiave per Veo, Kling e altri modelli). Così Montaggio genera da solo. Costo a secondo generato, da
     controllare sul piano scelto, insieme ai diritti d'uso commerciale.
  Prima di generare tutto: stesso prompt su Veo e Kling per una scena, si sceglie il migliore e si tiene quello.
Fonti: https://aimlapi.com/blog/best-ai-video-generators-2026-veo-3-1-kling-sora-2-seedance-more-compared ,
https://mstudio.ai/insights/best-ai-video-generator-2026 , https://pixflow.net/blog/best-ai-video-generator/

## Come lo fanno bene i documentari
- Progetto Happiness, il canale italiano più vicino a noi, usa l'IA in modo dichiarato: nella locandina del
  documentario sulla crioconservazione c'è il credito "AI creative director" (visto il 25/10).
- Linee guida dell'Archival Producers Alliance (2024, riportate da fonti secondarie): l'IA nel documentario
  è accettata se si tiene l'elenco delle scene generate, le si segnala a schermo, le si accredita, e si sta
  molto attenti con persone reali ed eventi storici realistici.
  https://www.screenweaver.ai/blog/ai-documentary-ethics-disclosure ,
  https://onira.studio/blog/historical-reconstruction-is-not-archive-footage
- YouTube: la dichiarazione "contenuti alterati o sintetici" serve quando una scena realistica può essere
  scambiata per una ripresa vera. Le illustrazioni chiaramente stilizzate non la richiedono. Qui ci saranno
  alcune scene realistiche (fabbrica, tazze), quindi va attivata.
  https://air.io/en/youtube-glossary/what-is-youtubes-ai-content-disclosure-policy
- YouTube penalizza i video "prodotti in serie" (slideshow di immagini IA senza contenuto originale). Il nostro
  girato e le interviste restano la spina dorsale: l'IA riempie solo i buchi del racconto storico.

## Regole di uso per Voci Vere (proposta di Insights)
1. **Due registri, mai mescolati:**
   - **Storia (blocchi 1-6, 9):** ILLUSTRAZIONE, mai fotorealismo. Stile unico per tutte le scene: incisione a
     inchiostro e acquerello su carta, toni seppia e verde tè, tratto visibile, come una tavola di un libro
     dell'Ottocento. Movimento lento. Si capisce subito che è una ricostruzione.
   - **Oggi (blocchi 7, 8, 12):** prima il girato di Manuel, poi Pixabay. IA realistica solo per oggetti e
     processi (foglie, macchine, tazze, sacchi) senza volti.
2. **Persone:** mai volti generati realistici. Nelle illustrazioni solo figure lontane, di spalle o in
   silhouette. Mai i Muthuvan e i Malayarayan (blocco 6): sono comunità reali, si mostrano foresta e colline.
   Mai persone IA montate vicino alle interviste.
3. **Niente testo dentro le immagini generate** (l'IA lo storpia, e date o firme inventate sono vietate).
   Date e nomi si mettono come grafica in montaggio, nello stile della linea del tempo.
4. **Scritta discreta "ricostruzione"** in basso a sinistra, piccola, sulle scene IA, come chiede l'APA.
   Da approvare da Manuel.
5. **Quantità:** al massimo circa il 20-25% della durata. Clip di 4-8 s, mai due scene IA realistiche di fila
   senza girato vero in mezzo. Mai nel gancio dei primi 30 s spacciate per vere.
6. **Look:** 16:9, 4K o upscale, movimenti di camera lenti (dolly, avvicinamento lento), niente movimenti
   veloci. Colori naturali, uguali al girato (niente arancio-verde da cinema, regola del montaggio).
   Controllare mani, dita e foglie fotogramma per fotogramma: sono il punto dove l'IA sbaglia.
7. **Audio:** l'audio generato da Veo si butta. Sulle illustrazioni storiche: musica originale di Audio più pochi
   suoni discreti (carta, penna, vento sulle colline, accette lontane). Sui processi di fabbrica: suoni veri se
   Manuel li ha registrati, altrimenti Audio.
8. **Dichiarazioni:** toggle YouTube "contenuti alterati o sintetici" attivo. Riga in descrizione (la scrive
   Copy), es. "Alcune scene storiche e di lavorazione sono ricostruzioni generate con IA." Elenco delle scene IA
   con prompt e strumento in `projects/te/broll_ia.md` (lo tiene Montaggio).

## Scene e prompt (inglese, da incollare)
Prefisso di stile per TUTTE le illustrazioni storiche:
"19th-century book illustration, ink engraving with soft watercolor wash, sepia and muted tea-green palette,
visible pen strokes, paper texture, no text, no letters, no signatures, wide 16:9 composition, slow gentle camera
push-in"

| Blocco | Scena | Registro | Prompt (dopo il prefisso, se illustrazione) |
|---|---|---|---|
| 1-2 | Contratto d'affitto e colline del 1877 | Illustrazione | "close-up of an old handwritten lease document and a fountain pen on a wooden colonial desk, oil lamp light, blank illegible handwriting" / "misty forested hills of the Western Ghats in 1877, untouched rainforest, no plantations" |
| 3 | Prime coltivazioni (caffè, cardamomo, china) | Illustrazione | "small experimental plantation clearing on a forested hillside, young coffee and cardamom plants in rows, a wooden hut, distant tiny figures seen from behind" |
| 4 | Compagnia scozzese di Glasgow, piantagioni d'epoca | Illustrazione | "Victorian trading company office in Glasgow, ledgers and maps of hills on a large table, empty room, window light" / "early tea estate on terraced hills with a colonial bungalow, 1890s" |
| 5 | Foresta tagliata, colline spoglie | Illustrazione | "rainforest being cleared on steep hills, felled trees and stumps, smoke in the distance, then bare hills being terraced, no close-up people" |
| 6 | Lavoratori portati dalle pianure | Illustrazione | "a long line of small distant figures walking up a mountain path from the plains toward misty tea hills, seen from far away and from behind, silhouettes only" |
| 7 | Mani che raccolgono | Girato di Manuel (prima scelta). IA solo se manca | "extreme close-up of two hands plucking the top two leaves and a bud from a tea bush, morning light, shallow depth of field, no face visible, realistic" |
| 8 | Fabbrica: appassimento, arrotolatura, ossidazione, essiccazione | IA realistica, solo oggetti | "fresh green tea leaves spread on long withering troughs with warm air, slow pan" / "orthodox tea rolling machine twisting leaves, close-up" / "rolled tea leaves turning copper-brown while oxidizing on a factory floor, macro" / "dried black tea leaves falling from a dryer conveyor, macro" |
| 9 | Carte e documenti di legge (1971) | Illustrazione o grafica | "stack of official government papers with a rubber stamp and a pen, blank illegible text"; anno e nome della legge come grafica |
| 11 | Sciopero 2015 | NO IA | Grafica con data e "Pombilai Orumai" (decisione di Copy) |
| 12 | Tè nelle tazze nel mondo, sacchi in partenza | IA realistica o Pixabay | "cups of tea served in different countries: a glass of chai, a porcelain cup, a clay kulhad, hands without faces" / "jute sacks of black tea stacked in a warehouse, a truck being loaded, no logos" |

Per ogni scena 2-3 varianti, poi si sceglie la migliore. Durata di ogni clip: 5-8 s.

## Decisione e alternative gratuite (26/10)
Manuel: per ora si rinuncia ai B-roll IA in "te" (linea del tempo + panorami veri + Pixabay). Alternative gratuite
da provare in futuro direttamente da qui. Video IA gratis via API non esiste (Veo e Kling via API sono a
pagamento): si generano IMMAGINI illustrate e le si anima in montaggio (zoom e parallasse lenti), cosa che si
adatta proprio allo stile "incisione".
1. **Cloudflare Workers AI**, consigliato: FLUX.1 schnell gratis entro una quota giornaliera (10K o 100K
   "neurons" al giorno a seconda della fonte, da verificare). Servono un account gratuito, i segreti
   `CLOUDFLARE_ACCOUNT_ID` e `CLOUDFLARE_API_TOKEN` (permesso Workers AI) e il dominio `api.cloudflare.com`.
2. **Hugging Face:** account gratuito con credito mensile per i modelli FLUX. Segreto `HF_TOKEN`, domini
   `huggingface.co` e `router.huggingface.co`.
3. **Pollinations.ai:** gratis senza chiave ma con limiti, filigrana senza account, nessuna garanzia.
   Dominio `image.pollinations.ai`. Buono per una prova veloce.
4. **Google Gemini API:** la quota gratuita per le immagini è contraddittoria nel 2026 (secondo alcune fonti
   non c'è più). Imagen e Veo richiedono la fatturazione. Gratis resta l'app Gemini, a mano.
Stato al 26/10: tutti e tre i domini sono bloccati dalla rete dell'ambiente (provato).
Fonti: https://www.edenai.co/post/top-free-image-generation-tools-apis-and-open-source-models ,
https://apiframe.ai/blog/free-ai-image-generation-api-2026 ,
https://blog.laozhang.ai/en/posts/gemini-image-generation-free-limit-2026
