import mimetypes
import fitz  # PyMuPDF
from PIL import Image
import io

def convert_pdf_to_images(file_path):
    """
    Converts either:
    - PDF → list of page images
    - PNG/JPG → list with a single image
    """

    # Detect file type
    mime = mimetypes.guess_type(file_path)[0]

    # Case 1: PNG / JPG images
    if mime in ["image/png", "image/jpeg"]:
        with open(file_path, "rb") as f:
            img_bytes = f.read()
        return [img_bytes]  # return a list (one page/image)

    # Case 2: PDF file
    if mime == "application/pdf":
        images = []
        pdf_document = fitz.open(file_path)

        for page in pdf_document:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)

        return images

    # Unsupported file type
    raise ValueError(f"Unsupported file type: {mime}")
