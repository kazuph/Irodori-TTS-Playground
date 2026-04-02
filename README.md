# Irodori-TTS Playground

![Screenshot](docs/screenshot-normal.png)

Docker Compose で [Irodori-TTS](https://github.com/Aratako/Irodori-TTS) の**通常版**と **VoiceDesign版**を同時に起動し、ブラウザから手軽に音声合成を試せる Web UI です。

## Features

- **通常版 / VoiceDesign 切り替え** - UI 上のトグルで即座にモデルを切り替え
- **VoiceDesign キャプション** - テキストで声質を自由にデザイン（例: 「低い声の女性が優しく話す」「ロボットの声」）
- **絵文字パレット** - Irodori-TTS 対応の全39種絵文字をワンクリックでテキストに挿入
- **絵文字サンプル即生成** - 40種のサンプルテキストをクリックするだけで即座に音声生成
- **プリセット音声** - 中二病・ラノベヒロイン・ASMR・HFサンプルなど事前生成済み音声を試聴
- **セクション折りたたみ** - localStorage でトグル状態を永続化
- **キーボードショートカット** - `Cmd+Enter` / `Ctrl+Enter` で音声生成

## Requirements

- NVIDIA GPU (RTX 3090 24GB で動作確認済み)
- Docker / Docker Compose
- NVIDIA Container Toolkit

## Quick Start

```bash
git clone https://github.com/kazuph/Irodori-TTS-Playground.git
cd Irodori-TTS-Playground

# 起動（初回はモデルDL + Dockerビルドで時間がかかります）
docker compose up -d

# ブラウザで開く
open http://localhost:8080
```

## Architecture

```
┌─────────────────────────────────────────────┐
│                nginx (:8080)                │
│   /api/irodori/  → irodori-tts (:8005)      │
│   /api/voicedesign/ → voicedesign (:8006)   │
│   /             → Web UI (index.html)       │
└─────────────────────────────────────────────┘
       │                        │
┌──────┴──────┐        ┌───────┴───────┐
│ irodori-tts │        │  voicedesign  │
│ (通常版)    │        │ (VoiceDesign) │
│ :8005       │        │ :8006         │
│ ~4.8GB VRAM │        │ ~4.7GB VRAM   │
└─────────────┘        └───────────────┘
         GPU (shared, ~9.5GB total)
```

## Models

| Model | HuggingFace | VRAM | Description |
|-------|------------|------|-------------|
| Irodori-TTS-500M-v2 | [Aratako/Irodori-TTS-500M-v2](https://huggingface.co/Aratako/Irodori-TTS-500M-v2) | ~4.8GB | 通常版。リファレンス音声 or ランダム生成 |
| Irodori-TTS-500M-v2-VoiceDesign | [Aratako/Irodori-TTS-500M-v2-VoiceDesign](https://huggingface.co/Aratako/Irodori-TTS-500M-v2-VoiceDesign) | ~4.7GB | テキストキャプションで声質をデザイン |

両モデル合計で約9.5GB。RTX 3090 (24GB) で余裕をもって同時稼働できます。

## Benchmark (RTX 3090)

| Text Length | Normal | VoiceDesign | Difference |
|-------------|--------|-------------|------------|
| Short (18 chars) | 2.97s | 2.97s | +0s |
| Long (87 chars) | 3.06s | 3.06s | +0s |

VoiceDesign のキャプション処理によるオーバーヘッドはほぼゼロです。

## API

### POST /api/irodori/v1/tts (通常版)

```bash
curl -X POST http://localhost:8080/api/irodori/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"こんにちは","num_steps":40}' \
  -o output.wav
```

### POST /api/voicedesign/v1/tts (VoiceDesign版)

```bash
curl -X POST http://localhost:8080/api/voicedesign/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"こんにちは","caption":"明るく元気な若い女性の声","num_steps":40}' \
  -o output.wav
```

## Credits

This project wraps the excellent [Irodori-TTS](https://github.com/Aratako/Irodori-TTS) by [Aratako](https://github.com/Aratako).

## License

MIT
