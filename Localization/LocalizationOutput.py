import json
from dataclasses import dataclass
from typing import Tuple


@dataclass
class LocalizationOutput:
    curr_pos: Tuple[float, float] = (-1.0, -1.0)
    next_node_r: Tuple[float, float] = (-1.0, -1.0)
    next_node_l: Tuple[float, float] = (-1.0, -1.0)
    has_reached_destination: bool = False

    def __dict__(self):
        d = {
            'CurrPosX': self.curr_pos[0],
            'CurrPosY': self.curr_pos[1],
            'NextNodeRX': self.next_node_r[0],
            'NextNodeRY': self.next_node_r[1],
            'NextNodeLX': self.next_node_l[0],
            'NextNodeLY': self.next_node_l[1],
            'HasReached': self.has_reached_destination
        }
        return d

    def __str__(self):
        return json.dumps(self.__dict__())
