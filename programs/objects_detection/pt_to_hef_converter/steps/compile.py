from hailo_sdk_client import ClientRunner

model_name = 'own_yolov8m_lca_light_v2_quantized_model'
quantized_model_har_path = f'<path_to>/manipulator_project/programs/pt_to_hef_converter/local_attenttion_yolov8m/{model_name}.har'

runner = ClientRunner(har=quantized_model_har_path)

hef = runner.compile()

file_name = f'{model_name}.hef'
with open(file_name, 'wb') as f:
    f.write(hef)

# har_path = f'{model_name}_compiled_model.har'
# runner.save_har(har_path)
# !hailo profiler {har_path}
