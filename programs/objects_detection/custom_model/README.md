Custom Ultralytics YOLO Extensions
==================================

This repository packages a customized [Ultralytics 8.3.160](https://community.ultralytics.com/t/new-release-ultralytics-v8-3-160/1185) build with additional layers for better small-object detection. The key addition is Local Context Attention (LCA), wired into Ultralytics' registry so it can be used directly in model YAMLs. A reference model (`own_yolov8m_lca_light_v2.yaml`) shows how to integrate the new blocks.

Contents
--------
- `ultralytics_custom/`: editable Ultralytics package with custom modules registered.
- `ultralytics_custom/ultralytics/nn/modules/custom_modules.py`: LCA, ConvLCA, and a Hailo-friendly Detect head.
- `own_yolov8m_lca_light_v2.yaml`: example YOLOv8 model using the custom layers.
- `trainer.py`: training entrypoint with default hyperparameters and resume/debug switches.
- `setup_yolo_env.sh`: helper to provision a Python 3.12 venv, install GPU drivers, and install the editable package.

Requirements
------------
- Python 3.12 (script installs `python3.12` and `python3.12-venv` on Ubuntu).
- NVIDIA driver/toolkit for GPU training (script installs driver 535).
- Access to the dataset repo `https://github.com/OlegQm/manipulator_project_datasets` (clone happens in the setup script).

Quickstart (scripted)
---------------------
1. Set the path to this project in `setup_yolo_env.sh`:
   - Edit `PATH_TO_CUSTOM_YOLO_MODEL_TRAINER` to the parent directory that contains `ultralytics_custom`.
2. Run the setup:
   ```bash
   bash setup_yolo_env.sh
   ```
   The script will clone the dataset repo (if accessible), fetch a sample image, create the `yolo_trainer` venv, and install the package in editable mode.

Manual Installation
-------------------
```bash
cd ultralytics_custom
python3.12 -m venv ../yolo_trainer
source ../yolo_trainer/bin/activate
pip install --upgrade pip
pip install -e .
```
If you need the demo image, download it to `ultralytics_custom/ultralytics/assets/`:
```bash
wget -nc https://ultralytics.com/images/bus.jpg -P ultralytics_custom/ultralytics/assets/
```

Training
--------
- Configure `trainer.py`:
  - `model_cfg`: path to a model YAML (e.g., `own_yolov8m_lca_light_v2.yaml`).
  - `data_cfg`: path to your `data.yaml`.
  - Toggle `FAST_DEBUG` for a 1-epoch sanity run; toggle `RESUME` to continue from a previous checkpoint in `runs/train/.../weights/best.pt`.
- Launch training:
  ```bash
  source yolo_trainer/bin/activate
  python trainer.py
  ```

Custom Layers
-------------
- `LocalContextAttention`: depthwise conv + bottleneck + sigmoid gate for local context.
- `LCA`: attention-only wrapper; use it like `- [from, 1, LCA, [channels]]`.
- `ConvLCA`: convolution followed by LCA; drop-in where ConvSE might be used.
- `Detect_HailoFriendly`: identical to Ultralytics Detect during training; splits bbox/cls heads separately during ONNX export for Hailo compatibility.

Example model usage (`own_yolov8m_lca_light_v2.yaml`)
-----------------------------------------------------
```yaml
backbone:
  - [-1, 1, ConvLCA, [128, 3, 2]]
  - [-1, 1, LCA,     [128]]

head:
  - [-1, 1, C2f, [128, False, ConvLCA]]   # LCA-enhanced head block
  - [[23, 26, 29], 1, Detect_HailoFriendly, [nc]]
```
Use this file as a template for new architectures; the custom modules are already registered in the package.
