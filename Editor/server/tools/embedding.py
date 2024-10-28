import re
from tools.log import log


def sapi_lines(raw_lines: list[str]) -> list[str]:
    in_sapi = False
    lines = []
    for line in raw_lines:
        print("line: ", line)
        in_sapi, processed_line = _process_sapi_line(line, '') if in_sapi else _process_surounding_line(line, '')
        print("in_sapi, processed_line: ", in_sapi, processed_line)
        lines.append(processed_line)
    
    # log("out lines length: ", len(lines))
    # log("out lines: ", lines)
    return lines



def _process_surounding_line(remaining_line: str, processed_line: str) -> tuple[bool, str]:
    begin = "(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?((?<!')'''|(?<!\")\"\"\"|(?<!\")\")" # (?i)
    if match_ := re.search(begin, remaining_line, re.IGNORECASE):
        print(f"BEGIN (before): R({remaining_line}), P({processed_line})")
        processed_line += ' ' * (match_.end() - 0)
        remaining_line = remaining_line[match_.end() - 0:]
        print(f"BEGIN (after): R({remaining_line}), P({processed_line})")
        in_sapi, processed_line = _process_sapi_line(remaining_line, processed_line)
    else:
        processed_line += ' ' * len(remaining_line)
        in_sapi = False
    return in_sapi, processed_line

def _process_sapi_line(remaining_line: str, processed_line: str) -> tuple[bool, str]:
    end = "('''(?!')|\"\"\"(?!\")|\"(?!\"))"
    if match_ := re.search(end, remaining_line, re.IGNORECASE):
        print(f"END (before): R({remaining_line}), P({processed_line})")
        processed_line += remaining_line[:match_.start()] + ' ' * (match_.end() - match_.start())
        remaining_line = remaining_line[match_.end():]
        print(f"END (after): R({remaining_line}), P({processed_line})")
        in_sapi, processed_line = _process_surounding_line(remaining_line, processed_line)
    else:
        processed_line += remaining_line
        in_sapi = True
    return in_sapi, processed_line
