import re
from tools.log import log
from dataclasses import dataclass

_sapi_begin = re.compile("(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?((?<!')'''|(?<!\")\"\"\"|(?<!\")\")", re.IGNORECASE)
_sapi_end = re.compile("('''(?!')|\"\"\"(?!\")|\"(?!\"))", re.IGNORECASE)

@dataclass
class Section:
    query: str
    leading_whitespace: str # temp
    # line_nr: int
    # char: int
    # index: int

@dataclass
class _QueryOrWhiteSpace:
    text: str
    is_query: bool

# def sapi_lines(raw_lines: list[str]) -> list[str]: # temp
    
#     sections = sapi_sections(raw_lines)
    
#     lines = []
#     for section in sections:
#         text = section.leading_whitespace + section.query
#         section_lines = text.split('\n')
#         # section_lines = section.text.split('\n')
#         if lines and section_lines:
#             lines[-1] += section_lines.pop(0)
#         lines += section_lines
#     return lines

def freeform_single_section(lines: list[str]) -> list[Section]: # returns [Section]
    return [Section(query = '\n'.join([line.strip('\n\r') for line in lines]), leading_whitespace='')]


def sapi_sections(raw_lines: list[str]) -> list[Section]:
    """
    Returns list of (sapi_code, whitespace)
    
    nb: We have to work line-by-line due to compatibility with tmGrammar json files.
    """
    in_sapi = False
    half_sections: list[_QueryOrWhiteSpace] = []
    for line in raw_lines:
        # was_in_sapi = in_sapi
        in_sapi, half_sections_within_line = _process_sapi_line(line, []
            ) if in_sapi else _process_surounding_line(line, [])
        # sections_within_line = [sections_within_line] # temp
        # if was_in_sapi:
        #     # handle sections that cover multiple lines by gluing them together
        #     assert sections_within_line, "expected section"
        #     next_section = sections_within_line.pop(0)
        #     sections[-1].query += '\n' + next_section.query
        #     sections[-1].trailing_whitespace += '\n' + next_section.trailing_whitespace
        if half_sections and half_sections_within_line:
            if half_sections[-1].is_query == half_sections_within_line[0].is_query:
                half_sections[-1].text += '\n' + half_sections_within_line.pop(0).text
        half_sections += half_sections_within_line
    
    sections: list[Section] = []
    length = len(half_sections)
    # is_even = len(half_sections) % 2 == 0
    i = 0
    while i < length - 1: # we exclude the last element to make room for index i + 1
        # is_query = half_sections[i].is_query
        # query = half_sections[i] if is_query else half_sections[i + 1] if i + 1 < length else _QueryOrWhiteSpace(text='', is_query=True)
        # whitespace = half_sections[i] if not is_query else half_sections[i + 1] if i + 1 < length else _QueryOrWhiteSpace(text='', is_query=False)
        whitespace = half_sections[i]
        query = half_sections[i + 1] # if i + 1 < length else _QueryOrWhiteSpace(text='', is_query=True)
        assert query.is_query, "expected query"
        assert not whitespace.is_query, "expected whitespace"
        sections.append(Section(query = query.text, leading_whitespace = whitespace.text))
        i += 2
    
    return sections


def _process_line(line: str, in_sapi: bool):
    in_sapi = False
    idx = 0
    length = len(line)

    while idx < length:
        if in_sapi:
            idx = _process_sapi_line(line, idx)
        else:
            _process_surounding_line()

def _process_surounding_line(remaining_line: str, out: list[_QueryOrWhiteSpace]) -> tuple[bool, list[_QueryOrWhiteSpace]]:
    if match_ := re.search(_sapi_begin, remaining_line):
        whitespace = ' ' * match_.end() # whitespace before _sapi_begin
        out.append(_QueryOrWhiteSpace(text=whitespace, is_query=False))
        remaining_line = remaining_line[match_.end():]
        in_sapi, out = _process_sapi_line(remaining_line, out)
    else:
        whitespace = ' ' * len(remaining_line)
        out.append(_QueryOrWhiteSpace(text=whitespace, is_query=False))
        in_sapi = False
    # out.append(_QueryOrWhiteSpace(text=whitespace, is_query=False))
    return in_sapi, out

def _process_sapi_line(remaining_line: str, out: list[_QueryOrWhiteSpace]) -> tuple[bool, list[_QueryOrWhiteSpace]]:
    if match_ := re.search(_sapi_end, remaining_line):
        boundery_whitespace = ' ' * (match_.end() - match_.start())
        # out.append(_QueryOrWhiteSpace(text=boundery_whitespace, is_query=False))
        query_line = remaining_line[:match_.start()]
        out.append(_QueryOrWhiteSpace(text=query_line + boundery_whitespace, is_query=True)) # temp

        # processed_line += remaining_line[:match_.start()] + ' ' * (match_.end() - match_.start())
        remaining_line = remaining_line[match_.end():]
        in_sapi, out = _process_surounding_line(remaining_line, out)
    else:
        query_line = remaining_line
        out.append(_QueryOrWhiteSpace(text=query_line, is_query=True))

        # processed_line += remaining_line
        in_sapi = True
    # out.append(_QueryOrWhiteSpace(text=query_line, is_query=True))
    return in_sapi, out


# ------------- OLD ------------- #

# def sapi_lines_old(raw_lines: list[str]) -> list[str]:
#     in_sapi = False
#     lines = []
#     for line in raw_lines:
#         in_sapi, processed_line = _process_sapi_line_old(line, '') if in_sapi else _process_surounding_line_old(line, '')
#         lines.append(processed_line)
    
#     return lines


# def _process_surounding_line_old(remaining_line: str, processed_line: str) -> tuple[bool, str]:
#     if match_ := re.search(_begin, remaining_line):
#         processed_line += ' ' * (match_.end() - 0)
#         remaining_line = remaining_line[match_.end() - 0:]
#         in_sapi, processed_line = _process_sapi_line(remaining_line, processed_line)
#     else:
#         processed_line += ' ' * len(remaining_line)
#         in_sapi = False
#     return in_sapi, processed_line

# def _process_sapi_line_old(remaining_line: str, processed_line: str) -> tuple[bool, str]:
#     if match_ := re.search(_end, remaining_line):
#         processed_line += remaining_line[:match_.start()] + ' ' * (match_.end() - match_.start())
#         remaining_line = remaining_line[match_.end():]
#         in_sapi, processed_line = _process_surounding_line(remaining_line, processed_line)
#     else:
#         processed_line += remaining_line
#         in_sapi = True
#     return in_sapi, processed_line
