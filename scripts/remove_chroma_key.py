#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from imagegen_chroma_cutout.chroma_key import main


if __name__ == "__main__":
    main()
