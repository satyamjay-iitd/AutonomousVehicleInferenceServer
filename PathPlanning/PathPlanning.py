from typing import Tuple
from pyroutelib3 import Router


class PathPlanning:
    def __init__(self, map_file_path, source_coord):
        self.destination_candidates = [(156, 167), (179, 156)]
        self.selected_destination = None
        self.lroute = None
        self.rroute = None
        self.router = Router("car", map_file_path)
        self.recalculate_path(source_coord)
        self.has_reached_destination = False

    def find_path(self, source_coord, destination_node) -> bool:

        start = self.router.findTwoParallelNodes(source_coord[0], source_coord[1])  # Find start and end nodes
        # if start_node tuple and dest_node tuple are in same order
        lstatus, lr = self.router.doRoute(start[0], destination_node[0])
        rstatus, rr = self.router.doRoute(start[1], destination_node[1])

        if lstatus == 'success' and rstatus == 'success':
            self.lroute = lr
            self.rroute = rr
            return True

        # if start_node tuple and dest_node tuple are in opposite order
        lstatus, lr = self.router.doRoute(start[1], destination_node[0])
        rstatus, rr = self.router.doRoute(start[0], destination_node[1])

        if lstatus == 'success' and rstatus == 'success':
            self.lroute = lr
            self.rroute = rr
            return True

        return False

    def two_closest_nodes(self, curr_pos):
        rnext_node_coord = None
        lnext_node_coord = None
        lnext_node_id = None
        rnext_node_id = None
        min_dist = float('inf')
        for i in range(len(self.rroute) - 1):
            dist_left = PathPlanning.dist_euclidian(curr_pos, self.router.coord_from_node(self.rroute[i]))
            dist_right = PathPlanning.dist_euclidian(curr_pos, self.router.coord_from_node(self.rroute[i + 1]))
            if (dist_left + dist_right) <= min_dist:
                rnext_node_id = self.rroute[i + 1]
                lnext_node_id = self.lroute[i + 1]
                lnext_node_coord = self.router.coord_from_node(lnext_node_id)
                rnext_node_coord = self.router.coord_from_node(rnext_node_id)
                min_dist = dist_left + dist_right
        return rnext_node_coord, rnext_node_id, lnext_node_coord, lnext_node_id

    def find_next_node(self, curr_pos, signal=True):
        # If lane change then re-calculate path
        if signal:
            self.recalculate_path(curr_pos)

        next_node, next_node_id, lnext_node, lnext_node_id = self.two_closest_nodes(curr_pos)
        if next_node_id == self.selected_destination[1]:
            self.has_reached_destination = True
        else:
            self.has_reached_destination = False
        return ((-next_node[1], next_node[0]), next_node_id), ((-lnext_node[1], lnext_node[0]), lnext_node_id)

    def recalculate_path(self, source_cord):
        for d_node in self.destination_candidates:
            if self.find_path(source_cord, d_node):
                self.selected_destination = d_node
                return
        raise PathNotFoundException

    @staticmethod
    def dist_euclidian(n1: Tuple[float, float], n2: Tuple[float, float]) -> float:
        """Calculates the distance in units between two nodes as an Euclidian 2D distance"""
        dx = n1[0] - n2[0]
        dy = n1[1] - n2[1]
        return dx ** 2 + dy ** 2

    @staticmethod
    def transform_coord(coord):
        # Transforming the Unity Coordinate to ORB-Coordinate
        return coord[1], - coord[0]


class PathNotFoundException(Exception):
    pass
