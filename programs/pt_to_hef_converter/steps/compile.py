from hailo_sdk_client import ClientRunner

model_name = 'yolov8m_model_v15_640'
quantized_model_har_path = f'yolov8m_640_v15/{model_name}_quantized_model.har'

runner = ClientRunner(har=quantized_model_har_path)

hef = runner.compile()

file_name = f'{model_name}.hef'
with open(file_name, 'wb') as f:
    f.write(hef)

# har_path = f'{model_name}_compiled_model.har'
# runner.save_har(har_path)
# !hailo profiler {har_path}