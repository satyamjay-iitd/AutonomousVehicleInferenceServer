from typing import Tuple

from IPC.IPC import IPC

class MappingIPC(IPC):
    __mapping_image_lock = None
    __mapping_ready_to_receive_lock = None
    __mapping_output_lock = None

    __mapping_left_image_mmf = None
    __mapping_right_image_mmf = None
    __mapping_time_mmf = None
    __mapping_ready_to_receive_mmf = None
    __mapping_output_mmf = None

    @staticmethod
    def read_data() -> Tuple[str, str, str]:
        IPC._dll.wait(MappingIPC.__mapping_image_lock)
        left_image = IPC._dll.readMMF(MappingIPC.__mapping_left_image_mmf)
        right_image = IPC._dll.readMMF(MappingIPC.__mapping_right_image_mmf)
        t = IPC._dll.readMMF(MappingIPC.__mapping_time_mmf)
        IPC._dll.post(MappingIPC.__mapping_image_lock)
        return left_image, right_image, t

    @staticmethod
    def write_output(output):
        IPC._dll.wait(MappingIPC.__mapping_output_lock)
        IPC._dll.writeMMF(output, MappingIPC.__mapping_output_mmf)
        IPC._dll.post(MappingIPC.__mapping_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(MappingIPC.__mapping_ready_to_receive_lock)
        IPC._dll.WriteInt(1, MappingIPC.__mapping_ready_to_receive_mmf)
        IPC._dll.post(MappingIPC.__mapping_ready_to_receive_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(MappingIPC.__mapping_ready_to_receive_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        MappingIPC.__mapping_image_lock = IPC.get_lock("mapping_image_lock")
        MappingIPC.__mapping_output_lock = IPC.get_lock("mapping_output_lock")
        MappingIPC.__mapping_ready_to_receive_lock = IPC.get_lock("mapping_ready_to_receive_lock")

        MappingIPC.__mapping_left_image_mmf = IPC.get_mmf("mapping_left_image_mmf", 100000000)
        MappingIPC.__mapping_right_image_mmf = IPC.get_mmf("mapping_right_image_mmf", 100000000)
        MappingIPC.__mapping_time_mmf = IPC.get_mmf("mapping_time_mmf", 4)
        MappingIPC.__mapping_output_mmf = IPC.get_mmf("mapping_output_mmf", 32768)
        MappingIPC.__mapping_ready_to_receive_mmf = IPC.get_mmf("mapping_ready_to_receive", 4)
        MappingIPC.set_output_ready()
