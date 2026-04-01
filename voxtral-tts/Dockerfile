FROM vllm/vllm-openai:latest

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir git+https://github.com/vllm-project/vllm-omni.git
