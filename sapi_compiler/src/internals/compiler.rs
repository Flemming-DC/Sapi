use std::array;
use bumpalo::Bump;
use bumpalo::collections::Vec as bVec;
use sqlparser::keywords::Keyword;
use sqlparser::tokenizer::Token;
use crate::internals::db_contact::DataModel;
use super::token::TokData;
use super::{tokenizer, select, db_contact};
use super::token_tree::*;

// mod sealed {
//     pub trait Outputs {}
//     impl Outputs for String {}
//     impl Outputs for Vec<String> {}
//     // impl Sealed for Vec<Vec<StrReplacement>> {}
// }

// pub fn parse<T: sealed::Outputs>(sapi_str: String, model: &DataModel) -> T {

// }


pub fn compile<'a>(sapi_str: &str, model_id: usize) -> String {
    let bump = Bump::new();
    let model = DataModel::get_model_copy(&bump, model_id);

    let statements: Vec<&str> = sapi_str.split(';').map(|s| s.trim()).collect();
    let mut sql_tok_trees_str: bVec<&str> = bVec::with_capacity_in(statements.len(), &bump);
    let mut replacements: bVec<bVec<StrReplacement>> = bVec::with_capacity_in(statements.len(), &bump);
    for stmt in statements {
        if let Some(sapi_tok_tree) = tokenizer::tokenize(&bump, model.dialect(), stmt) {
            let (sql, str_replacements) = compile_token_tree(&bump, model, stmt, sapi_tok_tree);
            sql_tok_trees_str.push(sql);
            replacements.push(str_replacements); // unused for all but one return type
        }
    }

    // find a solution for multiple return types
    sql_tok_trees_str.join("\n;\n")
}



fn compile_token_tree<'a>(bump: &'a Bump, model: &DataModel, sapi_stmt: &'a str, token_tree: &'a TokenTree<'a>) -> (&'a str, bVec<'a, StrReplacement<'a>>) {
    // Parse sapi TokenTree to sql TokenTree.
    // parse sub_trees
    for tok in &token_tree.tokens {
        if let TokData::Tree(tt) = tok.data { 
            compile_token_tree(&bump, &model, sapi_stmt, tt);
        }
    }
    // parse leaves
    let sql: &str = sapi_stmt; // copy ??
    let mut replacements = bVec::new_in(&bump);
    for tok in &token_tree.tokens {
        if let Some(keyword) = tok.keyword() { 
            match keyword {
                Keyword::SELECT => {
                    replacements = select::compile_select(bump, model, &token_tree, &sapi_stmt); // this only changes the leaf tokens
                    // sql = generate_sql_str::make_str(sapi_stmt, replacements);
                    break;
                }
                Keyword::INSERT => {
                    // sql_ = insert_parser::parse_insert(token_tree.tokens); // this only changes the leaf tokens
                    // sql = if sql_ { sql_ } else { sapi_stmt };
                    break;
                }
                Keyword::UPDATE | Keyword::DELETE | Keyword::CREATE | Keyword::ALTER | Keyword::DROP => {
                    eprint!(r"WARNING: {:?} is not yet implemented.
                        Sapi will ignore such inputs and pass them to sql unchanged.", keyword);
                    break;
                } 
                _ => { }
                
            }
                
        };
    };

    (sql, replacements)



}

