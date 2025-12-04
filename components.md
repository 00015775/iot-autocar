# Components Logic
---
## Combining L298N+DC motors, 2xIR sensors, Ultrasonic(HC-SR04) sensor+Servo(SG90) motor code so the system works as a single program

1. **IR sensors** (_mounted near the ground_) continuously check for obstacles at ground level.
2. **Ultrasonic sensor** (_mounted on a servo motor_) continuously checks the distance in the forward direction.
3. When either:
    * the **IR sensors** detect an obstacle, or
    * the **ultrasonic sensor** detects an object closer than a defined threshold,
    * the car **must stop immediately**.
4. When the car has stopped, the **servo motor** begins a full 180° scan to search for the clearest path:
    * The **servo** starts at its neutral position (90°).
    * It sweeps from 90° → 0°, then 0° → 180°, and finally returns 180° → 90°.
    * The **ultrasonic sensor** measures the distance at each angle.
    * While sweeping back and forth, some angles are scanned twice (e.g., 90°→0° and 0°→90°).
    * Duplicate readings are avoided and only one value for each angle is kept.
5. After the sweep, the program compares all stored distances and chooses the angle with the largest distance as the direction to move towards.
6. The **servo** then returns to its initial 90° position, but the **ultrasonic sensor** continues monitoring the front direction during driving.
7. Before moving toward the chosen direction, the car should reverse slightly to create space between itself and the detected obstacle standing in the front.
8. After reversing, the car rotates/moves toward the selected direction and continues driving normally.
9. This behavior repeats:
    * The **servo** only performs a sweep when an obstacle is detected by either the **IR sensors** or the **ultrasonic sensor**.
    * Otherwise, the car continues driving straight with continuous distance monitoring.


---

## Remote Control of the Car from 2-Axis HW-504 Joystick Module

The **HW-504 joystick** is physically wired to an Arduino. The Arduino reads the joystick's **SW**, **X** and **Y** pin values and sends these coordinates/values to the computer through a USB connection. Since the Raspberry Pi cannot be connected to the Arduino in this setup (*[it can be connected](https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/) but in this project the intention is to remotely control the car*), the computer acts as a bridge as it receives joystick inputs from Arduino and then sends that data across the local network to the RPi. RPi is connected to the same subnet as the computer, hence RPi can receive these coordinate values and interpret them as control commands for the car to be remotely controlled. 

To activate manual remote control, press the joystick twice (*twice!, and not once, in order to avoid accidental presses*). The car will stop and wait for coordinate inputs sent from the joystick to the Raspberry Pi. To exit remote control and return to autonomous mode, press the joystick twice again. The car will then resume navigating on its own(*based on description defined above*) using the **ultrasonic sensor**, **IR sensors**, and **Servo** to detect and avoid obstacles.

This architecture creates a clean separation of responsibilities:
* **Arduino Uno R3** handles input acquisition,
* **computer** handles data transmission, and
* **Raspberry Pi 3B v1.2** handles vehicle control.

### Remote control diagram

#### Hardware Flow
```
HW-504 Joystick
        ↓
     Arduino
        ↓ (USB connection)
     Computer
```
#### Network Flow
```
Computer
     ↓ (over local subnet)
Raspberry Pi 3B v1.2
     ↓
L298N motor → DC hobby motors
```
#### Complete End-to-End Flow
```
HW-504 Joystick
        ↓
     Arduino
        ↓ (USB connection)
     Computer
        ↓ (sends SW, X, Y over local subnet)
   Raspberry Pi 3B v1.2
        ↓
 L298N motor → DC hobby motors
```
#### Control-Flow and Component Diagrams (_for visual understanding_)

![control-flow-diagram](./diagrams/uml-diagrams/(edge-level)control-flow-diagram.png)

![component-diagram](./diagrams/uml-diagrams/(edge-level)component-diagram.png)

---

## Circuit Diagram

### Car chassis
![iot-autocar-full-circuit-diagram](./diagrams/circuit-diagrams/(_main_)iot-autocar-full-circuit-diagram.png)


### Remote joystick
![hw-504-joystick-rgb-led-circuit-diagram](./diagrams/circuit-diagrams/(_main_)hw-504-joystick-rgb-led-circuit-diagram.png)


## Sequential Order of locally running the program

As of now only **3 folders/files are of importance**:
```
iot-autocar/
│
├── arduino/
│   └── hw-504-joystick-send-values.ino              # STEP 1: upload to Arduino
│
├── raspberry-pi/
│   └── pi-receiver-mode-switcher.py                 # STEP 2: run on Raspberry Pi
│
└── computer/
    └── computer-bridge.py                           # STEP 3: run on computer/PC
```

#### The order of running these files (_Specify the file path, if it different for you_):

1. Upload `hw-504-joystick-send-values.ino` to Arduino
2. Followingly, run `pi-receiver-mode-switcher.py` from your RPi: 
    * ```python ./raspberry-pi/pi-receiver-mode-switcher.py``` or 
    * ```python3 ./raspberry-pi/pi-receiver-mode-switcher.py```
3. Only after than, run `computer-bridge.py` on your computer: 
    * ```python ./computer/computer-bridge.py``` or 
    * ```python3 ./computer/computer-bridge.py```


