use std::ffi::{CStr, CString};
use std::{str, usize};
use std::os::raw::{c_char, c_uchar, c_uint};
use super::db_contact::deployment::Cursor;
use super::compiler;
use super::DataModel;

#[repr(C)] #[allow(non_camel_case_types)] pub struct c_str {ptr: *const c_char, len: u32}
struct MD {id: u32} // temp



#[no_mangle] pub extern "C" 
fn compile(sapi_str: *const c_char, model_id: u32) -> *const c_char {
    // &parser::parse(sapi_str, DataModel::from_id(model_id))
    // c_str {ptr: "".as_ptr(), len: 0}
    let sapi_str = unsafe { CStr::from_ptr(sapi_str) };
    let s = sapi_str.to_str().unwrap();
    // let sapi_str = String::from_utf8(???).unwrap().to_string();
    // let sapi_str = String::from_utf8_lossy(sapi_str.to_bytes()).to_string();
    let md = MD { id: model_id }; 
    // call compiler::compile / parser::parse
    let sql_str = String::from(""); // temp
    let sql_str = CString::new(sql_str).unwrap();
    sql_str.as_ptr()
}


// --------- DateModel --------- //
#[no_mangle] pub extern "C" 
fn load_data_model(dialect: c_str, sys_schema: c_str, connection_str: c_str) -> u32 {
    // async ?
    // connection_str vs cursor?
    0 // model_id
}
#[no_mangle] pub extern "C" 
fn make_data_model(dialect: c_str, json_trees: c_str) -> u32 {
    // let deserialized: DataModel = serde_json::from_str(&serialized)
    0 // model_id
}
#[no_mangle] pub extern "C" 
fn free_data_model(model_id: u32) { } // leave a hole behind in the list of dm's

// --------- AutoGen --------- //
// evt. return generated sql or perhaps just the keys
#[no_mangle] pub extern "C" fn insert(json_data: c_str, model_id: u32) { } 
#[no_mangle] pub extern "C" fn update(json_data: c_str, model_id: u32) { }
// delete can by handled by `cascade`, `cascade upon table-list` or `delete from subtree` 



