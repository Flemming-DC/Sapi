use std::fmt;
use std::path::Display;

use bumpalo::Bump;
use sqlparser::tokenizer::Token;
use sqlparser::tokenizer::Whitespace;
use sqlparser::keywords;
use TokTy::*;
use super::token_tree::TokenTree;

#[derive(Debug, PartialEq, Clone, Copy)]
pub enum TokTy {
    Tree, // sapi specific token
    Generated, // sapi specific token
    EOF,
    Keyword,
    Identifier,
    Number,
    // Whitespace, 
        Space, Newline, Tab, SingleLineComment, MultiLineComment,
    Placeholder,
    CustomBinaryOperator,
    Char, // separated from text since it only contains char, not String
    // text
        SingleQuotedString, DoubleQuotedString, TripleSingleQuotedString, 
        TripleDoubleQuotedString, DollarQuotedString, SingleQuotedByteStringLiteral, 
        DoubleQuotedByteStringLiteral, TripleSingleQuotedByteStringLiteral,
        TripleDoubleQuotedByteStringLiteral, SingleQuotedRawStringLiteral, DoubleQuotedRawStringLiteral,
        TripleSingleQuotedRawStringLiteral, TripleDoubleQuotedRawStringLiteral, NationalStringLiteral,
        EscapedStringLiteral, UnicodeStringLiteral, HexStringLiteral,
    // special characters (contains no internal data)
        DoubleEq, Eq, Neq, Lt, Gt, LtEq, GtEq, Spaceship,
        Plus, Minus, Mul, Div, DuckIntDiv, Mod, StringConcat,
        LParen, RParen, LBracket, RBracket, LBrace, RBrace,
        Period, Colon, DoubleColon, Assignment, SemiColon, Backslash, Ampersand,
        Pipe, Caret, RArrow, Sharp, Tilde, TildeAsterisk,
        ExclamationMarkTilde, ExclamationMarkTildeAsterisk, DoubleTilde, 
        DoubleTildeAsterisk, ExclamationMarkDoubleTilde, ExclamationMarkDoubleTildeAsterisk,
        ShiftLeft, ShiftRight, Overlap, ExclamationMark, DoubleExclamationMark, AtSign, CaretAt, 
        PGSquareRoot, PGCubeRoot, Arrow, LongArrow, HashArrow, HashLongArrow, AtArrow, ArrowAt,
        HashMinus, AtQuestion, AtAt, Question, QuestionAnd, QuestionPipe, Comma,
}

#[derive(Debug, PartialEq, Clone)]
pub enum TokData<'a> {
    Tree(&'a TokenTree<'a>),
    Keyword(keywords::Keyword), 
    Text(String), 
    Placeholder(String), 
    CustomBinaryOperator(String), 
    MultiLineComment(String),
    Char(char),
    Number(String, bool),
    Identifier {value: String, quote_style: Option<char>},
    DollarQuotedString { value: String, tag: Option<String> },
    SingleLineComment { comment: String, prefix: String },
    None,
} 

#[derive(PartialEq, Clone)]
pub struct Location {
    pub idx: usize, // index. starting from 0.
    pub line: u64, // Line number, starting from 1. Note: Line 0 is used for empty spans
    pub column: u64, // Line column, starting from 1.Note: Column 0 is used for empty spans
}

#[derive(PartialEq, Clone)]
pub struct Tok<'a> { 
    pub typ: TokTy, 
    pub text: &'a str, 
    pub start: Location, // location could be stored out of band
    pub end: Location, // location could be stored out of band
    pub data: &'a TokData<'a>, // could be grouped as start, end, data and put behind shared ref
}

// ------------ conversion functions --------------- //

impl fmt::Debug for Location {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "L({}: {}, {})", self.idx, self.line, self.column)
    }
}
impl<'a> fmt::Debug for Tok<'a> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Tok{{{:?}, {:?}, {:?}, {:?} -> {:?}}}", self.data, self.text, self.typ, self.start, self.end)
    }
}



impl<'a> Tok<'a> { 
    pub fn keyword(&self) -> Option<keywords::Keyword> {
        match self.data {
            TokData::Keyword(kw) => Some(*kw),
            _ => None
        }
    }
    pub fn print_toks(toks: &[Tok<'a>]) { dbg!(); println!("{}", Tok::toks_str(toks)); }
    fn toks_str(toks: &[Tok<'a>]) -> String { // for debugging only
        let mut out = String::from("Toks [");
        for tok in toks {
            out += tok.text;//&format!("{:?}", tok);
            out += " ";
        }
        out = out.strip_suffix(" ").expect("it has the suffix").to_string();
        out += "]";
        return out;
    }
}




impl TokTy { 
    pub fn new(token: Token) -> TokTy {
        match token {
            Token::EOF => EOF,
            Token::Word(word) => match word.keyword {
                keywords::Keyword::NoKeyword => Identifier,
                _ => Keyword,
            },
            Token::Number(..) => Number,
            Token::Whitespace(ws) => match ws {
                Whitespace::Space => Space,
                Whitespace::Newline => Newline,
                Whitespace::Tab => Tab,
                Whitespace::SingleLineComment {..} => SingleLineComment,
                Whitespace::MultiLineComment(..) => MultiLineComment,
            }, 
            Token::Placeholder(..) => Placeholder,
            Token::CustomBinaryOperator(..) => CustomBinaryOperator,
            Token::Char(..) => Char, // separated from text since it only contains char, not String
            // text
                Token::SingleQuotedString(_) => SingleQuotedString, 
                Token::DoubleQuotedString(_) => DoubleQuotedString, 
                Token::TripleSingleQuotedString(_) => TripleSingleQuotedString, 
                Token::TripleDoubleQuotedString(_) => TripleDoubleQuotedString, 
                Token::DollarQuotedString(_) => DollarQuotedString, 
                Token::SingleQuotedByteStringLiteral(_) => SingleQuotedByteStringLiteral, 
                Token::DoubleQuotedByteStringLiteral(_) => DoubleQuotedByteStringLiteral, 
                Token::TripleSingleQuotedByteStringLiteral(_) => TripleSingleQuotedByteStringLiteral,
                Token::TripleDoubleQuotedByteStringLiteral(_) => TripleDoubleQuotedByteStringLiteral, 
                Token::SingleQuotedRawStringLiteral(_) => SingleQuotedRawStringLiteral, 
                Token::DoubleQuotedRawStringLiteral(_) => DoubleQuotedRawStringLiteral,
                Token::TripleSingleQuotedRawStringLiteral(_) => TripleSingleQuotedRawStringLiteral, 
                Token::TripleDoubleQuotedRawStringLiteral(_) => TripleDoubleQuotedRawStringLiteral, 
                Token::NationalStringLiteral(_) => NationalStringLiteral,
                Token::EscapedStringLiteral(_) => EscapedStringLiteral, 
                Token::UnicodeStringLiteral(_) => UnicodeStringLiteral, 
                Token::HexStringLiteral(_) => HexStringLiteral, 
            // special characters (contains no internal data)
                Token::DoubleEq => DoubleEq,
                Token::Eq => Eq,
                Token::Neq => Neq,
                Token::Lt => Lt,
                Token::Gt => Gt,
                Token::LtEq => LtEq,
                Token::GtEq => GtEq,
                Token::Spaceship => Spaceship,
                Token::Plus => Plus,
                Token::Minus => Minus,
                Token::Mul => Mul,
                Token::Div => Div,
                Token::DuckIntDiv => DuckIntDiv,
                Token::Mod => Mod,
                Token::StringConcat => StringConcat,
                Token::LParen => LParen,
                Token::RParen => RParen,
                Token::LBracket => LBracket,
                Token::RBracket => RBracket,
                Token::LBrace => LBrace,
                Token::RBrace => RBrace,
                Token::Period => Period,
                Token::Colon => Colon,
                Token::DoubleColon => DoubleColon,
                Token::Assignment => Assignment,
                Token::SemiColon => SemiColon,
                Token::Backslash => Backslash,
                Token::Ampersand => Ampersand,
                Token::Pipe => Pipe,
                Token::Caret => Caret,
                Token::RArrow => RArrow,
                Token::Sharp => Sharp,
                Token::Tilde => Tilde,
                Token::TildeAsterisk => TildeAsterisk,
                Token::ExclamationMarkTilde => ExclamationMarkTilde,
                Token::ExclamationMarkTildeAsterisk => ExclamationMarkTildeAsterisk,
                Token::DoubleTilde => DoubleTilde,
                Token::DoubleTildeAsterisk => DoubleTildeAsterisk,
                Token::ExclamationMarkDoubleTilde => ExclamationMarkDoubleTilde,
                Token::ExclamationMarkDoubleTildeAsterisk => ExclamationMarkDoubleTildeAsterisk,
                Token::ShiftLeft => ShiftLeft,
                Token::ShiftRight => ShiftRight,
                Token::Overlap => Overlap,
                Token::ExclamationMark => ExclamationMark,
                Token::DoubleExclamationMark => DoubleExclamationMark,
                Token::AtSign => AtSign,
                Token::CaretAt => CaretAt,
                Token::PGSquareRoot => PGSquareRoot,
                Token::PGCubeRoot => PGCubeRoot,
                Token::Arrow => Arrow,
                Token::LongArrow => LongArrow,
                Token::HashArrow => HashArrow,
                Token::HashLongArrow => HashLongArrow,
                Token::AtArrow => AtArrow,
                Token::ArrowAt => ArrowAt,
                Token::HashMinus => HashMinus,
                Token::AtQuestion => AtQuestion,
                Token::AtAt => AtAt,
                Token::Question => Question,
                Token::QuestionAnd => QuestionAnd,
                Token::QuestionPipe => QuestionPipe,
                Token::Comma => Comma,
        }
    }
}


impl<'a> TokData<'a> { 
    pub fn new(token: Token) -> TokData<'a> {
        match token {
            Token::Word(word) => match word.keyword {
                keywords::Keyword::NoKeyword => TokData::Identifier {value: word.value, quote_style: word.quote_style},
                _ => TokData::Keyword(word.keyword),
            },
            Token::Number(s, b) => TokData::Number(s, b),
            Token::Whitespace(ws) => match ws {
                Whitespace::SingleLineComment {comment: s, prefix: p} => TokData::SingleLineComment {comment: s, prefix: p},
                Whitespace::MultiLineComment(s) => TokData::MultiLineComment(s),
                _ => TokData::None,
            }, 
            Token::Placeholder(s) => TokData::Placeholder(s),
            Token::CustomBinaryOperator(s) => TokData::CustomBinaryOperator(s),
            Token::Char(c) => TokData::Char(c), // separated from text since it only contains char, not String
            // text
                Token::SingleQuotedString(s) => TokData::Text(s),
                Token::DoubleQuotedString(s) => TokData::Text(s),
                Token::TripleSingleQuotedString(s) => TokData::Text(s),
                Token::TripleDoubleQuotedString(s) => TokData::Text(s),
                Token::DollarQuotedString(s) => TokData::DollarQuotedString {value: s.value, tag: s.tag},
                Token::SingleQuotedByteStringLiteral(s) => TokData::Text(s),
                Token::DoubleQuotedByteStringLiteral(s) => TokData::Text(s),
                Token::TripleSingleQuotedByteStringLiteral(s) => TokData::Text(s),
                Token::TripleDoubleQuotedByteStringLiteral(s) => TokData::Text(s),
                Token::SingleQuotedRawStringLiteral(s) => TokData::Text(s),
                Token::DoubleQuotedRawStringLiteral(s) => TokData::Text(s),
                Token::TripleSingleQuotedRawStringLiteral(s) => TokData::Text(s),
                Token::TripleDoubleQuotedRawStringLiteral(s) => TokData::Text(s),
                Token::NationalStringLiteral(s) => TokData::Text(s),
                Token::EscapedStringLiteral(s) => TokData::Text(s),
                Token::UnicodeStringLiteral(s) => TokData::Text(s),
                Token::HexStringLiteral(s) => TokData::Text(s),
        _ => TokData::None,
    }
    }
}

