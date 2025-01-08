use sqlparser::{keywords::Keyword, tokenizer::Token};
use crate::internals::token_tree::{tok_text, TokNode, TokenTree}; // , Token, TokenType

pub struct AnalyzerLoop<'a> {
    token_tree: &'a TokenTree<'a>,
    i: isize, // index = token_index, not sapi_str index
    count: usize,
    breakpoint_index: Option<usize>,
}

impl<'a> AnalyzerLoop<'a> {
    pub fn new(token_tree: &'a TokenTree<'a>) -> Self {
        AnalyzerLoop {
            token_tree: token_tree,
            // tokens: token_tree.tokens // could be eliminated in favor of self._token_tree.tokens
            i: 0 - 1, // index = token_index, not sapi_str index (it starts with one less than the value at the first step)
            count: token_tree.tokens.len(),
            breakpoint_index: None,
        }
    }
    pub fn tok(&self) -> &TokNode { &self.token_tree.tokens[self.i as usize] }

    
    pub fn peek(&self, distance: isize) -> Option<&TokNode> {
        let index = self.i + distance;
        if index < 0 || index as usize >= self.count {
            return None; }
        return Some(&self.token_tree.tokens[index as usize]);
    }
    
    pub fn next(&mut self) -> bool {
        // Step to next element and return true, if a next element was found
        self.i += 1;
        if self.i as usize >= self.count {
            return false; }
        if self.breakpoint_index != None && Some(self.i as usize) >= self.breakpoint_index {
            unsafe { std::arch::asm!("int3"); } } // this triggers a breakpoint 
            self.breakpoint_index = None;
        return true;
    }
    
    pub fn found(&self, token_types: &[Token], after_steps: isize) -> bool {
        // Checks for tokenType after presicely the specified number of steps.
        let index = self.i + after_steps;
        if index < 0 || index as usize >= self.count {
            return false; }
        // token_types = if isinstance(tokenType, list) {tokenType}  else {[tokenType]};
        match &self.token_tree.tokens[index as usize] {
            TokNode::Tree(_) => { return false; }
            TokNode::Leaf(tok) => { return matches!(tok, token_types); }
        }
    }
    pub fn found_kw(&self, keywords: &[Keyword], after_steps: isize) -> bool {
        // Checks for tokenType after presicely the specified number of steps.
        let index = self.i + after_steps;
        if index < 0 || index as usize >= self.count {
            return false; }
        // token_types = if isinstance(tokenType, list) {tokenType}  else {[tokenType]};
        if let TokNode::Leaf(Token::Word(word)) = self.tok() { 
            return keywords.contains(&word.keyword) }
        else { 
            return false;}
    }

    // if let TokNode::Leaf(Token::Word(word)) = tok { 
    
    pub fn index(&self) -> isize { self.i }

    pub fn at_end(&self) -> bool { self.i as usize >= self.count }
    pub fn next_at_end(&self) -> bool { self.i as usize + 1 >= self.count }

    pub fn has_passed(&self, stopping_obj: &str) -> bool {
        // Meant for debugging
        return self.at_end() || self.view(None, Some(0)).contains(stopping_obj) // self._token_tree.has_passed(stopping_obj, self.tok().start)
    }   

    pub fn view(&self, from_: Option<isize>, to: Option<isize>) -> String {
        // Meant for debugging
        let from_ =  if from_ != None {(from_.expect("already checked") + self.i) as usize} else {0};
        let to = if to != None {(to.expect("already checked") + self.i) as usize} else {self.token_tree.tokens.len() - 1};
        
        let mut out = String::from("");
        for t in &self.token_tree.tokens[from_..to]{
            out += t.text();
            out += " ";
        }
        return out;
    }
}





