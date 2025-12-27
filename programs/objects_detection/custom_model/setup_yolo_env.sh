#!/bin/bash

set -e

PATH_TO_CUSTOM_YOLO_MODEL_TRAINER="path_to_yolo_model_trainer_parent_folder"

echo "=== Cloning dataset repo ==="
cd ~
git clone https://github.com/OlegQm/manipulator_project_datasets || echo "Repo manipulator_project_datasets already exists"

echo "=== Update apt and install dependencies ==="
sudo apt update
sudo apt install -y python3.12 python3.12-venv
sudo apt update
sudo apt install -y libgl1
sudo apt update
sudo apt install -y nvidia-driver-535 nvidia-utils-535

echo "=== Download the testing image ==="
cd "$PATH_TO_CUSTOM_YOLO_MODEL_TRAINER/ultralytics_custom/ultralytics/assets/"
wget -nc https://ultralytics.com/images/bus.jpg

echo "=== Virtual environment setup ==="
cd "$PATH_TO_CUSTOM_YOLO_MODEL_TRAINER"
python3.12 -m venv yolo_trainer
source yolo_trainer/bin/activate

echo "=== Install Ultralytics in editable-mode ==="
cd "$PATH_TO_CUSTOM_YOLO_MODEL_TRAINER/ultralytics_custom"
pip install --upgrade pip
pip install -e .
