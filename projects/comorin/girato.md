# Comorin: girato e montaggio (Montaggio, 4/11)

Cartella Drive 1z5BA2MoG69ExGT6ivPb9VAcbxV25VVmI, scaricata in `work/comorin/raw` con rclone (senza 135850,
140944, 125830). Clip DJI 3840x2160 a 29.97 fps (ritaglio 9:16 al centro); iPhone IMG_87xx verticali 1080x1920.
`122458` è capovolta anche dopo la rotazione dei metadati: `hflip,vflip` (FLIP in build.py).
Rifare: `python3 projects/comorin/build.py cocco|canna|statua|mari` (`--preview` per la prova a 540x960).

## Voiceover
Due file: `SH 179.m4a` = canna, `SH 179 2.m4a` = statua. Trascritti e riascoltati frase per frase sulla voce
pulita (RNNoise). Nella statua "Poi lui" è detto tre volte con "Ripeto": si usa l'ultima presa intera (28.07 s).
Tratti (s): canna 2.58-5.47, 5.75-8.33, 8.71-11.41, 11.73-14.53, 14.96-19.31; statua 3.14-6.15, 6.45-9.03,
9.34-14.09, 28.07-33.18, 33.66-39.41, 40.18-45.77, 47.54-49.17. Detto davvero: "si ripassa", "la punta più a sud"
(senza "alla"), "sharkara" (giusto).

## Persone (Manuel 4/11: solo chi lavora, mai Manuel né la sua ragazza)
Controllato fotogramma per fotogramma; da NON usare:
- `135906` da 4.4 a 7.8 s (la ragazza a 5-6.5 s, Manuel da 16 s) e da 11.1 s (braccio con braccialetto rosso);
- `140138` 0-3 s (braccio di Manuel) e da 27 s (la ragazza); `140346` 0-2 s (braccio di Manuel);
- `140244` Manuel che mangia; `140828` da 5 s (Manuel); `135736` 12.8-13.5 (mani che ricevono, non chiare);
- `122458` 0-11 s: la mano di Manuel e una ragazza con capelli ricci, top marrone e gonna bianca che può essere la
  sua ragazza. Usato solo da 12 s (panche e finestrini del traghetto).
- `132602` sono i piedi di Manuel (usati nel reel 3, solo i piedi).

## Montato consegnato (4/11, montati/comorin)
| Reel | Durata | Sequenza |
|---|---|---|
| 1 cocco | 16.7 s | sulla griglia della musica: colpo di machete (135736) / pila / tagli a 1.35x (135906, 135736) / porge (135736, 135906) / polpa (140138 11-13 s, solo mani) / gusci (140346) / prende il cocco dopo (135736) / logo su di lui |
| 2 canna | 18.8 s | ruota e canne (140516, 140434) / rulli e colino / piega e ripassa (140516 4 s, 1.5x) / succo dal colino (140808) / signora con i bicchieri (140828, cx 0.3) / rulli da vicino / chiosco (140724) / lui ai rulli (140622) e logo |
| 3 statua | 30.9 s | statua dal basso (130140, 132340) / grata del molo e traghetto (121640, 122458 da 17 s) / scoglio di Vivekananda e piedi / "Poi lui": la camera trova la statua (130308 da 1 s) / elefante / muro dei versi, scale / piedistallo / costa e onde / gente ai piedi e logo |
| 4 tre mari | 8.0 s | traghetto, scoglio, mare dal traghetto (1.3x) / onde IMG_8765 (0.9x); gli ultimi 0.3 s sfumano nei primi, così il loop non ha stacco; musica di Audio da 8.00 s messa dopo il 1.1x |
Titoli e scritte come in `copioni/comorin_testi.md`. Reel 3 a 30.9 s (copione 25-30 s): il VO intero è 28.8 s.
Controlli: fotogrammi di tutti i reel, trascrizione dei montati (nessuna parola tagliata o ripetuta), -14 LUFS.
`audio_check` segnala "fondo" in canna e statua: è la musica di Audio a 0.08 sotto la voce (B-roll muti), non rumore.

## v2 (4/11, note di Manuel), su Drive al posto della v1
- Statua: la chiusura resta ferma sulla statua (130308 da 6.0 a 8.2 s, il tratto più stabile misurato, rallentato a
  0.45x), il logo sfuma sullo stesso tratto. Tolti le onde e la gente della chiusura.
- Voce (canna e statua): il crepitio su "Thiruvalluvar" non era nella registrazione ma nella pulizia: il mono di ffmpeg
  somma i due canali (+3 dB) e su un file a 0 dBFS RNNoise saturava. `tools/voice_clean.py` ora abbassa di 6 dB prima
  di RNNoise (il livello lo rimette la normalizzazione). Rifatto anche il mix della canna (stesso difetto, file a 0 dBFS).
- Tre mari: solo le clip iPhone del 3/11 (IMG_8759 strada verso il mare, IMG_8761 sentiero fino alla scogliera,
  IMG_8762 onde sulla spiaggia, IMG_8765 le onde), niente DJI.
- Titoli oro su bianco più piccoli in tutti e 4 (corpo 82 invece di 96, riquadro 18 invece di 22, più margine ai lati):
  `TAG_SIZE, TAG_PAD, TAG_SIDE` in `tools/reel_kit.py`.
- Tre mari (v3, Manuel 4/11): "Qui si incontrano 3 mari" sull'arrivo, poi sulle onde i tre mari uno dopo l'altro
  ("Golfo del Bengala", "Mar Arabico", "Oceano Indiano", ~1.6 s ciascuno, stesso stile oro su bianco).
