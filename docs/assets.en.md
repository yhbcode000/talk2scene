# :art: Assets & Placeholder Generator

## :file_folder: Asset Structure

```
assets/
├── bg/    # Background images (opaque)
├── sta/   # Pose/stance images (transparent)
├── act/   # Action images (transparent)
├── exp/   # Expression images (transparent)
├── cg/    # CG illustrations (full-scene, replaces all other layers)
└── manifest.json
```

## :triangular_ruler: Canvas Size

All assets share the same canvas size (default: 1024x1024) with consistent alignment anchors.

## :hammer_and_wrench: Placeholder Generator

Generate debug placeholder assets:

```bash
uv run talk2scene mode=generate-assets
```

:sparkles: Features:

- :white_large_square: Transparent PNGs for STA/EXP/ACT
- :black_large_square: Opaque PNGs for BG and CG
- :label: Visual debug labels with code text
- :rainbow: Color-coded by category
- :arrows_counterclockwise: Idempotent (use `--force` to regenerate)
- :page_facing_up: Writes asset manifest

## :card_index: Manifest

`assets/manifest.json` contains paths, sizes, and anchor info for all generated assets.
