import cv2
import os
import random
import platform
import numpy as np
import time
from multiprocessing import Process
from ultralytics import YOLO

current_angles = np.array([20, 60, 90])
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 70)

CLASS_FILE = "coco.names"
WORDS_FILE = "words_file.txt"
GET_IMG_COMMAND = "<TSC>"
FORMED_IMG_NAME = "currentObjectsScreenshot.jpg"
COMMAND_FILE_FOLDER = "screenshot_request"
CURRENT_OBJECTS_PATH = "currentObjects.txt"
MODEL_PATH = "models/dataset_v2_models/yolov8n_model_v8_256.pt"
THRES = 0.45  # Threshold to detect object
IOU = 0.4
STOP_RADIUS = 85
STEP = 1
SERVOS_NUMBER = 3
SERVOS_LIMITS = np.array([[0, 60], [60, 155], [0, 180]])


def file_write(file_name, msg):
    with open(file_name, "w") as f:
        f.write(msg)


def activate_server(path_to_server, system):
    if system == "Windows":
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


def get_distance(
        screen_center_x, screen_center_y, obj_center_x, obj_center_y
    ):
    return obj_center_x - screen_center_x, obj_center_y - screen_center_y


def add_one_object(img, box, obj, obj_name, colors_map):
    color = colors_map[int(obj)]

    screen_center_x = img.shape[1] // 2
    screen_center_y = img.shape[0] // 2

    x1, y1, x2, y2 = box[0], box[1], box[2], box[3]

    obj_center_x = (x1 + x2) // 2
    obj_center_y = (y1 + y2) // 2

    distance_x, distance_y = get_distance(
        screen_center_x, screen_center_y, obj_center_x, obj_center_y
    )

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


def main():
    system = platform.system()  # "Linux", "Darwin", "Windows"
    server_path = find_executable_path("", system)

    server_process = Process(
        target=activate_server, args=(server_path, system)
    )
    server_process.start()

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
            _, img = cap.read()
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
            imgsz=256,
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
                imgsz=256,
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

    print("Stopping...")
    cap.release()
    cv2.destroyAllWindows()
    server_process.terminate()
    server_process.join()


if __name__ == "__main__":
    main()
