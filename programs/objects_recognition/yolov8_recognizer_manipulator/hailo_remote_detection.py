import json
import atexit
import random
from queue import Queue
from multiprocessing import Process, Pipe
from threading import Thread

import numpy as np
import cv2
from io import BytesIO
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import hailo
from cvzone.SerialModule import SerialObject
import os

from hailo_scripts.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class
)
from hailo_scripts.detection_pipeline import GStreamerDetectionApp
from server_part.server import TelegramServer

class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.serial = SerialObject("/dev/ttyUSB0", 9600, 3)
        self.token = os.getenv("TELEGRAM_SENDER_BOT_TOKEN") or "your token"
        self.current_angles = np.array([20, 60, 90])
        self.data_queue = Queue(maxsize=9)
        self.serial_thread = None
        self.server_process = None
        self.parent_pipe = None
        self.last_object_position = np.array([-1, -1])
        self.stop_radius = 85
        self.step = 1
        self.servos_number = 3
        # right (0 - higher, 60 - lower), left (60 - higher, 155 - lower),
        # bottom (0 - left, 180 - right)
        self.servos_limits = np.array([[0, 60], [60, 155], [0, 180]])
        self.route_angles = None
        self.route_distances = None
        self.object_last_direction = None

    def start_server(self, pipe):
        server = TelegramServer(self.token, pipe)
        server.run()

    def is_in(self, angle, interval):
        return interval[0] <= angle <= interval[1]

    def roll_back(self, i, new_angle, limits):
        if i != 1:
            return False
        if new_angle < limits[0] and (
            self.current_angles[0] + self.step > self.servos_limits[0][1]
        ):
            return True
        elif new_angle > limits[1] and (
            self.current_angles[0] - self.step < self.servos_limits[0][0]
        ):
            return True
        return False

    def update_angles(self, changes):
        for i in range(self.servos_number):
            new_angle = self.current_angles[i] + changes[i]
            limits = self.servos_limits[i]

            if self.roll_back(i, new_angle, limits):
                continue

            if self.is_in(new_angle, limits):
                self.current_angles[i] = new_angle
            elif new_angle < limits[0]:
                if i == 1 and (self.current_angles[0] + self.step) < self.servos_limits[0][1]:
                    self.current_angles[0] += self.step
                self.current_angles[i] = limits[0]
            elif new_angle > limits[1]:
                if i == 1 and (self.current_angles[0] - self.step) > self.servos_limits[0][0]:
                    self.current_angles[0] -= self.step
                self.current_angles[i] = limits[1]

    def one_turn(self, distance_x, distance_y, line_following_mode=False):
        if (
            not line_following_mode
            and abs(distance_x) <= self.stop_radius
            and abs(distance_y) <= self.stop_radius
        ):
            return

        curr_step_x, curr_step_y = self.step, self.step
        if not line_following_mode:
            curr_step_x += int(0.5 * (abs(distance_x) // self.stop_radius))
            curr_step_y += int(0.5 * (abs(distance_y) // self.stop_radius))

        changes = np.array([0, 0, 0])
        if distance_x < 0:
            changes[2] += curr_step_x
        else:
            changes[2] -= curr_step_x

        if distance_y < 0:
            changes[1] -= curr_step_y
        else:
            changes[1] += curr_step_y
        with open("steps.txt", "a") as file:
            file.write(f"{self.current_angles}->")
        self.update_angles(changes)
        with open("steps.txt", "a") as file:
            file.write(f"{self.current_angles}\n")
        self.data_queue.put(self.current_angles)

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

    def get_image_center(self, img):
        return img.shape[1] // 2, img.shape[0] // 2

    def add_one_object(
        self, img, detection, colors_map,
        name_index_map, width, height,
        image_to_send=False
    ):
        label = detection.get_label()
        color = colors_map[int(name_index_map[label])]

        screen_center_x, screen_center_y = self.get_image_center(img)
        bbox = detection.get_bbox()

        x_min = int(bbox.xmin() * width)
        y_min = int(bbox.ymin() * height)
        x_max = int(bbox.xmax() * width)
        y_max = int(bbox.ymax() * height)

        obj_center_x = (x_min + x_max) // 2
        obj_center_y = (y_min + y_max) // 2

        if not image_to_send:
            self.last_object_position[0] = obj_center_x
            self.last_object_position[1] = obj_center_y
            self.object_last_direction = None

        distance_x, distance_y = self.get_distance(
            screen_center_x, screen_center_y,
            obj_center_x, obj_center_y
        )
        if not image_to_send:
            self.one_turn(distance_x, distance_y)

        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, 2)
        cv2.circle(img, (obj_center_x, obj_center_y), 10, (0, 255, 0), -1)
        cv2.circle(img, (screen_center_x, screen_center_y), 10, (0, 0, 255), 2)
        cv2.putText(
            img,
            f"{label.upper()} " + (
                "Dis X: {distance_x} Dis Y: {distance_y}"
                if not image_to_send else ""
            ),
            (x_min, y_min),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
        )

    def generate_color(self, color_id):
        random.seed(int(color_id))
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        return color

    def serial_worker(self, serial, data_queue):
        while True:
            data = data_queue.get()
            if data is None:
                break
            serial.sendData(data)
            data_queue.task_done()

    def get_json_data(self, path_to_json):
        with open(path_to_json, encoding="utf-8") as file:
            json_data = json.load(file)

        class_dict = {
            index: label for index, label
            in enumerate(json_data["labels"])
        }
        return class_dict
    
    def find_point_interval(self, point):
        starts = self.route_angles[:, 0]
        ends = self.route_angles[:, 1]

        x1, y1 = starts[:, 0], starts[:, 1]
        x2, y2 = ends[:, 0], ends[:, 1]
        x, y = point
        
        print("X1: ", x1)
        print("Y1: ", y1)
        print("X2: ", x2)
        print("Y2: ", y2)
        print("POINT X: ", x)
        print("POINT Y: ", y)

        on_line = (y - y1) * (x2 - x1) == (y2 - y1) * (x - x1)
        print("ON LINE")

        within_x_bounds = (x >= np.minimum(x1, x2)) & (x <= np.maximum(x1, x2))
        within_y_bounds = (y >= np.minimum(y1, y2)) & (y <= np.maximum(y1, y2))

        valid_intervals = on_line & within_x_bounds & within_y_bounds
        
        print("VALID INTERVALS ", valid_intervals)

        if np.any(valid_intervals):
            return np.argmax(valid_intervals)
        return -1

    def generate_route(self):
        if (
            self.route_angles is not None
            and self.route_distances is not None
        ):
            return
        height_limits = self.servos_limits[1]
        width_limits = self.servos_limits[2]
        width, height = (
            width_limits[1] - width_limits[0],
            height_limits[1] - height_limits[0]
        )
        height_third_part = height // 3
        width_half = width // 2
        self.route_angles = np.array(
            [
                [
                    [height_limits[0], 0],
                    [height_limits[0], width_half - 1]
                ],
                [
                    [height_limits[0], width_half],
                    [height_limits[0], width - 1]
                ],
                [
                    [height_limits[0], width],
                    [height_limits[0] + height_third_part, width]
                ],
                [
                    [height_limits[0] + height_third_part, width - 1],
                    [height_limits[0] + height_third_part, width_half + 1]
                ],
                [
                    [height_limits[0] + height_third_part, width_half],
                    [height_limits[0] + 2*height_third_part, width_half]
                ],
                [
                    [height_limits[0] + 2*height_third_part, width_half + 1],
                    [height_limits[0] + 2*height_third_part, width - 1]
                ],
                [
                    [height_limits[0] + 2*height_third_part, width],
                    [height_limits[1] - 1, width]
                ],
                [
                    [height_limits[1], width],
                    [height_limits[1], width_half + 1]
                ],
                [
                    [height_limits[1], width_half],
                    [height_limits[1], 1]
                ],
                [
                    [height_limits[1], 0],
                    [height_limits[1] - height_third_part, 0]
                ],
                [
                    [height_limits[1] - height_third_part - 1, 0],
                    [height_limits[1] - 2*height_third_part, 0]
                ],
                [
                    [height_limits[1] - 2*height_third_part - 1, 0],
                    [height_limits[0] + 1, 0]
                ]
            ]
        )

        self.route_distances = np.array(
            [
                [-1, 0], [-1, 0], [0, 1], [1, 0],
                [0, 1], [-1, 0], [0, 1], [1, 0],
                [1, 0], [0, -1], [0, -1], [0, -1]
            ]
        )

    def check_changes_valid(self, angles):
        return np.all(
            (angles >= self.servos_limits[:, 0])
            & (angles <= self.servos_limits[:, 1])
        )

    def calculate_distance(self, points_begin, point_end):
        return np.linalg.norm(points_begin - point_end, axis=2)

    def get_on_route(self):
        distances = self.calculate_distance(
            self.route_angles,
            self.current_angles[1:]
        )
        min_index = np.argmin(distances)
        new_angles = self.route_angles[min_index // 2, min_index % 2] # 1 - min_index % 2
        changes = np.array([
            self.current_angles[0],
            new_angles[0],
            new_angles[1]
        ])
        print("STANDING ON ROUTE ", changes)
        with open("steps.txt", "a") as file:
            file.write(f"{self.current_angles}->")
        self.update_angles(changes)
        with open("steps.txt", "a") as file:
            file.write(f"{self.current_angles}\n")
        self.data_queue.put(self.current_angles)

    def follow_route(self, index):
        if index == -1:
            return
        distances = self.route_distances[index]
        print("TURNING ON DISTANCES: ", distances)
        self.one_turn(distances[0], distances[1], line_following_mode=True)

    def find_object(self, img):
        route_index = self.find_point_interval(self.current_angles[1:])
        is_on_route = route_index != -1
        if self.last_object_position[0] != -1:
            print("self.last_object_position[0] != -1")
            if self.object_last_direction is None:
                print("if self.object_last_direction is None")
                screen_center_x, screen_center_y = self.get_image_center(img)
                obj_center_x, obj_center_y = self.last_object_position.flatten()
                x_diff, y_diff = (obj_center_x - screen_center_x,
                                obj_center_y - screen_center_y)
                abs_x_diff, abs_y_diff = abs(x_diff), abs(y_diff)
                x_direction, y_direction = (
                    (x_diff // abs_x_diff, 0) if abs_x_diff >= abs_y_diff
                    else (0, y_diff // abs_y_diff)
                )
                self.object_last_direction = np.array([0, y_direction, x_direction])
            changes = self.object_last_direction * self.step + self.current_angles
            print("CHANGES: ", changes)
            if self.check_changes_valid(changes):
                self.one_turn(
                    self.object_last_direction[2],
                    self.object_last_direction[1],
                    line_following_mode=True
                )
                return
            self.object_last_direction = None
            self.last_object_position = np.array([-1, -1])
            self.get_on_route()
            route_index = self.find_point_interval(self.current_angles[1:])
            is_on_route = True
        if not is_on_route:
            self.get_on_route()
            route_index = self.find_point_interval(self.current_angles[1:])
        print("ROUTE INDEX", route_index)
        print("ROUTE: ", self.route_angles)
        self.follow_route(route_index)

def app_callback(pad, info, user_data: user_app_callback_class):
    if not hasattr(app_callback, "class_dict"):
        app_callback.class_dict = user_data.get_json_data(
            "hailo_scripts/labels.json"
        )
        app_callback.class_names = list(app_callback.class_dict.values())
        app_callback.class_ids = list(app_callback.class_dict.keys())
        app_callback.colors_map = {
            key: user_data.generate_color(key)
            for key in app_callback.class_ids
        }
        app_callback.name_index_map = {
            value: key for key, value in enumerate(app_callback.class_names)
        }
        app_callback.entered_name = ""
        app_callback.look_for_the_object = True

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

    if user_data.parent_pipe.poll():
        command = user_data.parent_pipe.recv()
        if command == "get_image":
            available_classes = set()
            frame_cpy = frame.copy()
            for detection in detections:
                user_data.add_one_object(
                    frame_cpy,
                    detection,
                    app_callback.colors_map,
                    app_callback.name_index_map,
                    width,
                    height,
                    image_to_send=True
                )
                available_classes.add(detection.get_label().lower())
            frame_cpy = cv2.cvtColor(frame_cpy, cv2.COLOR_RGB2BGR)
            _, img_encoded = cv2.imencode('.jpg', frame_cpy)
            image_data = BytesIO(img_encoded.tobytes())
            user_data.parent_pipe.send(
                (image_data, "\n".join(available_classes))
            )
        elif isinstance(command, tuple) and command[0] == "selection":
            app_callback.entered_name = command[1]
            user_data.last_object_position = np.array([-1, -1])
            user_data.object_last_direction = None

    object_found = False
    for detection in detections:
        label = detection.get_label()
        if label == app_callback.entered_name:
            object_found = True
            user_data.add_one_object(
                frame,
                detection,
                app_callback.colors_map,
                app_callback.name_index_map,
                width,
                height,
                image_to_send=False
            )
    if (
        not object_found
        and app_callback.look_for_the_object
        and app_callback.entered_name != ""
    ):
        user_data.find_object(frame)

    if user_data.use_frame:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    return Gst.PadProbeReturn.OK

def main():
    user_data = user_app_callback_class()
    user_data.generate_route()
    print("ROUTE: ", user_data.route_angles)
    atexit.register(user_data.cleanup)
    parent_pipe, child_pipe = Pipe()
    user_data.server_process = Process(
        target=user_data.start_server,
        args=(child_pipe,)
    )
    user_data.server_process.start()
    user_data.parent_pipe = parent_pipe
    print("Server started.")
    user_data.serial_thread = Thread(
        target=user_data.serial_worker,
        args=(user_data.serial, user_data.data_queue)
    )
    user_data.serial_thread.start()

    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()

if __name__ == "__main__":
    main()
