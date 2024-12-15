import os
import random
import atexit
import platform
import time
from queue import Queue
from multiprocessing import Process
from threading import Thread

import cv2
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO
from cvzone import SerialModule

os.system("sudo systemctl stop yolov8.service")

serial = SerialModule.SerialObject("/dev/ttyUSB0", 9600, 3)
current_angles = np.array([20, 60, 90])
serial_thread = None
server_process = None
data_queue = Queue()
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={
            "size": (640, 640),
            "format": "RGB888"
        }
    )
)
picam2.start()

CLASS_FILE = "coco.names"
WORDS_FILE = "words_file.txt"
GET_IMG_COMMAND = "<TSC>"
FORMED_IMG_NAME = "currentObjectsScreenshot.jpg"
COMMAND_FILE_FOLDER = "screenshot_request"
CURRENT_OBJECTS_PATH = "currentObjects.txt"
MODEL_PATH = "models/yolov8n_model_v8_256.pt"
IMGSZ = 256
THRES = 0.45  # Threshold to detect object
IOU = 0.4
STOP_RADIUS = 85
STEP = 1
SERVOS_NUMBER = 3
SERVOS_LIMITS = np.array([[0, 60], [60, 155], [0, 180]])


def file_write(file_name, msg):
    with open(file_name, "w") as f:
        f.write(msg)


def cleanup():
    print("Stopping...")
    serial.ser.close()
    picam2.close()
    cv2.destroyAllWindows()
    data_queue.put(None)
    if serial_thread is not None:
        serial_thread.join()
    if server_process is not None:
        server_process.terminate()
        server_process.join()


def activate_server(path_to_server, platform):
    if platform == "Windows":
        os.system(path_to_server)
    else:
        os.system(
            f"export PATH=$PATH:~/dotnet-core ; dotnet {path_to_server}"
        )


def read_word(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"File reading error: {e}")
        return None


def check_for_img_command(path):
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


def is_in(angle, interval):
    return interval[0] <= angle <= interval[1]


def roll_back(current_angles, i, new_angle, limits):
    if i != 1:
        return 0
    if new_angle < limits[0] and (
        current_angles[0] + STEP > SERVOS_LIMITS[0][1]
    ):
        return 1
    elif new_angle > limits[1] and (
        current_angles[0] - STEP < SERVOS_LIMITS[0][0]
    ):
        return 1
    return 0


def update_angles(current_angles, changes):
    for i in range(SERVOS_NUMBER):
        new_angle = current_angles[i] + changes[i]
        limits = SERVOS_LIMITS[i]

        if roll_back(current_angles, i, new_angle, limits):
            continue

        if is_in(new_angle, limits):
            current_angles[i] = new_angle
        elif new_angle < limits[0]:
            if i == 1 and (current_angles[0] + STEP) <= SERVOS_LIMITS[0][1]:
                current_angles[0] += STEP
            current_angles[i] = limits[0]
        elif new_angle > limits[1]:
            if i == 1 and (current_angles[0] - STEP) >= SERVOS_LIMITS[0][0]:
                current_angles[0] -= STEP
            current_angles[i] = limits[1]


def one_turn(distance_x, distance_y, current_angles):
    if abs(distance_x) <= STOP_RADIUS and abs(distance_y) <= STOP_RADIUS:
        return

    curr_step_x = STEP + int(0.5 * (abs(distance_x) // STOP_RADIUS))
    curr_step_y = STEP + int(0.5 * (abs(distance_x) // STOP_RADIUS))

    changes = np.array([0, 0, 0])
    if distance_x < 0:
        changes[2] += curr_step_x
    else:
        changes[2] -= curr_step_x

    if distance_y < 0:
        changes[1] -= curr_step_y
    else:
        changes[1] += curr_step_y

    update_angles(current_angles, changes)
    data_queue.put(current_angles)


def get_distance(screen_center_x, screen_center_y,
                 obj_center_x, obj_center_y):
    return obj_center_x - screen_center_x, obj_center_y - screen_center_y


def add_one_object(img, box, obj, obj_name, colors_map, current_angles):
    color = colors_map[int(obj)]

    screen_center_x = img.shape[1] // 2
    screen_center_y = img.shape[0] // 2

    x1, y1, x2, y2 = box[0], box[1], box[2], box[3]

    obj_center_x = (x1 + x2) // 2
    obj_center_y = (y1 + y2) // 2

    distance_x, distance_y = get_distance(
        screen_center_x, screen_center_y, obj_center_x, obj_center_y
    )
    one_turn(distance_x, distance_y, current_angles)

    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.circle(img, (obj_center_x, obj_center_y), 10, (0, 255, 0), -1)
    cv2.circle(img, (screen_center_x, screen_center_y), 10, (0, 0, 255), 2)
    cv2.putText(
        img,
        f"{obj_name.upper()} Dis X: {distance_x} Dis Y: {distance_y}",
        (x1, y1),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 255),
        2,
    )


def generate_color(color_id):
    random.seed(int(color_id))
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    return color


def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' has been deleted.")
        except Exception as e:
            print(f"An error occurred while deleting the file: {e}")


def activate_server(path_to_server, system):
    if system == "Windows":
        os.system(path_to_server)
    else:
        os.system(
            f"export PATH=$PATH:~/dotnet-core ; dotnet {path_to_server}"
        )


def find_executable_path(base_path, system):
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


def serial_worker(serial, data_queue):
    while True:
        data = data_queue.get()
        if data is None:
            break
        serial.sendData(data)
        data_queue.task_done()


def main():
    atexit.register(cleanup)
    system = platform.system()  # "Linux", "Darwin", "Windows"
    server_path = find_executable_path("", system)

    server_process = Process(
        target=activate_server,
        args=(server_path, system)
    )
    server_process.start()
    serial_thread = Thread(target=serial_worker, args=(serial, data_queue))
    serial_thread.start()

    file_write(WORDS_FILE, "")
    delete_file_if_exists(FORMED_IMG_NAME)

    model = YOLO(MODEL_PATH)
    class_names = model.model.names
    num_classes = len(class_names)
    class_ids = np.arange(num_classes)  # list(range(num_classes))
    class_index_map = {value: key for key, value in class_names.items()}
    colors_map = {key: generate_color(key) for key in class_names}
    entered_name = str()

    while True:
        start_time = time.time()
        try:
            img = picam2.capture_array()
        except Exception as e:
            print(f"Error fetching or decoding image: {e}")
            continue

        entered_name = read_word(WORDS_FILE).strip().lower()
        name_index = []
        if entered_name:
            name_index.append(class_index_map.get(entered_name, -1))
        results = model.track(
            img,
            iou=IOU,
            conf=THRES,
            imgsz=IMGSZ,
            verbose=False,
            tracker="botsort.yaml",
            classes=name_index,
        )
        is_command = check_for_img_command(COMMAND_FILE_FOLDER)
        available_classes = set()
        if is_command:
            results_to_send = model.track(
                img,
                iou=IOU,
                conf=THRES,
                imgsz=IMGSZ,
                verbose=False,
                tracker="botsort.yaml",
                classes=class_ids,
            )
            if results_to_send[0].boxes.id is not None:
                boxes = results_to_send[0].boxes.xyxy.cpu().numpy().astype(int)
                classes = results_to_send[0].boxes.cls.cpu().numpy().astype(int)
                img_cpy = img.copy()
                for clss, box in zip(classes, boxes):
                    class_name = class_names[clss]
                    add_one_object(
                        img_cpy,
                        box,
                        clss,
                        class_name,
                        colors_map,
                        current_angles
                    )
                    available_classes.add(class_name.lower())
                cv2.imwrite(FORMED_IMG_NAME, img_cpy)
                file_write(CURRENT_OBJECTS_PATH, "\n".join(available_classes))
            else:
                cv2.imwrite(FORMED_IMG_NAME, img)
                file_write(CURRENT_OBJECTS_PATH, " ")

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_box = boxes[0]

            add_one_object(
                img,
                track_box,
                name_index[0],
                class_names[name_index[0]],
                colors_map,
                current_angles,
            )
            fps = 1.0 / (time.time() - start_time)

            cv2.putText(
                img,
                f"FPS: {fps:.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Output", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cleanup()


if __name__ == "__main__":
    main()
