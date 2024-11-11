import re, os
from dataclasses import dataclass

_sapi_begin = re.compile("(?i)(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?('{3}|\"{3}|\"{1})", re.IGNORECASE)
_sapi_end = re.compile("('{3}|\"{3}|\"{1})", re.IGNORECASE)
# _sapi_begin = re.compile("(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?((?<!')'''|(?<!\")\"\"\"|(?<!\")\")", re.IGNORECASE)
# _sapi_end = re.compile("('''(?!')|\"\"\"(?!\")|\"(?!\"))", re.IGNORECASE)

@dataclass
class Section:
    query: str
    leading_whitespace: str # evt. temp
    # index: int
    line_nr_start: int 
    line_nr_end: int
    char_start: int
    char_end: int

@dataclass
class _HalfSection: # a _HalfSection is either a query or a piece of whitespace
    text: str
    is_query: bool
    # index: int # this can be constructed from match start/end in the line processing funcitons, if necessary
    end_char: int
    line_nr_start: int|None = None # this is nullable to allow for unfinished halfSections
    line_nr_end: int|None = None # this is nullable to allow for unfinished halfSections
    # line_length: int|None = None # used for making index

# def sapi_lines(raw_lines: list[str], use_os_line_ending: bool) -> list[str]: # temp
#     line_ending = os.linesep if use_os_line_ending else '\n'
#     sections = sapi_sections(raw_lines, use_os_line_ending)

#     lines = []
#     for section in sections:
#         text = section.leading_whitespace + section.query
#         section_lines = text.split(line_ending)
#         # section_lines = section.text.split('\n')
#         if lines and section_lines:
#             lines[-1] += section_lines.pop(0)
#         lines += section_lines
#     return lines


def freeform_single_section(lines: list[str], use_os_line_ending: bool) -> list[Section]: # returns [Section]
    line_ending = os.linesep if use_os_line_ending else '\n'
    return [Section(
        query = line_ending.join([line.strip('\n\r') for line in lines]), 
        leading_whitespace='',
        line_nr_start = 0,
        line_nr_end = len(lines),
        char_start = 0,
        char_end = len(lines[-1]),
        )]


def sapi_sections(raw_lines: list[str], use_os_line_ending: bool) -> list[Section]:
    """
    Returns list of (sapi_code, whitespace)
    
    nb: We have to work line-by-line due to compatibility with tmGrammar json files.
    """
    line_ending = os.linesep if use_os_line_ending else '\n'
    half_sections: list[_HalfSection] = []
    for line_nr, line in enumerate(raw_lines):
        in_sapi = half_sections[-1].is_query if half_sections else False
        half_sections_within_line = _process_sapi_line(line, [], 0) if in_sapi else _process_surounding_line(line, [], 0)
        
        for hs in half_sections_within_line:
            hs.line_nr_start = line_nr
            hs.line_nr_end = line_nr

        if half_sections and half_sections_within_line:
            # glue them together across lines
            if half_sections[-1].is_query == half_sections_within_line[0].is_query:
                half_section = half_sections_within_line.pop(0)
                half_sections[-1].text += line_ending + half_section.text
                half_sections[-1].line_nr_end = line_nr
                half_sections[-1].end_char = half_section.end_char

        # for s in half_sections:
        #     assert not (s.is_query and 2 * line_ending in s.text), repr(s.text)
        half_sections += half_sections_within_line
    
    return _build_sections(half_sections)


def _process_surounding_line(remaining_line: str, out: list[_HalfSection], char: int) -> list[_HalfSection]:
    if match_ := re.search(_sapi_begin, remaining_line):
        # surrounding code end. Sapi begin
        whitespace = ' ' * match_.end() # whitespace before _sapi_begin
        out.append(_HalfSection(text=whitespace, is_query=False, end_char=char + match_.end()))
        remaining_line = remaining_line[match_.end():]
        out = _process_sapi_line(remaining_line, out, char + match_.end())
    else:
        # entire line is surrounding code
        whitespace = ' ' * len(remaining_line)
        out.append(_HalfSection(text=whitespace, is_query=False, end_char=char + len(remaining_line)))

    return out


def _process_sapi_line(remaining_line: str, out: list[_HalfSection], char: int) -> list[_HalfSection]:
    if match_ := re.search(_sapi_end, remaining_line):
        # sapi code end. Surrounding code begin
        boundery_whitespace = ' ' * (match_.end() - match_.start()) # end_char doesn't include boundery_whitespace
        query_line = remaining_line[:match_.start()]
        out.append(_HalfSection(text=query_line + boundery_whitespace, is_query=True, end_char=char + match_.start()))

        remaining_line = remaining_line[match_.end():]
        out = _process_surounding_line(remaining_line, out, char + match_.start())
    else:
        # entire line is sapi code
        query_line = remaining_line
        out.append(_HalfSection(text=query_line, is_query=True, end_char=char + len(remaining_line)))

    return out


def _build_sections(half_sections: list[_HalfSection]) -> list[Section]:
    sections: list[Section] = []
    length = len(half_sections)
    i = 0
    while i < length - 1: # we exclude the last element to make room for index i + 1
        whitespace = half_sections[i]
        query = half_sections[i + 1] # if i + 1 < length else _QueryOrWhiteSpace(text='', is_query=True)
        assert query.is_query, "expected query"
        assert not whitespace.is_query, "expected whitespace"
        assert query.text is not None, repr(query)
        assert whitespace.text is not None, repr(whitespace)
        assert query.line_nr_start is not None, repr(query)
        assert query.line_nr_end is not None, repr(query)
        assert whitespace.end_char is not None, repr(whitespace)
        assert query.end_char is not None, repr(query)
        sections.append(Section(
            query = query.text, 
            leading_whitespace = whitespace.text, 
            line_nr_start = query.line_nr_start,
            line_nr_end = query.line_nr_end,
            char_start = whitespace.end_char,
            char_end = query.end_char,
            ))
        i += 2
    return sections


