#!/usr/bin/env python3
"""Convert SquareLine image arrays to 240x240 RGB565 for ESP32."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DST_W = 240
DST_H = 240
HEX_RE = re.compile(r"0x([0-9A-Fa-f]{2})")
SIZE_RE = re.compile(r"\.header\.w\s*=\s*(\d+).*?\.header\.h\s*=\s*(\d+)", re.S)
DATA_RE = re.compile(r"const\s+.*?uint8_t\s+\w+\[\]\s*=\s*\{(.*?)\};", re.S)
SWAP_RE = re.compile(r"LV_COLOR_16_SWAP\s*!=\s*(\d+)")

IMAGES = (
    ("ui_img_1phongsang_png.c", "img_1phongsang", "1phongsang"),
    ("ui_img_2phongsang_png.c", "img_2phongsang", "2phongsang"),
    ("ui_img_3phongsang_png.c", "img_3phongsang", "3phongsang"),
    ("ui_img_tatcasang_png.c", "img_tatcasang", "tatcasang"),
    ("ui_img_toiom_png.c", "img_toiom", "toiom"),
)

# Square crop window (side, x, y) in source pixels. toiom/1phong/2phong share
# one framing. 3phong/tatca are framed differently; their windows were fitted
# by edge correlation against toiom so the house matches in scale and
# position. Pixels outside the source are filled black, the background color.
CROP_WINDOW_BY_LABEL = {
    "1phongsang": (1020, 117, 117),
    "2phongsang": (1020, 117, 117),
    "toiom": (1020, 117, 117),
    "3phongsang": (1072, 92, 124),
    "tatcasang": (1072, 92, 124),
}


def detect_swap(src_dir: Path) -> bool:
    ui_c = src_dir / "ui.c"
    if not ui_c.exists():
        return True
    text = ui_c.read_text(encoding="utf-8", errors="ignore")
    match = SWAP_RE.search(text)
    if match is None:
        return True
    # "#if LV_COLOR_16_SWAP !=1" means the export stored swapped RGB565.
    return match.group(1) == "1"


def parse_image(path: Path) -> tuple[int, int, int, bytes]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    size = SIZE_RE.search(text)
    if size is None:
        raise RuntimeError(f"{path.name}: missing header.w / header.h")
    width = int(size.group(1))
    height = int(size.group(2))
    data = DATA_RE.search(text)
    blob = data.group(1) if data else text
    values = bytes(int(match.group(1), 16) for match in HEX_RE.finditer(blob))
    pixels = width * height
    if len(values) >= pixels * 4:
        bpp = 4
    elif len(values) >= pixels * 2:
        bpp = 2
    else:
        raise RuntimeError(
            f"{path.name}: parsed {len(values)} bytes, need {pixels * 2} for {width}x{height}"
        )
    return width, height, bpp, values[: pixels * bpp]


def sample_pixel(src: bytes, src_w: int, bpp: int, swap16: bool, x: int, y: int) -> tuple[int, int, int]:
    index = (y * src_w + x) * bpp
    if bpp == 4:
        return src[index + 2], src[index + 1], src[index]
    if swap16:
        pixel = (src[index] << 8) | src[index + 1]
    else:
        pixel = src[index] | (src[index + 1] << 8)
    red = ((pixel >> 11) & 0x1F) * 255 // 31
    green = ((pixel >> 5) & 0x3F) * 255 // 63
    blue = (pixel & 0x1F) * 255 // 31
    return red, green, blue


def store_rgb565(out: bytearray, dx: int, dy: int, red: int, green: int, blue: int) -> None:
    rgb565 = ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)
    offset = (dy * DST_W + dx) * 2
    # Packed little-endian; the board swaps to SPI/GC9A01 byte order on blit.
    out[offset] = rgb565 & 0xFF
    out[offset + 1] = rgb565 >> 8


def downscale_rgb565(
    src: bytes, src_w: int, src_h: int, bpp: int, swap16: bool, window: tuple[int, int, int]
) -> bytearray:
    out = bytearray(DST_W * DST_H * 2)
    side, crop_x, crop_y = window
    print(f"  crop {side}x{side} from ({crop_x},{crop_y}) -> {DST_W}x{DST_H}")
    for dy in range(DST_H):
        y0 = crop_y + dy * side // DST_H
        y1 = crop_y + max(dy * side // DST_H + 1, (dy + 1) * side // DST_H)
        y0 = max(y0, 0)
        y1 = min(y1, src_h)
        for dx in range(DST_W):
            x0 = crop_x + dx * side // DST_W
            x1 = crop_x + max(dx * side // DST_W + 1, (dx + 1) * side // DST_W)
            x0 = max(x0, 0)
            x1 = min(x1, src_w)
            total_r = 0
            total_g = 0
            total_b = 0
            count = 0
            for sy in range(y0, y1):
                for sx in range(x0, x1):
                    red, green, blue = sample_pixel(src, src_w, bpp, swap16, sx, sy)
                    total_r += red
                    total_g += green
                    total_b += blue
                    count += 1
            if count == 0:
                continue
            store_rgb565(out, dx, dy, total_r // count, total_g // count, total_b // count)
    return out


def write_c_array(path: Path, symbol: str, label: str, data: bytes) -> None:
    lines = [
        "/* Packed from SquareLine export to RGB565 240x240. */",
        "",
        "#include <stdint.h>",
        "",
        f"const uint8_t {symbol}_map[] __attribute__((aligned(4))) = {{",
    ]
    row = []
    for value in data:
        row.append(f"0x{value:02X}")
        if len(row) == 16:
            lines.append("    " + ", ".join(row) + ",")
            row = []
    if row:
        lines.append("    " + ", ".join(row) + ",")
    lines.extend(
        [
            "};",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    nonzero = sum(1 for value in data if value)
    print(f"Wrote {path.name} ({len(data)} bytes RGB565, source {label}, nonzero_bytes={nonzero})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="all", help="Pack one label, or 'all'")
    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent.parent
    src_dir = repo_dir / "tools" / "squareline_export"
    if not src_dir.is_dir():
        print(f"Missing source folder: {src_dir}", file=sys.stderr)
        return 1

    swap16 = detect_swap(src_dir)
    print(f"SquareLine RGB565 swap={swap16}")

    wanted = None if args.only == "all" else {name.strip() for name in args.only.split(",")}
    selected = IMAGES if wanted is None else tuple(item for item in IMAGES if item[2] in wanted)
    if not selected:
        print(f"Unknown image label: {args.only}", file=sys.stderr)
        return 1

    parsed = []
    for src_name, symbol, label in selected:
        src_path = src_dir / src_name
        if not src_path.exists():
            print(f"Missing {src_path}", file=sys.stderr)
            return 1
        print(f"Reading {src_name} ...")
        src_w, src_h, bpp, pixels = parse_image(src_path)
        side = min(src_w, src_h)
        window = CROP_WINDOW_BY_LABEL.get(label, (side, (src_w - side) // 2, (src_h - side) // 2))
        print(f"  source {src_w}x{src_h}, {bpp * 8}-bit, window={window}")
        parsed.append((src_name, symbol, label, src_w, src_h, bpp, pixels, window))

    out_dir = repo_dir / "src" / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for src_name, symbol, label, src_w, src_h, bpp, pixels, window in parsed:
        print(f"Packing {src_name} ...")
        packed = downscale_rgb565(pixels, src_w, src_h, bpp, swap16, window)
        write_c_array(out_dir / f"{symbol}.c", symbol, label, packed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
