from anytree import AnyNode, RenderTree, Node

# root = AnyNode(id="root")
# s0   = AnyNode(id="sub0", parent=root)
# s0b  = AnyNode(id="sub0B", parent=s0, foo=4, bar=109)
# s0a  = AnyNode(id="sub0A", parent=s0)
# s1   = AnyNode(id="sub1", parent=root)
# s1a  = AnyNode(id="sub1A", parent=s1)
# s1b  = AnyNode(id="sub1B", parent=s1, bar=8)
# s1c  = AnyNode(id="sub1C", parent=s1)
# s1ca = AnyNode(id="sub1Ca", parent=s1c)

root = Node(name="root")
s0   = Node(name="sub0")
s0b  = Node(name="sub0B")
s0a  = Node(name="sub0A")
s1   = Node(name="sub1")
s1a  = Node(name="sub1A")
s1b  = Node(name="sub1B")
s1c  = Node(name="sub1C")
s1ca = Node(name="sub1Ca")

root.parent = None
s0.parent = root
s0b.parent = s0
s0a.parent = s0
s1.parent = root
s1a.parent = s1
s1b.parent = s1
s1c.parent = s1
s1ca.parent = s1c



# root
# AnyNode(id='root')
# s0
# AnyNode(id='sub0')
print(RenderTree(root))
# AnyNode(id='root')
# ├── AnyNode(id='sub0')
# │   ├── AnyNode(bar=109, foo=4, id='sub0B')
# │   └── AnyNode(id='sub0A')
# └── AnyNode(id='sub1')
#     ├── AnyNode(id='sub1A')
#     ├── AnyNode(bar=8, id='sub1B')
#     └── AnyNode(id='sub1C')
#         └── AnyNode(id='sub1Ca')







