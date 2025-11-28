from pdf2image import convert_from_path
import os
def pdf_to_images(pdf_path, out_dir, dpi=300):
    os.makedirs(out_dir, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=dpi)
    results = []
    for i, page in enumerate(pages, 1):
        p = os.path.join(out_dir, f"{os.path.basename(pdf_path)}_page_{i}.png")
        page.save(p, 'PNG')
        results.append(p)
    return results
