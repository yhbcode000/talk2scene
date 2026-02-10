"""Scene rendering engine: compose layers into a single PNG deterministically.

Layer order for normal scenes: BG -> STA -> ACT -> EXP
When CG is active: CG replaces the entire scene (full-screen illustration).
"""

import json
import logging
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)


def load_asset(path: str) -> Image.Image:
    img = Image.open(path)
    return img.copy()


def render_scene(
    scene_state: dict,
    asset_dirs: dict,
    canvas_size: tuple[int, int] = (1024, 1024),
) -> Image.Image:
    """Render a scene state dict into a composed PNG.

    If CG is set (not CG_None), the CG illustration replaces the entire
    layered composition — just like a CG scene in a visual novel.
    Otherwise, normal layering: BG -> STA -> ACT -> EXP.
    """
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

    cg_code = scene_state.get("cg")
    if cg_code and cg_code != "CG_None":
        # CG mode: full-scene illustration replaces everything
        cat_dir = Path(asset_dirs.get("cg", "assets/cg"))
        asset_path = cat_dir / f"{cg_code}.png"
        if asset_path.exists():
            cg_img = load_asset(str(asset_path))
            if cg_img.size != canvas_size:
                cg_img = cg_img.resize(canvas_size, Image.LANCZOS)
            if cg_img.mode != "RGBA":
                cg_img = cg_img.convert("RGBA")
            return cg_img
        else:
            logger.warning(f"CG asset not found: {asset_path}, falling back to normal layers")

    # Normal layering: BG -> STA -> ACT -> EXP
    normal_layers = ["bg", "sta", "act", "exp"]

    for layer in normal_layers:
        code = scene_state.get(layer)
        if not code or code.endswith("_None"):
            continue

        cat_dir = Path(asset_dirs.get(layer, f"assets/{layer}"))
        asset_path = cat_dir / f"{code}.png"

        if not asset_path.exists():
            logger.warning(f"Asset not found: {asset_path}")
            continue

        layer_img = load_asset(str(asset_path))

        # Resize to canvas if needed
        if layer_img.size != canvas_size:
            layer_img = layer_img.resize(canvas_size, Image.LANCZOS)

        # Ensure RGBA
        if layer_img.mode != "RGBA":
            layer_img = layer_img.convert("RGBA")

        # Composite
        canvas = Image.alpha_composite(canvas, layer_img)

    return canvas


def render_scene_to_file(
    scene_state: dict,
    output_path: str,
    asset_dirs: dict,
    canvas_size: tuple[int, int] = (1024, 1024),
) -> str:
    img = render_scene(scene_state, asset_dirs, canvas_size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Convert to RGB for PNG output (flatten alpha onto white)
    bg = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    final = Image.alpha_composite(bg, img)
    final.convert("RGB").save(output_path)
    logger.info(f"Rendered scene to: {output_path}")
    return output_path
