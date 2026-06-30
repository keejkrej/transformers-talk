#!/usr/bin/env python3
"""
Build a standalone .excalidraw file from the live scene + locally-generated
LaTeX formula SVGs.

The Excalidraw MCP API cannot create embeddable or image elements, so this
script bypasses it entirely:
  1. Reads the scene JSON (exported from get_scene_content).
  2. Removes the old plain-text formula elements and orphan embeddables
     left from failed MCP attempts.
  3. Reads each SVG from assets/formulas/, encodes it as a base64 data URL,
     and registers it in the Excalidraw `files` map.
  4. Creates `image` elements (with fileId references) at the planned
     coordinates inside each slide frame.
  5. Writes transformers-talk.excalidraw — a fully self-contained file that
     renders in any Excalidraw instance (web app, local viewer, or import).

Usage:
  python3 gen_excalidraw_file.py [scene_artifact_path]

If no artifact path is given, uses the most recent get_scene_content artifact.
"""

import base64
import glob
import json
import os
import re
import sys
import time

REPO = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(REPO, "assets", "formulas")
PLAN_PATH = "/tmp/svg_plan.json"
OUTPUT_PATH = os.path.join(REPO, "transformers-talk.excalidraw")
ARTIFACTS_DIR = os.path.expanduser(
    "~/.factory/artifacts/tool-outputs"
)


def find_scene_artifact():
    """Find the most recent get_scene_content artifact."""
    pattern = os.path.join(ARTIFACTS_DIR, "mcp_excalidraw_get_scene_content-call_*.log")
    artifacts = sorted(glob.glob(pattern))
    if not artifacts:
        sys.exit("ERROR: No get_scene_content artifact found. Run the MCP tool first.")
    return artifacts[-1]


def load_scene(artifact_path):
    """Load scene JSON from an artifact file."""
    with open(artifact_path, "r") as f:
        return json.load(f)


def load_plan():
    """Load the SVG placement plan."""
    with open(PLAN_PATH, "r") as f:
        return json.load(f)


def extract_svg_filename(link_url):
    """Extract the SVG filename from a jsdelivr URL."""
    # URL format: https://cdn.jsdelivr.net/gh/keejkrej/transformers-talk@main/assets/formulas/s01_attention_core.svg
    return link_url.rsplit("/", 1)[-1]


def svg_to_data_url(svg_path):
    """Read an SVG file and convert to a base64 data URL."""
    with open(svg_path, "rb") as f:
        svg_bytes = f.read()
    encoded = base64.b64encode(svg_bytes).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def generate_id():
    """Generate a random-looking Excalidraw-style ID."""
    import random
    import string
    chars = string.ascii_letters + string.digits + "-_"
    return "".join(random.choices(chars, k=20))


def generate_seed():
    """Generate a random seed for Excalidraw elements."""
    import random
    return random.randint(100000000, 2147483647)


def main():
    # --- Load inputs ---
    artifact_path = sys.argv[1] if len(sys.argv) > 1 else find_scene_artifact()
    print(f"Loading scene from: {artifact_path}")
    scene = load_scene(artifact_path)

    plan = load_plan()
    print(f"Loaded plan: {len(plan)} slides, "
          f"{sum(len(v.get('add', [])) for v in plan.values())} SVGs to place")

    # --- Collect IDs to remove ---
    ids_to_delete = set()
    for slide_data in plan.values():
        for elem_id in slide_data.get("delete", []):
            ids_to_delete.add(elem_id)

    # Also remove orphan embeddables left from failed MCP attempts
    # (elements with type "embeddable" that were created experimentally)
    orphan_embeddable_ids = set()
    for elem in scene.get("elements", []):
        if elem.get("type") == "embeddable":
            orphan_embeddable_ids.add(elem["id"])
            ids_to_delete.add(elem["id"])

    if orphan_embeddable_ids:
        print(f"Removing {len(orphan_embeddable_ids)} orphan embeddable elements "
              f"(leftovers from failed MCP attempts)")

    print(f"Total elements to remove: {len(ids_to_delete)}")

    # --- Filter out deleted elements ---
    scene["elements"] = [
        elem for elem in scene.get("elements", [])
        if elem.get("id") not in ids_to_delete
    ]

    # --- Build files map and image elements ---
    files_map = scene.get("files", {})
    if not isinstance(files_map, dict):
        files_map = {}

    now_ms = int(time.time() * 1000)
    new_elements = []
    svgs_added = 0
    svgs_missing = 0

    for slide_key in sorted(plan.keys(), key=lambda k: int(k)):
        slide_data = plan[slide_key]
        for add_spec in slide_data.get("add", []):
            link_url = add_spec.get("link", "")
            svg_filename = extract_svg_filename(link_url)
            svg_path = os.path.join(SVG_DIR, svg_filename)

            if not os.path.exists(svg_path):
                print(f"  WARNING: SVG not found: {svg_filename}")
                svgs_missing += 1
                continue

            # Create file entry
            file_id = generate_id()
            data_url = svg_to_data_url(svg_path)
            files_map[file_id] = {
                "id": file_id,
                "mimeType": "image/svg+xml",
                "dataURL": data_url,
                "created": now_ms,
                "lastRetrieved": now_ms,
            }

            # Create image element
            image_elem = {
                "type": "image",
                "id": generate_id(),
                "x": add_spec["x"],
                "y": add_spec["y"],
                "width": add_spec["width"],
                "height": add_spec["height"],
                "angle": 0,
                "strokeColor": "transparent",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": add_spec.get("roughness", 0),
                "opacity": 100,
                "groupIds": [],
                "frameId": add_spec.get("frameId"),
                "roundness": add_spec.get("roundness"),
                "seed": generate_seed(),
                "version": 1,
                "versionNonce": generate_seed(),
                "isDeleted": False,
                "boundElements": None,
                "updated": now_ms,
                "link": None,
                "locked": False,
                "fileId": file_id,
                "scale": [1, 1],
            }
            new_elements.append(image_elem)
            svgs_added += 1

    print(f"Added {svgs_added} SVG image elements "
          f"({svgs_missing} missing files skipped)")

    # --- Merge new elements into scene ---
    scene["elements"].extend(new_elements)
    scene["files"] = files_map

    # Ensure required top-level fields
    scene.setdefault("type", "excalidraw")
    scene.setdefault("version", 2)
    scene.setdefault("source", "https://app.excalidraw.com")
    scene.setdefault("appState", {})
    scene["appState"].setdefault("viewBackgroundColor", "#ffffff")

    # --- Write output ---
    with open(OUTPUT_PATH, "w") as f:
        json.dump(scene, f, separators=(",", ":"))

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"\nWrote: {OUTPUT_PATH}")
    print(f"Size: {file_size / 1024:.0f} KB "
          f"({file_size / 1024 / 1024:.1f} MB)")
    print(f"Elements: {len(scene['elements'])}")
    print(f"Files (SVGs): {len(files_map)}")


if __name__ == "__main__":
    main()
