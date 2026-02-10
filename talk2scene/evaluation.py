"""Evaluation framework: render scenes, compare with expected PNGs, report results."""

import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image

from talk2scene.renderer import render_scene

logger = logging.getLogger(__name__)


def pixel_diff(img_a: Image.Image, img_b: Image.Image) -> tuple[float, Image.Image]:
    """Compute pixel-level difference between two images.

    Returns (diff_percentage, diff_image).
    """
    a = np.array(img_a.convert("RGB"), dtype=np.int16)
    b = np.array(img_b.convert("RGB"), dtype=np.int16)

    if a.shape != b.shape:
        # Resize b to match a
        img_b = img_b.resize(img_a.size, Image.LANCZOS)
        b = np.array(img_b.convert("RGB"), dtype=np.int16)

    diff = np.abs(a - b).astype(np.uint8)
    diff_pct = round(float(np.count_nonzero(diff > 0)) / float(diff.size) * 100.0, 4)
    diff_img = Image.fromarray(diff.astype(np.uint8))
    return diff_pct, diff_img


def perceptual_hash_diff(img_a: Image.Image, img_b: Image.Image) -> int:
    """Compute perceptual hash difference (Hamming distance)."""
    try:
        import imagehash
        hash_a = imagehash.phash(img_a)
        hash_b = imagehash.phash(img_b)
        return int(hash_a - hash_b)
    except ImportError:
        logger.warning("imagehash not installed, skipping perceptual hash comparison")
        return -1


def run_evaluation(
    cases_dir: str = "evaluation/cases",
    expected_dir: str = "evaluation/expected",
    output_dir: str = "evaluation/output",
    diffs_dir: str = "evaluation/diffs",
    asset_dirs: dict | None = None,
    canvas_size: tuple[int, int] = (1024, 1024),
    tolerance: float = 5.0,
) -> dict:
    """Run evaluation on all cases.

    Each case is a JSON file in cases_dir with scene state.
    Expected PNGs are in expected_dir with matching filenames (.png).
    """
    if asset_dirs is None:
        asset_dirs = {
            "sta": "assets/sta",
            "exp": "assets/exp",
            "act": "assets/act",
            "bg": "assets/bg",
            "cg": "assets/cg",
        }

    cases_path = Path(cases_dir)
    expected_path = Path(expected_dir)
    output_path = Path(output_dir)
    diffs_path = Path(diffs_dir)

    for p in [output_path, diffs_path]:
        p.mkdir(parents=True, exist_ok=True)

    results = {"cases": [], "summary": {"total": 0, "passed": 0, "failed": 0}}

    if not cases_path.exists():
        logger.warning(f"No cases directory: {cases_dir}")
        return results

    case_files = sorted(cases_path.glob("*.json"))
    if not case_files:
        logger.warning(f"No case files found in {cases_dir}")
        return results

    for case_file in case_files:
        case_name = case_file.stem
        results["summary"]["total"] += 1

        with open(case_file) as f:
            scene_state = json.load(f)

        # Render
        rendered = render_scene(scene_state, asset_dirs, canvas_size)
        rendered_rgb = rendered.convert("RGB")
        rendered_path = output_path / f"{case_name}.png"
        rendered_rgb.save(str(rendered_path))

        # Compare with expected
        expected_file = expected_path / f"{case_name}.png"
        case_result = {
            "name": case_name,
            "rendered": str(rendered_path),
        }

        if expected_file.exists():
            expected_img = Image.open(str(expected_file))
            diff_pct, diff_img = pixel_diff(rendered_rgb, expected_img)
            phash_diff = perceptual_hash_diff(rendered_rgb, expected_img)

            case_result["expected"] = str(expected_file)
            case_result["pixel_diff_pct"] = round(diff_pct, 2)
            case_result["phash_diff"] = phash_diff
            case_result["passed"] = diff_pct <= tolerance

            if not case_result["passed"]:
                diff_path = diffs_path / f"{case_name}_diff.png"
                diff_img.save(str(diff_path))
                case_result["diff_image"] = str(diff_path)
                results["summary"]["failed"] += 1
            else:
                results["summary"]["passed"] += 1
        else:
            # No expected image: generate it as golden
            expected_path.mkdir(parents=True, exist_ok=True)
            golden_path = expected_path / f"{case_name}.png"
            rendered_rgb.save(str(golden_path))
            case_result["note"] = "No expected image found; generated golden image"
            case_result["passed"] = True
            results["summary"]["passed"] += 1

        results["cases"].append(case_result)

    # Write report
    report_path = output_path / "eval_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    # Text summary
    summary_path = output_path / "eval_summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Evaluation Summary\n{'='*40}\n")
        f.write(f"Total cases: {results['summary']['total']}\n")
        f.write(f"Passed: {results['summary']['passed']}\n")
        f.write(f"Failed: {results['summary']['failed']}\n\n")
        for case in results["cases"]:
            status = "PASS" if case["passed"] else "FAIL"
            f.write(f"[{status}] {case['name']}")
            if "pixel_diff_pct" in case:
                f.write(f" (pixel diff: {case['pixel_diff_pct']}%)")
            if "note" in case:
                f.write(f" ({case['note']})")
            f.write("\n")

    logger.info(
        f"Evaluation complete: {results['summary']['passed']}/{results['summary']['total']} passed"
    )
    return results
