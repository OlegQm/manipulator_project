# YOLOv8 Recognizer Manipulator

This folder contains the detection module that runs on a Raspberry Pi with a Hailo accelerator. It uses a YOLOv8 model to detect objects for the manipulator project.

## Setup

Run the installation script to create the virtual environment and download necessary resources:

```bash
cd hailo_scripts
./install.sh
cd ..
```

## Running

Start the detection pipeline with the provided model:

```bash
python3 hailo_remote_detection.py -i rpi -u \
    --hef models/dataset_v3_models/hailo_models/own_yolov8m_lca_light_v2_quantized_model.hef \
    --labels-json hailo_scripts/labels.json
```

Adjust the model or labels if you use your own dataset.
