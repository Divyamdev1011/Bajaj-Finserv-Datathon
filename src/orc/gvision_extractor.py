import io
from google.cloud import vision

def extract_with_gvision(image):

    client = vision.ImageAnnotatorClient()

    _, img_bytes = cv2.imencode('.png', image)
    content = img_bytes.tobytes()

    image_obj = vision.Image(content=content)
    response = client.text_detection(image=image_obj)

    if response.error.message:
        return ""

    if response.text_annotations:
        return response.text_annotations[0].description

    return ""
