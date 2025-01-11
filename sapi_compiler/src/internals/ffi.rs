use std::ffi::{CStr, CString};
use std::{str, usize};
use std::os::raw::{c_char, c_uchar, c_uint};
use super::db_contact::deployment::Cursor;
use super::{compiler, Tree};
use super::DataModel;

#[repr(C)] #[allow(non_camel_case_types)] pub struct c_str {ptr: *const c_char, len: u32}
// struct MD {id: u32} // temp


#[no_mangle] pub extern "C" 
fn compile(sapi_str: *const c_char, model_id: usize) -> *const c_char {
    to_c_str(&compiler::compile(to_rust_str(sapi_str), model_id))
}


// --------- DateModel --------- //
// #[no_mangle] pub extern "C" 
// fn load_data_model(dialect: c_str, sys_schema: c_str, connection_str: c_str) -> u32 {
//     // async ?
//     // connection_str vs cursor?
//     0 // model_id
// }
#[no_mangle] pub extern "C" 
fn make_data_model(dialect: *const c_char, json_trees: *const c_char) -> usize {
    let dialect = to_rust_str(dialect);
    let json_trees = to_rust_str(json_trees);
    let trees: Vec<Tree> = serde_json::from_str(&json_trees).unwrap(); // fixme
    let model_id = DataModel::new(dialect, trees);
    model_id
}
// #[no_mangle] pub extern "C" 
// fn free_data_model(model_id: u32) { } // leave a hole behind in the list of dm's

// --------- AutoGen --------- //
// evt. return generated sql or perhaps just the keys
// #[no_mangle] pub extern "C" fn insert(json_data: c_str, model_id: u32) { } 
// #[no_mangle] pub extern "C" fn update(json_data: c_str, model_id: u32) { }
// delete can by handled by `cascade`, `cascade upon table-list` or `delete from subtree` 


// ---------Helpers --------- //

fn to_rust_str(s: *const c_char) -> &'static str { // really 'static ?
    dbg!(&s);
    let s = unsafe { CStr::from_ptr(s) };
    s.to_str().unwrap()
}

fn to_c_str(s: &str) -> *const c_char {
    let s = CString::new(s).unwrap();
    let s = s.as_ptr();
    dbg!(&s);
    s
}




// #[no_mangle] pub extern "C" 
// fn compile(sapi_str: *const c_char, model_id: usize) -> *const c_char {
//     // &parser::parse(sapi_str, DataModel::from_id(model_id))
//     // c_str {ptr: "".as_ptr(), len: 0}
//     let sapi_str = unsafe { CStr::from_ptr(sapi_str) };
//     let sapi_str = sapi_str.to_str().unwrap();
//     // let sapi_str = String::from_utf8(???).unwrap().to_string();
//     // let sapi_str = String::from_utf8_lossy(sapi_str.to_bytes()).to_string();
//     // let md = MD { id: model_id }; 
//     let sql_str = compiler::compile(sapi_str, model_id);
//     // let sql_str = String::from(""); // temp
//     let sql_str = CString::new(sql_str).unwrap();
//     sql_str.as_ptr()
// }

