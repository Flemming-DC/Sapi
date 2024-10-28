import re
from typing import Any
from pygls.server import LanguageServer
from tools.log import log

class SapiLanguageServer(LanguageServer):
   
    def send_output(self, data: Any):
        self.send_notification('output', str(data))

    def file_types(_): return [".sapi", ".sapir", ".py"]

    # def sapi_lines(_, uri: str) -> list[str]:
    #     log("--- sapi_lines ---")
    #     document = _.workspace.get_text_document(uri)
    #     if uri.endswith(".sapi"): return document.lines
    #     log("not in .sapi")
    #     log("in lines length: ", len(document.lines))

    #     begin = "(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?((?<!')'''|(?<!\")\"\"\"|(?<!\")\")" # (?i)
    #     end = "('''(?!')|\"\"\"(?!\")|\"(?!\"))"
    #     # def _to_white_space(code: str) -> str:
    #     #     return ''.join(['\n' if char == '\n' else ' ' for char in code])
        
    #     in_sapi = False
    #     lines = []
    #     for line in document.lines:
    #         log("line: ", line)
    #         # duer ikke til multiple sapi stumper i samme linje
    #         if not in_sapi:
    #             if match_ := re.match(begin, line, re.IGNORECASE):
    #                 log("begin")
    #                 in_sapi = True
    #                 lines.append(' ' * match_.endpos + line[match_.endpos:])
    #                 log('in_sapi: ', in_sapi)
    #                 log("append: ", ' ' * match_.endpos + line[match_.endpos:])
    #                 log("out lines length: ", len(lines))
    #         if in_sapi:
    #             if match_ := re.match(end, line, re.IGNORECASE):
    #                 log("end")
    #                 in_sapi = False
    #                 lines.append(line[:match_.pos] + ' ' * match_.pos)
    #                 log('in_sapi: ', in_sapi)
    #                 log("append: ", line[:match_.pos] + ' ' * match_.pos)
    #                 log("out lines length: ", len(lines))
    #         else: # bug
    #             log('in_sapi: ', in_sapi)
    #             log("append: ", line if in_sapi else ' ' * len(line))
    #             lines.append(line if in_sapi else ' ' * len(line))
    #             log("out lines length: ", len(lines))
        
    #     log("out lines length: ", len(lines))
    #     log("out lines: ", lines)
    #     return lines

    def sapi_lines(_, uri: str) -> list[str]:
        log("--- sapi_lines ---")
        document = _.workspace.get_text_document(uri)
        if uri.endswith(".sapi"): return document.lines
        log("not in .sapi")
        log("in lines length: ", len(document.lines))
        
        in_sapi = False
        lines = []
        for line in document.lines:
            log("line: ", line)
            in_sapi, processed_line = _process_sapi_line(line, '') if in_sapi else _process_surounding_line(line, '')
            lines.append(processed_line)
        
        log("out lines length: ", len(lines))
        log("out lines: ", lines)
        return lines



def _process_surounding_line(remaining_line: str, processed_line: str) -> tuple[bool, str]:
    begin = "(?<!#).*(?<=pg)\\s*\\W?\\s*f?r?((?<!')'''|(?<!\")\"\"\"|(?<!\")\")" # (?i)
    if match_ := re.match(begin, remaining_line, re.IGNORECASE):
        processed_line += ' ' * match_.endpos
        in_sapi, processed_line = _process_sapi_line(remaining_line[match_.endpos:], processed_line)
    else:
        processed_line += ' ' * len(remaining_line)
        in_sapi = False
    return in_sapi, processed_line

def _process_sapi_line(remaining_line: str, processed_line: str) -> tuple[bool, str]:
    end = "('''(?!')|\"\"\"(?!\")|\"(?!\"))"
    if match_ := re.match(end, remaining_line, re.IGNORECASE):
        processed_line += remaining_line[:match_.pos]
        in_sapi, processed_line = _process_surounding_line(remaining_line[match_.pos:], processed_line)
    else:
        processed_line += remaining_line
        in_sapi = True
    return in_sapi, processed_line




server = SapiLanguageServer("sapi-server", "v1")
serverType = SapiLanguageServer


