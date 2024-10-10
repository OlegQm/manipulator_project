import cv2
import os
import random
import platform
from threading import Thread
from ultralytics import YOLOWorld
import numpy as np
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
cap.set(10, 70)

CLASS_FILE = "coco.names"
WORDS_FILE = "words_file.txt"
GET_IMG_COMMAND = "<TSC>"
FORMED_IMG_NAME = "currentObjectsScreenshot.jpg"
COMMAND_FILE_PATH = "screenshotRequest.txt"
CURRENT_OBJECTS_PATH = "currentObjects.txt"
MODEL_PATH = "models/dataset_v2_models/yolov8s-world.pt"
EMPTY_LINE = ""

STOP_RADIUS = 85
STEP = 1
SERVOS_NUMBER = 3
SERVOS_LIMITS = np.array([[0, 60], [60, 155], [0, 180]])
current_angles = np.array([20, 60, 90])


def empty_file(path):
    with open(path, "w") as f:
        f.write(EMPTY_LINE)


def activate_server(path_to_server, platform):
    if platform == "Windows":
        os.system(path_to_server)
    elif platform == "Linux":
        os.system(
            f"export PATH=$PATH:~/dotnet-core ; dotnet {path_to_server}"
        )
    else:
        os.system(f"dotnet {path_to_server}")


def read_word(file_path):
    try:
        with open(file_path, "r+") as f:
            word = f.read().strip()
            f.write("")
            return word
    except Exception as e:
        print(f"File reading error: {e}")
        return None


def check_for_img_command(path):
    try:
        with open(path, "r") as file:
            for line in file:
                if GET_IMG_COMMAND in line:
                    with open(path, "w") as f:
                        f.write(EMPTY_LINE)
                    return True
        return False
    except FileNotFoundError:
        print(f"File '{path}' not found.")
        return False


def get_distance(screen_center_x, screen_center_y,
                 obj_center_x, obj_center_y):
    return obj_center_x - screen_center_x, obj_center_y - screen_center_y


def add_one_object(img, box, obj, obj_name, colors_map):
    color = colors_map[obj]

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
            "arm": "win-arm",
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


system = platform.system()  # "Linux", "Darwin", "Windows"
server_path = find_executable_path("", system)


def main():
    empty_file(WORDS_FILE)
    delete_file_if_exists(FORMED_IMG_NAME)
    model = YOLOWorld(MODEL_PATH, verbose=False)
    # general_classes = ["apple", "bear", "bird", "dog",
    #                    "boar", "cat", "cow", "raccoon", "deer", "person"]
    general_classes = list(model.model.names.values())
    model.set_classes(["Nothing"])
    colors_map = {
        key: generate_color(key) for key, _ in enumerate(general_classes)
    }
    server = Thread(
        target=activate_server,
        args=(
            server_path,
            system,
        ),
    )
    server.start()
    entered_name = str()

    while True:
        start_time = time.time()
        try:
            ret, img = cap.read()
            # img = cv2.flip(img, 0)
            # img = cv2.flip(img, 1)
        except Exception as e:
            print(f"Error fetching or decoding image: {e}")
            continue

        entered_name = read_word(WORDS_FILE).strip()
        if entered_name:
            model.set_classes([entered_name])
        results = model.predict(img, verbose=False)
        is_command = check_for_img_command(COMMAND_FILE_PATH)
        available_classes = set()

        if is_command:
            model.set_classes(general_classes)
            results_to_send = model.predict(img, verbose=False)
            if results_to_send[0].boxes.xyxy.cpu().numpy().size != 0:
                boxes = results_to_send[0].boxes.xyxy.cpu().numpy().astype(int)
                classes = results_to_send[0].boxes.cls.cpu().numpy().astype(int)
                img_cpy = img.copy()
                for clss, box in zip(classes, boxes):
                    class_name = general_classes[clss]
                    add_one_object(img_cpy, box, clss, class_name, colors_map)
                    available_classes.add(class_name.lower())
                cv2.imwrite(FORMED_IMG_NAME, img_cpy)
                with open(CURRENT_OBJECTS_PATH, "w") as file:
                    file.write("\n".join(available_classes))
            else:
                cv2.imwrite(FORMED_IMG_NAME, img)
                with open(CURRENT_OBJECTS_PATH, "w") as file:
                    file.write(" ")
            model.set_classes([entered_name])

        if results[0].boxes.xyxy.cpu().numpy().size != 0:
            track_box = results[0].boxes.xyxy.cpu().numpy().astype(int)[0]
            clss = results[0].boxes.cls.cpu().numpy().astype(int)[0]
            add_one_object(img, track_box, clss, entered_name, colors_map)
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

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
