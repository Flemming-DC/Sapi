import re
from tools.log import log


def sapi_lines(raw_lines: list[str]) -> list[str]:
    in_sapi = False
    lines = []
    for line in raw_lines:
        in_sapi, processed_line = _process_sapi_line(line, '') if in_sapi else _process_surounding_line(line, '')
        lines.append(processed_line)
    
    return lines


def _process_surounding_line(remaining_line: str, processed_line: str) -> tuple[bool, str]:
    begin = "(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?((?<!')'''|(?<!\")\"\"\"|(?<!\")\")" # (?i)
    if match_ := re.search(begin, remaining_line, re.IGNORECASE):
        processed_line += ' ' * (match_.end() - 0)
        remaining_line = remaining_line[match_.end() - 0:]
        in_sapi, processed_line = _process_sapi_line(remaining_line, processed_line)
    else:
        processed_line += ' ' * len(remaining_line)
        in_sapi = False
    return in_sapi, processed_line

def _process_sapi_line(remaining_line: str, processed_line: str) -> tuple[bool, str]:
    end = "('''(?!')|\"\"\"(?!\")|\"(?!\"))"
    if match_ := re.search(end, remaining_line, re.IGNORECASE):
        processed_line += remaining_line[:match_.start()] + ' ' * (match_.end() - match_.start())
        remaining_line = remaining_line[match_.end():]
        in_sapi, processed_line = _process_surounding_line(remaining_line, processed_line)
    else:
        processed_line += remaining_line
        in_sapi = True
    return in_sapi, processed_line
