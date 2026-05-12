#!/usr/bin/env -S uv run --with pillow --script
"""
Render and print a multi-line label to a Niimbot K3 over USB.

Usage:
    ./print_label.py "first line" "second line" "third line"
    ./print_label.py --no-print "first line"   # render only, opens preview
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PRINTER_ADDR = "/dev/cu.usbmodemK3_G4011101331"
MODEL = "b1"  # K3 speaks the b1 protocol family
W, H = 380, 192  # b1 max width 384; height assumes ~24mm tape
PAD = 10

FONT = "/System/Library/Fonts/Helvetica.ttc"

# (font size, line spacing after) by line index — tune as needed
LINE_STYLES = [
    (34, 48),
    (22, 32),
    (20, 26),
    (20, 26),
    (20, 26),
]


def fit_font(text: str, max_size: int, max_px: int) -> ImageFont.FreeTypeFont:
    """Shrink font until text fits within max_px."""
    size = max_size
    while size > 6:
        f = ImageFont.truetype(FONT, size)
        bbox = f.getbbox(text)
        if bbox[2] - bbox[0] <= max_px:
            return f
        size -= 1
    return ImageFont.truetype(FONT, size)


def render(lines: list[str], out_path: Path) -> None:
    img = Image.new("1", (W, H), 1)
    d = ImageDraw.Draw(img)
    usable = W - 2 * PAD
    y = PAD
    for i, text in enumerate(lines):
        max_size, advance = LINE_STYLES[min(i, len(LINE_STYLES) - 1)]
        font = fit_font(text, max_size, usable)
        d.text((PAD, y), text, font=font, fill=0)
        y += advance
    img.save(out_path)


def send(image_path: Path) -> None:
    cmd = [
        "uv", "tool", "run",
        "--from", "git+https://github.com/AndBondStyle/niimprint",
        "python", "-m", "niimprint",
        "--model", MODEL,
        "--conn", "usb",
        "--addr", PRINTER_ADDR,
        "--image", str(image_path),
    ]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines", nargs="+", help="one positional arg per line")
    ap.add_argument("--no-print", action="store_true", help="render only, open preview")
    ap.add_argument("--out", default="label.png")
    args = ap.parse_args()

    out = Path(args.out)
    render(args.lines, out)
    print(f"wrote {out} ({W}x{H})")

    if args.no_print:
        if shutil.which("open"):
            subprocess.run(["open", str(out)])
    else:
        send(out)


if __name__ == "__main__":
    main()
