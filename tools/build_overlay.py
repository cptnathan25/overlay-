#!/usr/bin/env python3
"""Build the 4K transparent Void Azul stream overlay and matching webcam module.

The source painting lives in assets/; this script removes its original, oversized
camera surround, reuses that same hand-painted ornament at a more stream-friendly
size, and makes both gameplay and webcam openings genuinely transparent.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "void_frame_source.png"
OUTPUT = ROOT / "overlay_sylvanas_void_4k.png"
WEBCAM_OUTPUT = ROOT / "webcam_void_azul.png"
EXPORT_SIZE = (3840, 2160)
SOURCE_SIZE = (1672, 941)


def smoothstep(values: np.ndarray, start: float, end: float) -> np.ndarray:
    t = np.clip((values - start) / (end - start), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def rounded_rectangle_coverage(
    x: np.ndarray,
    y: np.ndarray,
    left: float,
    top: float,
    right: float,
    bottom: float,
    radius: float,
    softness: float = 2.0,
) -> np.ndarray:
    """Antialiased coverage of a rounded rectangle in source-image coordinates."""
    cx = (left + right) / 2.0
    cy = (top + bottom) / 2.0
    qx = np.abs(x - cx) - ((right - left) / 2.0 - radius)
    qy = np.abs(y - cy) - ((bottom - top) / 2.0 - radius)
    signed_distance = (
        np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0))
        + np.minimum(np.maximum(qx, qy), 0.0)
        - radius
    )
    return 1.0 - smoothstep(signed_distance, -softness, softness)


def recolor_warm_eye_glints(rgb: np.ndarray, x: np.ndarray, y: np.ndarray) -> None:
    """Keep even Sylvanas's tiny eye reflections in the cold Void palette."""
    red = rgb[:, :, 0].astype(np.float32)
    green = rgb[:, :, 1].astype(np.float32)
    blue = rgb[:, :, 2].astype(np.float32)
    warm_eye_glints = (
        (x > 155.0)
        & (x < 310.0)
        & (y > 185.0)
        & (y < 294.0)
        & (red > 35.0)
        & (red > green * 1.25)
        & (red > blue * 1.12)
    )
    rgb[:, :, 0][warm_eye_glints] = np.clip(red[warm_eye_glints] * 0.28, 0, 255)
    rgb[:, :, 1][warm_eye_glints] = np.clip(red[warm_eye_glints] * 0.73, 0, 255)
    rgb[:, :, 2][warm_eye_glints] = np.clip(red[warm_eye_glints] * 1.03, 0, 255)


def main() -> None:
    painting = Image.open(SOURCE).convert("RGB")
    if painting.size != SOURCE_SIZE:
        raise ValueError(f"Expected the {SOURCE_SIZE} source painting; got {painting.size}")
    width, height = painting.size
    y, x = np.mgrid[:height, :width].astype(np.float32)
    rgb = np.asarray(painting, dtype=np.uint8).copy()
    recolor_warm_eye_glints(rgb, x, y)

    # A tailored alpha silhouette instead of a full-screen, opaque wallpaper.
    # The fine frame remains on the perimeter; hair and dimensional energy
    # feather out into transparent gameplay at the edge of Sylvanas's portrait.
    portrait = 1.0 - smoothstep(x, 306.0, 488.0)
    top_edge = 1.0 - smoothstep(y, 27.0, 69.0)
    bottom_edge = smoothstep(y, height - 78.0, height - 25.0)
    right_edge = smoothstep(x, width - 76.0, width - 26.0)
    top_left_void = (
        (1.0 - smoothstep(x, 235.0, 490.0))
        * (1.0 - smoothstep(y, 48.0, 210.0))
    )
    top_right_void = (
        smoothstep(x, 1360.0, 1515.0)
        * (1.0 - smoothstep(y, 77.0, 222.0))
    )
    bottom_left_void = (
        (1.0 - smoothstep(x, 235.0, 550.0))
        * smoothstep(y, 709.0, 901.0)
    )
    bottom_right_void = (
        smoothstep(x, 1445.0, 1590.0)
        * smoothstep(y, 743.0, 893.0)
    )
    matte = np.maximum.reduce(
        [
            portrait,
            top_edge,
            bottom_edge,
            right_edge,
            top_left_void,
            top_right_void,
            bottom_left_void,
            bottom_right_void,
        ]
    )

    # Lift the painted camera surround off the source canvas, rather than
    # leaving an oversized old frame underneath the new compact one.
    old_camera_footprint = rounded_rectangle_coverage(
        x, y, 1129.0, 573.0, 1644.0, 905.0, radius=10.0, softness=5.0
    )
    matte *= 1.0 - old_camera_footprint
    base = Image.fromarray(
        np.dstack((rgb, np.uint8(np.rint(matte * 255)))), "RGBA"
    )

    # The webcam uses the exact same carved dark metal and blue jewels as the
    # outer frame. Its viewport is resized to ~21% of a 16:9 canvas, rather
    # than swallowing the lower right quadrant of the gameplay.
    camera_outer = rounded_rectangle_coverage(
        x, y, 1140.0, 585.0, 1637.0, 890.0, radius=12.0, softness=5.0
    )
    camera_inner = rounded_rectangle_coverage(
        x, y, 1167.0, 612.0, 1617.0, 869.0, radius=20.0, softness=1.5
    )
    camera_ring = camera_outer * (1.0 - camera_inner)
    painted_camera = Image.fromarray(
        np.dstack((rgb, np.uint8(np.rint(camera_ring * 255)))), "RGBA"
    )
    crop_box = (1130, 580, 1640, 895)
    painted_camera = painted_camera.crop(crop_box)
    camera_scale = 0.78
    camera_size = tuple(round(size * camera_scale) for size in painted_camera.size)
    painted_camera = painted_camera.resize(camera_size, Image.Resampling.LANCZOS)
    camera_x = width - 42 - camera_size[0]
    camera_y = height - 53 - camera_size[1]

    # A restrained cobalt halo grounds the camera module over busy gameplay.
    # The aperture is cut again below, so the camera stays 100% transparent.
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(
        (camera_x + 10, camera_y + 8, camera_x + camera_size[0] - 10,
         camera_y + camera_size[1] - 10),
        radius=14,
        outline=(0, 105, 235, 170),
        width=5,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=11))
    base = Image.alpha_composite(base, glow)
    base.alpha_composite(painted_camera, (camera_x, camera_y))

    inner_left = camera_x + (1167 - crop_box[0]) * camera_scale
    inner_top = camera_y + (612 - crop_box[1]) * camera_scale
    inner_right = camera_x + (1617 - crop_box[0]) * camera_scale
    inner_bottom = camera_y + (869 - crop_box[1]) * camera_scale
    aperture = rounded_rectangle_coverage(
        x, y, inner_left, inner_top, inner_right, inner_bottom,
        radius=20 * camera_scale, softness=1.2,
    )
    finished = np.asarray(base).copy()
    finished[:, :, 3] = np.uint8(
        np.rint(finished[:, :, 3].astype(np.float32) * (1.0 - aperture))
    )
    overlay = Image.fromarray(finished, "RGBA").resize(
        EXPORT_SIZE, Image.Resampling.LANCZOS
    )
    overlay.save(OUTPUT, optimize=True)

    # Optional movable, independent webcam source. Use this OR the integrated
    # webcam in the full overlay, not both simultaneously.
    independent_camera = painted_camera.resize((1200, 750), Image.Resampling.LANCZOS)
    independent_camera.save(WEBCAM_OUTPUT, optimize=True)

    sx, sy = EXPORT_SIZE[0] / width, EXPORT_SIZE[1] / height
    print(f"Exported {OUTPUT.name}: {overlay.width} × {overlay.height}, RGBA")
    print(f"Exported {WEBCAM_OUTPUT.name}: 1200 × 750, RGBA")
    print(
        "Webcam opening at 4K (approx.): "
        f"x={inner_left * sx:.0f}, y={inner_top * sy:.0f}, "
        f"w={(inner_right - inner_left) * sx:.0f}, "
        f"h={(inner_bottom - inner_top) * sy:.0f}"
    )


if __name__ == "__main__":
    main()
