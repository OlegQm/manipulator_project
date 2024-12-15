import os
import random
import platform
import atexit
from queue import Queue
from multiprocessing import Process
from threading import Thread
import json

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import cv2
import hailo
from cvzone import SerialModule
from hailo_scripts.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class
)

from hailo_scripts.detection_pipeline import GStreamerDetectionApp

class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.serial = SerialModule.SerialObject("/dev/ttyUSB0", 9600, 3)
        self.current_angles = np.array([20, 60, 90])
        self.data_queue = Queue(maxsize=3)
        self.serial_thread = None
        self.server_process = None
        self.words_file = "words_file.txt"
        self.get_img_command = "<TSC>"
        self.formed_img_name = "currentObjectsScreenshot.jpg"
        self.command_file_folder = "screenshot_request"
        self.current_objects_path = "currentObjects.txt"
        self.stop_radius = 85
        self.step = 1
        self.servos_number = 3
        self.servos_limits = np.array([[0, 60], [60, 155], [0, 180]])

    def file_write(self, file_name, msg):
        with open(file_name, "w") as f:
            f.write(msg)

    def read_word(self, file_path):
        try:
            with open(file_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"File reading error: {e}")
            return None

    def check_for_img_command(self, path):
        try:
            old_file_path = os.path.join(path, "1")
            new_file_path = os.path.join(path, "0")
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
                return True
            return False
        except Exception as ex:
            print(f"Error: {ex}")
            return False

    def is_in(self, angle, interval):
        return interval[0] <= angle <= interval[1]

    def roll_back(self, current_angles, i, new_angle, limits):
        if i != 1:
            return 0
        if new_angle < limits[0] and (
            current_angles[0] + self.step > self.servos_limits[0][1]
        ):
            return 1
        elif new_angle > limits[1] and (
            current_angles[0] - self.step < self.servos_limits[0][0]
        ):
            return 1
        return 0

    def update_angles(self, current_angles, changes):
        for i in range(self.servos_number):
            new_angle = current_angles[i] + changes[i]
            limits = self.servos_limits[i]

            if self.roll_back(current_angles, i, new_angle, limits):
                continue

            if self.is_in(new_angle, limits):
                current_angles[i] = new_angle
            elif new_angle < limits[0]:
                if i == 1 and (current_angles[0] + self.step) <= self.servos_limits[0][1]:
                    current_angles[0] += self.step
                current_angles[i] = limits[0]
            elif new_angle > limits[1]:
                if i == 1 and (current_angles[0] - self.step) >= self.servos_limits[0][0]:
                    current_angles[0] -= self.step
                current_angles[i] = limits[1]

    def one_turn(self, distance_x, distance_y, current_angles):
        if abs(distance_x) <= self.stop_radius and abs(distance_y) <= self.stop_radius:
            return

        curr_step_x = self.step + int(0.5 * (abs(distance_x) // self.stop_radius))
        curr_step_y = self.step + int(0.5 * (abs(distance_x) // self.stop_radius))

        changes = np.array([0, 0, 0])
        if distance_x < 0:
            changes[2] += curr_step_x
        else:
            changes[2] -= curr_step_x

        if distance_y < 0:
            changes[1] -= curr_step_y
        else:
            changes[1] += curr_step_y

        self.update_angles(current_angles, changes)
        self.data_queue.put(current_angles)

    def cleanup(self):
        print("Stopping...")
        self.serial.ser.close()
        self.data_queue.put(None)
        if self.serial_thread is not None:
            self.serial_thread.join()
        if self.server_process is not None:
            self.server_process.terminate()
            self.server_process.join()

    def get_distance(self, screen_center_x, screen_center_y,
                    obj_center_x, obj_center_y):
        return obj_center_x - screen_center_x, obj_center_y - screen_center_y

    def add_one_object(
            self, img, detection, colors_map,
            name_index_map, current_angles, width, height,
            image_to_send=False
    ):
        label = detection.get_label()
        color = colors_map[int(name_index_map[label])]

        screen_center_x = img.shape[1] // 2
        screen_center_y = img.shape[0] // 2
        bbox = detection.get_bbox()

        x_min = int(bbox.xmin() * width)
        y_min = int(bbox.ymin() * height)
        x_max = int(bbox.xmax() * width)
        y_max = int(bbox.ymax() * height)

        obj_center_x = (x_min + x_max) // 2
        obj_center_y = (y_min + y_max) // 2

        distance_x, distance_y = self.get_distance(
            screen_center_x, screen_center_y, obj_center_x, obj_center_y
        )
        if not image_to_send:
            self.one_turn(distance_x, distance_y, current_angles)

        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, 2)
        cv2.circle(img, (obj_center_x, obj_center_y), 10, (0, 255, 0), -1)
        cv2.circle(img, (screen_center_x, screen_center_y), 10, (0, 0, 255), 2)
        cv2.putText(
            img,
            f"{label.upper()} " + (
                "Dis X: {distance_x} Dis Y: {distance_y}" if not image_to_send else ""
            ),
            (x_min, y_min),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
        )

    def activate_server(self, path_to_server, platform):
        if platform == "Windows":
            os.system(path_to_server)
        else:
            os.system(
                f"export PATH=$PATH:~/dotnet-core ; dotnet {path_to_server}"
            )

    def generate_color(self, color_id):
        random.seed(int(color_id))
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        return color

    def delete_file_if_exists(self, file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File '{file_path}' has been deleted.")
            except Exception as e:
                print(f"An error occurred while deleting the file: {e}")

    def find_executable_path(self, base_path, system):
        system_arch_mapping = {
            "Linux": {
                "x86_64": "linux-x64",
                "armv7l": "linux-arm",
                "aarch64": "linux-arm64",
            },
            "Darwin": {
                "x86_64": "osx-x64",
                "arm64": "osx-arm64",
            },
            "Windows": {
                "x86": "win-x86",
                "AMD64": "win-x64",
                "arm64": "win-arm64",
            },
        }

        architecture = platform.machine()  # "x86_64", "armv7l", "aarch64"

        arch_folder = system_arch_mapping.get(system, {}).get(architecture, "")
        if not arch_folder:
            raise Exception(
                f"Unsupported system or architecture: {system}, {architecture}"
            )

        executable_folder = os.path.join(
            base_path, "server_part", system, arch_folder
        )
        executable_file = "manipulatorServerPart" + (
            ".exe" if system == "Windows" else ".dll"
        )

        return os.path.join(executable_folder, executable_file)

    def serial_worker(self, serial, data_queue):
        while True:
            data = data_queue.get()
            if data is None:
                break
            serial.sendData(data)
            data_queue.task_done()

    def get_json_data(self, path_to_json):
        with open(path_to_json) as file:
            json_data = json.load(file)

        class_dict = {index: label for index, label in enumerate(json_data["labels"])}
        return class_dict


def app_callback(pad, info, user_data: user_app_callback_class):
    if not hasattr(app_callback, "class_dict"):
        app_callback.class_dict = user_data.get_json_data("hailo_scripts/labels.json")
        app_callback.class_names = list(app_callback.class_dict.values())
        app_callback.class_ids = list(app_callback.class_dict.keys())
        app_callback.colors_map = {
            key: user_data.generate_color(key) for key in app_callback.class_ids
        }
        app_callback.name_index_map = {
            value: key for key, value in enumerate(app_callback.class_names)
        }
        app_callback.entered_name = str()

    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    user_data.increment()
    pad_format, width, height = get_caps_from_pad(pad)

    frame = None
    if (
        user_data.use_frame
        and pad_format is not None
        and width is not None
        and height is not None
    ):
        frame = get_numpy_from_buffer(buffer, pad_format, width, height)

    if frame is None or frame.size == 0:
        print("Error: Frame is empty.")
        return Gst.PadProbeReturn.OK

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    entered_name = user_data.read_word(user_data.words_file).strip().lower()
    is_command = user_data.check_for_img_command(user_data.command_file_folder)
    available_classes = set()

    if is_command:
        frame_cpy = frame.copy()
        for detection in detections:
            user_data.add_one_object(
                frame_cpy,
                detection,
                app_callback.colors_map,
                app_callback.name_index_map,
                user_data.current_angles,
                width,
                height,
                image_to_send=True
            )
            available_classes.add(detection.get_label().lower())
        cv2.imwrite(user_data.formed_img_name, cv2.cvtColor(frame_cpy, cv2.COLOR_RGB2BGR))
        user_data.file_write(
            user_data.current_objects_path,
            "\n".join(available_classes)
        )

    for detection in detections:
        label = detection.get_label()
        if label == entered_name:
            user_data.add_one_object(
                frame,
                detection,
                app_callback.colors_map,
                app_callback.name_index_map,
                user_data.current_angles,
                width,
                height,
                image_to_send=False
            )

    if user_data.use_frame:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    return Gst.PadProbeReturn.OK


def main():
    user_data = user_app_callback_class()
    atexit.register(user_data.cleanup)
    system = platform.system()  # "Linux", "Darwin", "Windows"
    server_path = user_data.find_executable_path("", system)
    user_data.server_process = Process(
        target=user_data.activate_server,
        args=(server_path, system)
    )
    user_data.server_process.start()
    user_data.serial_thread = Thread(
        target=user_data.serial_worker,
        args=(user_data.serial, user_data.data_queue)
    )
    user_data.serial_thread.start()

    user_data.file_write(user_data.words_file, "")
    user_data.delete_file_if_exists(user_data.formed_img_name)

    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
    user_data.cleanup()

if __name__ == "__main__":
    main()
