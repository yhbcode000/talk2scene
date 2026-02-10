# 配置说明

Talk2Scene 使用 [Hydra](https://hydra.cc/) 进行分层配置。

## 配置组

| 组 | 文件 | 说明 |
|---|------|------|
| model | `conf/model/default.yaml` | Whisper 和 LLM 设置 |
| stream | `conf/stream/default.yaml` | Redis 流设置 |
| render | `conf/render/default.yaml` | 画布、渲染和视频设置 |
| assets | `conf/assets/default.yaml` | 素材路径和层级 |
| character | `conf/character/default.yaml` | 角色默认值和过渡 |
| io | `conf/io/default.yaml` | 输入/输出路径和格式 |

## LLM 设置

默认模型为 `gpt-4o`，启用 JSON 模式（`response_format: json_object`），保证场景生成器输出有效 JSON。

| 设置 | 默认值 | 说明 |
|------|--------|------|
| `model.llm.model` | `gpt-4o` | OpenAI 模型（须支持 JSON 模式） |
| `model.llm.temperature` | `0.3` | 越低场景代码越确定 |
| `model.llm.max_tokens` | `4096` | 场景生成响应最大 token 数 |

通过命令行覆盖模型：
```bash
uv run talk2scene mode=text io.input.text_file=input/transcript.jsonl model.llm.model=gpt-4o-mini
```

## 流设置

| 设置 | 默认值 | 说明 |
|------|--------|------|
| `stream.redis.stream_key` | `stream:mic` | 原始音频流 key |
| `stream.redis.stt_stream_key` | `stream:stt` | 预转写文本流 key（优先级更高） |
| `stream.redis.consumer_group` | `talk2scene` | Redis 消费者组名称 |
| `stream.redis.consumer_name` | `worker-1` | 组内消费者名称 |
| `stream.redis.block_ms` | `1000` | XREADGROUP 阻塞超时 |
| `stream.redis.batch_size` | `10` | 每次读取最大消息数 |
| `stream.redis.backpressure_max` | `100` | 暂停前最大待处理消息数 |

## 渲染设置

| 设置 | 默认值 | 说明 |
|------|--------|------|
| `render.canvas.width` | `1024` | 画布宽度（像素） |
| `render.canvas.height` | `1024` | 画布高度（像素） |
| `render.scene_on_event` | `false` | 每批场景事件后渲染 `front_page.png`（流式模式） |
| `render.video.fps` | `30` | 视频输出帧率 |
| `render.video.crf` | `18` | 恒定质量因子（越低质量越高） |
| `render.video.format` | `webm` | 视频格式：`webm`、`mp4` 或 `avi` |
| `render.video.subtitle` | `true` | 在视频中烧录字幕 |
| `render.video.subtitle_font_size` | `32` | 字幕字号（像素） |
| `render.video.preview` | `true` | 渲染后打开视频 |

## 命令行覆盖

```bash
uv run talk2scene model.whisper.model_size=medium stream.redis.host=myhost
```

## 环境变量

- `OPENAI_API_KEY`：LLM 场景生成必需
