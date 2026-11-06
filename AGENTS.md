# AGENTS.md

## Project

MoodMixer — a speech-emotion-recognition drink machine. A user speaks or uploads a
voice clip; a Hugging Face model classifies the emotion, and the UI recommends a
drink recipe made from four raw ingredients that an Arduino dispensing rig pours.

## Stack

- Backend: Python 3.13 + FastAPI + Uvicorn
- Model: `superb/wav2vec2-base-superb-er` via `transformers` `pipeline("audio-classification")`
- Frontend: single-page vanilla HTML/CSS/JS (`static/index.html`), no build step
- Audio: `soundfile` for decoding, `scipy.signal.resample_poly` for resampling to 16 kHz

## Setup / Run

```powershell
# one-time (already done in this repo)
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# run (from project root)
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
# or double-click run.bat (starts server + opens browser)
```

Open http://127.0.0.1:8000

Note: uvicorn resolves the `app` module relative to the current directory. Run from
the project root, or pass `--app-dir "<project root>"`.

## Files

- `app.py` — FastAPI app. Loads the pipeline on startup, serves `/` and `/predict`.
- `static/index.html` — UI: file upload + mic recording, WAV encoding, results + drink recipe.
- `requirements.txt` — Python dependencies.
- `run.bat` — launcher (starts uvicorn, opens browser).

## API

- `GET /` — serves the UI.
- `POST /predict` — multipart form field `file` (audio). Returns:
  ```json
  { "predictions": [ { "emotion": "happy", "score": 0.99 }, ... ] }
  ```

## Emotion model

The model outputs 4 classes. `app.py` maps raw labels to friendly names:

| raw | emotion |
|-----|---------|
| neu | neutral |
| hap | happy   |
| ang | angry   |
| sad | sad     |

## Ingredients & recipes

Four raw ingredients, each dispensed by a solenoid valve:

| key   | ingredient |
|-------|-----------|
| black | 錫蘭紅茶 (Ceylon black tea) |
| green | 茉莉綠茶 (Jasmine green tea) |
| syrup | 蔗糖漿 (sugarcane syrup) |
| milk  | 鮮奶 (fresh milk) |

Recipes (per emotion, in `static/index.html` `RECIPES`) are `parts: { key: ml }`:

- happy → 焦糖鮮奶茶: black 180, milk 100, syrup 20
- sad → 暖心鮮奶綠: green 160, milk 130, syrup 10
- angry → 清心茉莉綠: green 300
- neutral → 經典錫蘭紅: black 300

## Conventions

- No comments in code unless requested.
- Frontend is a single self-contained HTML file (CSS + JS inline).
- Keep the drink recipe data in the frontend `RECIPES` map for now; move to the API
  if the machine controller needs to consume it.
- Do not commit the `.venv/` directory or the Hugging Face model cache.
