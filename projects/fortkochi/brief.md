# fortkochi (NGO): decisioni di Manuel per il montaggio

## 16/11, primo messaggio
- Focus: quanto bene fanno le persone che lavorano lì, quanto i bambini vengono accompagnati, e noi che siamo
  fortunati senza rendercene conto. La storia dei bambini si fa sentire con le parole di chi ci lavora e le immagini
  di quello che fanno, anche senza volti. Mai musica o rallenty da pietà.
- Struttura come coir e te: apertura sulle scene più forti col VO; Manuel in camera solo dopo la sigla e dove spiega;
  VO classico sulle immagini; interviste con la loro voce e sottotitolate, mai VO sopra chi parla.
- Nessun tratto muto lungo: ogni immagine ha la voce, un'intervista o un suono vero. Non riempire per allungare.
- Ashwasa: volti dei bambini sfocati quando si vedono, ma meglio inquadrature senza volto che tante facce sfocate.
  Raksha: B-roll con le persone senza sfocare.
- Sempre: promessa di titolo e miniatura nel primo minuto, capitoli, ultimi 15 s puliti per la schermata finale.

## 16/11, audio e qualità
- B-roll SEMPRE MUTI: il suono originale delle clip di B-roll si azzera (in alcune si sente un ventilatore o un fondo
  continuo). Sotto il B-roll solo VO di Manuel o musica/segni della chat Audio.
- Interviste: voce pulita (RNNoise, `tools/voice_clean.py`), fondo della clip abbassato al minimo; controllo con
  `tools/audio_check.py` su ogni finestra con ventilatore o ronzio.
- Video molto curato: scegliere solo le riprese fatte bene (stabili, a fuoco, esposte bene; niente camminate mosse o
  capovolte come `0039`, niente inquadrature storte). Fluidità: si monta e si esporta a 23.976 fps come il girato,
  niente conversioni di frame rate; movimenti di camera tenuti interi, tagli puliti.
- Voce di Manuel: sia in camera sia in VO sul B-roll (registra lui). Musiche dalla chat Audio, fatte bene.

## v3 (Manuel 18/11, da fare dopo arthunkal; revisione Insights in `analisi/fortkochi.md`)
- BAMBINI SENZA SFOCATURA: Manuel ha il consenso di tutti. Si usano le clip originali (niente `work/fortkochi/blur`, `B(k)` -> `C(k)`).
- Apertura: SUBITO il ragazzo seduto che saluta Manuel (immagine molto forte), poi i ragazzi di Raksha al lavoro inquadrati
  bene (i ragazzi, non la stanza), con sopra la voce dell'educatrice; lei in video dopo. Circa 3 s dopo che torna l'educatrice,
  di nuovo il ragazzo che saluta. VIA il ragazzo che fa le pulizie (Manuel: "leva quello che pulisce").
- Interviste accorciate alla frase forte (15-20 s), il resto coperto da B-roll o da un'inquadratura più stretta: suore 1:00-1:50
  e 3:06-3:32, educatrice 4:00-4:20, 5:00-5:45, 5:51-6:39 (tempi della v2).
- Tagli netti al posto delle dissolvenze (0:27, 2:36, 4:24, 4:45, 6:54). Sottotitoli delle interviste 1.5 volte più grandi.
- Raksha: meno ripetizioni di scale e corridoio; se manca girato, un pezzo di Manuel in camera. La durata può scendere.
- Poi Copy rifà sottotitoli e capitoli.
