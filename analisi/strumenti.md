# Strumenti di Voci Vere: cosa usiamo, cosa serve, cosa no

Revisione periodica chiesta da Manuel (26/10). Obiettivo: poche cose, tutte gratuite o già pagate, e ognuna con
uno scopo chiaro. Si aggiorna a ogni revisione.

## In uso (26/10)
| Strumento | A cosa serve | Chi lo usa | Giudizio |
|---|---|---|---|
| Google Drive + rclone (`GDRIVE_RCLONE_TOKEN`) | girato in entrata, consegna dei montati | Montaggio | Indispensabile |
| GitHub (repo) | memoria comune tra le chat | tutte | Indispensabile |
| ffmpeg, Python, font, parakeet (trascrizione) | montaggio, sottotitoli, tagli delle pause | Montaggio, Copy | Indispensabile, gratis |
| Pixabay (`PIXABAY_API_KEY`) | stock generico e grafiche | Montaggio | Utile, poco usato: tenere |
| Freesound (`FREESOUND_API_KEY`) | effetti sonori con licenza | Audio | Da verificare se Audio lo usa davvero |
| yt-dlp + accesso a YouTube | analisi dei competitor | Insights | Utile |
| Accesso a Instagram | caroselli e reel dei competitor | Insights | Quasi inutile senza login: tenere solo per le immagini |
| Messaggi tra le chat | coordinamento | tutte | Utile |

## Da valutare
- Cloudflare Workers AI (immagini IA gratis): Manuel lo configura il 27/10, poi prova sulle scene storiche di "te".
  Si tiene solo se le immagini reggono la qualità del canale.
- Una chiave AWS è presente nell'ambiente ma nessun file del repo la usa: chiedere a Manuel a cosa serve, se non
  serve va tolta (meno chiavi = meno rischi).

## Non servono (per ora)
- Pexels, Veo/Kling a pagamento, servizi di analytics esterni (bastano YouTube Studio e le statistiche IG).

## Prossime revisioni
- Dopo i dati di mercato a 7 giorni (8/11) e poi a fine viaggio in Kerala: cosa è servito davvero e cosa togliere.

Nota da Pianificazione, 27/10: Manuel ha deciso di NON usare immagini IA (Cloudflare Workers AI incluso), nemmeno per `te`. Voce "Da valutare" chiusa.
