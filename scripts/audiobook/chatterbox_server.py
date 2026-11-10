"""Local OpenAI-compatible TTS server for Chatterbox Turbo.

The BookForge pipeline can talk to a resident GPU model instead of loading the
500M engine per run. Start it with the venv that has chatterbox installed:

  ~/.venv-chatterbox/bin/python scripts/audiobook/chatterbox_server.py

Then run the pipeline with:

  python3 scripts/audiobook/make_audiobook.py --engine server --voice eli --publish

Voice reference files live in ``voices/`` at the repo root; set
``CHATTERBOX_VOICES`` to a ``name=path,name=path`` override if needed.
"""
import io
import os
import re
import subprocess
import threading
from pathlib import Path

import torch
import torchaudio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from chatterbox.tts_turbo import ChatterboxTurboTTS

HOST = os.environ.get("CHATTERBOX_HOST", "127.0.0.1")
PORT = int(os.environ.get("CHATTERBOX_PORT", "8890"))
VOICES_DIR = Path(__file__).resolve().parents[2] / "voices"


def discover_voices():
    voices = {}
    for path in sorted(VOICES_DIR.glob("*_voice_ref*.wav")):
        name = path.name.split("_voice_ref")[0].lower()
        voices[name] = str(path)
    for pair in os.environ.get("CHATTERBOX_VOICES", "").split(","):
        if "=" in pair:
            name, path = pair.split("=", 1)
            voices[name.strip().lower()] = path.strip()
    return voices


VOICES = discover_voices()
DEFAULT_VOICE = os.environ.get("CHATTERBOX_DEFAULT_VOICE", next(iter(VOICES), "eli"))
MAX_CHUNK_CHARS = 280

FORMATS = {
    "mp3": (["-f", "mp3", "-b:a", "128k"], "audio/mpeg"),
    "opus": (["-f", "ogg", "-c:a", "libopus", "-b:a", "64k"], "audio/ogg"),
    "aac": (["-f", "adts", "-c:a", "aac", "-b:a", "128k"], "audio/aac"),
    "flac": (["-f", "flac"], "audio/flac"),
    "wav": (None, "audio/wav"),
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = ChatterboxTurboTTS.from_pretrained(device=DEVICE)
lock = threading.Lock()
app = FastAPI()


class SpeechRequest(BaseModel):
    input: str
    voice: str = DEFAULT_VOICE
    model: str = "chatterbox-turbo"
    response_format: str = "mp3"
    speed: float = 1.0


def split_text(text):
    """Split into sentence-ish chunks so long replies don't hit the model's length cap."""
    sentences = re.split(r"(?<=[.!?…])\s+", text.strip())
    chunks, cur = [], ""
    for s in sentences:
        if cur and len(cur) + len(s) + 1 > MAX_CHUNK_CHARS:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def synthesize(text, ref):
    pieces = []
    silence = torch.zeros(1, int(model.sr * 0.2))
    for chunk in split_text(text):
        pieces += [model.generate(chunk, audio_prompt_path=ref).cpu(), silence]
    return torch.cat(pieces[:-1], dim=1)


def encode(wav, fmt):
    buf = io.BytesIO()
    torchaudio.save(buf, wav, model.sr, format="wav")
    args, ctype = FORMATS[fmt]
    if args is None:
        return buf.getvalue(), ctype
    out = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", "pipe:0", *args, "pipe:1"],
        input=buf.getvalue(), capture_output=True, check=True,
    )
    return out.stdout, ctype


@app.get("/health")
def health():
    return {"ok": True, "voices": list(VOICES), "device": DEVICE}


@app.get("/v1/models")
def models():
    return {"object": "list", "data": [{"id": "chatterbox-turbo", "object": "model"}]}


@app.post("/v1/audio/speech")
def speech(req: SpeechRequest):
    text = req.input.strip()
    if not text:
        raise HTTPException(400, "input is empty")
    ref = VOICES.get(req.voice.lower(), VOICES.get(DEFAULT_VOICE))
    if not ref:
        raise HTTPException(400, f"unknown voice {req.voice!r}; available: {list(VOICES)}")
    fmt = req.response_format if req.response_format in FORMATS else "mp3"
    try:
        with lock:
            wav = synthesize(text, ref)
        data, ctype = encode(wav, fmt)
    except Exception as e:
        return JSONResponse({"error": {"message": str(e)}}, status_code=500)
    return Response(content=data, media_type=ctype)


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
