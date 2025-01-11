using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace cs
{
    class Program
    {
        
        static void Main(string[] args)
        {
            Console.WriteLine(Sapi.sapi_add(5, 10));
            Console.WriteLine(Sapi.ib_nt("Hello, World!"));
            // Console.WriteLine(Sapi.make_data_model("postgres", "[]")); // panic
        }

        public struct Sapi {
            public static int sapi_add(int a, int b) => ffi.sapi_add(a, b);
            public static string ib_nt(string x) {
                IntPtr ret;
                unsafe { fixed (char* xPtr = x) {
                    ret = (IntPtr)ffi.ib_nt(xPtr); 
                }}
                return Marshal.PtrToStringUni(ret);
            }
            public static int make_data_model(string dialect, string json_trees) {
                unsafe { fixed (char* dialectPtr = dialect, json_trees_ptr = json_trees) {
                    return ffi.make_data_model(dialectPtr, json_trees_ptr); 
                }}
            }

            public static string compile(string sapi_str, int model_id) {
                IntPtr ret;
                unsafe { fixed (char* sapi_str_ptr = sapi_str) {
                    ret = (IntPtr)ffi.compile(sapi_str_ptr, model_id); 
                }}
                return Marshal.PtrToStringUni(ret);

            }
        }


        struct ffi
        {
            const string sapi = "C:/Mine/Rust/sapi/target/debug/sapi_compiler.dll";
            // const string dll = "C:/Mine/Rust/sapi/target/release/sapi_compiler.dll";

            [DllImport(sapi)]        extern public static int sapi_add(int a, int b);
            [DllImport(sapi)] unsafe extern public static char* ib_nt(char* x);
            [DllImport(sapi)] unsafe extern public static int make_data_model(char* dialect, char* json_trees);
            [DllImport(sapi)] unsafe extern public static char* compile(char* sapi_str, int model_id);
        }

    }
}