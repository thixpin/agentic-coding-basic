#!/usr/bin/env python3
"""Shared helper: extract Regular + Bold Noto Sans Myanmar TTFs from the macOS
system font collection into a build directory. Noto fonts are OFL-licensed, so
embedding them into the EPUB/PDF is permitted."""
import os
from fontTools.ttLib import TTCollection

TTC = "/System/Library/Fonts/NotoSansMyanmar.ttc"


def extract_fonts(build_dir):
    """Return (regular_ttf_path, bold_ttf_path), extracting them if missing."""
    reg = os.path.join(build_dir, "NotoSansMyanmar-Regular.ttf")
    bold = os.path.join(build_dir, "NotoSansMyanmar-Bold.ttf")
    if os.path.exists(reg) and os.path.exists(bold):
        return reg, bold
    if not os.path.exists(TTC):
        raise SystemExit(
            "Myanmar font not found at %s\n"
            "This build currently targets macOS (uses the bundled Noto Sans Myanmar).\n"
            "On other systems, place NotoSansMyanmar-Regular.ttf and "
            "NotoSansMyanmar-Bold.ttf in %s manually." % (TTC, build_dir)
        )
    ttc = TTCollection(TTC)
    picks = {400: reg, 700: bold}
    done = set()
    for f in ttc.fonts:
        w = f["OS/2"].usWeightClass
        fam = f["name"].getDebugName(1) or ""
        if "Zawgyi" in fam:          # skip the Zawgyi encoding variants
            continue
        if w in picks and w not in done:
            f.save(picks[w])
            done.add(w)
    return reg, bold
