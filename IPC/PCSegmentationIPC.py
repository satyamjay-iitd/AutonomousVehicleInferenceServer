from typing import Tuple
import json
from IPC.IPC import IPC


class PCSegmentationIPC(IPC):
    __pc_segmentation_output_lock = None
    __depth_image_lock = None
    __pc_segmentation_output_ready_lock = None

    __depth_image_mmf = None
    __pc_segmentation_output_mmf = None
    __pc_segmentation_output_ready_mmf = None

    @staticmethod
    def read_data() -> str:
        IPC._dll.wait(PCSegmentationIPC.__depth_image_lock)
        img = IPC._dll.readMMF(PCSegmentationIPC.__depth_image_mmf)
        IPC._dll.post(PCSegmentationIPC.__depth_image_lock)
        return img

    @staticmethod
    def write_output(output):
        IPC._dll.wait(PCSegmentationIPC.__pc_segmentation_output_lock)
        IPC._dll.writeMMF(output, PCSegmentationIPC.__pc_segmentation_output_mmf)
        IPC._dll.post(PCSegmentationIPC.__pc_segmentation_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(PCSegmentationIPC.__pc_segmentation_output_ready_lock)
        IPC._dll.WriteInt(1, PCSegmentationIPC.__pc_segmentation_output_ready_mmf)
        IPC._dll.post(PCSegmentationIPC.__pc_segmentation_output_ready_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(PCSegmentationIPC.__pc_segmentation_output_ready_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        PCSegmentationIPC.__pc_segmentation_output_lock = IPC.get_lock("pc_segmentation_output_lock")
        PCSegmentationIPC.__depth_image_lock = IPC.get_lock("depth_image_lock")
        PCSegmentationIPC.__pc_segmentation_output_ready_lock = IPC.get_lock("pc_segmentation_output_ready_lock")

        PCSegmentationIPC.__depth_image_mmf = IPC.get_mmf("depth_image_mmf", 102400)
        PCSegmentationIPC.__pc_segmentation_output_mmf = IPC.get_mmf("pc_segmentation_output_mmf", 10240)
        PCSegmentationIPC.__pc_segmentation_output_ready_mmf = IPC.get_mmf("pc_segmentation_output_ready_mmf", 4)
        PCSegmentationIPC.set_output_ready()
        d = {
            'CurrPosX': -1.0,
            'CurrPosY': -1.0,
            'NextNodeRX': -1.0,
            'NextNodeRY': -1.0,
            'NextNodeLX': -1.0,
            'NextNodeLY': -1.0,
            'HasReached': False,
        }
        PCSegmentationIPC.write_output(bytes(str(json.dumps(d)), encoding='utf-8'))
