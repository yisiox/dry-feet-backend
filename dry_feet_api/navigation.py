from collections import defaultdict
from typing import Any, Dict, List, Tuple
import yaml

DATA_YAML_FILE = 'data/linkways.yaml'

Node = str

class Edge:
    def __init__(self, raw_edge: Dict[str, Any]) -> None:
        self.edge = raw_edge

    def get_endpoints(self) -> Tuple[Node, Node]:
        return tuple(link_end['location'] for link_end in self.edge['link'])

class Navigation:
    def __init__(self) -> None:
        with open(DATA_YAML_FILE, 'r') as f:
            edges: list[Edge] = [Edge(raw_edge) for raw_edge in yaml.load(f)['linkways']]
            self.graph: dict[Node, list[Edge]] = defaultdict(list)
            for edge in edges:
                node1, node2 = edge.get_endpoints()
                self.graph[node1].append(edge)
                self.graph[node2].append(edge)

    def get_all_locations(self) -> List[Node]:
        return sorted(self.graph)
