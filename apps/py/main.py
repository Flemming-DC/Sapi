import ctypes as c

mydll = c.cdll.LoadLibrary("C:/Mine/Rust/sapi/target/debug/sapi_compiler.dll")
result = mydll.sapi_add(10, 1)
print(f"Addition value: {result}")


