# arthunkal RIFATTO (18/11): girato, trascrizione e scelte di Montaggio

Girato: Drive 1-31YVr-_SzqFcstOSf8RrILg_0iVDqSX, 84 clip (79 DJI del 24/10 + 0224 e 5 dji_mimo del 23/10), 2.7K 29.97 fps.
Scaricato con rclone in `work/arthunkal/raw`; trascrizione (parakeet, `tools/transcribe_segments.py`) in
`work/arthunkal/tr/tutte.json` e `log.txt`; provini (3 fotogrammi per clip) in `work/arthunkal/sheet/`.
Numero clip = le 4 cifre nel nome (`DJI_20261024023744_0236_D.MP4` = `0236`). Codice: `projects/arthunkal/rifacimento.py`.

## Cosa c'è (e cosa no)
- La STATUA non c'è in nessuna clip (confermato da Manuel 18/11): si vedono la basilica, la folla e le mani alzate.
  Milano e il 1647 restano nella voce di Manuel (`0320`) e nella linea del tempo (`tools/timeline_anim.py`).
- Notte (02:33-02:38): `0231` pentoloni e bicchieri (11 s), `0233` bancarelle con le luci, `0234` la colonna nel buio,
  `0235` pentola che luccica, `0236` lampioni e folla col rosario, `0237` volti che camminano. ~31 s in tutto.
  Lungo e trailer usano `0236` 0-3.0, `0234` 0.2-3.1, `0237` 0-2.4, `0233` 0-2.4, `0235` 1.6-4.0, `0231` 0.2-3.2;
  il reel "13 km" usa il resto (`0236` 3.0-4.8, `0234` 3.1-4.1, `0237` 2.4-3.4, `0231` 3.5-11, `0235` 0-1.6).
- Alba sulla spiaggia: `0246` folla controluce, `0243` (camera di Manuel sulla folla, voce sua 0.7-18.3), `0264` piedi e
  vestiti col canto del rosario (suono vero), `0263` (voce di Manuel "Siamo a Marari": muta).
- Basilica: `0296` selfie tra la folla "E dopo chilometri di cammino!" e poi l'arco con la basilica, `0297`/`0298` da
  lontano, `0299` folla, `0302` mani alzate (miniatura M3), `0305`-`0308` piazza e facciata, `0309` Manuel davanti alla
  basilica (audio coperto dalla folla: si usa solo dopo 15 s, senza di lui, come B-roll).
- NON si usano: `0224` parlato (giorno prima, "milioni di persone" senza fonte; la spiaggia vuota sì, muta, in chiusura),
  `0321` vecchia chiusura in camera (si usa `assets/voce/chiusura_vocivere.m4a`), mimo del 23/10 parlati (giorno prima).

## Parlato usato (tempi nella clip, tagliati sulla voce vera)
Manuel in camera, 1.05x senza pause:
- `0243` 0.7-18.3 "Sono le sette del mattino e queste persone camminano da mezzanotte. Tredici chilometri lungo la costa del
  Kerala. Pregando il rosario senza mai fermarsi. Centinaia di migliaia di persone. La prima volta nel 2002 ne erano poche centinaia."
- `0244` 1.35-4.6 "si parte da un santuario dedicato a Maria a Kalavoor", `0245` 0-3.6 "per 13-14 km fino ad Arthunkal".
- `0254` "In Kerala il cristianesimo è antico. Addirittura si dice sia arrivato nel 52 d.C. con l'apostolo Tommaso."
- `0255` "una comunità intera che... da bere e da mangiare", `0262` "Chi prega, chi guarda dalle case, chi offre acqua e chi
  è solo curioso", `0265` "volontari e volontarie devoti alla causa", `0267` "Volontari induisti che danno la loro mano...",
  `0268` "Davvero una comunità riunita", `0274` "una sosta per bere e mangiare qualcosino".
- `0270` "Proviamo per un pezzettino ad unirci a loro, nel rispetto della tradizione", `0276` "Prima lo facevano totalmente in
  strada. Poi con il traffico... direttamente in spiaggia".
- `0296` "E dopo chilometri di cammino!", `0316` "La chiesa l'ha ricostruita un gesuita italiano nel 1584. Padre Giacomo
  Fenicio. Qui lo chiamano ancora Veluthachan", `0320` "Il padre bianco. Nel 1647 arrivò una statua di San Sebastiano da
  depositare nella chiesa", `0325` "Fa caldissimo. Un sacco umido."
Interviste (sottotitoli 1.5x, zoom secco a ogni taglio): organizzatore `0240` (marcia ogni anno, apparizione di Maria ad
Alappuzha, "circa quattrocentomila persone": numero suo), ragazzi `0247` ("come una preghiera a Gesù"), `0249` ("per la
Madre, Maria. Veniamo sempre"), `0250` ("cristiani... musulmani... tutti insieme"), Elizabeth `0261` (devozione,
benedizioni, 26 anni, prima volta), pellegrina `0281` (non è la prima volta; spiaggia e strada; "è fede", "lì succedono
tanti miracoli", "chi partecipa ci trova qualcosa", "un po' di felicità").

## Mancano (segnalato a Manuel)
- Voiceover di chiusura (riflessione finale come in Progetto Happiness): per ora solo la chiusura fissa.
- Il materiale regge circa 4 minuti senza riempitivi (niente voiceover nuovo): il lungo v1 dura ~3:50.
