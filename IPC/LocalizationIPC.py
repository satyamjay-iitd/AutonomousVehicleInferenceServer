from typing import Tuple
import json
from IPC.IPC import IPC


class LocalizationIPC(IPC):
    __path_position_lock = None
    __path_ready_to_receive_lock = None
    __path_output_lock = None

    __path_coord_mmf = None
    __path_ready_to_receive_mmf = None
    __path_output_mmf = None

    @staticmethod
    def read_data() -> Tuple[float, float]:
        IPC._dll.wait(LocalizationIPC.__path_position_lock)
        coord = IPC._dll.readMMF(LocalizationIPC.__path_coord_mmf)
        IPC._dll.post(LocalizationIPC.__path_position_lock)
        coords = list(map(float, coord.split()))
        return coords[0], coords[1]

    @staticmethod
    def write_output(output):
        IPC._dll.wait(LocalizationIPC.__path_output_lock)
        IPC._dll.writeMMF(output, LocalizationIPC.__path_output_mmf)
        IPC._dll.post(LocalizationIPC.__path_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(LocalizationIPC.__path_ready_to_receive_lock)
        IPC._dll.WriteInt(1, LocalizationIPC.__path_ready_to_receive_mmf)
        IPC._dll.post(LocalizationIPC.__path_ready_to_receive_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(LocalizationIPC.__path_ready_to_receive_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        LocalizationIPC.__path_position_lock = IPC.get_lock("map_unity_coord_lock")
        LocalizationIPC.__path_output_lock = IPC.get_lock("map_coord_output_lock")
        LocalizationIPC.__path_ready_to_receive_lock = IPC.get_lock("map_output_ready_lock")

        LocalizationIPC.__path_coord_mmf = IPC.get_mmf("map_unity_coord_mmf", 100)
        LocalizationIPC.__path_output_mmf = IPC.get_mmf("map_coord_output_mmf", 300)
        LocalizationIPC.__path_ready_to_receive_mmf = IPC.get_mmf("map_output_ready_mmf", 4)
        LocalizationIPC.set_output_ready()
        d = {
            'CurrPosX': -1.0,
            'CurrPosY': -1.0,
            'NextNodeRX': -1.0,
            'NextNodeRY': -1.0,
            'NextNodeLX': -1.0,
            'NextNodeLY': -1.0,
            'HasReached': False,
        }
        LocalizationIPC.write_output(bytes(str(json.dumps(d)), encoding='utf-8'))
