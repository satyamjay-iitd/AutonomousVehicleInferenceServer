import logging
import numpy as np

from Common.SensorReceiver import SensorReceiver
from Localization.LocalizationOutput import LocalizationOutput
from IPC import LocalizationIPC
from PathPlanning import PathPlanning


class GPSLocalizationProcess(SensorReceiver):

    def __init__(self, logger: logging.Logger, map_file_path: str):
        super().__init__(logger)
        LocalizationIPC.init_ipc()
        # self.path_planning = PathPlanning.PathPlanning(map_file_path)
        source_coord = PathPlanning.PathPlanning.transform_coord((1280, 365))
        self.path_planning = PathPlanning.PathPlanning(map_file_path, source_coord)
        # self.__next_position: LocalizationOutput = LocalizationOutput()

    def process_data(self, curr_pos: np.array) -> None:
        """
        :return: Returns nothing just sets the __position
        """
        if not LocalizationIPC.is_output_ready():
            transformed_curr_pos = PathPlanning.PathPlanning.transform_coord(curr_pos)
            next_node_r, next_node_l = self.path_planning.find_next_node(transformed_curr_pos)
            self.__next_position = LocalizationOutput((curr_pos[0], curr_pos[1]), next_node_r[0], next_node_l[0],
                                                      self.path_planning.has_reached_destination)

    def read_data(self) -> np.array:
        # If output has been consumed by Unity
        
        if not LocalizationIPC.is_output_ready():
            xy_coord = np.array(LocalizationIPC.read_data())
            return xy_coord
        return None

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        LocalizationIPC.write_output(bytes(str(self.__next_position), encoding='utf-8'))
        LocalizationIPC.set_output_ready()

    def start_message(self):
        msg = "GPS Localization started"
        return msg


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('PathPlanning')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/PathPlanning.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    ld = GPSLocalizationProcess(logger=logger,
                                map_file_path="/home/janib/Downloads/Editor/AutonomousDriving-Refactored/Inference_Server/map.osm")
    ld.run()
