"""
Image Cache Engine — Pre-generate + Cache + Offline Serve
============================================================
1. Pre-generates images for top combinations and saves locally
2. Caches any image generated during use
3. Serves cached images instantly (no internet needed)
4. Only generates new images for completely new combinations

Cache location: data/cached_drawings/{combo_id}.png
"""
import os
import json
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "data" / "cached_drawings"
CACHE_INDEX = CACHE_DIR / "_cache_index.json"


def _ensure_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _load_index():
    """Load cache index — maps combo_id to file path + metadata."""
    if CACHE_INDEX.exists():
        try:
            return json.loads(CACHE_INDEX.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_index(index):
    """Save cache index."""
    _ensure_dir()
    CACHE_INDEX.write_text(json.dumps(index, indent=2, default=str), encoding="utf-8")


def get_combo_id(process_id, capacity_tpd, state, drawing_type):
    """Generate unique combo ID for caching."""
    state_short = state[:3].upper() if state else "MH"
    return f"P{process_id}_C{int(capacity_tpd)}_{state_short}_{drawing_type}"


def get_cached_image(combo_id):
    """Get cached image path if it exists. Returns path or None."""
    index = _load_index()
    entry = index.get(combo_id)
    if entry:
        path = entry.get("path", "")
        if os.path.exists(path):
            return path
    # Also check by filename directly
    fpath = CACHE_DIR / f"{combo_id}.png"
    if fpath.exists():
        return str(fpath)
    return None


def save_to_cache(combo_id, image_path, metadata=None):
    """Save a generated image to cache."""
    _ensure_dir()
    index = _load_index()

    # Copy or move image to cache dir
    cache_path = str(CACHE_DIR / f"{combo_id}.png")
    if image_path != cache_path:
        try:
            import shutil
            shutil.copy2(image_path, cache_path)
        except Exception:
            cache_path = image_path

    index[combo_id] = {
        "path": cache_path,
        "created": time.strftime("%Y-%m-%d %H:%M"),
        "metadata": metadata or {},
    }
    _save_index(index)
    return cache_path


def get_or_generate(combo_id, prompt, drawing_type_label=""):
    """Get from cache or generate new image. Returns path or None."""
    # Check cache first
    cached = get_cached_image(combo_id)
    if cached:
        return cached, "cache"

    # Generate new image
    try:
        from engines.ai_image_generator import generate_with_pollinations
        filename = f"{combo_id}.png"
        path = generate_with_pollinations(prompt, filename)
        if path:
            # Save to cache
            cache_path = save_to_cache(combo_id, path, {"type": drawing_type_label})
            return cache_path, "generated"
    except Exception:
        pass

    return None, "failed"


def get_cache_stats():
    """Get cache statistics."""
    _ensure_dir()
    index = _load_index()
    total_files = len(list(CACHE_DIR.glob("*.png")))
    total_indexed = len(index)
    total_size_mb = sum(os.path.getsize(str(CACHE_DIR / f)) for f in CACHE_DIR.glob("*.png")) / (1024 * 1024)

    return {
        "total_cached": total_files,
        "indexed": total_indexed,
        "size_mb": round(total_size_mb, 1),
        "cache_dir": str(CACHE_DIR),
    }


def get_cached_for_config(process_id, capacity_tpd, state):
    """Get all cached images for a specific configuration."""
    from engines.combination_engine import DRAWING_TYPES
    results = {}
    for dt in DRAWING_TYPES:
        combo_id = get_combo_id(process_id, capacity_tpd, state, dt)
        path = get_cached_image(combo_id)
        results[dt] = {
            "combo_id": combo_id,
            "cached": path is not None,
            "path": path,
        }
    return results


# ══════════════════════════════════════════════════════════════════════
# BATCH PRE-GENERATOR — Generate top combinations
# ══════════════════════════════════════════════════════════════════════
TOP_COMBINATIONS = [
    # Most common client configurations
    (1, 5, "Gujarat"), (1, 10, "Gujarat"), (1, 20, "Gujarat"), (1, 25, "Gujarat"), (1, 50, "Gujarat"),
    (1, 5, "Maharashtra"), (1, 10, "Maharashtra"), (1, 20, "Maharashtra"), (1, 25, "Maharashtra"),
    (1, 20, "Punjab"), (1, 25, "Punjab"), (1, 20, "Uttar Pradesh"), (1, 25, "Uttar Pradesh"),
    (1, 20, "Madhya Pradesh"), (1, 25, "Rajasthan"), (1, 20, "Tamil Nadu"),
    (2, 10, "Gujarat"), (2, 20, "Gujarat"), (2, 20, "Maharashtra"),
    (3, 20, "Gujarat"), (3, 25, "Gujarat"), (3, 20, "Maharashtra"),
]

# Priority drawing types (generate these first)
PRIORITY_DRAWINGS = ["site_layout", "3d_isometric", "process_flow"]


def pre_generate_batch(progress_callback=None, max_images=None):
    """Pre-generate images for top combinations.

    Args:
        progress_callback: function(current, total, combo_id) for progress
        max_images: limit number of images to generate (None = all)

    Returns:
        dict with generated/cached/failed counts
    """
    from engines.combination_engine import generate_combination_prompt, DRAWING_TYPES

    tasks = []
    for pid, tpd, state in TOP_COMBINATIONS:
        for dt in PRIORITY_DRAWINGS:
            combo_id = get_combo_id(pid, tpd, state, dt)
            if not get_cached_image(combo_id):
                tasks.append((pid, tpd, state, dt, combo_id))

    if max_images:
        tasks = tasks[:max_images]

    results = {"generated": 0, "cached": 0, "failed": 0, "total": len(tasks)}

    for i, (pid, tpd, state, dt, combo_id) in enumerate(tasks):
        if progress_callback:
            progress_callback(i + 1, len(tasks), combo_id)

        cfg = dict(
            capacity_tpd=tpd, process_id=pid, state=state,
            bio_oil_yield_pct=32, bio_char_yield_pct=28,
            syngas_yield_pct=22, process_loss_pct=18, bio_blend_pct=20,
            plot_length_m=max(60, tpd * 4), plot_width_m=max(40, tpd * 3),
        )

        result = generate_combination_prompt(cfg, dt)
        path, source = get_or_generate(combo_id, result["prompt"], result.get("drawing_label", dt))

        if source == "cache":
            results["cached"] += 1
        elif source == "generated":
            results["generated"] += 1
        else:
            results["failed"] += 1

    return results


def clear_cache():
    """Clear all cached images."""
    _ensure_dir()
    count = 0
    for f in CACHE_DIR.glob("*.png"):
        f.unlink()
        count += 1
    _save_index({})
    return count
