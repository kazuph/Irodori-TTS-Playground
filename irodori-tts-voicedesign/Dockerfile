FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ffmpeg libsndfile1 python3.11 python3.11-venv python3.11-dev git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/bin/uv

# Clone latest Irodori-TTS (includes VoiceDesign support)
RUN git clone --depth 1 https://github.com/Aratako/Irodori-TTS.git /app/irodori-tts

WORKDIR /app/irodori-tts
RUN uv sync --python python3.11

# Install server deps into the same venv
RUN uv pip install fastapi uvicorn[standard] soundfile numpy

COPY server.py /app/irodori-tts/server.py

EXPOSE 8006

CMD ["/app/irodori-tts/.venv/bin/python", "server.py"]
