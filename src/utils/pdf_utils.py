import fitz  # PyMuPDF

def convert_pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)

    return images
