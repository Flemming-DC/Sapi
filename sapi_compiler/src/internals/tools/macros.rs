
/// this is a geinue debug_assert. As opposed to the builtin BS that uses an if check in release build.
#[macro_export] macro_rules! dbg_assert { 
    ($($arg:tt)*) => {
        #[cfg(debug_assertions)] assert!($($arg)*);
    };
}
// macro_rules! if_dbg {
//     ($($arg:tt)*) => {
//         #[cfg(debug_assertions)] $($arg)*;
//     };
// }

#[macro_export] macro_rules! brk { 
    () => {
        #[cfg(debug_assertions)] black_box(unsafe { std::arch::asm!("int3"); });
    };
}

#[macro_export] macro_rules! brk_if { 
    ($condition:expr) => {
        #[cfg(debug_assertions)] if $condition { black_box(unsafe { std::arch::asm!("int3"); }) };
    };
}


#[cfg(debug_assertions)]
#[macro_export] macro_rules! Q {
    // Cupy paste of dbg! with minor canges. 
    // (1) Verbose formatting is replaced with compact formatting.
    // (2) 
    // --------------------------------
    // NOTE: We cannot use `concat!` to make a static string as a format argument
    // of `eprintln!` because `file!` could contain a `{` or
    // `$val` expression could be a block (`{ .. }`), in which case the `eprintln!`
    // will be malformed.
    () => {
        eprintln!("[{}:{}:{}]", std::file!(), std::line!(), std::column!())
    };
    ($val:expr $(,)?) => {
        // Use of `match` here is intentional because it affects the lifetimes
        // of temporaries - https://stackoverflow.com/a/48732525/1063961
        match $val {
            tmp => {
                eprintln!("[{}:{}:{}] {} = {:#?}",
                    std::file!(), std::line!(), std::column!(), std::stringify!($val), &tmp);
                tmp
            }
        }
    };
    // ($($val:expr),+ $(,)?) => {
    //     ($($crate::Q!($val)),+,)
    // };
    ($first:expr $(, $rest:expr)*) => {
        match $first {
            tmp => {
                eprintln!("[{}:{}:{}] {} = {:#?}",
                    std::file!(), std::line!(), std::column!(), std::stringify!($first), &tmp);
                // tmp
            }
        }

        ($(match $rest {
            tmp => {
                let prefix = format!("[{}:{}:{}] ", std::file!(), std::line!(), std::column!());
                let blanks = " ".repeat(prefix.len());
                eprintln!("{}{} = {:?}",
                blanks, std::stringify!($rest), &tmp);
                tmp
            }
        }),+,)
    };
}



