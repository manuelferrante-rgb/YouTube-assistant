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

## Revisione del 9/11 (ultime due settimane: git log, regole, projects/)
| Strumento | Stato al 9/11 | Note |
|---|---|---|
| Google Drive + rclone | In uso | consegna di tutti i lunghi e verticali, registrazioni dello schermo per Insights |
| GitHub (repo) | In uso | memoria comune, passaggi di consegne tra chat (STATO.md) |
| ffmpeg, Python, font, parakeet | In uso | sottotitoli di arthunkal, te, coir; tutti gli strumenti in `tools/` |
| YuNet + SFace (volti) | In uso, NUOVO | Copy: carosello "I volti" e miniature v3 (`copioni/caroselli/volti_scan.py`) |
| Generatori di Copy (miniature v3, caroselli, stories) | In uso, NUOVO | `copioni/miniature_v3/`, `copioni/caroselli/`, `copioni/stories/` |
| Pixabay | Poco usato | solo in `projects/te` e `projects/comunismo`; tenere (gratis, serve per grafiche generiche) |
| yt-dlp | Usato da Insights | competitor (25/10, 4/11) |
| Freesound (`FREESOUND_API_KEY`) | Non serve | Audio fa solo musica originale, mai librerie (regola di Manuel 27-29/10), e il server rifiuta i computer cloud (`audio/STATO.md`) |
| Chiave AWS | Non serve | nessun file del repo la usa |
| Cloudflare Workers AI | Chiuso | Manuel non vuole immagini IA (27/10) |
| Messaggi tra le chat | Solo eccezioni | regola del risparmio: tutto passa dai file |

Da fare: togliere dall'ambiente FREESOUND_API_KEY e le chiavi AWS (meno chiavi = meno rischi; le toglie Manuel in Settings).
Nella riga "librerie CC0 (Freesound...)" di `regole/audio.md` c'è ancora un riferimento vecchio: lo sistema Audio se vuole.

## Prossime revisioni
- A fine viaggio in Kerala (fine novembre): cosa è servito davvero e cosa togliere.

Nota da Pianificazione, 27/10: Manuel ha deciso di NON usare immagini IA (Cloudflare Workers AI incluso), nemmeno per `te`. Voce "Da valutare" chiusa.
