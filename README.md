# Autonomous Object Recognition Manipulator

This is a solo project by **Oleh Savchenko**, aimed at creating a fully autonomous, self-built device capable of recognizing objects selected via a custom mobile application. The system integrates hardware components, AI-driven object detection, and intuitive user interaction through a mobile interface.

---

## 📷 Photos

![image](https://github.com/user-attachments/assets/40056989-6e84-4b2b-adb6-74e7e2116489)
![image](https://github.com/user-attachments/assets/45d18611-813d-4b63-b7f0-def2c072c46d)

---

## Project Structure

```
├── 3D_models
│   └── [3D models for printing device components]
├── programs
│   ├── arduino
│   │   ├── servos                     # Code for servo motors
│   │   └── old/esp32                  # Deprecated ESP32 camera code
│   ├── mobile
│   │   └── manipulatorMobileApp       # Mobile app source code
│   ├── objects_recognition            # Object detection setup on Raspberry Pi
│   └── pt_to_hef_converter            # Convert trained models to HEF format
└── README.md
```

### 3D\_models

Contains all 3D-printable models for assembling the manipulator device.

### programs

* **arduino**: Arduino sketches for controlling servo motors and legacy ESP32 camera modules.
* **mobile/manipulatorMobileApp**: Source code for the mobile application that sends commands and receives results from the device.
* **objects\_recognition**: Python scripts and configurations for object detection on a Raspberry Pi.
* **pt\_to\_hef\_converter**: Utility to convert PyTorch-trained models into HEF format optimized for the Hailo AI Kit accelerator.

---

## 🌐 System Workflow

1. **User Request**: The user sends a query via the mobile app, asking which objects the device sees.
2. **Server**: A server program receives the request and forwards it to the object recognition module.
3. **Object Detection**: The recognition module processes the camera feed, detects objects, and returns an annotated image plus a list of detected items.
4. **User Selection**: The mobile app displays the list, and the user selects the desired object.
5. **Command Dispatch**: The selection is sent back through the same pipeline to the recognition module.
6. **Actuation**: The recognition module signals the Arduino, which activates servo motors to physically track the chosen object.

![image](https://github.com/user-attachments/assets/57ca8aa4-502c-43f5-a355-dea349cb5c62)

---

## 🍓 Raspberry Pi

The Raspberry Pi serves as an energy-efficient and high-performance computer for object recognition. It interfaces with:

* **Battery pack**
* **Arduino**
* **Display**
* **Power button**

![image](https://github.com/user-attachments/assets/609eaace-a846-4e91-b363-97ee4fb4dc34)

---

## 🤖 Hailo AI Kit

The project leverages the Hailo AI Kit, a specialized accelerator for object detection tasks. Benchmark results:

* **Raspberry Pi CPU**: YOLOv8n at 256×256 resolution → \~9 FPS
* **Hailo AI Kit**: YOLOv8m at 640×640 resolution → >100 FPS

![image](https://github.com/user-attachments/assets/30269dce-7b4b-4198-aa8d-8022412a04c2)

---

## 🖨️ 3D Models

The device uses 3D models from the EEZYbotARM project (purple components) and custom-designed parts (black components).

![image](https://github.com/user-attachments/assets/fd1c634f-6133-43cd-9727-adaeeecfe192)

---

## 📱 Mobile Application

Communication between the app and device is handled via Telegram bots (to minimize costs). Setup steps:

1. Create two bots in a single chat:

   * **Manipulator bot** (connected to the device)
   * **User bot** (connected to the mobile app)
2. In the app, enter the bot token and chat ID.
3. Choose one of two modes:

   * **List Selection**: Filter and select objects from a predefined list.
   * **Live Recognition**: Select from objects currently visible to the device.
4. Send your request and view results.

Users can filter objects by name or by photo (helpful if you forget an object’s name).

![image](https://github.com/user-attachments/assets/8ac4c757-1b7f-4d4a-bab2-d2177b3967b6)
![image](https://github.com/user-attachments/assets/6fb6a896-f102-4f7c-91d7-303cb5345019)

