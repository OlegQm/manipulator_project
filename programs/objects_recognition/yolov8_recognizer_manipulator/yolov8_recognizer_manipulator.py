import cv2
import os
import sys
import random
import platform
from threading import Thread
from pathlib import Path
from ultralytics import YOLO
from cvzone import SerialModule
import urllib.request
import numpy as np
import time

thres = 0.45  # Threshold to detect object
iou = 0.4

# serial = SerialModule.SerialObject("COM16", 9600, 3) # "/dev/ttyUSB0"
#url = "http://192.168.233.156/cam-hi.jpg"
cap = cv2.VideoCapture(0) # url -> 0
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 70)
# if not cap.isOpened():
#     print("Failed to open the IP camera stream")
#     sys.exit(1)

CLASS_FILE = "coco.names"
WORDS_FILE = "words_file.txt"
GET_IMG_COMMAND = "<TSC>"
FORMED_IMG_NAME = "currentObjectsScreenshot.jpg"
COMMAND_FILE_PATH = "screenshotRequest.txt"
CURRENT_OBJECTS_PATH = "currentObjects.txt"
MODEL_PATH = "models/yolov8n_model_v9_224.pt" # yolov10n_v5_lite_416.pt

STOP_RADIUS = 85
STEP = 1
SERVOS_NUMBER = 3
SERVOS_LIMITS = np.array([[0, 60], [60, 155], [0, 180]])
current_angles = np.array([20, 60, 90])

#serial.sendData(current_angles)

def activate_server(path_to_server, platform):
    if platform == "Windows":
        os.system(path_to_server)
    elif platform == "Linux":
        os.system(f"export PATH=$PATH:~/dotnet-core ; dotnet {path_to_server}")
    else:
        os.system(f"dotnet {path_to_server}")

def read_word(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"File reading error: {e}")
        return None

def check_for_img_command(path):
    try:
        with open(path, 'r') as file:
            for line in file:
                if GET_IMG_COMMAND in line:
                    with open(path, 'w') as f:
                        f.write("")
                    return True
        return False
    except FileNotFoundError:
        print(f"File '{path}' not found.")
        return False

def is_in(angle, interval):
        return interval[0] <= angle <= interval[1]

def roll_back(current_angles, changes,
              i, new_angle, limits):
    if i == 1 and new_angle < limits[0] and (
        current_angles[0] + STEP > SERVOS_LIMITS[0][1]):
        return 1
    elif i == 1 and new_angle > limits[1] and (
        current_angles[0] - STEP < SERVOS_LIMITS[0][0]):
        return 1
    return 0

def update_angles(current_angles, changes):
    previous_angles = current_angles.copy()

    for i in range(SERVOS_NUMBER):
        new_angle = current_angles[i] + changes[i]
        limits = SERVOS_LIMITS[i]
        
        if roll_back(current_angles, changes,
              i, new_angle, limits):
            current_angles = previous_angles.copy()
            break
        
        if is_in(new_angle, limits):
            current_angles[i] = new_angle
        elif new_angle < limits[0]:
            if i == 1 and (
                (current_angles[0] + STEP) <= SERVOS_LIMITS[0][1]):
                current_angles[0] += STEP
            current_angles[i] = limits[0]
        elif new_angle > limits[1]:
            if i == 1 and (
                (current_angles[0] - STEP) >= SERVOS_LIMITS[0][0]):
                current_angles[0] -= STEP
            current_angles[i] = limits[1]

def one_turn(distance_x, distance_y):
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
    #serial.sendData(current_angles)
    
def get_distance(screen_center_x, screen_center_y,
                  obj_center_x, obj_center_y):
    return obj_center_x - screen_center_x, obj_center_y - screen_center_y

def add_one_object(img, box, obj, obj_name, colors_map):
    color = colors_map[int(obj)]
    
    screen_center_x = img.shape[1] // 2
    screen_center_y = img.shape[0] // 2

    x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
    
    obj_center_x = (x1 + x2) // 2
    obj_center_y = (y1 + y2) // 2
    
    distance_x, distance_y = get_distance(screen_center_x, screen_center_y,
                                            obj_center_x, obj_center_y)
    server = Thread(target=one_turn, args=(distance_x, distance_y))
    server.start()

    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.circle(img, (obj_center_x, obj_center_y), 10, (0, 255, 0), -1)
    cv2.circle(img, (screen_center_x, screen_center_y), 10, (0, 0, 255), 2)
    cv2.putText(img, f"{obj_name.upper()} Dis X: {distance_x} Dis Y: {distance_y}",
                    (x1, y1),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2,
                )
    #server.join()

def generate_color(color_id):
    random.seed(int(color_id))
    color = (random.randint(0,255),
                random.randint(0,255),
                random.randint(0,255))
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
        os.system(f"export PATH=$PATH:~/dotnet-core ; dotnet {path_to_server}")

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
        }
    }

    system = platform.system()  # "Linux", "Darwin", "Windows"
    architecture = platform.machine()  # "x86_64", "armv7l", "aarch64"

    arch_folder = system_arch_mapping.get(system, {}).get(architecture, "")
    if not arch_folder:
        raise Exception(f"Unsupported system or architecture: {system}, {architecture}")

    executable_folder = os.path.join(base_path, "server_part",
                                        system, arch_folder)
    executable_file = "manipulatorServerPart" + (".exe" if system == "Windows" else ".dll");

    return os.path.join(executable_folder, executable_file)

system = platform.system()
server_path = find_executable_path("", system)

def main():
    with open(WORDS_FILE, 'w') as f:
        f.write("")
    delete_file_if_exists(FORMED_IMG_NAME)
    model = YOLO(MODEL_PATH)
    class_names = model.model.names
    num_classes = len(class_names)
    class_ids = np.arange(num_classes) # list(range(num_classes))
    
    class_index_map = {value: key for key, value in class_names.items()}
    colors_map = {key : generate_color(key) for key, _ in class_names.items()}
    
    server = Thread(target=activate_server, args=(server_path, system,))
    server.start()

    while True:
        start_time = time.time()
        try:
            # img_resp = urllib.request.urlopen(url)
            # imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            # img = cv2.imdecode(imgnp, -1)
            ret, img = cap.read()
            #img = cv2.flip(img, 0)
            #img = cv2.flip(img, 1)
        except Exception as e:
            print(f"Error fetching or decoding image: {e}")
            continue
        
        entered_name = read_word(WORDS_FILE).strip()
        name_index = []
        if entered_name:
            name_index.append(class_index_map.get(entered_name, -1))
        results = model.track(img, iou=iou, conf=thres, imgsz=224,
                              verbose=False, tracker="botsort.yaml", classes=name_index)
        is_command = check_for_img_command(COMMAND_FILE_PATH)
        available_classes = set()
        
        if is_command:
            results_to_send = model.track(img, iou=iou, conf=thres, imgsz=224,
                                verbose=False, tracker="botsort.yaml", classes=class_ids)
            if results_to_send[0].boxes.id is not None:
                boxes = results_to_send[0].boxes.xyxy.cpu().numpy().astype(int)
                classes = results_to_send[0].boxes.cls.cpu().numpy().astype(int)
                img_cpy = img.copy()
                for clss, box in zip(classes, boxes):
                    class_name = class_names[clss]
                    add_one_object(img_cpy, box, clss, class_name, colors_map)
                    available_classes.add(class_name.lower())
                cv2.imwrite(FORMED_IMG_NAME, img_cpy)
                with open(CURRENT_OBJECTS_PATH, 'w') as file:
                    file.write("\n".join(available_classes))
            else:
                cv2.imwrite(FORMED_IMG_NAME, img)
                with open(CURRENT_OBJECTS_PATH, 'w') as file:
                    file.write(" ")
                
        if results[0].boxes.id is not None:
            screen_center_x = img.shape[1] // 2
            screen_center_y = img.shape[0] // 2
            
            track_box = results[0].boxes.xyxy.cpu().numpy().astype(int)[0]
            #classes = results[0].boxes.cls.cpu().numpy().astype(int)
            #ids = results[0].boxes.id.cpu().numpy().astype(int)
            
            #track_index = ids[0]
            #track_class = classes[0]
            
            add_one_object(img, track_box, name_index[0],
                           class_names[name_index[0]], colors_map)
            fps = 1.0 / (time.time() - start_time)

            cv2.putText(img, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # show_distance(img, track_box, screen_center_x, screen_center_y)

        cv2.imshow("Output", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()