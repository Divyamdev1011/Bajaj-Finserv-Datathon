"""
Utility helpers for preprocessing tasks.
"""
import os
from pathlib import Path
from pdf2image import convert_from_path

def pdf_to_images(pdf_path: str, out_dir: str, dpi: int = 300):
    os.makedirs(out_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=dpi)
    paths = []
    for i, page in enumerate(pages, start=1):
        p = Path(out_dir) / f"{Path(pdf_path).stem}_page_{i}.png"
        page.save(p, 'PNG')
        paths.append(str(p))
    return paths
