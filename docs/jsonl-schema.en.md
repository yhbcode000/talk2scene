# :page_facing_up: JSONL Schema

JSONL is the primary output format. Each line is a JSON object.

## :bookmark_tabs: Event Types

### :clapper: Scene Event
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

### :arrows_counterclockwise: Transition Event
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

### :studio_microphone: Transcript Event
```json
{
    "type": "transcript",
    "start": 0.0,
    "end": 3.5,
    "text": "Hello, how are you?",
    "speaker_id": "unknown"
}
```

## :card_file_box: Derived Formats

- :clipboard: **timeline.json**: Snapshot of all events as a JSON array
- :bar_chart: **timeline.csv**: CSV export of scene events only
