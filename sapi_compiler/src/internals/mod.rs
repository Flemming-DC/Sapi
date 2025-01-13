
// from sapi._internals.parser import parse
// from sapi._internals.insert.insert_generator import insert_into_tree
// from sapi._internals.db_contact import dialect
// from sapi._internals.db_contact.deployment import setup_sapi
// from sapi._internals.db_contact.data_model import DataModel #, Tree, Table
// from sapi._internals.execution import Transaction, read, QueryResult, Database, CommitPolicy
// # The (Tree, Table) approach to making a datamodel isnt very user friendly right now. 
// # if it becomes user friendly, then expose it.

// from sapi import _editor # only for use by Sapi Editor
// from sapi import _test # only for use by Sapi AutoTests

pub mod tools;
pub mod ffi;
pub mod compiler;
pub use tools::*;
pub use db_contact::DataModel;
pub use db_contact::data_model::{Table, Tree}; // temp

mod tokenizer;
mod token_tree;
mod error;
mod generate_sql_str;
mod select;
mod db_contact;
mod token;

