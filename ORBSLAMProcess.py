import base64
import json
from dataclasses import dataclass
from io import BytesIO
import logging
from typing import Union
from PIL import Image
import numpy as np

from Localization import LocalizationOutput
from Common.SensorReceiver import SensorReceiver
from IPC import MappingIPC
from Localization import ORBSlam
from PathPlanning import PathPlanning

import argparse


@dataclass
class CameraData:
    first_image: np.ndarray = None
    second_image: np.ndarray = None
    timestamp: float = 0.0


class ORBSLAMProcess(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """

    def __init__(self, logger: logging.Logger, localization_only: bool):
        super().__init__(logger)
        vocab_path = '/home/janib/Downloads/Editor/AutonomousDriving-Refactored/Inference_Server/' \
                     'Localization/ORBvoc.txt'
        settings_path = '/home/janib/Downloads/Editor/AutonomousDriving-Refactored/Inference_Server/Localization/' \
                        'stereo_settings.yaml'
        map_file_path = '/home/janib/Downloads/Editor/AutonomousDriving-Refactored/Inference_Server/map.osm'
        self.mode = ORBSlam.STEREO
        self.orb_slam = ORBSlam(vocab_path=vocab_path, settings_path=settings_path, use_viewer=True,
                                only_localization=localization_only, map_path='stereo_1k_13oct.map', mode=self.mode)

        MappingIPC.init_ipc()
        self.__localized_coord = [-1, -1, -1]
        self.__pose = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        source_coord = PathPlanning.PathPlanning.transform_coord((1280, 365))
        self.path_planning = PathPlanning.PathPlanning(map_file_path, source_coord)
        #self.__next_position: LocalizationOutput = LocalizationOutput()

    @staticmethod
    def orb_to_unity_coord(orb_cord):
        transform_mat = np.array([[9.53085000e-01, 3.50840946e-05, -3.55865664e-03],
                                  [-8.36288126e+00, -8.40891136e-03, -6.03384672e+00],
                                  [1.62661798e-01, 1.50399175e-04, 1.01332284e+00]])
        x_off = 1280.0 - 0.2886205
        y_off = 0.1 + 0.1646024
        z_off = 370.7 - 3.553366
        transformed = np.matmul([orb_cord[0]+x_off, orb_cord[1]+y_off, orb_cord[2]+z_off], transform_mat)
        return transformed

    def process_data(self, data: Union[CameraData, None]) -> None:
        """
        :param data:
        :return: Returns nothing just sets the __inference
        """
        if not MappingIPC.is_output_ready():
            self.__pose = self.orb_slam.process(data.first_image, data.timestamp, data.second_image)

            if self.orb_slam.only_localization:
                # Convert from self.pose to array of slam coord using R*T rule
                if self.__pose is not None:
                    rotation = self.__pose[:-1, :-1]
                    translation = self.__pose[:-1, -1]

                    # (array of 3 coordinates derived from pose)
                    self.__localized_coord = np.matmul(rotation.T, translation) * -1
                    self.__localized_coord = self.orb_to_unity_coord(self.__localized_coord)
                    curr_pos = (self.__localized_coord[0], self.__localized_coord[2])
                    transformed_curr_pos = PathPlanning.PathPlanning.transform_coord(curr_pos)
                    next_node_r, next_node_l = self.path_planning.find_next_node(transformed_curr_pos)
                    self.__next_position = LocalizationOutput((curr_pos[0], curr_pos[1]), next_node_r[0],
                                                              next_node_l[0],
                                                              self.path_planning.has_reached_destination)


    def read_data(self) -> Union[CameraData, None]:
        """
        Read image from client
        :return: Image sent by the client
        """
        # If output has been consumed by Unity
        if not MappingIPC.is_output_ready():
            first_img_str, second_img_str, time_str = MappingIPC.read_data()
            fi = BytesIO(base64.b64decode(first_img_str))
            si = BytesIO(base64.b64decode(second_img_str))
            first_image = np.array(Image.open(fi))
            second_image = np.array(Image.open(si))
            time_float = float(time_str)
            return CameraData(first_image=first_image, second_image=second_image, timestamp=time_float)

        return None

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        if self.orb_slam.only_localization:
            MappingIPC.write_output(bytes(str(self.__next_position), encoding='utf-8'))

        else:
            if self.__pose is not None:
                d = {
                    'Pose': np.array(self.__pose).tolist()
                }
            else:
                d = {
                    'Pose': None
                }

            MappingIPC.write_output(bytes(json.dumps(d), encoding='utf-8'))

        MappingIPC.set_output_ready()

    def start_message(self):
        msg = "Mapping Main loop started"
        return msg

    def on_quit(self):
        self.orb_slam.shutdown()
        exit(0)


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('Mapping')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/Mapping.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    # my_parser = argparse.ArgumentParser(description='ORB SLAM')
    # # default = 0 if for mapping and default = 1 for localization
    # my_parser.add_argument('--localization-only',
    #                        metavar='localization_only',
    #                        type=int,
    #                        default=1,
    #                        help='False, when mapping')
    #
    # args = my_parser.parse_args()

    mp = ORBSLAMProcess(logger=logger, localization_only=True)

    mp.run()
