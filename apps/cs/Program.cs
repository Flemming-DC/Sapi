using System;
using System.Runtime.InteropServices;

namespace cs
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine(sapi_add(5, 10));
        }

        [DllImport("C:/Mine/Rust/sapi/target/debug/sapi_compiler.dll")]
        // [DllImport("C:/Mine/Rust/sapi/target/release/sapi_compiler.dll")]
        static extern int sapi_add(int a, int b);
    }
}
