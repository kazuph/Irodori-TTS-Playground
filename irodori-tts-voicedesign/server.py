"""
FastAPI server wrapping Irodori-TTS VoiceDesign InferenceRuntime.
POST /v1/tts  → WAV audio response (with optional caption for voice design)
GET  /health  → {"status": "ok"}
"""
import io
import os
import time
import logging
import tempfile

import torch
import torchaudio
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("irodori-tts-voicedesign")

app = FastAPI(title="irodori-tts-voicedesign")

runtime = None
HF_CHECKPOINT = os.environ.get("IRODORI_HF_CHECKPOINT", "Aratako/Irodori-TTS-500M-v2-VoiceDesign")
MODEL_DEVICE = os.environ.get("IRODORI_DEVICE", "cuda")
MODEL_PRECISION = os.environ.get("IRODORI_PRECISION", "bf16")


class TTSRequest(BaseModel):
    text: str
    caption: Optional[str] = None
    num_steps: int = 40
    cfg_scale_text: float = 3.0
    cfg_scale_caption: float = 3.0
    cfg_scale_speaker: float = 5.0
    seed: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    model: str
    ready: bool


@app.on_event("startup")
def load_model():
    global runtime
    logger.info(f"Loading Irodori-TTS VoiceDesign: {HF_CHECKPOINT}")

    from huggingface_hub import hf_hub_download
    from irodori_tts.inference_runtime import InferenceRuntime, RuntimeKey

    checkpoint_path = hf_hub_download(
        repo_id=HF_CHECKPOINT,
        filename="model.safetensors",
    )
    logger.info(f"Checkpoint downloaded: {checkpoint_path}")

    runtime = InferenceRuntime.from_key(
        RuntimeKey(
            checkpoint=checkpoint_path,
            model_device=MODEL_DEVICE,
            codec_repo="Aratako/Semantic-DACVAE-Japanese-32dim",
            model_precision=MODEL_PRECISION,
            codec_device=MODEL_DEVICE,
            codec_precision=MODEL_PRECISION,
            codec_deterministic_encode=True,
            codec_deterministic_decode=True,
            enable_watermark=False,
            compile_model=False,
            compile_dynamic=False,
        )
    )
    logger.info("Irodori-TTS VoiceDesign loaded")


@app.get("/health")
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=HF_CHECKPOINT,
        ready=runtime is not None,
    )


@app.post("/v1/tts")
def synthesize(req: TTSRequest):
    if runtime is None:
        raise HTTPException(503, "Model not loaded")

    from irodori_tts.inference_runtime import SamplingRequest

    t0 = time.time()
    result = runtime.synthesize(
        SamplingRequest(
            text=req.text,
            caption=req.caption,
            ref_wav=None,
            ref_latent=None,
            no_ref=True,
            num_candidates=1,
            decode_mode="sequential",
            seconds=30.0,
            num_steps=req.num_steps,
            cfg_scale_text=req.cfg_scale_text,
            cfg_scale_caption=req.cfg_scale_caption,
            cfg_scale_speaker=req.cfg_scale_speaker,
            cfg_guidance_mode="independent",
            cfg_min_t=0.5,
            cfg_max_t=1.0,
            context_kv_cache=True,
            seed=req.seed,
            trim_tail=True,
            tail_window_size=20,
            tail_std_threshold=0.05,
            tail_mean_threshold=0.1,
        ),
        log_fn=None,
    )
    elapsed = time.time() - t0

    audio = result.audio.float().cpu()  # (1, N)
    sr = result.sample_rate

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
        torchaudio.save(tmp.name, audio, sr)
        tmp.seek(0)
        wav_bytes = tmp.read()

    audio_duration = audio.shape[-1] / sr
    logger.info(
        f"TTS VoiceDesign: {len(req.text)} chars "
        f"(caption={'yes' if req.caption else 'no'}) "
        f"-> {audio_duration:.1f}s audio in {elapsed:.2f}s "
        f"(RTF: {audio_duration/elapsed:.2f})"
    )

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={
            "X-TTS-Duration": f"{audio_duration:.2f}",
            "X-TTS-Elapsed": f"{elapsed:.2f}",
            "X-TTS-RTF": f"{audio_duration/elapsed:.2f}",
        },
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("IRODORI_PORT", "8006"))
    uvicorn.run(app, host="0.0.0.0", port=port)
