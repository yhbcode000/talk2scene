<p align="center">
  <h1 align="center">🎙️ Talk2Scene</h1>
  <p align="center">
    <em>Audio-driven intelligent animation generation — from dialogue to visual storytelling.</em>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License">
    <img src="https://img.shields.io/badge/package_manager-uv-blueviolet?logo=uv" alt="uv">
    <img src="https://img.shields.io/badge/config-Hydra-orange?logo=meta" alt="Hydra">
    <img src="https://img.shields.io/badge/LLM-GPT--4o-black?logo=openai" alt="GPT-4o">
  </p>
</p>

---

Talk2Scene is an **audio-driven intelligent animation tool** that automatically parses voice dialogue files, recognizes text content and timestamps, and uses AI to recommend matching **character stances (STA)**, **expressions (EXP)**, **actions (ACT)**, **backgrounds (BG)**, and **CG illustrations** inserted at the right moments. It produces structured scene event data and composes preview videos showing AI characters performing dynamically across scenes.

Designed for **content creators**, **educators**, **virtual streamers**, and **AI enthusiasts** — Talk2Scene turns audio into engaging visual narratives for interview videos, AI interactive demos, educational presentations, and more.

## 💡 Why Talk2Scene

Manually composing visual scenes for dialogue-driven content is tedious and error-prone. Talk2Scene automates the entire workflow: feed in audio or a transcript, and the pipeline produces **time-synced scene events** — ready for browser playback or video export — without touching a single frame by hand.

## 🏗️ Architecture

```mermaid
flowchart LR
    A[Audio] --> B[Transcription\nWhisper / OpenAI API]
    T[Text JSONL] --> C
    B --> C[Scene Generation\nLLM]
    C --> D[JSONL Events]
    D --> E[Browser Viewer]
    D --> F[Static PNG Render]
    D --> G[Video Export\nffmpeg]
```

Scenes are composed from **five layer types** stacked bottom-up:

```mermaid
flowchart LR
    BG --> STA --> ACT --> EXP
```

> A **CG** illustration, when active, replaces the entire layered scene.

## 🖼️ Example Output

### Example Video

<p align="center">
  <img src="evaluation/expected/example_output.gif" width="600" alt="Example output video">
</p>

### Rendered Scenes

<p align="center">
  <img src="evaluation/expected/basic_scene.png" width="280" alt="Basic Scene — Lab + Stand Front + Neutral">
  <img src="evaluation/expected/cafe_thinking.png" width="280" alt="Cafe Scene — Cafe + Stand Front + Thinking">
  <img src="evaluation/expected/cg_pandora.png" width="280" alt="CG Mode — Pandora's Tech">
</p>

<p align="center">
  <em>Left: Basic scene (Lab + Stand Front + Neutral) · Center: Cafe scene (Cafe + Stand Front + Thinking) · Right: CG mode (Pandora's Tech)</em>
</p>

### Asset Layers

Each scene is composed by stacking transparent asset layers on a background. Below is one sample from each category:

| Layer | Sample | Code | Description |
|:-----:|:------:|------|-------------|
| 🌅 **BG** | <img src="assets/bg/BG_Lab_Modern.png" width="120"> | `BG_Lab_Modern` | Background (opaque) |
| 🧍 **STA** | <img src="assets/sta/STA_Stand_Front.png" width="120"> | `STA_Stand_Front` | Stance / pose (transparent) |
| 🎭 **EXP** | <img src="assets/exp/EXP_Smile_EyesClosed.png" width="120"> | `EXP_Smile_EyesClosed` | Expression overlay (transparent) |
| 🤚 **ACT** | <img src="assets/act/ACT_WaveGreeting.png" width="120"> | `ACT_WaveGreeting` | Action overlay (transparent) |
| ✨ **CG** | <img src="assets/cg/CG_PandorasTech.png" width="120"> | `CG_PandorasTech` | Full-scene illustration (replaces all layers) |

## 📦 Install

> [!IMPORTANT]
> Requires **Python 3.11+**, [uv](https://docs.astral.sh/uv/), and **FFmpeg**.

```bash
uv sync
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-key"
```

## 🚀 Usage

```bash
uv run talk2scene --help
```

### 📝 Text Mode

Generate scenes from a pre-transcribed JSONL file:

```bash
uv run talk2scene mode=text io.input.text_file=path/to/transcript.jsonl
```

### 🎧 Batch Mode

Process an audio file end-to-end (place audio in `input/`):

```bash
uv run talk2scene mode=batch
```

### 🎬 Video Mode

Render a completed session into video:

```bash
uv run talk2scene mode=video session_id=SESSION_ID
```

### 📡 Stream Mode

Consume audio or pre-transcribed text from Redis in real time:

```bash
uv run talk2scene mode=stream
```

## 📚 Documentation

Full documentation (English & 中文) is available at **[discover304.top/talk2scene](https://discover304.top/talk2scene)**.

## 📬 Contact

- ✉️ Email: **hobart.yang@qq.com**
- 🐛 Issues: [Open an issue](../../issues) on GitHub

## 📄 License

Licensed under the [Apache License 2.0](LICENSE).
