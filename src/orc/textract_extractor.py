"""
AWS Textract extractor with safe fallback (synchronous detect_document_text).
For multi-page PDFs use StartDocumentTextDetection in production.
"""
import os, logging
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    _HAS_BOTO = True
except Exception:
    _HAS_BOTO = False

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    if _HAS_BOTO and os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
        try:
            client = boto3.client('textract', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
            with open(pdf_path, 'rb') as f:
                b = f.read()
            resp = client.detect_document_text(Document={'Bytes': b})
            lines = [blk.get('Text', '') for blk in resp.get('Blocks', []) if blk.get('BlockType') == 'LINE']
            return "\n".join(lines) if lines else "EXTRACTED TEXT FROM TEXTRACT (no lines)"
        except Exception:
            logger.exception("Textract failed, falling back")
            return "EXTRACTED TEXT FROM TEXTRACT (fallback)\nLine Item A - 100\nLine Item B - 200\nTotal - 300"
    else:
        logger.info("Textract not configured - using fallback text")
        return "EXTRACTED TEXT FROM TEXTRACT (fallback)\nLine Item A - 100\nLine Item B - 200\nTotal - 300"
