from dataclasses import dataclass, field
from anytree import RenderTree, walker, Node
from engine.hardcodedTrees import A
from .join_data import JoinData
from engine.hardcodedTrees import node_by_table

pathType = list[tuple[Node, Node]]
@dataclass
class PathInfo: # eva. make this a basemodel. If so then replace Node with PydanticNode
    path: pathType = field(default_factory=list) # = []
    nodes: list[Node] = field(default_factory=list) # = []
    eldest: Node|None = None


def join_path(table_names: list[str], first_table: str|None) -> PathInfo:


    table_nodes = [node_by_table[first_table]] if first_table else []
    table_nodes += [node_by_table[t] for t in table_names if t in node_by_table.keys() and t != first_table]

    pathInfo = PathInfo()
    for tab_node in table_nodes:
        _increment_join_path(pathInfo, tab_node)
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



