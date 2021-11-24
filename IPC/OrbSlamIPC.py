from IPC.ipc import IPC


class OrbSlamIPC(IPC):
    __orb_slam_img_lock = None
    __orb_slam_output_lock = None
    __orb_slam_output_ready_lock = None

    __orb_slam_img_mmf = None
    __orb_slam_output_mmf = None
    __orb_slam_output_ready_mmf = None

    @staticmethod
    def read_data() -> str:
        IPC._dll.wait(OrbSlamIPC.__orb_slam_img_lock)
        img = IPC._dll.readMMF(OrbSlamIPC.__orb_slam_img_mmf)
        IPC._dll.post(OrbSlamIPC.__orb_slam_img_lock)
        return img

    @staticmethod
    def write_output(output):
        IPC._dll.wait(OrbSlamIPC.__orb_slam_output_lock)
        IPC._dll.writeMMF(output, OrbSlamIPC.__orb_slam_output_mmf)
        IPC._dll.post(OrbSlamIPC.__orb_slam_output_lock)

    @staticmethod
    def set_output_ready():
        IPC._dll.wait(OrbSlamIPC.__orb_slam_output_ready_lock)
        IPC._dll.WriteInt(1, OrbSlamIPC.__orb_slam_output_ready_mmf)
        IPC._dll.post(OrbSlamIPC.__orb_slam_output_ready_lock)

    @staticmethod
    def is_output_ready() -> bool:
        return IPC._dll.ReadInt(OrbSlamIPC.__orb_slam_output_ready_mmf) == 1

    @staticmethod
    def init_ipc():
        IPC._load_dll()
        OrbSlamIPC.__orb_slam_image_lock = IPC.get_lock("orbslam_image_lock")
        OrbSlamIPC.__orb_slam_output_lock = IPC.get_lock("orbslam_output_lock")
        OrbSlamIPC.__orb_slam_output_ready_lock = IPC.get_lock("orbslam_ready_lock")

        OrbSlamIPC.__orb_slam_image_mmf = IPC.get_mmf("orbslam_image_mmf", 1000000)
        OrbSlamIPC.__orb_slam_output_mmf = IPC.get_mmf("orbslam_output_mmf", 65536)
        OrbSlamIPC.__orb_slam_output_ready_mmf = IPC.get_mmf("orbslam_ready_mmf", 4)

        OrbSlamIPC.write_output(bytes('[]', encoding='utf-8'))
        OrbSlamIPC.set_output_ready()

