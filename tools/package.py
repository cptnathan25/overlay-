#!/usr/bin/env python3
"""Create the small, self-contained OBS delivery ZIP after building the PNGs."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pacote_void_azul_stream.zip"
FILES = (
    "overlay_sylvanas_void_4k.png",
    "webcam_void_azul.png",
    "obs_overlay.html",
    "README.md",
)

with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(f"Required delivery file is missing: {path}")
        archive.write(path, arcname=f"Void_Azul_Stream/{name}")

print(f"Created {OUTPUT.name} with {len(FILES)} ready-to-use files.")
