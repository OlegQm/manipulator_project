# YOLO and HAILO Setup Guide (On Ubuntu 24.04, officially not supported)

## 1) Create environment (YOLO) with Python 3.10.18 (you may need to install it)

Create a virtual environment (`venv_yolov8` in my case):

```sh
python3.10 -m venv venv_yolov8
```

Activate the environment:

```sh
source venv_yolov8/bin/activate
```

Then download the **3.27.0 Hailo dataflow compiler** ([direct link](https://hailo.ai/?dl_dev=1&file=8791984ee2b2999850f5a55fbdb8c46f)) 
from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/). You may need to register.

Copy the downloaded file to the same directory as `hailo_model_zoo-2.11.0-py3-none-any.whl`.

Now install the required modules:

```sh
pip install -r yolo_env_requirements.txt
```

Then copy your `.pt` model to `<path_to>/pt_to_hef_converter/steps`,
for instance `best.pt` (in my case), and execute in terminal:

```sh
python3 simpify_model.py
```

And the copy best_fused.onnx to local_attenttion_yolov8m folder

---

## 2) Create environment (HAILO) with Python 3.10.18

Create a virtual environment (`venv_hailo` in my case):

```sh
deactivate
python3.10 -m venv venv_hailo
```

Install system dependencies (Ubuntu):

```sh
sudo apt update
sudo apt install -y \
    python3.10-dev python3.10-distutils \
    build-essential cython3 pkg-config \
    graphviz libgraphviz-dev
```

Activate the environment:

```sh
source venv_hailo/bin/activate
```

Now install the required modules:

```sh
python -m pip install -U pip wheel "setuptools<60"
python -m pip install numpy==1.23.5 cython==0.29.36
python -m pip install --no-binary :all: --no-build-isolation lap==0.4.0

python -m pip install --no-deps \
    hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl \
    hailo_model_zoo-2.11.0-py3-none-any.whl

pip install -r hailo_env_requirements.txt
```

Then enter your model name instead of `own_yolov8m_lca_light_v2`, `own_yolov8m_lca_light_v2.onnx` and `own_yolov8m_lca_light_v2.har` in `steps/parse.py`.
`local_attenttion_yolov8m` is the folder where `own_yolov8m_lca_light_v2.onnx` and `own_yolov8m_lca_light_v2.har` will be saved:

```python
onnx_model_name = 'own_yolov8m_lca_light_v2'
onnx_path = 'local_attenttion_yolov8m/own_yolov8m_lca_light_v2.onnx'
har_path = 'local_attenttion_yolov8m/own_yolov8m_lca_light_v2.har'
```

Then go to [Netron](https://netron.app/) (or any other model visualizer) and
open your `.onnx` model for visualization (`local_attenttion_yolov8m/own_yolov8m_lca_light_v2.onnx` in my case).

When visualizing the model, copy the names of the convolution layers before each output. The output with dimensions `1 * 64 * 20 * 20` is the regression head, and the one with dimensions `1 * 14 * 20 * 20` is the classification head. For example, in my case `/model.30/cv3.2/cv3.2.2/Conv` is the classification part (list all classification parts second), and `/model.30/cv2.2/cv2.2.2/Conv` is the regression part.

You will see two `Conv` layers. Click on the left one (`/model.22/cv2.0/cv2.0.2/Conv` in my case) and copy its name (`name`).
Repeat this for the second one (`/model.22/cv3.0/cv3.0.2/Conv` in my case).
Continue this process for the remaining layers, saving all names sequentially.

I have the following list:

```python
[
    '/model.30/cv2.0/cv2.0.2/Conv', '/model.30/cv3.0/cv3.0.2/Conv',
    '/model.30/cv2.1/cv2.1.2/Conv', '/model.30/cv3.1/cv3.1.2/Conv',
    '/model.30/cv2.2/cv2.2.2/Conv', '/model.30/cv3.2/cv3.2.2/Conv',
]
```

Copy this list and replace it in `steps/parse.py`.

Now execute the following command in the terminal:

```sh
python3.10 steps/parse.py
```

---

## 3) Add Images and Optimize

Add images to `data/images` following the instructions in `data/images/README.txt`,
and add captions to `data/labels`.

Also, add the images to `calibration_set` as instructed in `calibration_set/README.txt`.

Then open `steps/optimize.py`, find `MODEL_NAME`,
and copy the same name from `steps/parse.py` under `har_path`.

Now, enter the number of dataset classes in `NUM_CLASSES`
and specify the image size from the `.pt` model in `IMG_SIZE`.

To visualize the `.har` model, use:

```sh
hailo visualizer local_attenttion_yolov8m/own_yolov8m_lca_light_v2.har
```

(`local_attenttion_yolov8m/own_yolov8m_lca_light_v2.svg` in my case).

Now, locate all 6 output layers: `output_layer1`, `output_layer2`, ..., `output_layer6`.
Identify the `conv` layers preceding each of them.

In my case (`own_yolov8m_lca_light_v2.svg`), they are:

`conv57`, `conv58`, `conv68`, `conv69`, `conv78`, and `conv79`.

Save these names.

Now, copy the file `config/postprocess_config/own_yolov8m_lca_light_v2_nms_config.json`
and replace my names with yours. You can also rename the file as needed
(files for YOLO nano, medium, and large are already included).

Specify the path to this file in `alls`:

```python
alls = '''
quantisation_param([conv58, conv69, conv79], force_range_out=[0.0, 1.0])
normalisation1 = normalization([0.0, 0.0, 0.0, 0.0], [255.0, 255.0, 255.0])
nms_postprocess("config/postprocess_config/own_yolov8m_lca_light_v2_nms_config.json" meta_arch=yolov8, engine=cpu)
'''
```

Also, replace `[conv58, conv69, conv79]`
with the names of the `conv` layers before `output_layer2`, `output_layer4`, and `output_layer6`.

Now execute the following command:

```sh
python3.10 steps/optimize.py
```

After optimization, you can test the resulting model with:

```python
python3 test_har_emulator.py
```

---

## 4) Compile the Model

Open `steps/compile.py` and replace `model_name` with your model name.

Then execute:

```sh
python3.10 steps/compile.py
```

After this command, your `.hef` file will be generated.
The process may take some time.
