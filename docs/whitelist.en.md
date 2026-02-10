# Whitelist & Layering Rules

## Whitelist

`conf/whitelist.yaml` is the single source of truth for valid component codes.

### Categories

- **STA** (Stance/Pose): Character body pose
- **EXP** (Expression): Facial expression overlay
- **ACT** (Action): Character action animation
- **BG** (Background): Scene background
- **CG** (CG illustration): Full-scene illustration that replaces the entire layered composition (like a CG scene in visual novels/games). When CG is not `CG_None`, BG/STA/ACT/EXP are all hidden.

### Valid Codes

| Category | Codes |
|----------|-------|
| STA | `STA_Stand_Front`, `STA_Stand_Side`, `STA_Stand_Lean` |
| EXP | `EXP_Neutral`, `EXP_Thinking`, `EXP_Astonished`, `EXP_Concerned`, `EXP_Laugh`, `EXP_Smile_EyesClosed`, `EXP_PretendClueless` |
| ACT | `ACT_None`, `ACT_ArmsCrossed`, `ACT_PalmOpen`, `ACT_GlassesPush`, `ACT_HandOnHip`, `ACT_HeadTilt`, `ACT_MouthCover`, `ACT_ObjectPresent`, `ACT_WaveGreeting`, `ACT_WaveFarewell` |
| BG | `BG_Lab_Modern`, `BG_Garden_Rooftop`, `BG_Cafe_Starbucks` |
| CG | `CG_None`, `CG_PandorasTech` |

### Validation

All scene events are validated against the whitelist. Invalid codes are auto-repaired to the default (first) code in each category.

## Layering Order

### Normal mode (`CG_None`)

```
Bottom → Top:
BG → STA → ACT → EXP
```

### CG mode (any CG other than `CG_None`)

The CG illustration replaces the entire scene. BG, STA, ACT, and EXP are all hidden.

This order is enforced in both the renderer and the frontend.
