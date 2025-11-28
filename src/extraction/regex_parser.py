"""Regex fallback parser to extract line items and amounts."""
import re
AMOUNT_RE = re.compile(r"(\d+[,.]?\d*)")

def parse_lines_from_text(text: str):
    lines = []
    for row in text.splitlines():
        row = row.strip()
        if not row:
            continue
        nums = AMOUNT_RE.findall(row)
        if nums:
            amount_token = nums[-1]
            try:
                amount = float(amount_token.replace(',', ''))
            except:
                amount = None
            desc = row.rsplit(amount_token, 1)[0].strip(' -,:')
            if not desc:
                desc = 'UNKNOWN'
            lines.append({'description': desc, 'amount': amount})
        else:
            lines.append({'description': row, 'amount': None})
    return lines
