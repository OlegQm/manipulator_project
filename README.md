# Autonomous Object Recognition Manipulator

This is a solo project by **Oleh Savchenko** focused on building a self-made autonomous manipulator that can detect objects and react to user commands from a mobile app. The repository now combines hardware control, on-device vision, mobile UX, and a separate multimodal chatbot service for image Q&A.

---

## 📷 Photos

<img width="1920" height="1080" alt="bird_photo_for_readme_1" src="https://github.com/user-attachments/assets/3c9d5385-0a83-4f27-81d5-20a131e22268" />
<img width="1920" height="1080" alt="bird_photo_for_readme_2" src="https://github.com/user-attachments/assets/16c8b461-5542-4c83-aeed-d534cf7fc98f" />

---

## Project Structure

```
├── 3D_models
│   └── [3D models for printing device components]
├── programs
│   ├── arduino
│   │   ├── servos_and_led             # Servo + LED control sketch
│   │   └── old/esp32                  # Legacy ESP32 camera code
│   ├── mobile
│   │   └── manipulatorMobileApp       # Mobile app source code
│   ├── multimodal_chatbot             # FastAPI + LangGraph image Q&A service
│   └── objects_detection
│       ├── pt_to_hef_converter        # Convert trained models to HEF format
│       ├── robotic_arm_scripts        # Raspberry Pi + Hailo runtime scripts
│       └── custom_model               # Custom YOLO model configs and training assets
└── README.md
```

### 3D\_models

Contains all 3D-printable models for assembling the manipulator device.

### programs

* **arduino**: Arduino sketches for low-level manipulator control (servos/LED) and archived ESP32 experiments.
* **mobile/manipulatorMobileApp**: Xamarin.Forms mobile client (Android/iOS) used to configure bot access, send commands, and work with detected object lists.
* **objects\_detection**: Raspberry Pi object detection stack, custom model assets, and scripts for manipulator interaction.
* **multimodal\_chatbot**: Dockerized FastAPI service (LangGraph-based) that accepts text + image and returns responses, with Redis sessions and Nginx basic auth.

---

## 🌐 System Workflow

1. **User Request**: The user sends a command from the mobile app (for example, request screenshot / object list / selection).
2. **Bot Transport Layer**: Communication is currently handled through Telegram bot endpoints to keep infrastructure simple and low-cost.
3. **Detection Runtime**: The Raspberry Pi module in `programs/objects_detection/robotic_arm_scripts` runs inference (with Hailo acceleration when enabled).
4. **Result Delivery**: The app receives an image and/or recognized object names and renders them for user interaction.
5. **Selection Command**: The user chooses an object or action, and the command is sent back through the same channel.
6. **Actuation**: The detection/control side sends control signals to Arduino logic that drives the manipulator servos.

In parallel, the repository also includes `programs/multimodal_chatbot`, a standalone API flow for image + text question answering.

![image](https://github.com/user-attachments/assets/57ca8aa4-502c-43f5-a355-dea349cb5c62)

---

## 🍓 Raspberry Pi

The Raspberry Pi is the main compute node for on-device vision and control scripts. In the current setup, it works as the bridge between camera inference and actuator logic, and interfaces with:

* **Battery pack**
* **Arduino**
* **Display**
* **Power button**

<img width="960" height="469" alt="raspberry_pi_newest_device" src="https://github.com/user-attachments/assets/a0ebe9d5-7ac2-4496-8fee-5f7f11fc7747" />

---

## 🤖 Hailo AI Kit

The project uses the Hailo AI Kit as a hardware accelerator for real-time detection. The measured project-level comparison remains:

* **Raspberry Pi CPU**: YOLOv8n at 256×256 resolution → \~9 FPS
* **Hailo AI Kit**: YOLOv8m at 640×640 resolution → >100 FPS

<img width="960" height="475" alt="ai_kit_newest_device" src="https://github.com/user-attachments/assets/b43d1d7e-1a86-497d-99d5-a80d432c783f" />

---

## 🖨️ 3D Models

The mechanical design combines EEZYbotARM-based parts (purple) with custom printed components (black) adapted for this build.

<img width="1647" height="924" alt="image" src="https://github.com/user-attachments/assets/9f899904-bf0e-4698-b7d2-a17ea22b1f60" />

---

## 📱 Mobile Application

The mobile client is implemented with Xamarin.Forms and currently communicates with the device via Telegram bots. Typical setup:

1. Create two bots in a single chat:

   * **Manipulator bot** (device-side command receiver)
   * **User bot** (app-side interaction bot)
2. In the app, provide bot token and chat ID in the server settings screen.
3. Choose one of two operation modes:

   * **Objects List**: Manage/filter object names and send direct selection commands.
   * **Possible Objects**: Request fresh screenshot + caption from the device and pick from currently detected items.
4. Send a request, review response, and dispatch selection/search commands.

The app also supports object filtering by text prompt and by photo, which helps when the exact object name is unknown.

![image](https://github.com/user-attachments/assets/8ac4c757-1b7f-4d4a-bab2-d2177b3967b6)
![image](https://github.com/user-attachments/assets/6fb6a896-f102-4f7c-91d7-303cb5345019)
