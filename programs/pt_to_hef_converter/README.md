# YOLO and HAILO Setup Guide

## 1) Create environment (YOLO) with Python 3.8.20

Create a virtual environment (`venv_yolov8` in my case):

```sh
python3.8 -m venv venv_yolov8
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

Then copy your `.pt` model to `/pt_to_hef_converter`,  
for instance `yolov8m_model_v15_640.pt` (in my case), and execute in terminal:

```sh
yolo export model=./yolov8m_model_v15_640.pt imgsz=640 format=onnx opset=11
```

---

## 2) Create environment (HAILO) with Python 3.8.20

Create a virtual environment (`venv_hailo` in my case):

```sh
python3.8 -m venv venv_hailo
```

Activate the environment:

```sh
source venv_hailo/bin/activate
```

Now install the required modules:

```sh
pip install -r hailo_env_requirements.txt
```

Then enter your model name instead of `yolov8m_model_v15_640`, `yolov8m_model_v15_640.onnx`,  
and `yolov8m_model_v15_640.har` in `steps/parse.py`.  
`yolov8m_640_v15` is the folder where `yolov8m_model_v15_640.onnx` and `yolov8m_model_v15_640.har` will be saved:

```python
onnx_model_name = 'yolov8m_model_v15_640'
onnx_path = 'yolov8m_640_v15/yolov8m_model_v15_640.onnx'
har_path = 'yolov8m_640_v15/yolov8m_model_v15_640.har'
```

Then go to [Netron](https://netron.app/) (or any other model visualizer) and  
open your `.onnx` model for visualization (`yolov8m_640_v15/yolov8m_model_v15_640.onnx` in my case).  

Find the last `Concat` layer, which includes 3 arrows (`/model.22/Concat_3` on `yolov8m_model_v15_640.onnx` visualization).

Now, follow the leftmost branch all the way to `Reshape`.  
You will see two `Conv` layers. Click on the left one (`/model.22/cv2.0/cv2.0.2/Conv` in my case) and copy its name (`name`).  
Repeat this for the second one (`/model.22/cv3.0/cv3.0.2/Conv` in my case).  
Continue this process for the remaining layers, saving all names sequentially.  

I have the following list:

```python
[
    '/model.22/cv2.0/cv2.0.2/Conv',
    '/model.22/cv3.0/cv3.0.2/Conv',
    '/model.22/cv2.1/cv2.1.2/Conv',
    '/model.22/cv3.1/cv3.1.2/Conv',
    '/model.22/cv2.2/cv2.2.2/Conv',
    '/model.22/cv3.2/cv3.2.2/Conv'
]
```

Copy this list and replace it in `steps/parse.py`.

Now execute the following command in the terminal:

```sh
python3.8 steps/parse.py
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
hailo visualizer yolov8m_640_v15/yolov8m_model_v15_640.har
```

(`yolov8m_640_v15/yolov8l_model_v16_640.svg` in my case).

Now, locate all 6 output layers: `output_layer1`, `output_layer2`, ..., `output_layer6`.  
Identify the `conv` layers preceding each of them.  

In my case (`yolov8l_model_v16_640.svg`), they are:  

`conv57`, `conv58`, `conv70`, `conv71`, `conv82`, and `conv83`.  

Save these names.

Now, copy the file `config/postprocess_config/yolov8m_nms_config.json`  
and replace my names with yours. You can also rename the file as needed  
(files for YOLO nano, medium, and large are already included).  

Specify the path to this file in `alls`:

```python
alls = '''
quantisation_param([conv58, conv71, conv83], force_range_out=[0.0, 1.0])
normalisation1 = normalization([0.0, 0.0, 0.0, 0.0], [255.0, 255.0, 255.0])
nms_postprocess("config/postprocess_config/yolov8m_nms_config.json" meta_arch=yolov8, engine=cpu)
'''
```

Also, replace `[conv58, conv71, conv83]`  
with the names of the `conv` layers before `output_layer2`, `output_layer4`, and `output_layer6`.

Now execute the following command:

```sh
python3.8 steps/optimize.py
```

---

## 4) Compile the Model

Open `steps/compile.py` and replace `model_name` with your model name.  

Then execute:

```sh
python3.8 steps/compile.py
```

After this command, your `.hef` file will be generated.  
The process may take some time.
