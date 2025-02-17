# Importing required libraries
from hailo_sdk_client import ClientRunner
import os
import random
import numpy as np
from PIL import Image

# Define constants
IMAGES_PATH = '/pt_to_hef_converter/data/images'
LABELS_PATH = '/pt_to_hef_converter/data/labels'
OUTPUT_CALIB_PATH = '/pt_to_hef_converter/calibration_set'
MODEL_NAME = 'yolov8m_640_v15/yolov8m_model_v15_640.har'
QUANTIZED_MODEL_NAME = f'{MODEL_NAME}_quantized_model.har'
NUM_CLASSES = 14
IMAGES_PER_CLASS = 4
IMG_SIZE = 640  # Image size for calibration dataset

# Helper function to create a stratified calibration set
def create_stratified_calib_set(images_path, labels_path, output_path, num_classes, images_per_class):
    class_dict = {i: [] for i in range(num_classes)}

    # Group images by class
    for label_file in os.listdir(labels_path):
        if label_file.endswith('.txt'):
            with open(os.path.join(labels_path, label_file), 'r') as f:
                for line in f:
                    class_id = int(line.split()[0])
                    class_dict[class_id].append(label_file.replace('.txt', '.jpg'))
                    break  # Use first class from annotation

    # Select a subset of images for each class
    calib_set = []
    for class_id, files in class_dict.items():
        selected_files = random.sample(files, min(len(files), images_per_class))
        calib_set.extend(selected_files)

    # Save selected images to a separate folder
    os.makedirs(output_path, exist_ok=True)
    for img_name in calib_set:
        img_src = os.path.join(images_path, img_name)
        img_dst = os.path.join(output_path, img_name)
        Image.open(img_src).resize((IMG_SIZE, IMG_SIZE)).save(img_dst)

    print(f"Created stratified calibration set with {len(calib_set)} images in {output_path}")

# Preprocessing function
def preproc(image_path):
    image = Image.open(image_path).convert('RGB')
    image = image.resize((IMG_SIZE, IMG_SIZE))
    return np.array(image, dtype=np.int16)

# Create calibration set
create_stratified_calib_set(IMAGES_PATH, LABELS_PATH, OUTPUT_CALIB_PATH, NUM_CLASSES, IMAGES_PER_CLASS)

# Prepare calibration dataset
calib_images = [os.path.join(OUTPUT_CALIB_PATH, img) for img in os.listdir(OUTPUT_CALIB_PATH)]
calib_dataset = np.array([preproc(img) for img in sorted(calib_images)], dtype=np.int16)
print(f"Loaded calibration dataset with shape: {calib_dataset.shape}")

# Save calibration dataset for reuse
np.save('calib_set.npy', calib_dataset)

# Ensure HAR file exists
assert os.path.isfile(MODEL_NAME), f"HAR file {MODEL_NAME} not found. Please provide a valid path."

# Load HAR file and perform optimization
runner = ClientRunner(har=MODEL_NAME)
alls = '''
quantization_param([conv58, conv71, conv83], force_range_out=[0.0, 1.0])
normalization1 = normalization([0.0, 0.0, 0.0], [255.0, 255.0, 255.0])
nms_postprocess("config/postprocess_config/yolov8m_nms_config.json", meta_arch=yolov8, engine=cpu)
'''

runner.load_model_script(alls)
runner.optimize(calib_dataset)

# Save quantized HAR file
runner.save_har(QUANTIZED_MODEL_NAME)
print(f"Quantized HAR model saved to {QUANTIZED_MODEL_NAME}")
