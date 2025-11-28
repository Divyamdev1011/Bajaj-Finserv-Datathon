"""
LLM-based parser wrapper using OpenAI ChatCompletion, with safe fallback to regex parser.
"""
import os, json, logging
from .regex_parser import parse_lines_from_text

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

def _build_prompt(text: str) -> str:
    return (
        "You receive OCR-extracted text from a medical invoice. Return a JSON array ONLY:\n"
        "[{\"description\": \"...\", \"amount\": 123.45}, ...]\n"
        "Rules: amounts numeric (no currency). If ambiguous set amount to null.\n\nText:\n" + text
    )

def parse_with_llm(raw_text: str):
    if os.environ.get('OPENAI_API_KEY'):
        try:
            import openai
            openai.api_key = os.environ.get('OPENAI_API_KEY')
            prompt = _build_prompt(raw_text)
            resp = openai.ChatCompletion.create(
                model=DEFAULT_MODEL,
                messages=[{"role":"system","content":"You are a JSON extractor."},
                          {"role":"user","content":prompt}],
                temperature=0,
                max_tokens=1500
            )
            content = resp['choices'][0]['message']['content']
            try:
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    result = []
                    for item in parsed:
                        if not isinstance(item, dict):
                            continue
                        desc = item.get('description') or 'UNKNOWN'
                        amount = item.get('amount')
                        result.append({'description': desc, 'amount': amount})
                    return result
                else:
                    logging.warning("LLM returned non-list JSON; fallback to regex")
                    return parse_lines_from_text(raw_text)
            except Exception:
                logging.warning("Unable to parse LLM JSON; fallback to regex")
                return parse_lines_from_text(raw_text)
        except Exception:
            logging.exception("LLM call failed; using regex fallback")
            return parse_lines_from_text(raw_text)
    else:
        logging.info("OPENAI_API_KEY not set; using regex fallback")
        return parse_lines_from_text(raw_text)
