from ultralytics import YOLO

model = YOLO("./best.pt")

model.export(
    format="onnx",
    imgsz=640,
    opset=11,
    dynamic=False,
    simplify=True,
    project="custom_yolov8m",
    name="best_fused"
)

print("Ready! Look at custom_yolov8m/best_fused.onnx")

