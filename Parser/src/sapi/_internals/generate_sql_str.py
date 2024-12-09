from sapi._internals.token_tree import StrReplacement, common_select_clauses




def make_str(sapi_str: str, str_replacements: list[StrReplacement]) -> str:
    if not str_replacements:
        return sapi_str # handle the None case

    # make string
    # sql_str is on the form: 
    #   sapi-segment + replacement +
    #   ...
    #   sapi-segment + replacement +
    #   sapi-segment 
    sql_str = ""
    str_replacements.sort(key = lambda r: r.str_from)
    for i, rep in enumerate(str_replacements):
        last_rep_to = str_replacements[i - 1].str_to if i > 0 else 0 # helper-data
        sql_str += sapi_str[last_rep_to:rep.str_from]                # appending a sapi-segment
        sql_str = _add_token_str2(sql_str, rep.text, rep.is_new_clause)   # appending a token of replacement
        if _if_new_clause_add_newline(sapi_str, sql_str, rep.str_from):
            sql_str += '\n'

    last_rep_to = str_replacements[-1].str_to
    sql_str += sapi_str[last_rep_to:]
    return sql_str # + '\n;'




def _add_token_str2(so_far: str, text: str, is_join_clause: bool) -> str:
    no_space_prefix = [')', ']', '}', '.', ',']
    no_space_suffix = ['(', '[', '{', '.'     ]

    if is_join_clause:
        so_far = so_far.rstrip(' \n') # remove uncontrolled whitespace and newline
        so_far += '\n' + _last_indention(so_far) # add newline and preserve indention
        return so_far + text
    
    elif so_far != "" and so_far[-1] in no_space_suffix: # previous has have no space suffix
        return so_far.rstrip(' ') + text
    elif text in no_space_prefix:
        return so_far.rstrip(' ') + text
    else:
        return (so_far if so_far.endswith(' ') else so_far + ' ') + text
    

def _last_indention(s: str) -> str:
    last_line = s.split('\n')[-1]
    indention_count = 0
    for char in last_line:
        if char == ' ': indention_count += 1
        else: break
    return indention_count * ' '

def _if_new_clause_add_newline(sapi_str: str, sql_str: str, str_index_from_: int) -> bool:
    if sql_str[-1] == '\n':
        return False
    remainder = sapi_str[str_index_from_:].upper()
    common_select_clauses_str = [str(t).lstrip('TokenType.') for t in common_select_clauses()]
    for clause in common_select_clauses_str:
        if remainder.startswith(clause):
            return True
    return False

