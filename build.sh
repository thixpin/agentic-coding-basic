#!/usr/bin/env bash
#
# Build the book into dist/ as EPUB and PDF.
#
#   ./build.sh            # build both EPUB + PDF
#   ./build.sh epub       # EPUB only
#   ./build.sh pdf        # PDF only (also builds EPUB's fonts step)
#
# Requirements (macOS): python3, and Google Chrome / Chromium / Edge for the PDF.
# Override the browser with:  CHROME=/path/to/chrome ./build.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$ROOT/build"
DIST="$ROOT/dist"
VENV="$BUILD/venv"
mkdir -p "$BUILD" "$DIST"

TARGET="${1:-all}"

# --- 1. Python venv + dependencies -----------------------------------------
if [ ! -x "$VENV/bin/python" ]; then
  echo "==> Creating Python venv in build/venv …"
  python3 -m venv "$VENV"
fi
if ! "$VENV/bin/python" -c "import markdown, fontTools" >/dev/null 2>&1; then
  echo "==> Installing dependencies (markdown, fonttools) …"
  "$VENV/bin/pip" install --quiet markdown fonttools
fi

build_epub() {
  echo "==> Building EPUB …"
  "$VENV/bin/python" "$ROOT/scripts/build_epub.py"
}

build_pdf() {
  echo "==> Building print HTML …"
  "$VENV/bin/python" "$ROOT/scripts/build_pdf.py"

  echo "==> Locating a Chromium-based browser …"
  local chrome="${CHROME:-}"
  if [ -z "$chrome" ]; then
    for c in \
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
      "/Applications/Chromium.app/Contents/MacOS/Chromium" \
      "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
      "$(command -v google-chrome 2>/dev/null || true)" \
      "$(command -v chromium 2>/dev/null || true)"; do
      if [ -n "$c" ] && [ -x "$c" ]; then chrome="$c"; break; fi
    done
  fi
  if [ -z "$chrome" ]; then
    echo "!! No Chrome/Chromium/Edge found. Set CHROME=/path/to/browser and re-run." >&2
    echo "   (The EPUB, if requested, was still built.)" >&2
    exit 1
  fi

  echo "==> Rendering PDF with: $chrome"
  "$chrome" --headless --disable-gpu --no-sandbox \
    --print-to-pdf="$DIST/agentic-coding-basic-mm.pdf" --no-pdf-header-footer \
    --run-all-compositor-stages-before-draw --virtual-time-budget=15000 \
    "file://$BUILD/book_print.html" >/dev/null 2>&1
}

case "$TARGET" in
  epub) build_epub ;;
  pdf)  build_pdf ;;
  all)  build_epub; build_pdf ;;
  *)    echo "Unknown target '$TARGET' (use: all | epub | pdf)" >&2; exit 2 ;;
esac

echo "==> Done. Output in dist/:"
ls -la "$DIST"
