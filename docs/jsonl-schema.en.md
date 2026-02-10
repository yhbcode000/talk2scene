# 📄 JSONL Schema

JSONL is the primary output format. Each line is a JSON object.

## 📑 Event Types

### 🎬 Scene Event
```json
{
    "type": "scene",
    "seq": 0,
    "speaker_id": "speaker_1",
    "text": "Hello, how are you?",
    "sta": "STA_Stand_Front",
    "exp": "EXP_Smile_EyesClosed",
    "act": "ACT_WaveGreeting",
    "bg": "BG_Lab_Modern",
    "cg": "CG_None",
    "start": 0.0,
    "end": 3.5
}
```

### 🔄 Transition Event
```json
{
    "type": "transition",
    "character_id": "speaker_1",
    "changes": {
        "exp": {"from": "EXP_Neutral", "to": "EXP_Smile_EyesClosed", "fade_ms": 200}
    },
    "state": {
        "character_id": "speaker_1",
        "sta": "STA_Stand_Front",
        "exp": "EXP_Smile_EyesClosed",
        "act": "ACT_WaveGreeting",
        "bg": "BG_Lab_Modern",
        "cg": "CG_None"
    }
}
```

### 🎙️ Transcript Event
```json
{
    "type": "transcript",
    "start": 0.0,
    "end": 3.5,
    "text": "Hello, how are you?",
    "speaker_id": "unknown"
}
```

## 🗃️ Derived Formats

- 📋 **timeline.json**: Snapshot of all events as a JSON array
- 📊 **timeline.csv**: CSV export of scene events only
