import base64
from io import BytesIO
import logging
import json

from PIL import Image
import numpy as np

from IPC import PCSegmentationIPC
from Common.SensorReceiver import SensorReceiver
from PCSegmentation import get_bboxes


class PCSegmentationOdProcess(SensorReceiver):
    """
    Responsible for Receiving and Processing Lane Image, and process that image.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        PCSegmentationIPC.init_ipc()
        self.__bboxes = []

    def process_data(self, img: np.array) -> None:
        """
        :param img:
        :return: Returns nothing just sets the __inference
        """
        self.__bboxes = get_bboxes(img)

    def read_data(self) -> np.array:
        """
        Read image from client
        :return: Image sent by the client
        """
        # If output has been consumed by Unity
        img = None
        if not PCSegmentationIPC.is_output_ready():
            img_str = PCSegmentationIPC.read_data()
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img = np.array(img)
        return img

    def send_data(self) -> None:
        """
        Put the output in the buffer(q)
        :return: None
        """
        output_json = {"signal": self.__detected_color}
        PCSegmentationIPC.write_output(bytes(json.dumps(output_json), encoding='utf-8'))
        PCSegmentationIPC.set_output_ready()

    def start_message(self):
        msg = "Signal Detection Main loop started"
        return msg


if __name__ == '__main__':
    # Create a custom logger
    logger = logging.getLogger('PCSegmentation_OD')
    logger.setLevel(logging.INFO)

    # Create handler
    f_handler = logging.FileHandler('debug/logs/PCSegmentation_OD.log')

    # Create formatter and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)

    td = PCSegmentationIPC(logger=logger)
    td.run()

