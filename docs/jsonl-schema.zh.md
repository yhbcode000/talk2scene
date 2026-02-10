# 📄 JSONL 格式规范

JSONL 是主要输出格式。每行是一个 JSON 对象。

## 📑 事件类型

### 🎬 场景事件
```json
{
    "type": "scene",
    "seq": 0,
    "speaker_id": "speaker_1",
    "text": "你好，你怎么样？",
    "sta": "STA_Stand_Front",
    "exp": "EXP_Smile_EyesClosed",
    "act": "ACT_WaveGreeting",
    "bg": "BG_Lab_Modern",
    "cg": "CG_None",
    "start": 0.0,
    "end": 3.5
}
```

### 🔄 过渡事件
```json
{
    "type": "transition",
    "character_id": "speaker_1",
    "changes": {
        "exp": {"from": "EXP_Neutral", "to": "EXP_Smile_EyesClosed", "fade_ms": 200}
    }
}
```

## 🗃️ 派生格式

- 📋 **timeline.json**: 所有事件的 JSON 快照
- 📊 **timeline.csv**: 仅场景事件的 CSV 导出
