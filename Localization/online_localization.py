#!/usr/bin/env python3
import os.path
import orbslam2
import time
import cv2


def main(vocab_path, settings_path, sequence_path):

    left_image, right_image, timestamps = load_images(sequence_path)
    left_num_images = len(left_image)

    slam = orbslam2.System(vocab_path, settings_path, orbslam2.Sensor.STEREO)
    slam.set_use_viewer(True)
    slam.initialize()
    slam.deactivate_localization_mode()

    times_track = [0 for _ in range(left_num_images)]
    print('-----')
    print('Start processing sequence ...')
    print('Images in the sequence: {0}'.format(left_num_images))

    for idx in range(left_num_images):
        l_image = cv2.imread(left_image[idx], cv2.IMREAD_UNCHANGED)
        r_image = cv2.imread(right_image[idx], cv2.IMREAD_UNCHANGED)
        tframe = timestamps[idx]

        if l_image is None:
            print("failed to load image at {0}".format(left_image[idx]))
            return 1
        if r_image is None:
            print("failed to load image at {0}".format(right_image[idx]))
            return 1

        t1 = time.time()
        pose = slam.process_image_stereo(l_image, r_image, tframe)
        print(pose)
        t2 = time.time()

        ttrack = t2 - t1
        times_track[idx] = ttrack

        t = 0
        if idx < left_num_images - 1:
            t = timestamps[idx + 1] - tframe
        elif idx > 0:
            t = tframe - timestamps[idx - 1]

        if ttrack < t:
            time.sleep(t - ttrack)

    # save_trajectory(slam.get_trajectory_points(), 'trajectory.txt')
    slam.save_map('map.bin')
    slam.shutdown()

    # times_track = sorted(times_track)
    # total_time = sum(times_track)
    # print('-----')
    # print('median tracking time: {0}'.format(times_track[num_images // 2]))
    # print('mean tracking time: {0}'.format(total_time / num_images))

    return 0


def load_images(path_to_sequence):
    timestamps = []
    with open(os.path.join(path_to_sequence, 'time.txt')) as times_file:
        for line in times_file:
            if len(line) > 0:
                timestamps.append(float(line))

    return [
        os.path.join(path_to_sequence, '1', "{}.png".format(idx))
        for idx in range(len(timestamps))
    ], [
        os.path.join(path_to_sequence, '2', "{}.png".format(idx))
        for idx in range(len(timestamps))
    ], timestamps


def save_trajectory(trajectory, filename):
    with open(filename, 'w') as traj_file:
        traj_file.writelines('{time} {r00} {r01} {r02} {t0} {r10} {r11} {r12} {t1} {r20} {r21} {r22} {t2}\n'.format(
            time=repr(t),
            r00=repr(r00),
            r01=repr(r01),
            r02=repr(r02),
            t0=repr(t0),
            r10=repr(r10),
            r11=repr(r11),
            r12=repr(r12),
            t1=repr(t1),
            r20=repr(r20),
            r21=repr(r21),
            r22=repr(r22),
            t2=repr(t2)
        ) for t, r00, r01, r02, t0, r10, r11, r12, t1, r20, r21, r22, t2 in trajectory)


class ORBSlam:
    MONO = orbslam2.Sensor.MONOCULAR
    STEREO = orbslam2.Sensor.STEREO
    RGBD = orbslam2.Sensor.RGBD

    def __init__(self, vocab_path, settings_path, use_viewer, only_localization, map_path, mode):
        self.slam = orbslam2.System(vocab_path, settings_path, mode)
        self.slam.set_use_viewer(use_viewer)
        self.slam.initialize()
        self.only_localization = only_localization
        self.map_path = map_path
        self.mode = mode
        if self.only_localization:
            self.slam.load_map(map_path)
            self.slam.activate_localization_mode()
        else:
            self.slam.deactivate_localization_mode()

    def process(self, img_1, t, img_2=None):
        if self.mode == orbslam2.Sensor.MONOCULAR:
            pose = self.slam.process_image_mono(img_1, t)
        elif self.mode == orbslam2.Sensor.STEREO:
            pose = self.slam.process_image_stereo(img_1, img_2, t)
        elif self.mode == orbslam2.Sensor.RGBD:
            pose = self.slam.process_image_rgbd(img_1, img_2, t)
        return pose

    def shutdown(self):
        if self.only_localization:
            self.slam.shutdown()
        else:
            self.slam.save_map(self.map_path)
            self.slam.shutdown()


if __name__ == '__main__':
    # from common.image_to_video import img_2_video
    # video_path = os.path.join(os.getcwd(), 'temp', 'project.avi')
    # img_2_video(video_path, 10)
    #
    # from Localization.videoToFiles import CreateVideoimages
    # CreateVideoimages(video_path, 'temp/simulation/rgb', True)

    main('custom_vocab.txt', '/home/janib/Downloads/Editor/AutonomousDriving-Refactored/Inference_Server/Localization/stereo_settings.yaml',
         '/home/janib/Downloads/Editor/AutonomousDriving-Refactored/'
         'city/calibration/Stereo')

