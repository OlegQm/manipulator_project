# Background

The device is controlled by three servos via Arduino:
The left and right servos are used to adjust the camera height.
The bottom servo (in the base) rotates the device.

I could have done without Arduino, but I added it as an extra layer against high-voltage events and incorrect wiring.

# Arduino Servo Controller

This sketch reads rotation angles and drives three servo motors on an Arduino Uno.

## Wiring

- **Flashlight** → Data Pin 5
- **Base servo** → Data Pin 4
- **Left servo** (camera facing you) → Data Pin 3
- **Right servo** → Data Pin 2 
- **All servos and flashlight** → +5 V (use common ground with Arduino)

## Installation

1. Open the `.ino` file in the Arduino IDE. 
2. Select **Arduino Uno** as the board. 
3. Upload at 115200 bps.

## Usage

1. Send angle data over Serial (e.g. `$090090060` (`$090` - 90 deg, `$090` - 90 deg, `$060` - 60 deg)).
2. The sketch parses each value and moves the corresponding servo.
3. Send `@ON` to turn the flashlight on and `@OFF` to turn it off.
