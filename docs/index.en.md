# :microphone: Talk2Scene

Talk2Scene converts audio dialogue into a stream of scene events (JSONL) that can be animated in a browser in realtime or replay mode.

## :star: Key Features

- :jigsaw: **Scene-first architecture**: Scenes are composable, testable, and renderable as static PNGs or animated in the frontend
- :page_facing_up: **JSONL streaming**: Primary output format with derived JSON and CSV exports
- :white_check_mark: **Strict whitelist**: STA/EXP/ACT/BG/CG codes validated against whitelist
- :lock: **Deterministic rendering**: Scene composition is deterministic for evaluation
- :globe_with_meridians: **Bilingual docs**: English and Chinese documentation

## :gear: Pipeline

```mermaid
flowchart LR
    A[Audio] --> B[Transcription\nWhisper]
    T[Text JSONL] --> C
    B --> C[Scene Generation\nLLM]
    C --> D[JSONL Events]
    D --> E[Browser Animation]
    D --> F[Static PNG Render]
    D --> G[Evaluation]
```

## :rocket: Quick Start

```bash
# Install
uv sync

# Generate placeholder assets
uv run talk2scene mode=generate-assets

# Process transcript text directly (no audio needed)
uv run talk2scene mode=text io.input.text_file=input/sample_transcript.jsonl

# Run batch mode (audio → transcription → scenes)
uv run talk2scene mode=batch

# Run evaluation
uv run talk2scene eval.run=true

# Start streaming mode
uv run talk2scene mode=stream
```
