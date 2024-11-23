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


def freeform_single_section(lines: list[str], use_os_line_ending: bool, range: t.Range|None) -> list[Section]: # returns [Section]
    line_ending = os.linesep if use_os_line_ending else '\n'
    sections = [Section(
        query = line_ending.join([line.strip('\n\r') for line in lines]), 
        leading_whitespace='',
        line_nr_start = 0,
        line_nr_end = len(lines),
        char_start = 0,
        char_end = len(lines[-1]),
        )]
    return _adjust_for_semicolon(sections, range, line_ending) if range else sections

def sapi_sections(raw_lines: list[str], use_os_line_ending: bool, range: t.Range = None) -> list[Section]:
    """
    Returns list of (sapi_code, whitespace)
    
    nb: We have to work line-by-line due to compatibility with tmGrammar json files.
    """
    line_ending = os.linesep if use_os_line_ending else '\n'
    half_sections: list[_HalfSection] = []
    previous_semicolon_line_nr = 0
    for line_nr, line in enumerate(raw_lines):
        # find half_sections in the line
        in_sapi = half_sections[-1].is_query if half_sections else False
        half_sections_within_line = _process_sapi_line(line, [], 0) if in_sapi else _process_surounding_line(line, [], 0)
        if half_sections_within_line == []:
            continue
        
        # set line_nr
        for hs in half_sections_within_line: 
            hs.line_nr_start = line_nr
            hs.line_nr_end = line_nr # kan overskrives
            if hs.is_query:
                ...
        
        if range:
            half_sections_within_line = _glue_if_before_range(half_sections_within_line, range) # duer ik', da slutning af half_section ikke kendes
            # break after range
            if any(hs for hs in half_sections_within_line if hs.is_query and ';' in hs.text):
                previous_semicolon_line_nr = line_nr
            # first_or_prev = half_sections_within_line[0] if half_sections_within_line else half_sections[-1]
            # line_nr_start = max(first_or_prev.line_nr_start, previous_semicolon_line_nr) 
            # if line_nr_start > range.end.line:
            #     break

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
        if range:
            first_or_prev = half_sections_within_line[0] if half_sections_within_line else half_sections[-1]
            line_nr_start = max(first_or_prev.line_nr_start, previous_semicolon_line_nr) 
            if line_nr_start > range.end.line:
                break

        if half_sections_within_line == []:
            continue

        half_sections += half_sections_within_line

    
    sections = _build_sections(half_sections)
    if range:
        sections = _adjust_for_semicolon(sections, range, line_ending)
    return sections


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


def _build_sections(half_sections: list[_HalfSection]) -> list[Section]:
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


def _adjust_for_semicolon(sections: list[Section], range: t.Range, line_ending: str) -> list[Section]:
    if sections == []: 
        return []
    
    first = sections[0]
    range_start_index = _index(first.query.split(line_ending), range.start.line - first.line_nr_start, range.start.character, line_ending)
    if range_start_index:
        last_semicolon_before_range = first.query.rfind(';', 0, range_start_index)
        if last_semicolon_before_range != -1:
            first.leading_whitespace = first.leading_whitespace + ' ' * (last_semicolon_before_range + 1)
            first.query = first.query[(last_semicolon_before_range + 1):]
            first.line_nr_start = range.start.line
            first.char_start = range.start.character
    
    last = sections[-1]
    range_end_index = _index(last.query.split(line_ending), range.end.line - last.line_nr_start, range.end.character, line_ending)
    if range_end_index:
        first_semicolon_after_range = last.query.find(';', range_end_index)
        if first_semicolon_after_range != -1:
            # last.leading_whitespace = last.leading_whitespace + ' ' * (first_semicolon_after_range + 1)
            last.query = last.query[:(first_semicolon_after_range + 1)]
            last.line_nr_end = range.end.line
            last.char_end = range.end.character

    return sections

def _index(lines: list[str], line_nr: int, char: int, line_ending: str) -> int|None:
    if line_nr < 0: return None
    if line_nr >= len(lines): return None
    # char is unchecked

    index = 0
    for _line_nr, line in enumerate(lines):
        if _line_nr < line_nr:
            index += len(line + line_ending)
            continue
        elif _line_nr == line_nr:
            index += char
            return index
        else:
            raise IndexError(f"Cannot get index from line_nr={line_nr}, char={char}")
    raise IndexError(f"Cannot get index from line_nr={line_nr}, char={char}")

def _glue_if_before_range(half_sections_within_line: list[_HalfSection], range: t.Range) -> list[_HalfSection]:
    out: list[_HalfSection] = []
    line_nr = half_sections_within_line[0].line_nr_end
    for hs in half_sections_within_line:
        # if before 
        if line_nr < range.start.line or (line_nr == range.start.line and hs.char_end < range.start.character):
            hs.text = ' ' * len(hs.text)
            hs.is_query = False
            if out and not out[-1].is_query: # glue
                print("glue:", half_sections_within_line)
                previous = out[-1]
                previous.text += hs.text
                previous.line_nr_end = line_nr
                previous.char_end = hs.char_end
                continue
        out.append(hs)        
    return out



