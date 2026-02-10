"""Placeholder asset generation utility using Pillow."""

import json
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

DEFAULT_CANVAS = (1024, 1024)

# Color schemes per category
CATEGORY_COLORS = {
    "STA": (100, 150, 255, 180),   # Blue, semi-transparent (character body)
    "EXP": (255, 180, 100, 180),   # Orange, semi-transparent (face overlay)
    "ACT": (100, 255, 150, 180),   # Green, semi-transparent (arm/action overlay)
    "BG":  (80, 80, 120, 255),     # Dark blue-gray, opaque (full background)
    "CG":  (140, 60, 160, 255),    # Purple, opaque (full-scene illustration)
}

# Full-canvas categories: these fill the whole canvas as opaque images
FULL_CANVAS_CATEGORIES = {"BG", "CG"}


def _get_font(size: int = 28):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", size)
        except OSError:
            return ImageFont.load_default()


def generate_placeholder(
    code: str,
    category: str,
    output_path: Path,
    canvas_size: tuple[int, int] = DEFAULT_CANVAS,
    force: bool = False,
) -> Path:
    if output_path.exists() and not force:
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    color = CATEGORY_COLORS.get(category, (128, 128, 128, 180))
    is_full_canvas = category in FULL_CANVAS_CATEGORIES

    if is_full_canvas:
        img = Image.new("RGB", canvas_size, color[:3])
        draw = ImageDraw.Draw(img)
    else:
        img = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

    w, h = canvas_size

    if category == "BG":
        # Full canvas background with gradient-like pattern
        for y in range(0, h, 64):
            shade = int(color[0] * (1 - y / h * 0.3))
            draw.rectangle([0, y, w, y + 64], fill=(shade, shade, shade + 40))
    elif category == "CG":
        # Full-scene illustration: fills entire canvas with a distinct look
        # Diagonal gradient to distinguish from BG
        for y in range(0, h, 32):
            r = int(color[0] + (y / h) * 60)
            g = int(color[1] + (y / h) * 40)
            b = int(color[2] + (y / h) * 80)
            draw.rectangle([0, y, w, y + 32], fill=(min(r, 255), min(g, 255), min(b, 255)))
        # Draw a decorative frame border to indicate it's an illustration
        border = 20
        draw.rectangle(
            [border, border, w - border, h - border],
            outline=(255, 220, 180), width=4,
        )
        # Inner vignette corners
        corner = 60
        for cx, cy in [(border, border), (w - border, border),
                       (border, h - border), (w - border, h - border)]:
            draw.ellipse([cx - corner//2, cy - corner//2, cx + corner//2, cy + corner//2],
                         fill=(180, 120, 200))
    elif category in ("STA", "ACT", "EXP"):
        # Character layers: anchored at bottom-right
        # Body occupies the right portion of the canvas
        body_w = w // 3
        body_h = h * 2 // 3
        margin_r = w // 10          # right margin
        body_cx = w - margin_r - body_w // 2   # body center-x
        body_x0 = body_cx - body_w // 2
        body_y0 = h - body_h

        if category == "STA":
            # Half-body shape at bottom-right
            draw.rounded_rectangle([body_x0, body_y0, body_x0 + body_w, h], radius=20, fill=color)
            # Head circle
            head_r = body_w // 3
            head_cy = body_y0 - head_r + 10
            draw.ellipse([body_cx - head_r, head_cy - head_r, body_cx + head_r, head_cy + head_r], fill=color)
        elif category == "ACT":
            # Arms on sides of the body
            arm_w = body_w // 2
            arm_h = h // 3
            y_mid = body_y0 + body_h // 3
            # Left arm
            draw.rounded_rectangle(
                [body_x0 - arm_w, y_mid - arm_h // 2, body_x0, y_mid + arm_h // 2],
                radius=12, fill=color,
            )
            # Right arm
            draw.rounded_rectangle(
                [body_x0 + body_w, y_mid - arm_h // 2, body_x0 + body_w + arm_w, y_mid + arm_h // 2],
                radius=12, fill=color,
            )
        elif category == "EXP":
            # Face overlay on the head
            face_r = w // 8
            head_r = body_w // 3
            head_cy = body_y0 - head_r + 10
            draw.ellipse([body_cx - face_r, head_cy - face_r, body_cx + face_r, head_cy + face_r], fill=color)

    # Debug labels
    font_large = _get_font(32)
    font_small = _get_font(20)
    label_color = (255, 255, 255) if is_full_canvas else (255, 255, 255, 255)

    if is_full_canvas:
        # BG/CG: labels at top-center
        label_x_fn = lambda tw: (w - tw) // 2
        label_y = 20
    else:
        # STA/ACT/EXP: labels near the character (bottom-right area)
        margin_r = w // 10
        body_w_lbl = w // 3
        body_cx_lbl = w - margin_r - body_w_lbl // 2
        label_x_fn = lambda tw: body_cx_lbl - tw // 2
        label_y = 20

    # Category label
    bbox = draw.textbbox((0, 0), category, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text((label_x_fn(tw), label_y), category, fill=label_color, font=font_large)

    # Code label
    bbox = draw.textbbox((0, 0), code, font=font_small)
    tw = bbox[2] - bbox[0]
    draw.text((label_x_fn(tw), label_y + 40), code, fill=label_color, font=font_small)

    img.save(str(output_path))
    logger.info(f"Generated placeholder: {output_path}")
    return output_path


def generate_all_placeholders(
    whitelist_path: str = "conf/whitelist.yaml",
    asset_base: str = "assets",
    canvas_size: tuple[int, int] = DEFAULT_CANVAS,
    force: bool = False,
) -> dict:
    import yaml

    with open(whitelist_path) as f:
        whitelist = yaml.safe_load(f)

    manifest = {"canvas_size": list(canvas_size), "anchors": {}, "assets": {}}
    base = Path(asset_base)

    for category, codes in whitelist.items():
        cat_lower = category.lower()
        cat_dir = base / cat_lower
        cat_dir.mkdir(parents=True, exist_ok=True)

        if category in FULL_CANVAS_CATEGORIES:
            anchor = "top-left"
        else:
            anchor = "bottom-right"
        manifest["anchors"][category] = anchor
        manifest["assets"][category] = {}

        for code in codes:
            filename = f"{code}.png"
            out_path = cat_dir / filename
            generate_placeholder(code, category, out_path, canvas_size, force)
            manifest["assets"][category][code] = {
                "path": str(out_path),
                "size": list(canvas_size),
                "anchor": anchor,
            }

    # Write manifest
    manifest_path = base / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Asset manifest written: {manifest_path}")

    return manifest
