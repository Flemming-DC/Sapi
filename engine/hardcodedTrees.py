from anytree import Node

# dublicate names must be resolved. either here or later
table_by_var = {
    'a_1'  : 'a',
    'a_2'  : 'a',
    'a0_1' : 'a0',
    'a0_2' : 'a0',
    'a1_1' : 'a1',
    'a1_2' : 'a1',
    'a2_1' : 'a2',
    'a2_2' : 'a2',
    'a00_1': 'a00',
    'a00_2': 'a00',
    'a01_1': 'a01',
    'a01_2': 'a01',
    'a10_1': 'a10',
    'a10_2': 'a10',
    'a20_1': 'a20',
    'a20_2': 'a20',
    'a21_1': 'a21',
    'a21_2': 'a21',
    'b_1'  : 'b',
    'b_2'  : 'b',
    'b0_1' : 'b0',
    'b0_2' : 'b0',
    'b1_1' : 'b1',
    'b1_2' : 'b1',
    }
# table_by_var = {k.lower(): v.lower() for k, v in table_by_var}

class V:
    a_1: str   = 'a_1'
    a_2: str   = 'a_2'
    a0_1: str  = 'a0_1'
    a0_2: str  = 'a0_2'
    a1_1: str  = 'a1_1'
    a1_2: str  = 'a1_2'
    a2_1: str  = 'a2_1'
    a2_2: str  = 'a2_2'
    a00_1: str = 'a00_1'
    a00_2: str = 'a00_2'
    a01_1: str = 'a01_1'
    a01_2: str = 'a01_2'
    a10_1: str = 'a10_1'
    a10_2: str = 'a10_2'
    a20_1: str = 'a20_1'
    a20_2: str = 'a20_2'
    a21_1: str = 'a21_1'
    a21_2: str = 'a21_2'
    b_1: str   = 'b_1'
    b_2: str   = 'b_2'
    b0_1: str  = 'b0_1'
    b0_2: str  = 'b0_2'
    b1_1: str  = 'b1_1'
    b1_2: str  = 'b1_2'
# vars = list(V.model_fields.keys()) # works for V being a BaseModel

class A:
    n   = Node('a',   parent=None, vars=[V.a_1, V.a_2])
    n0  = Node('a0',  parent=n   , vars=[V.a0_1, V.a0_2])
    n1  = Node('a1',  parent=n   , vars=[V.a1_1, V.a1_2])
    n2  = Node('a2',  parent=n   , vars=[V.a2_1, V.a2_2])
    n00 = Node('a00', parent=n0  , vars=[V.a00_1, V.a00_2])
    n01 = Node('a01', parent=n0  , vars=[V.a01_1, V.a01_2])
    n10 = Node('a10', parent=n1  , vars=[V.a10_1, V.a10_2])
    n20 = Node('a20', parent=n2  , vars=[V.a20_1, V.a20_2])
    n21 = Node('a21', parent=n2  , vars=[V.a21_1, V.a21_2])

class B:
    n   = Node('b',   parent=None, vars=[V.b_1, V.b_2])
    n0  = Node('b0',  parent=n   , vars=[V.b0_1, V.b0_2])
    n1  = Node('b1',  parent=n   , vars=[V.b1_1, V.b1_2])

node_by_table = {
    'a':   A.n,
    'a0':  A.n0,
    'a1':  A.n1,
    'a2':  A.n2,
    'a00': A.n00,
    'a01': A.n01,
    'a10': A.n10,
    'a20': A.n20,
    'a21': A.n21,
    'b':   B.n,
    'b0':  B.n0,
    'b1':  B.n1,
}
# node_by_table = {k.lower(): v for k, v in node_by_table}

table_trees = ['A', 'B']
