# Arduino Servo Controller

This sketch reads rotation angles and drives three servo motors on an Arduino Uno.

## Wiring

- **Base servo** → Data Pin 4  
- **Left servo** (camera facing you) → Data Pin 3  
- **Right servo** → Data Pin 2  
- **All servos** → +5 V (use common ground with Arduino)

## Installation

1. Open the `.ino` file in the Arduino IDE.  
2. Select **Arduino Uno** as the board.  
3. Upload at 115200 bps.

## Usage

1. Send angle data over Serial (e.g. `$090090060` (`$090` - 90 deg, `$090` - 90 deg, `$060` - 60 deg)).
2. The sketch parses each value and moves the corresponding servo.
