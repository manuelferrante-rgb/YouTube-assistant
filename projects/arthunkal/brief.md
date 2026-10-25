# Prossimo lungo: cammino verso Arthunkal (16:9, ~9 min) - in preparazione

Manuel ha mandato uno script (22/10, scritto con un'IA) con prompt per scene generate: NON utilizzabili (regole:
solo girato di Manuel + mappe/grafiche; niente persone ricostruite con IA in un documentario).

Fatti verificati:
- Arthunkal Perunnal (San Sebastiano): 10-27 gennaio, giorno principale 20 gennaio. I pellegrini di Sabarimala
  passano da Arthunkal (stagione nov-gen). Basilica di Sant'Andrea dal 2010.
- Chiesa ricostruita nel 1584 sotto p. Giacomo Fenicio, gesuita italiano, morto nel 1632: è lui "Arthunkal
  Veluthachan" (padre bianco), NON San Sebastiano. Statua di San Sebastiano scolpita a Milano, arrivata nel 1647.
- San Tommaso 52 d.C.: tradizione, va detta come tale.
- "Milioni di persone", "15 km": nessuna fonte; Arthunkal è a pochi km dal mercato di Marari in linea d'aria.
Da chiedere a Manuel: evento filmato (nome, data, percorso), cosa ha detto l'host, interviste.
Tono: togliere retorica ("paradiso tropicale", "magia sociale", "milioni di cuori"...).
Gancio: partire dal momento più forte del girato (lezione del mercato), non da "Immaginate una spiaggia...".

Aggiornamento 22/10 (info dell'host + verifiche):
- Evento: Kreupasanam Akhanda Japamala (marcia del rosario ininterrotto), dal santuario mariano di Kreupasanam,
  Kalavoor (sud di Marari) alla basilica di Arthunkal (nord), ~13 km lungo la costa. Prima edizione 2002 (poche
  centinaia, fonte: santuario). 2025: ~100.000 (CatholicConnect). Host: 500.000 nel 2026 (attribuire).
- Data: host e Instagram del santuario dicono sabato 24/10; una fonte dice "ultimo sabato di ottobre" (= 31/10).
  Da confermare con l'host. Partenza prima dell'alba (fonti: 4:00 o 6:00; host: da mezzanotte).
- Copione in camera e voiceover in 16 blocchi dati a Manuel in chat (22/10), da registrare in un unico audio.
- YouTube non raggiungibile dalla rete dell'ambiente: video di riferimento da farsi mandare come file.

Montaggio (22/10): seguire le istruzioni dell'altra AI di Manuel (stile realistico, VO sui B-roll, mappa
Kalavoor->Arthunkal, linea del tempo 52 d.C. tradizione/2002/1584/1647, interviste lingua originale + sottotitoli
italiani, suoni veri) MA: niente pescatore di Marari ne' altri richiami ai video vecchi; niente titoli dei capitoli
nel video (solo minutaggi per la descrizione); VO finale in 10 blocchi (8 chi cammina, 9 arrivo, 10 chiusura con la
riflessione "viaggiare non significa soltanto..."); durata dettata dal materiale (8-9 min se regge, mai allungare).
Musica: brani YouTube Audio Library calmi se Manuel li carica, altrimenti solo suoni veri. Sigla fissa dopo l'intro.
Cartella Drive: 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX ("Festa pellegrinaggio Kerala").

Metodo di lavoro (Manuel, 23/10, vale per tutti i video): durante il montaggio gli mando in anteprima SOLO le
transizioni e le soluzioni particolari (effetti sonori, passaggi tra scene, idee nate dal montato), non pezzo per
pezzo; lui approva o chiede modifiche. Obiettivo dichiarato: ogni video migliore del precedente.
Mappa (tools/route_map.py, carta nautica chiara, globo -> India -> Kerala -> percorso con km): APPROVATA 23/10.
Effetti della mappa v2 (projects/arthunkal/map_sfx.py): un whoosh verso l'India, tick dei km, ding leggero.
Girato del 23/10 (spiaggia vuota, Manuel in camera) = il "prima"; del VO blocco 1 solo l'ultima frase.
Note di Manuel sulla mappa v2 (23/10), da sistemare in montaggio (non serve rimandargliela):
- all'inizio l'immagine sembra bloccata: niente fermo immagine prima del globo (nell'anteprima c'era 1.9 s di
  frame clonato), il globo deve già muoversi dal primo fotogramma e la mappa deve partire a tempo con la voce;
- "13 km" compare prima che lui dica "tredici chilometri": il contachilometri deve arrivare a 13 sulla parola
  "Tredici" (togliere la pausa nel VO tra "Arthunkal." e "Tredici" e/o far contare i km fino a quel momento);
- in generale sistemare script e parlato in montaggio perché il video non risulti morto (ritmo, pause tolte).
Indicazioni di Manuel sul girato del 24/10:
- Interviste: la stessa domanda fatta a più persone si mette UNA volta sola, poi le risposte di tutti in fila;
  la domanda si può anche togliere se dalle risposte si capisce. Manuel farà anche parlato suo in camera.
- Riprese delle 2:30 di notte (più clip, Manuel non parla perché stanco): piccolo montaggio con scritta in
  sovrimpressione grande e centrale, che entra in modo discreto: "2:30 di notte" (tutto in italiano).
- Parlato in camera spezzato (Manuel pensa a cosa dire e scandisce): tagliare le pause lunghe tra una frase e
  l'altra, tenendo il respiro naturale; dove il salto si vede, coprire con B-roll invece di un jump cut secco.
- FINALE: voiceover del blocco 10 (vo_take1 162.42-182.33, al singolare) sulle immagini che Manuel indicherà,
  poi Manuel in camera che dice il claim finale su Voci Vere (lo gira lui).
- Finale: le immagini nell'ORDINE in cui Manuel le carica.
- STILE (24/10): più cinematografico e professionale. Transizioni zoom -> nero breve -> nuova scena dal nero con
  effetto sonoro (prova: work/arthunkal/gfx/transizione_zoom_nero.mp4); cambi scena veloci, lenti dove serve.
- Grafiche storiche oltre alla mappa: linea del tempo (52 d.C. tradizione, 1584 Fenicio, 1647 statua da Milano;
  2002 prima edizione nel blocco 4), stesso stile carta nautica della mappa.
- Conclusione in camera girata due volte: preferita quella IN CHIESA (rumore di fondo ma si capisce); l'altra,
  girata più avanti, solo se quella in chiesa proprio non si sente.
- Regola per tutto il video: dove c'è confusione ma la voce si capisce, tenerla e mettere i sottotitoli in
  italiano, stesso stile delle traduzioni (vale anche per il parlato di Manuel in quei punti).
- 24/10: transizione zoom->nero un filo più veloce; linea del tempo più rapida (ogni data quando la dice, poi
  riparte da lì alla data successiva: approvata l'idea). Effetti sonori: Manuel li vuole NATURALI e professionali,
  non sintetici "forzati": lista proposta in chat, si usano suoni veri (girato, YouTube Audio Library caricati da
  Manuel su Drive). Pixabay/Freesound non raggiungibili dall'ambiente.
Riferimento per l'INTRO (25/10, registrazioni schermo di Manuel: "Inside India's longest train", @kk.create, primi
30 s): lei in camera che cammina e lancia la promessa del video nei primi secondi; stacchi veloci (~1 s) sui momenti
più forti (salita caotica sul treno, interni); un'inquadratura-simbolo del luogo tenuta in mano/in primo piano
(il cartello del treno); poi la mappa del percorso e si torna a lei che cammina. Da prendere: ritmo, promessa
detta in camera, inquadratura-simbolo, mappa subito dopo il gancio. Da NON prendere: il treno 3D generato
(niente scene IA), la mappa satellitare (la nostra carta nautica è già approvata).
Secondo riferimento per l'INTRO (25/10): "30 Days on a Death Ship" (@ruhicenetdocs), primi ~50 s. Apre sul momento
più spettacolare (onde che si abbattono sulla prua), poi la persona dentro la scena, poi la tensione con le persone
(equipaggio), poi il GLOBO che individua il luogo, poi stacchi veloci con piccole etichette in corsivo nell'angolo
che dicono cosa si vede ("Emergency Drill"). Da prendere: apertura sul colpo d'occhio più forte (la folla), globo
subito dopo (già nella nostra mappa), etichette discrete in corsivo nell'angolo per luoghi/ore (es. "Kalavoor,
2:30 di notte") oltre alla scritta grande centrale già decisa per le 2:30.
Registrazioni dei due riferimenti (con audio, utili alla chat Audio per il sound design) su Drive:
cartella del video -> montati/riferimenti (treno_kkcreate_a/b.mov, nave_ruhicenet_a/b.mov).

Nota da Insights, 25/10 (approvata da Manuel): per arthunkal 4 verticali, teaser + 3 dopo il lungo (nuova regola
in CLAUDE.md). Angoli proposti dall'analisi dei competitor, dettagli in `analisi/competitor/pattern.md`:
teaser "2:30 di notte" con domanda aperta senza l'arrivo; statua scolpita a Milano nel 1647 e il gesuita
"padre bianco"; un solo pellegrino che risponde a "perché cammini?"; come funziona il rosario ininterrotto
(Kalavoor -> Arthunkal, 13 km, dal 2002). Ognuno autonomo, 30-60 s, titolo = la curiosità.
- 25/10: brani musicali ed effetti sonori li fornisce direttamente la chat Audio (non scegliere io tra i 2 mp3
  della cartella Drive); il montaggio li chiede in projects/arthunkal/audio_cue.md.
