use super::token_tree::StrReplacement; // , common_select_clauses
use bumpalo::{collections::String as bString, Bump};


pub fn make_str<'a>(bump: &'a Bump, sapi_str: &'a str, str_replacements: &'a mut [StrReplacement]) -> bString<'a> {
    if str_replacements.is_empty() { return bString::from_str_in(sapi_str, bump); }

    // make string
    // sql_str is on the form: 
    //   sapi-segment + replacement +
    //   ...
    //   sapi-segment + replacement +
    //   sapi-segment 
    let mut sql_str = bString::with_capacity_in(sapi_str.len(), bump);
    str_replacements.sort_by_key(|r| r.str_from);
    for (i, rep) in str_replacements.iter().enumerate() {
        let last_rep_to = if i > 0 {str_replacements[i - 1].str_to} else {0}; // helper-data
        sql_str += &sapi_str[last_rep_to..rep.str_from];                // appending a sapi-segment
        sql_str = add_token_str2(sql_str, rep.text, rep.is_new_clause);   // appending a token of replacement
        if if_new_clause_add_newline(sapi_str, &sql_str, rep.str_from) {
            sql_str += "\n";}
    }
    let last_rep_to = str_replacements.last().expect("checked").str_to;
    sql_str += &sapi_str[last_rep_to..];
    return sql_str; // + '\n;'
}



fn add_token_str2<'a>(so_far: bString<'a>, text: &'a str, is_join_clause: bool) -> bString<'a> {
    so_far
    // let no_space_prefix = [")", "]", "}", ".", ","];
    // let no_space_suffix = ["(", "[", "{", "."     ];

    // if is_join_clause {
    //     so_far = so_far.trim_end(" \n"); // remove uncontrolled whitespace and newline
    //     so_far += "\n" + last_indention(so_far); // add newline and preserve indention
    //     return so_far + text;
    // }
    // else if so_far != "" && no_space_suffix.contains(so_far.last()) { // previous has have no space suffix
    //     return so_far.trim_end(' ') + text; }
    // else if no_space_prefix.contains(text) {
    //     return so_far.trim_end(' ') + text; }
    // else {
    //     return (if so_far.ends_with(' ') {so_far} else {so_far + " "}) + text; }
}

fn last_indention(s: &str) -> String {
    let last_line = s.split('\n').last();
    if last_line == None { return "".into(); }
    let mut indention_count = 0;
    for char in last_line.expect("checked").chars() {
        if char == ' ' {indention_count += 1;} else {break};
    }
    return " ".repeat(indention_count);
}
fn if_new_clause_add_newline(sapi_str: &str, sql_str: &str, str_index_from_: usize) -> bool {
    if sql_str.chars().last() == None || sql_str.chars().last() == Some('\n') {
        return false; }
    let remainder = sapi_str[str_index_from_..].to_ascii_uppercase();
    let common_select_clauses_str = [""];//[str(t).lstrip("TokenType.") for t in common_select_clauses()]; // fix me!
    assert!(false, "fix common_select_clauses_str");
    for clause in common_select_clauses_str {
        if remainder.starts_with(clause) {
            return true;}}
    return false;
}
