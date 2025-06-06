# ESP32-CAM Video Streamer

This sketch boots an ESP32-Wrover module with camera, connects to Wi-Fi, and streams JPEG frames over HTTP.

## Wiring

- **5 V** → VIN (or 5 V) pin on ESP32 module  
- **GND** → GND pin on ESP32 module  
- **LED (flash)** → GPIO 4 (configured as PWM output)  
- **Camera** → Built-in camera header (uses Ai-Thinker pin mapping)  
- **Common ground** between camera module and ESP32

> **Note:** No other external connections are required—power on the board and camera initialization happens in code.

## Configuration

1. Open the `.ino` file in the Arduino IDE (select "ESP32 Wrover Module" as the board).  
2. Set your network credentials:
    
        const char* WIFI_SSID = "WIFI_NETWORK_NAME";
        const char* WIFI_PASS = "WIFI_NETWORK_PASSWORD";
    
3. Optionally adjust:
   - PWM LED brightness (`freq`, `resolution`, `ledOn`, `ledOff`)  
   - JPEG quality (`cfg.setJpeg(80)`)  
   - Resolution presets (`loRes`, `midRes`, `hiRes`)

## Installation

1. Install the **ESP32** board support via Boards Manager.  
2. Install the **esp32cam** library.  
3. Select **115200 bps** for Serial Monitor.  
4. Upload the sketch to your ESP32-Wrover module.

## Usage

1. After power-up, the module will:
   - Initialize camera (hi-res by default)  
   - Connect to Wi-Fi (status printed in Serial)  
   - Start HTTP server on port 80  
2. Check Serial Monitor for your module’s IP address, for example:
    
        http://192.168.1.42
          /cam-hi.jpg
    
3. Open a browser or embed the URL:
   - **High-resolution stream:**  
        
        http://<ESP32_IP>/cam-hi.jpg  
     
   - *(You can enable `/cam-lo.jpg` and `/cam-mid.jpg` by uncommenting the handlers in code.)*

## Endpoints

- **/cam-hi.jpg** → capture at 800×600  
- **/cam-mid.jpg** → capture at 350×530  
- **/cam-lo.jpg** → capture at 320×240  
