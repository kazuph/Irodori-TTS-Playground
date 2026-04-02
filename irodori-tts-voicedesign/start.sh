#!/bin/bash
cd /app/irodori-tts
.venv/bin/python server.py &
.venv/bin/python gradio_app.py --server-name 0.0.0.0 --server-port 7860 &
wait
