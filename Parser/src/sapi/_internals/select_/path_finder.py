from dataclasses import dataclass, field
from anytree import walker, Node
from sapi._internals.externals.database_py import data_model

pathType = list[tuple[Node, Node]]
@dataclass
class _PathInfo:
    path: pathType = field(default_factory=list) # = []
    nodes: list[Node] = field(default_factory=list) # = []
    eldest: Node|None = None


def join_path(table_names: list[str], first_table: str|None, tree_name: str) -> tuple[pathType, Node|None]:
    if not first_table:
        return [], None # this means that there is nothing to join. e.g. "select 1 from A"

    ordered_tabs = [first_table] + [t for t in table_names if t != first_table] 
    table_nodes = [data_model.node_by_tab_and_tree(t, tree_name) for t in ordered_tabs]# if t in node_by_table.keys()]

    pathInfo = _PathInfo()
    for tab_node in table_nodes:
        _increment_join_path(pathInfo, tab_node)
    assert not pathInfo.nodes or len(pathInfo.nodes) == len(pathInfo.path) + 1, "Expected final table count to be 0 or 1 + path length"


    return pathInfo.path, pathInfo.eldest

def _increment_join_path(pathInfo: _PathInfo, next_node: Node) -> None:
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



