import re, os
from lsprotocol import types as t
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
    char_end: int
    line_nr_start: int|None = None # this is nullable to allow for unfinished halfSections
    line_nr_end: int|None = None # this is nullable to allow for unfinished halfSections
    # line_length: int|None = None # used for making index
    # def char_start(_, leading_whitespace: '_HalfSection'): return leading_whitespace.text
    # out_of_range: bool


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


def sapi_sections(raw_lines: list[str], use_os_line_ending: bool, range: t.Range = None) -> list[Section]:
    """
    Returns list of (sapi_code, whitespace)
    
    nb: We have to work line-by-line due to compatibility with tmGrammar json files.
    """
    line_ending = os.linesep if use_os_line_ending else '\n'
    half_sections: list[_HalfSection] = []
    for line_nr, line in enumerate(raw_lines):
        # find half_sections in the line
        in_sapi = half_sections[-1].is_query if half_sections else False
        half_sections_within_line = _process_sapi_line(line, [], 0) if in_sapi else _process_surounding_line(line, [], 0)
        if half_sections_within_line == []:
            continue
        
        # set line_nr
        for hs in half_sections_within_line: 
            hs.line_nr_start = line_nr
            hs.line_nr_end = line_nr
        
        half_sections_within_line = _glue_if_before_range(half_sections_within_line, range)

        # glue sections together across lines
        if half_sections != []:
            previous = half_sections[-1]
            # glue sections of the same type
            if previous.is_query == half_sections_within_line[0].is_query:
                half_section = half_sections_within_line.pop(0)
                previous.text += line_ending + half_section.text
                previous.line_nr_end = line_nr
                previous.char_end = half_section.char_end
                if half_sections_within_line == []:
                    continue

        # after range
        first_section = half_sections_within_line[0]
        if range and first_section.line_nr_start > range.end.line:
            break
        char_start = half_sections[-1].char_end if half_sections else 0 # = prev_end
        if range and first_section.line_nr_start == range.end.line and char_start > range.end.character:
            break

        half_sections += half_sections_within_line

    
    return _build_sections(half_sections, range)


def _process_surounding_line(remaining_line: str, out: list[_HalfSection], char: int) -> list[_HalfSection]:
    match_ = re.search(_sapi_begin, remaining_line)
    if match_:
        # surrounding code end. Sapi begin
        whitespace = ' ' * match_.end() # whitespace before _sapi_begin
        out.append(_HalfSection(text=whitespace, is_query=False, char_end=char + match_.end()))
        remaining_line = remaining_line[match_.end():]
        out = _process_sapi_line(remaining_line, out, char + match_.end())
    else:
        # entire line is surrounding code
        whitespace = ' ' * len(remaining_line)
        out.append(_HalfSection(text=whitespace, is_query=False, char_end=char + len(remaining_line)))

    return out


def _process_sapi_line(remaining_line: str, out: list[_HalfSection], char: int) -> list[_HalfSection]:
    match_ = re.search(_sapi_end, remaining_line)
    if match_:
        # sapi code end. Surrounding code begin
        boundery_whitespace = ' ' * (match_.end() - match_.start()) # end_char doesn't include boundery_whitespace
        query_line = remaining_line[:match_.start()]
        out.append(_HalfSection(text=query_line + boundery_whitespace, is_query=True, char_end=char + match_.start()))

        remaining_line = remaining_line[match_.end():]
        out = _process_surounding_line(remaining_line, out, char + match_.start())
    else:
        # entire line is sapi code
        query_line = remaining_line
        out.append(_HalfSection(text=query_line, is_query=True, char_end=char + len(remaining_line)))

    return out


def _build_sections(half_sections: list[_HalfSection], range: t.Range|None) -> list[Section]:
    sections: list[Section] = []
    length = len(half_sections)
    i = 0
    while i < length - 1: # we exclude the last element to make room for index i + 1
        whitespace = half_sections[i]
        query = half_sections[i + 1] # if i + 1 < length else _QueryOrWhiteSpace(text='', is_query=True)
        
        section = Section(
            query = query.text, 
            leading_whitespace = whitespace.text, 
            line_nr_start = query.line_nr_start,
            line_nr_end = query.line_nr_end,
            char_start = whitespace.char_end,
            char_end = query.char_end,
            )
        sections.append(section)
        i += 2
    return sections



def _glue_if_before_range(
        half_sections_within_line: list[_HalfSection], range: t.Range|None) -> list[_HalfSection]:
    if range is None:
        return half_sections_within_line
    
    out: list[_HalfSection] = []
    line_nr = half_sections_within_line[0].line_nr_end
    for s in half_sections_within_line:
        # before 
        if line_nr < range.start.line or (line_nr == range.start.line and s.char_end < range.start.character):
            s.text = ' ' * len(s.text)
            s.is_query = False
            if out and not out[-1].is_query: # glue
                previous = out[-1]
                previous.text += s.text
                previous.line_nr_end = line_nr
                previous.char_end = s.char_end
                continue
        out.append(s)        
    return out



