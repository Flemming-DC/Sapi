import ctypes as c
from dataclasses import dataclass

# fn compile(sapi_str: *const c_char, model_id: usize) -> *const c_char {
# fn make_data_model(dialect: *const c_char, json_trees: *const c_char) -> usize {

# sapi_str = """
#         WITH cte AS (
#             SELECT col0_1, col0_2, col00_2 FROM tree
#         )
#         SELECT 
#             cte.col00_2,
#             col10_2,
#             (SELECT count(col20_2) FROM tree)
#         --FROM tree
#         --join cte ON tree.col_1 = cte.col0_1
#         FROM cte 
#         join tree ON tree.col_1 = cte.col0_1
#     """

def _to_c(s: str): return c.c_char_p(s.encode('utf-8'))
def _to_py(s: c.c_char_p): 
    if s is None: raise Exception("Null pointer encountered from ffi.")
    return s.decode('utf-8') 

_dll = c.cdll.LoadLibrary("C:/Mine/Rust/sapi/target/debug/sapi_compiler.dll")


_dll.sapi_add.argtypes = [c.c_uint64, c.c_uint64]
_dll.sapi_add.restype = c.c_uint64
def sapi_add(x: int, y: int) -> int: 
    return _dll.sapi_add(x, y)

_dll.ib_nt.argtypes = [c.c_char_p]
_dll.ib_nt.restype = c.c_char_p
def ib_nt(x: str) -> str: 
    return _to_py(_dll.ib_nt(_to_c(x)))


result = sapi_add(10, 1)
print(f"sapi_add: {result}")

result = ib_nt("hello, c")
print(f"ib_nt: {result}")

