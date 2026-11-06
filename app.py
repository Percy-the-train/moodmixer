import io
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from scipy.signal import resample_poly
from transformers import pipeline

MODEL_ID = "superb/wav2vec2-base-superb-er"
SAMPLE_RATE = 16000

EMOTION_LABELS = {
    "neu": "neutral",
    "hap": "happy",
    "ang": "angry",
    "sad": "sad",
}

BASE_DIR = Path(__file__).resolve().parent

_emotion_pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _emotion_pipeline
    _emotion_pipeline = pipeline("audio-classification", model=MODEL_ID)
    yield


app = FastAPI(title="Speech Emotion Recognition", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


def load_audio_16k(data: bytes) -> np.ndarray:
    audio, sr = sf.read(io.BytesIO(data), dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != SAMPLE_RATE:
        audio = resample_poly(audio, SAMPLE_RATE, sr).astype("float32")
    return audio


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio file")
    try:
        audio = load_audio_16k(data)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode audio")
    if len(audio) == 0:
        raise HTTPException(status_code=400, detail="No audio samples found")
    result = _emotion_pipeline(audio)
    predictions = [
        {"emotion": EMOTION_LABELS.get(p["label"], p["label"]), "score": float(p["score"])}
        for p in result
    ]
    return {"predictions": predictions}
