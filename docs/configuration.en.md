# ⚙️ Configuration

Talk2Scene uses [Hydra](https://hydra.cc/) for hierarchical configuration.

## 📁 Config Groups

| Group | File | Description |
|-------|------|-------------|
| 🧠 model | `conf/model/default.yaml` | Whisper and LLM settings |
| 📡 stream | `conf/stream/default.yaml` | Redis stream settings |
| 🖼️ render | `conf/render/default.yaml` | Canvas, render, and video settings |
| 🎨 assets | `conf/assets/default.yaml` | Asset paths and z-order |
| 👤 character | `conf/character/default.yaml` | Character defaults and transitions |
| 📂 io | `conf/io/default.yaml` | Input/output paths and formats |

## 🤖 LLM Settings

Default model is `gpt-4o` with JSON mode enabled (`response_format: json_object`). This guarantees valid JSON output from the scene generator.

| Setting | Default | Description |
|---------|---------|-------------|
| `model.llm.model` | `gpt-4o` | OpenAI model (must support JSON mode) |
| `model.llm.temperature` | `0.3` | Lower = more deterministic scene codes |
| `model.llm.max_tokens` | `4096` | Max tokens for scene generation response |

Override the model via CLI:
```bash
uv run talk2scene mode=text io.input.text_file=input/transcript.jsonl model.llm.model=gpt-4o-mini
```

## 📡 Stream Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `stream.redis.stream_key` | `stream:mic` | Raw audio stream key |
| `stream.redis.stt_stream_key` | `stream:stt` | Pre-transcribed text stream key (higher priority) |
| `stream.redis.consumer_group` | `talk2scene` | Redis consumer group name |
| `stream.redis.consumer_name` | `worker-1` | Consumer name within the group |
| `stream.redis.block_ms` | `1000` | Block timeout for XREADGROUP |
| `stream.redis.batch_size` | `10` | Max messages per read |
| `stream.redis.backpressure_max` | `100` | Max pending messages before pausing |

## 🖼️ Render Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `render.canvas.width` | `1024` | Canvas width in pixels |
| `render.canvas.height` | `1024` | Canvas height in pixels |
| `render.scene_on_event` | `false` | Render `front_page.png` on each scene event batch (stream mode) |
| `render.video.fps` | `30` | Video output frame rate |
| `render.video.crf` | `18` | Constant rate factor (lower = higher quality) |
| `render.video.format` | `webm` | Video format: `webm`, `mp4`, or `avi` |
| `render.video.subtitle` | `true` | Burn subtitles into video |
| `render.video.subtitle_font_size` | `32` | Subtitle font size in pixels |
| `render.video.preview` | `true` | Open video after rendering |

## ⌨️ CLI Overrides

Hydra supports dot-notation overrides:

```bash
uv run talk2scene model.whisper.model_size=medium stream.redis.host=myhost
```

## 🔑 Environment Variables

- `OPENAI_API_KEY`: Required for LLM scene generation
