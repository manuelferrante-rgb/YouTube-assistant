# Meenakshi: girato (Montaggio, 29/10)

Cartella Drive 1Gov2PE4EU32BZPdJW3miH3oYPc68Iv8v ("Madurai Temple"). Scaricato il 29/10 alle 14:38 UTC in
`work/meenakshi/raw` (rclone). Tutte le clip: DJI Mimo, verticali 2160x3840, 23.976 fps, audio AAC stereo 48 kHz.
Totale: 6 clip, 22.9 s. Trascrizione (`tools/transcribe_segments.py`): NESSUN parlato (solo un "Oh." a 4.3 s di
175458). Quindi il verticale si regge tutto sul voiceover.

| Clip (ora di ripresa) | Durata | Cosa si vede | Uso |
|---|---|---|---|
| 175458 (17:54) | 4.7 s | Manuel in selfie camminando, dietro la torre (gopuram) colorata intera, cielo di giorno, jeep e passanti | Manuel in camera davanti alla torre; NON è la rotazione d'ingresso |
| 175530 (17:55) | 1.9 s | Torre dal basso, grandangolo, colori e sculture; luce di giorno | torre sotto "i colori delle torri" |
| 180328 (18:03) | 2.0 s | Elefante di pietra consumato davanti a un recinto, tettoia, bandiere rosse e bianche | dettaglio del tempio |
| 180344 (18:03) | 4.1 s | Carrellata che gira attorno alla torre all'imbrunire, luci accese, strada lastricata, transenne, poche persone | la più "rivelazione": candidata per "Guardatelo oggi" se la rotazione d'ingresso non arriva |
| 181902 (18:19) | 5.6 s | Panoramica di sera dall'alto (terrazza): torri illuminate dietro gli alberi | chiusura / torri di sera |
| 182956 (18:29) | 4.5 s | Signore anziano con turbante bianco e segno rosso sulla fronte, si avvicina alla camera e sorride; sera | gancio (zoom lento sul viso) |

Torri: sì, ci sono (175458, 175530, 180344, 181902), quindi la riga 3 di Copy ("i colori delle torri") regge.

## Secondo caricamento (29/10, 15:20 UTC): 7 clip + voiceover
| Clip | Durata | Cosa si vede | Uso nel reel |
|---|---|---|---|
| 174632 (17:46) | 10.3 s | Sala interna del tempio, soffitto dipinto, colonne, gente e addetti | "Lo ricostruiscono e lo ampliano" |
| 180356 (18:03) | 11.1 s | Torre all'imbrunire con folla che cammina, luci accese | "Tempio di Meenakshi..." e "...ogni consacrazione" |
| 180524 (18:05) | 8.4 s | Donna in sari: saluta a mani giunte, poi prega verso il tempio dietro il cancello | "Secoli dopo, qui si viene ancora a pregare" (da 5.6 s) |
| 180606 (18:06) | 4.9 s | Strada, rotazione della camera (fine a 1.25 s), Manuel davanti alla torre intera | "Guardatelo oggi" a fine rotazione |
| 181242 (18:12) | 6.3 s | Manuel in selfie in strada al tramonto | non usata |
| 181916 (18:19) | 7.8 s | Torre illuminata di sera dalla terrazza | non usata |
| 193642 (19:36) | 5.8 s | Signora anziana a una bancarella, sorride; parla in tamil (non tradotto) | chiusura, muta |

Voiceover `Mudakathan.m4a` (26.7 s, ogni riga una volta, frasi a 3.04-6.22, 7.07-8.01, 8.99-11.86, 12.57-16.52,
17.12-19.78, 20.62-22.81 sulla voce pulita). Riascoltato a pezzi: "questo tempio fu saccheggiato" (la trascrizione
intera sente "tempio e fu"), "i re Nayak", "tra il Cinquecento e il Seicento", "li rifanno ogni consacrazione".

## Consegnato (29/10, versione finale)
`montati/meenakshi/VociVere_meenakshi_reel_1080x1920.mp4`, 19.3 s (tutto a 1.1x, Manuel 29/10), -14.4 LUFS. Rifare: `python3 projects/meenakshi/build.py`
(`--preview` per la prova; cancellare `work/meenakshi/out/reel_*_work` se cambia un pezzo generato, la cache è per file).
Scelte di Manuel sul montato: signore già zoomato 1.1 s, torre con folla, rotazione solo nel giro, "Guardatelo oggi",
1.3 s dall'alto di notte, elefante su "...in India" prima dell'interno, nessuna pausa tra le frasi del VO; tra la donna
che prega e la signora solo l'inizio della carrellata; signora 2 s; frase di Copy "Ascolta altre voci, su" da quando
sparisce l'ultimo sottotitolo; logo centrato che sfuma sulla signora sotto un velo nero leggero (35%), 2 s.
Titoli: Poppins ExtraBold oro su riquadro bianco, una riga grande (stile `Tag` di `tools/reel_kit.py`, font
`assets/fonts/VVTitolo-PoppinsExtraBold.ttf`). Sottotitoli: fascia scura semitrasparente, parola corrente in oro
(`Reel(cap_box=True)`), tutti alla stessa altezza.
