from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
import yaml

DATA_YAML_FILE = 'data/linkways.yaml'

Location = str
Step = Dict[str, str]
Point = List[float]

class Edge:
    def __init__(self, raw_edge: Dict[str, Any]) -> None:
        endpoint1, endpoint2 = raw_edge['link']
        self.loc1: Location = endpoint1['location']
        self.floor1: int = endpoint1['floor']
        self.loc2: Location = endpoint2['location']
        self.floor2: int = endpoint2['floor']
        self.sheltered: bool = raw_edge['shelter']
        self.accessible: bool = raw_edge['accessible']
        self.description: Optional[str] = raw_edge.get('description', None)
        self.points: List[Point] = raw_edge['points']

    def get_locations(self) -> Tuple[Location, Location]:
        return self.loc1, self.loc2

    def get_other_location(self, location: Location):
        return self.loc2 if self.loc1 == location else self.loc1

    def get_floor(self, location: Location):
        return self.floor1 if self.loc1 == location else self.floor2

    def get_points(self, start_location: Location):
        return self.points if self.loc1 == start_location else self.points[::-1]

class Navigation:
    def __init__(self) -> None:
        with open(DATA_YAML_FILE, 'r') as f:
            edges: list[Edge] = [Edge(raw_edge)
                                 for raw_edge in yaml.load(f, Loader=yaml.Loader)['linkways']]
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
            accessible: bool) -> Optional[Tuple[List[Step], List[Point]]]:
        if src_location == dst_location:
            return None
        parent_edges = self._bfs(
            src_location, dst_location, sheltered, accessible)
        if parent_edges is None:
            return None
        return self._get_route_and_points(parent_edges, dst_location)

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
                    if ((sheltered and not edge.sheltered) or
                        (accessible and not edge.accessible)):
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

    def _get_route_and_points(
            self,
            parent_edges: Dict[Location, Optional[Edge]],
            dst_location: Location) -> Tuple[List[Step], List[Point]]:
        curr_location = dst_location
        edge = parent_edges[curr_location]
        route: List[Step] = []
        points: List[Point] = []
        while edge is not None:
            prev_location = edge.get_other_location(curr_location)
            route.append(self._format_step(edge, prev_location, curr_location))
            edge_points = edge.get_points(curr_location)
            if points and points[-1] == edge_points[0]:
                points.pop()
            points.extend(edge_points)
            curr_location = prev_location
            edge = parent_edges[curr_location]
        return route[::-1], points[::-1]

    def _format_step(self, edge: Edge, start_location: Location, end_location: Location) -> Step:
        description = (
            f'From {self._format_location(edge, start_location)}, ' +
            f'cross over to {self._format_location(edge, end_location)}' +
            (f' ({edge.description})' if edge.description is not None else ''))
        step = {'from': start_location, 'to': end_location, 'description': description}
        return step

    def _format_location(self, edge: Edge, location: Location) -> str:
        floor = edge.get_floor(location)
        if floor == 0:
            return location
        if floor < 0:
            return f'{location} B{abs(floor)}'
        return f'{location} L{floor}'
