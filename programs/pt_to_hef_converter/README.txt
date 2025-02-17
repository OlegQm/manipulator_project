1) Create environment (YOLO) with Python 3.8.20 (`venv_yolov8` in my case):

After that activate environment:
`source venv_yolov8/bin/activate`

Then donload the 3.27.0 Hailo dataflow compiler (https://hailo.ai/?dl_dev=1&file=8791984ee2b2999850f5a55fbdb8c46f)
from https://hailo.ai/developer-zone/software-downloads/. You may need to register here.
Copy the downloaded file to the same directory as `hailo_model_zoo-2.11.0-py3-none-any.whl`.

And install modules:
`pip install -r yolo_env_requirements.txt`

Then copy your .pt model in `/pt_to_hef_converter`,
for instance `yolov8m_model_v15_640.pt` (my case), and execute in terminal:
`yolo export model=./yolov8m_model_v15_640.pt imgsz=640 format=onnx opset=11`


2) Create environment (HAILO) with Python 3.8.20 (`venv_hailo` in my case):

After that activate environment:
`source venv_hailo/bin/activate`

And install modules:
`pip install -r hailo_env_requirements.txt`

Then enter your model name instead of `yolov8m_model_v15_640`, `yolov8m_model_v15_640.onnx`
and `yolov8m_model_v15_640.har` in `steps/parse.py`. `yolov8m_640_v15` is the folder where the
`yolov8m_model_v15_640.onnx` and `yolov8m_model_v15_640.har` will be saved:

`onnx_model_name = 'yolov8m_model_v15_640'`
`onnx_path = 'yolov8m_640_v15/yolov8m_model_v15_640.onnx'`
`har_path = 'yolov8m_640_v15/yolov8m_model_v15_640.har'`

Then move to https://netron.app/ (or any other model) and visualize your `.onnx` (in the future instructions I will refer
to yolov8m_640_v15/yolov8m_model_v15_640.onnx` visualization, that's my case):
On the image you will find the last `Concat` layer, which includes the 3 arrows (`/model.22/Concat_3` on
`yolov8m_model_v15_640.onnx` visualization).

Then go up the leftmost branch of this word all the way to `Reshape'. After that you will see 2 `Conv` layers.
Click on the left one (`/model.22/cv2.0/cv2.0.2/Conv` in my case) and copy its name (`name`),
do the same with the second one (`/model.22/cv3.0/cv3.0.2/Conv` in my case)
and copy its name right after the first one.
Do the same with the rest of the layers, saving all the names one after the other. I have such a list:
`[
        '/model.22/cv2.0/cv2.0.2/Conv',
        '/model.22/cv3.0/cv3.0.2/Conv',
        '/model.22/cv2.1/cv2.1.2/Conv',
        '/model.22/cv3.1/cv3.1.2/Conv',
        '/model.22/cv2.2/cv2.2.2/Conv',
        '/model.22/cv3.2/cv3.2.2/Conv'
]`
After that, copy this list instead of mine into `steps/parse.py`.

Then go to the terminal and execute:
`python3.8 steps/parse.py`


3) Add images to `data/images` following the instructions in `data/images/README.txt`, and add captions to `data/labels`.
Also add the images to `calibration_set` as instructed in `calibration_set/README.txt`.
Then open `steps/optimize.py` and in `MODEL_NAME`, copy the same name that was in the `steps/parse.py` file in `har_path`.
Now enter the number of classes from the dataset in `NUM_CLASSES` and enter the image size in the `.pt` model to `IMG_SIZE`.

Then visualise the `.har` model using the `hailo visualizer yolov8m_640_v15/yolov8m_model_v15_640.har`
command (`yolov8m_640_v15/yolov8l_model_v16_640.svg` in my case).

Now find all 6 output layers: `output_layer1`, `output_layer2`,..., `output_layer6` and look at the `conv` layers in front of each of them.
In my case (`yolov8l_model_v16_640.svg`) these are layers `conv57`, `conv58`, `conv70`, `conv71`, `conv82` and `conv83`, keep these names.
After that copy the file `config/postprocess_config/yolov8m_nms_config.json` to yourself and replace my names with your own,
you can also rename the file as desired. Also specify the path to this file in `alls`:

alls = '''
quantisation_param([conv58, conv71, conv83], force_range_out=[0.0, 1.0])
normalisation1 = normalization([0.0, 0.0, 0.0, 0.0], [255.0, 255.0, 255.0])
nms_postprocess("config/postprocess_config/yolov8m_nms_config.json" meta_arch=yolov8, engine=cpu)
'''
Also in `alls` replace the names `[conv58, conv71, conv83]` with the names of the `conv` layers before `output_layer2`,
`output_layer4` and `output_layer6`.

Then go to the terminal and execute:
`python3.8 steps/optimize.py`


4) Go to `steps/compile.py`. Replace `model_name` with your model name. Then go to the terminal and execute:
`python3.8 steps/compile.py`

After this command you will get your `.hef` file, the command may take a long time.
