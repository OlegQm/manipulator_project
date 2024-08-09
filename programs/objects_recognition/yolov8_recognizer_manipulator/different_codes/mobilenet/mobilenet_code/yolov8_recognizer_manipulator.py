import cv2
import os
import sys
import random
import platform
from threading import Thread
from pathlib import Path
#from cvzone import SerialModule
import numpy as np
import time

thres = 0.45  # Threshold to detect object
iou = 0.4

# serial = SerialModule.SerialObject("COM16", 9600, 3) # "/dev/ttyUSB0"
cap = cv2.VideoCapture(0) # url -> 0
cap.set(3, 1280)
cap.set(4, 720)
cap.set(10, 70)
# if not cap.isOpened():
#     print("Failed to open the IP camera stream")
#     sys.exit(1)

CLASS_FILE = "coco.names"
WORDS_FILE = "words_file.txt"
GET_IMG_COMMAND = "<TSC>"
FORMED_IMG_NAME = "currentObjectsScreenshot.jpg"
COMMAND_FILE_PATH = "screenshotRequest.txt"
CURRENT_OBJECTS_PATH = "currentObjects.txt"
PROTOTXT_PATH = "mobilenet_files/deploy.prototxt"
MODEL_PATH = "mobilenet_files/mobilenet_iter_73000.caffemodel"
CLASSES = np.array(["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", 
        "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", 
        "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"])
CLASSES_IDS = np.arange(CLASSES.size)

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
    
    distance_x, distance_y = get_distance(screen_center_x, screen_center_y, obj_center_x, obj_center_y)
    
    server = Thread(target=one_turn, args=(distance_x, distance_y))
    server.start()
    
    cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    cv2.circle(img, (int(obj_center_x), int(obj_center_y)), 10, (0, 0, 255), 2)
    
    cv2.putText(img, f"{obj_name} Dis X: {distance_x} Dis Y: {distance_y}", 
                (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
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

def preprocess_image(image):
    return cv2.dnn.blobFromImage(image, 0.007843, (300, 300), 127.5)

def detect_objects(net, image):
    blob = preprocess_image(image)
    net.setInput(blob)
    detections = net.forward()
    return detections

def draw_detections(image, detections, target_class_name,
                    colors_map, confidence_threshold=thres):
    (h, w) = image.shape[:2]
    available_classes = set()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            idx = int(detections[0, 0, i, 1])
            class_name = CLASSES[idx]
            if class_name in target_class_name:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                add_one_object(image, box, idx, class_name, colors_map)
                available_classes.add(class_name.lower())

    return image, available_classes

system = platform.system()
server_path = find_executable_path("", system)

def main():
    with open(WORDS_FILE, 'w') as f:
        f.write("")
    delete_file_if_exists(FORMED_IMG_NAME)
    
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
        
        colors_map = {key : generate_color(key) for key, _ in enumerate(CLASSES)}
        entered_name = read_word(WORDS_FILE).strip()
        
        model = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
        detections = detect_objects(model, img)
        is_command = check_for_img_command(COMMAND_FILE_PATH)
        
        if is_command:
            if detections.shape[2] != 0:
                img_cpy = img.copy()
                img_cpy, available_classes = draw_detections(img_cpy, detections, CLASSES,
                                                             colors_map=colors_map)
                cv2.imwrite(FORMED_IMG_NAME, img_cpy)
                with open(CURRENT_OBJECTS_PATH, 'w') as file:
                    file.write("\n".join(available_classes))
            else:
                cv2.imwrite(FORMED_IMG_NAME, img)
                with open(CURRENT_OBJECTS_PATH, 'w') as file:
                    file.write(" ")
                    
        class_ids = detections[0, 0, :, 1].astype(int)
        class_boxes = detections[0, 0, :, 3:7]
        target_index = np.where(CLASSES == entered_name)[0]
        (h, w) = img.shape[:2]
                
        if target_index in class_ids:
            screen_center_x = img.shape[1] // 2
            screen_center_y = img.shape[0] // 2
            
            target_index_pos = np.where(class_ids == target_index)[0]
            
            track_box = class_boxes[target_index_pos] * np.array([w, h, w, h])
            
            add_one_object(img, track_box[0], target_index,
                           entered_name, colors_map)
            fps = 1.0 / (time.time() - start_time)

            cv2.putText(img, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Output", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()