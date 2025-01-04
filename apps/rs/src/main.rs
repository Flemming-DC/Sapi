use sapi_compiler;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        let result = sapi_compiler::sapi_add(2, 2);
        assert_eq!(result, 4);
    }
}


fn main() {
    let result = sapi_compiler::sapi_add(2, 2);
    println!("Hello {}", result);
}

