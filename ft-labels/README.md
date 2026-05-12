# ft-labels

Print labels to a **Niimbot K3** from macOS over USB.

## Hardware setup

- Printer: Niimbot K3
- Connection: USB-C (the K3 enumerates as `/dev/cu.usbmodemK3_*` when powered ON)
  - The K3's USB only works when the printer is powered on — a powered-off K3 looks like a charge-only device.
  - The cable must be a data-capable USB-C cable.
- Loaded media: ~24mm tape (192 dots). For 12mm tape, change `H` in `print_label.py` to `96`.

## How it actually works

- macOS has no Niimbot driver. The K3 isn't a CUPS printer.
- We talk to it directly via a CDC-ACM serial endpoint using the community tool
  [`AndBondStyle/niimprint`](https://github.com/AndBondStyle/niimprint).
- The K3 isn't in niimprint's model list, but it speaks the same protocol as the
  `b1` family. `--model b1` works. `b1` caps `image.width` at **384 dots** — that
  is the long axis of a landscape label.
- niimprint expects the image with: `width` = along the feed direction (label length),
  `height` = tape width.

## Install

```bash
# One-time: niimprint from source (PyPI version is a stub)
uv tool install --from git+https://github.com/AndBondStyle/niimprint niimprint
# uv pulls pillow/pyserial/click as deps automatically.
```

The `print_label.py` script has a uv shebang (`#!/usr/bin/env -S uv run --with pillow --script`)
so it self-installs Pillow on first run.

## Usage

```bash
# Print
./print_label.py "first line" "second line" "third line"

# Preview only (writes label.png and opens it in Preview.app)
./print_label.py --no-print "first line" "second line"
```

Each line auto-shrinks its font to fit. The first line gets the largest font
(34pt max), subsequent lines get progressively smaller (22pt, 20pt…). Edit
`LINE_STYLES` in `print_label.py` to change.

## Known constraints

- **Max ~38 chars on a single line** at 20pt with the current 380×192 canvas.
  Longer text wraps as a second positional argument or auto-shrinks.
- **One printer hardcoded**: `PRINTER_ADDR = "/dev/cu.usbmodemK3_G4011101331"`.
  This is the K3's serial number — check yours with `ls /dev/cu.usbmodemK3_*`.

## Reprinting the cluster labels

```bash
# Control plane
./print_label.py "Talos Cluster Control Plane" "FT Learning Layer" \
  "Ask Glo for access to this K8S cluster" "@elg0nz on Telegram"

# Workers 1–4
for n in 1 2 3 4; do
  ./print_label.py "Talos Worker $n" "FT Learning Layer" \
    "Ask Glo for access to this K8S cluster" "@elg0nz on Telegram"
  sleep 2
done
```

## Troubleshooting

- **`No such file or directory: /dev/cu.usbmodemK3_*`** — printer is off, or cable
  is charge-only. Power it on, swap cable, re-check with `ls /dev/cu.usbmodemK3_*`.
- **`Image width too big for B1`** — image.width > 384. Either reduce `W` or split
  text across more lines.
- **Output is blank past a certain point** — the loaded tape is narrower than `H`
  dots. Lower `H` to match (`96` for 12mm, `192` for 24mm).
