#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const int ledPin = 4;
const int ledChannel = 0;
const int freq = 5000;
const int resolution = 8;
const int ledOn = 32;
const int ledOff = 0;
 
const char* WIFI_SSID = "OnePlus 10T";
const char* WIFI_PASS = "25Oleg25";
 
WebServer server(80);
 
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);
void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    ledcWrite(ledChannel, ledOff);
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));
 
  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}
 
void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}
 
void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}
 
void handleJpgMid()
{
  if (!esp32cam::Camera.changeResolution(midRes)) {
    Serial.println("SET-MID-RES FAIL");
  }
  serveJpg();
}
 
void checkConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    ledcWrite(ledChannel, ledOff);
    Serial.println("Connecting to WiFi...");
    WiFi.disconnect();
    WiFi.reconnect();

    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startTime < 5000) {
      delay(500);
      Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\nReconnected to WiFi");
      ledcWrite(ledChannel, ledOn);
    } else {
      Serial.println("\nFailed to reconnect to WiFi");
    }
  }
}
 
void setup() {
  Serial.println("setup\n");
  Serial.begin(115200);
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(ledPin, ledChannel);
  Serial.println();
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
 
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  checkConnection();
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  // Serial.println("  /cam-lo.jpg");
  // Serial.println("  /cam-mid.jpg");
  Serial.println("  /cam-hi.jpg");
 
  // server.on("/cam-lo.jpg", handleJpgLo);
  // server.on("/cam-mid.jpg", handleJpgMid);
  server.on("/cam-hi.jpg", handleJpgHi);
  ledcWrite(ledChannel, ledOn);

  delay(500);
 
  server.begin();
}
 
void loop() {
  server.handleClient();
  
  checkConnection();
}