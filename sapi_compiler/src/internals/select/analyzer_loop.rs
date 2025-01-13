use std::{cell::Cell, hint::black_box};

use sqlparser::{keywords::Keyword, tokenizer::Token};
use crate::{brk, brk_if, internals::{token::{Tok, TokTy}, token_tree::TokenTree}, P}; // , Token, TokenType

pub struct AnalyzerLoop<'a> {
    token_tree: &'a TokenTree<'a>,
    i: Cell<isize>, // index = token_index, not sapi_str index
    count: usize,
    breakpoint_index: Cell<Option<usize>>,
}

impl<'a> AnalyzerLoop<'a> {
    pub fn new(token_tree: &'a TokenTree<'a>) -> Self {
        AnalyzerLoop {
            token_tree: token_tree,
            // tokens: token_tree.tokens // could be eliminated in favor of self._token_tree.tokens
            i: Cell::new(0 - 1), // index = token_index, not sapi_str index (it starts with one less than the value at the first step)
            count: token_tree.tokens.len(),
            breakpoint_index: Cell::new(None),
        }
    }
    pub fn tok(&self) -> &Tok { 
        &self.token_tree.tokens[self.i.get() as usize] }
        
    
    pub fn peek(&self, distance: isize) -> Option<&Tok> {
        let index = self.i.get() + distance;
        if index < 0 || index as usize >= self.count {
            return None; }
        return Some(&self.token_tree.tokens[index as usize]);
    }
    
    pub fn next(&self) -> bool {
        // Step to next element and return true, if a next element was found
        self.i.set(self.i.get() + 1);
        if self.i.get() as usize >= self.count {
            return false; 
        }
        if self.breakpoint_index.get() != None && Some(self.i.get() as usize) >= self.breakpoint_index.get() {
            brk!();
            self.breakpoint_index.set(None);}
        return true;
    }
    
    pub fn found(&self, token_types: &[TokTy], after_steps: isize) -> bool {
        // Checks for tokenType after presicely the specified number of steps.
        let index = self.i.get() + after_steps;
        if index < 0 || index as usize >= self.count {
            return false; }
        return matches!(&self.token_tree.tokens[index as usize], token_types);
    }
    pub fn found_kw(&self, keywords: &[Keyword], after_steps: isize) -> bool {
        // Checks for tokenType after presicely the specified number of steps.
        let index = self.i.get() + after_steps;
        if index < 0 || index as usize >= self.count {
            return false; 
        }
        return matches!(self.tok().keyword(), Some(keywords));
    }

    // if let Tok::Leaf(Token::Word(word)) = tok { 
    
    pub fn index(&self) -> isize { self.i.get() }

    pub fn at_end(&self) -> bool { self.i.get() as usize >= self.count }
    pub fn next_at_end(&self) -> bool { self.i.get() as usize + 1 >= self.count }

    #[cfg(debug_assertions)] pub fn has_passed(&self, stopping_obj: &str) -> bool {
        // Meant for debugging
        return self.at_end() || self.view_abs(0, self.i.get() as usize).contains(stopping_obj) // self._token_tree.has_passed(stopping_obj, self.tok().start)
    }   

    #[cfg(debug_assertions)] pub fn view_abs(&self, from_: usize, to: usize) -> String { // Meant for debugging
        let from_ =  from_.clamp(0, self.token_tree.tokens.len());
        let to =  to.clamp(0, self.token_tree.tokens.len());
        
        let mut out = String::from("");
        for t in &self.token_tree.tokens[from_..to]{
            out += t.text;
            out += " ";
        }
        return out;
    }
    #[cfg(debug_assertions)] pub fn view_rel(&self, from_: isize, to: isize) -> String {
        let from_ = (from_ + self.i.get()).clamp(0, self.token_tree.tokens.len() as isize) as usize;
        let to =  (to + self.i.get()).clamp(0, self.token_tree.tokens.len() as isize) as usize;
        
        let mut out = String::from("");
        for t in &self.token_tree.tokens[from_..to]{
            out += t.text;
            out += " ";
        }
        return out;
    }
}





