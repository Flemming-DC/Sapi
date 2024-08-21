from dataclasses import dataclass, field
from anytree import RenderTree, walker, Node
from engine.hardcodedTrees import A
from .join_data import JoinData

pathType = list[tuple[Node, Node]]
@dataclass
class PathInfo: # eva. make this a basemodel. If so then replace Node with PydanticNode
    path: pathType = field(default_factory=list) # = []
    nodes: list[Node] = field(default_factory=list) # = []
    eldest: Node|None = None


def join_path(table_nodes: list[Node]) -> PathInfo:
    pathInfo = PathInfo()
    for node in table_nodes:
        _increment_join_path(pathInfo, node)
    assert not pathInfo.nodes or len(pathInfo.nodes) == len(pathInfo.path) + 1, "Expected final table count to be 0 or 1 + path length"
    return pathInfo

def _increment_join_path(pathInfo: PathInfo, next_node: Node) -> None:
    if pathInfo.nodes == []:
        pathInfo.nodes.append(next_node)
        pathInfo.eldest = next_node
        # we don't init path, since len(path) == len(nodes) - 1 == 0
        return
    assert pathInfo.nodes and pathInfo.eldest, "missing values"

    upwards, top, downwards = walker.Walker.walk(pathInfo.eldest, next_node)
    walk_path = upwards + (top,) + downwards
    pathInfo.eldest = top
    
    previous = None # the first node in the walk_path is in pathInfo.nodes, so it doesn't need a previous node
    for n in walk_path: 
        if n not in pathInfo.nodes:
            pathInfo.nodes.append(n)
            pathInfo.path.append((previous, n))
        previous = n

if __name__ == '__main__':
    nodes = [A.n00, A.n0, A.n1, A.n20]
    expected_answer = [
        (A.n00, A.n0),
        (A.n0, A.n),
        (A.n, A.n1),
        (A.n, A.n2),
        (A.n2, A.n20),
        ]
    print(RenderTree(A.n))
    
    path = join_path(nodes)
    print('path:')
    for from_, to_ in path.path:
        print(f"    {from_.name}, {to_.name}")

    assert expected_answer == path, "unexpected answer"

