#include <Servo.h>
#define numOfValsRec 3
#define digitsPerValRec 3

Servo servo1;
Servo servo2;
Servo servo3;

const int flashlightPin = 5;

int const STEP = 1;
int angles[] = {20, 60, 90};
int stringLength = numOfValsRec * digitsPerValRec + 1;
int counter = 0;
bool counterStart = false;
String recievedString = "";

void setup() {
  Serial.begin(9600);
  servo1.attach(2);
  servo2.attach(3);
  servo3.attach(4);

  servo1.write(angles[0]);
  servo2.write(angles[1]);
  servo3.write(angles[2]);

  pinMode(flashlightPin, OUTPUT);
  digitalWrite(flashlightPin, LOW);
}

void reciveData() {
  static String input = "";
  while (Serial.available()) {
    char c = Serial.read();
    input += c;
    if (input.endsWith("@ON")) {
      digitalWrite(flashlightPin, HIGH);
      input = "";
    } else if (input.endsWith("@OFF")) {
      digitalWrite(flashlightPin, LOW);
      input = "";
    } 
    else if (input.startsWith("$") && input.length() == stringLength) {
      for (int i = 0; i < 3; ++i) {
        angles[i] = input.substring(1 + i * 3, 1 + (i + 1) * 3).toInt();
      }
      input = "";
    }
    if (input.length() > 20) input = input.substring(input.length() - 20);
  }
}

void writeAngle(Servo serv, int& angle) {
  int passed = 0;
  while(passed < angle) {
    serv.write(STEP);
    passed += STEP;
    delay(5);
  }
}

void loop() {
  reciveData();

  if (angles[0] >= 0 && angles[0] <= 60) {
    servo1.write(angles[0]);
  }
    //writeAngle(servo1, angles[0]);
  if (angles[1] >= 50 && angles[1] <= 180) {
    servo2.write(angles[1]);
  }
    //writeAngle(servo2, angles[1]);
  if (angles[2] >= 0 && angles[2] <= 180) { 
    servo3.write(angles[2]);
  }
    //writeAngle(servo3, angles[2]);
}
