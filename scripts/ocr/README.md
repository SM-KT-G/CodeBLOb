# OCR Examples

This directory hosts small OCR-oriented utilities intended to be easy to read
and adapt. The first script focuses on showing how to combine Pillow and
pytesseract to read text from an image that the script generates on the fly.

## Goals

- Keep dependencies minimal and well-documented.
- Provide runnable examples that do not require external assets.
- Explain the moving pieces so the code doubles as a tutorial.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You also need the native Tesseract binary on your system. macOS users can run
`brew install tesseract`, while Linux users can install the `tesseract-ocr`
package from their distro.

## Usage

The `simple_ocr.py` script generates an image containing the text you pass via
`--text`, saves it if you pass `--output`, optionally shows it, and then feeds
the image into pytesseract to recover the text.

```bash
python scripts/ocr/simple_ocr.py \
  --text "Codex OCR demo" \
  --output demo.png \
  --show-image \
  --debug
```
