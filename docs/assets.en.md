# Assets & Placeholder Generator

## Asset Structure

```
assets/
├── bg/    # Background images (opaque)
├── sta/   # Pose/stance images (transparent)
├── act/   # Action images (transparent)
├── exp/   # Expression images (transparent)
├── cg/    # CG illustrations (full-scene, replaces all other layers)
└── manifest.json
```

## Canvas Size

All assets share the same canvas size (default: 1024x1024) with consistent alignment anchors.

## Placeholder Generator

Generate debug placeholder assets:

```bash
uv run talk2scene mode=generate-assets
```

Features:
- Transparent PNGs for STA/EXP/ACT
- Opaque PNGs for BG and CG
- Visual debug labels with code text
- Color-coded by category
- Idempotent (use `--force` to regenerate)
- Writes asset manifest

## Manifest

`assets/manifest.json` contains paths, sizes, and anchor info for all generated assets.
