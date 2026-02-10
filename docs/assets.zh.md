# :art: 素材与占位生成器

## :file_folder: 素材结构

```
assets/
├── bg/    # 背景图片（不透明）
├── sta/   # 姿态图片（透明）
├── act/   # 动作图片（透明）
├── exp/   # 表情图片（透明）
├── cg/    # CG插画（全场景，替换所有其他图层）
└── manifest.json
```

## :triangular_ruler: 画布大小

所有素材共享相同画布大小（默认：1024x1024），具有一致的对齐锚点。

## :hammer_and_wrench: 占位生成器

```bash
uv run talk2scene mode=generate-assets
```

:sparkles: 特点：

- :white_large_square: STA/EXP/ACT 生成透明 PNG
- :black_large_square: BG 和 CG 生成不透明 PNG
- :label: 带代码文本的可视调试标签
- :rainbow: 按类别着色
- :arrows_counterclockwise: 幂等操作（使用 `--force` 重新生成）
