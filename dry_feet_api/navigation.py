from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
import yaml

DATA_YAML_FILE = 'data/linkways.yaml'

Location = str
Step = Dict[str, str]

class Edge:
    def __init__(self, raw_edge: Dict[str, Any]) -> None:
        endpoint1, endpoint2 = raw_edge['link']
        self.loc1 = endpoint1['location']
        self.floor1 = endpoint1['floor']
        self.loc2 = endpoint2['location']
        self.floor2 = endpoint2['floor']
        self.sheltered = raw_edge['shelter']
        self.accessible = raw_edge['accessible']

    def get_locations(self) -> Tuple[Location, Location]:
        return self.loc1, self.loc2

    def get_other_location(self, location: Location):
        if self.loc1 == location:
            return self.loc2
        else:
            return self.loc1

    def get_floor(self, location: Location):
        return self.floor1 if location == self.loc1 else self.floor2

class Navigation:
    def __init__(self) -> None:
        with open(DATA_YAML_FILE, 'r') as f:
            edges: list[Edge] = [Edge(raw_edge) for raw_edge in yaml.load(f)['linkways']]
            self.graph: dict[Location, list[Edge]] = defaultdict(list)
            for edge in edges:
                location1, location2 = edge.get_locations()
                self.graph[location1].append(edge)
                self.graph[location2].append(edge)

    def get_all_locations(self) -> List[Location]:
        return sorted(self.graph)

    def find_path(
            self,
            src_location: Location,
            dst_location: Location,
            sheltered: bool,
            accessible: bool) -> Optional[List[Step]]:
        if src_location == dst_location:
            return []
        parent_edges = self._bfs(src_location, dst_location, sheltered, accessible)
        if parent_edges is None:
            return None
        return self._get_route(parent_edges, dst_location)

    def _bfs(
            self,
            src_location: Location,
            dst_location: Location,
            sheltered: bool,
            accessible: bool) -> Optional[Dict[Location, Optional[Edge]]]:

        parent_edges: Dict[Location, Optional[Edge]] = {}
        parent_edges[src_location] = None
        queue: List[Location] = [src_location]
        while queue:
            next_queue: List[Location] = []
            for location in queue:
                for edge in self.graph[location]:
                    if (sheltered and not edge.sheltered) or (accessible and not edge.accessible):
                        continue
                    next_location = edge.get_other_location(location)
                    if next_location in parent_edges:
                        continue
                    parent_edges[next_location] = edge
                    if next_location == dst_location:
                        return parent_edges
                    next_queue.append(next_location)
            queue = next_queue
        return None

    def _get_route(
            self,
            parent_edges: Dict[Location, Optional[Edge]],
            dst_location: Location) -> List[Step]:

        curr_location = dst_location
        edge = parent_edges[curr_location]
        route: List[Step] = []
        while edge is not None:
            prev_location = edge.get_other_location(curr_location)
            route.append(self._format_step(edge, prev_location, curr_location))
            curr_location = prev_location
            edge = parent_edges[curr_location]
        return route[::-1]

    def _format_step(self, edge: Edge, start_location: Location, end_location: Location) -> Step:
        description = (
            f'From {self._format_location(edge, start_location)}, ' +
            f'cross over to {self._format_location(edge, end_location)}')
        step = {'from': start_location, 'to': end_location, 'description': description}
        return step

    def _format_location(self, edge: Edge, location: Location) -> str:
        floor = edge.get_floor(location)
        if floor == 0:
            return location
        if floor < 0:
            return f'{location} B{abs(floor)}'
        return f'{location} L{floor}'
