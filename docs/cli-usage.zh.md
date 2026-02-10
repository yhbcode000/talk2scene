# :keyboard: 命令行使用

Talk2Scene 使用 Hydra 进行配置。所有配置值可通过命令行覆盖。

## :play_or_pause_button: 模式

### :repeat: 批处理模式
```bash
uv run talk2scene mode=batch
```

### :memo: 文本模式
直接从转写 JSONL 文件生成场景事件（跳过音频/转写）：
```bash
uv run talk2scene mode=text io.input.text_file=input/sample_transcript.jsonl
```

输入格式——每行一个 JSON 对象：
```json
{"type": "transcript", "start": 0.0, "end": 3.0, "text": "大家好。", "speaker_id": "researcher"}
```

### :satellite: 流式模式
从 Redis 流实时消费。同时支持两个输入流：

- :speech_balloon: **stream:stt** — 预转写文本（优先级更高，跳过 Whisper）
- :studio_microphone: **stream:mic** — 原始 PCM 音频（通过滚动窗口 + Whisper 处理）

```bash
uv run talk2scene mode=stream
```

两个流同时有消息时，STT 消息优先处理。流格式和发布示例见 [Redis 音频流](redis-streaming.md)。

### :clapper: 视频模式
将会话事件渲染为带字幕的视频。场景使用多进程并行渲染，再通过 ffmpeg concat 分离器拼接：
```bash
uv run talk2scene mode=video session_id=my_session
```

支持格式：`webm`（默认）、`mp4`、`avi`。

```bash
# MP4 输出，不自动预览
uv run talk2scene mode=video session_id=my_session render.video.format=mp4 render.video.preview=false
```

### :framed_picture: 渲染模式
```bash
uv run talk2scene render.scene=true render.scene_file=scene.json
```

### :bar_chart: 评估模式
```bash
uv run talk2scene eval.run=true
```

### :art: 生成素材
```bash
uv run talk2scene mode=generate-assets
```

## :level_slider: 常用覆盖参数

```bash
# 自定义会话 ID
uv run talk2scene mode=batch session_id=my_session

# 更改 Whisper 模型
uv run talk2scene mode=batch model.whisper.model_size=medium

# 更改画布大小
uv run talk2scene render.scene=true render.canvas.width=512 render.canvas.height=512

# 更改日志级别
uv run talk2scene mode=batch log_level=DEBUG

# 在流式模式下启用实时场景渲染
uv run talk2scene mode=stream render.scene_on_event=true
```
