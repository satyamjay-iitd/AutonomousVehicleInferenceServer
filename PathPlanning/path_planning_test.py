import unittest
from PathPlanning import PathPlanning

class PathPlanningTest(unittest.TestCase):
    def test_closet(self):
        path_planning = PathPlanning("/home/janib/Downloads/Editor/AutonomousDriving-Refactored/Inference_Server/map.osm", None, None)
        assert path_planning.find_next_node((1313.468, 337.8259))[1] == 30
        assert path_planning.find_next_node((1311.05, 335.72))[1] == 30
        assert path_planning.find_next_node((1283.45, 345.92))[1] in [34, 35, 36, 37]

if __name__ == '__main__':
    unittest.main(verbosity=2)
