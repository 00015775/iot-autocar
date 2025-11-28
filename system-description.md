# Project Overview

## Hardwares

1. Robot Chassis 
2. L298N Motor Drive Controller Board
3. Raspberry Pi 3 Model B v1.2
4. Infrared sensors (×2) 
5. Servo motor
6. Two 3.7 V batteries + battery holder 
7. Power bank 10,000mah (for Raspberry Pi) 
8. Ultrasonic distance sensor (HC-SR04)
9. Jumper wires & Resistors
10. LEDs & (actuators)
11. 2-Axis Joystick (HW-504)
12. Arduino Uno R3
13. DC hobby motor (x2)

#### Sensors (Unique Types)
1. **Infrared sensor**
2. **Ultrasonic distance sensor**
3. **2-Axis joystick**

**Total unique sensors:** 3

#### Actuators (Unique Types)
1. **Servo motor**
2. **DC hobby motor**
3. **LEDs**

**Total unique actuators:** 3

**Overall Total**
**Unique sensors + actuators:** 6


## System components — responsibilities
- **Raspberry Pi:**
    - Runs Flask web app (control UI + API).
    - Runs motor control code, sensor readers, servo controller.
    - Exposes REST/WS endpoints for control/status.

- **L298N motor driver:**
    - Drives the two DC motors. Controlled by Pi GPIO (direction pins + PWM).

- **IR sensors (×2):**
    - Line following (left/right). Digital outputs read by Pi GPIO.

- **Ultrasonic sensor (HC-SR04):**
    - Mounted on a servo to scan; Pi measures distances via trigger/echo pins.

- **Servo motor:**
    - Sweeps ultrasonic sensor to scan ahead (used in ultrasonic mode).

- **Arduino Uno + Joystick:**
    - Reads joystick axes, sends X/Y over serial to PC. (Arduino remains on PC side)

- **PC (bridge):**
    - Reads serial from Arduino, forwards joystick commands to Raspberry Pi over network (HTTP POST or WebSocket).

- **Power:**
    - Power bank → Raspberry Pi (USB).
    - Battery pack (two 3.7 V) → L298N (motors).
    - Ground common: Pi ground and motor driver ground(*GND*) MUST be common.


## System Description/Requirements (*High-level*)

I plan to build a multi-mode driving robot using the collection of hardware components I already have. The robot will operate in three distinct control modes. The first mode relies on **infrared line-following sensors** to detect and track a path(*duct tape*) laid out on the ground. The second mode uses an **ultrasonic distance sensor** mounted on a **servo motor**, by sweeping the sensor left and right, the robot continuously measures surrounding distances and chooses the direction that offers the farthest(*obstacle-free*) range. The third mode is a manual control mode operated through a **2-axis joystick (HW-504)** connected to an **Arduino Uno R3** on my computer. The Arduino reads the joystick's X and Y coordinates, then sends these values to the computer over USB serial, and the computer then forwards these X/Y coordinates to a Raspberry Pi over the local network. The Raspberry Pi, mounted on the robot chassis and powered by a power bank, receives the joystick commands and drives the motors accordingly. The joystick and the Arduino remain separate from the robot chassis(*off-board*) and receive power directly from the computer.

I also need the functionality to switch between these three control modes remotely. To accomplish this, I will develop a web application using **Flask**. This web app will be hosted at both the edge and cloud levels: locally on the Raspberry Pi, which will be exposed to the internet through a **Cloudflare Tunnel**, and also on **PythonAnywhere (*or any other free cloud-hosting servers*)** usings its free tier. From this interface, I should be able to select any of the robot's operating modes. In summary, the system integrates onboard sensors and compute on the Raspberry Pi with remote user controls and dual web-hosting, hence enabling flexible and accessibly robot operation from anywhere.


## High-level Overview

* *Robot-mounted*: **Raspberry Pi 3 (master controller)**, **L298N motor driver**, **2 DC motors**, **ultrasonic sensor** mounted on **servo**, **2 IR line sensors**, **LEDs/actuators**, **power bank (10,000 mAh) + two 3.7V batteries** (for motors via L298N / battery holder).
* *User workstation*: **Arduino Uno R3 + HW-504 joystick** connected by USB to PC. Arduino reads joystick X/Y and sends coordinates over serial to the PC.
* PC acts as a **bridge client**: reads serial from Arduino, and forwards joystick commands to the robot’s Flask server (Raspberry Pi) over the network (HTTP/WS).
* *Web app*: **Flask** hosted on Raspberry Pi (edge) and also on the cloud (PythonAnywhere free tier). **Cloudflare Tunnel** is used to expose the Pi-hosted endpoint to the internet.
* *Mode switching done via the web UI* — toggles robot between (1) IR Line follow, (2) Ultrasonic-path selection, (3) Joystick remote.


## Pseudo code (*High-level*)

```python
Initialize Raspberry Pi
Initialize IR sensors
Initialize Ultrasonic sensor with Servo
Initialize Motors

while True:
    mode = get_mode_from_web()  # Fetch mode from Flask Web Interface

    if mode == "IR_Line_Follow":
        while mode == "IR_Line_Follow":
            sensor_data = read_IR_sensors()
            motor_commands = compute_line_following(sensor_data)
            drive_motors(motor_commands)
            mode = get_mode_from_web()

    elif mode == "Ultrasonic_Path_Follow":
        while mode == "Ultrasonic_Path_Follow":
            distances = scan_with_ultrasonic_servo()
            best_direction = select_longest_path(distances)
            drive_motors(best_direction)
            mode = get_mode_from_web()

    elif mode == "Joystick_Control":
        while mode == "Joystick_Control":
            coordinates = read_coordinates_from_computer()
            motor_commands = convert_coordinates_to_motor_commands(coordinates)
            drive_motors(motor_commands)
            mode = get_mode_from_web()
```


## System ASCII Diagram (*High-level*)

```
                     ┌───────────────────────────────────────────┐
                     │               USER COMPUTER               │
                     │───────────────────────────────────────────│
                     │   - Web Browser (Flask UI remote mode)    │
                     │   - USB Serial to Arduino Uno R3          │
                     │   - Sends joystick data to Raspberry Pi   │
                     └───────────────┬───────────────────────────┘
                                     │ Local Network (Wi-Fi / LAN)
                                     ▼
                           ┌──────────────────────┐
                           │   Cloud Hosting      │
                           │  (PythonAnywhere)    │
                           │  Flask Web App       │
                           └─────────▲────────────┘
                                     │ Public Internet
                                     ▼
                         ┌───────────────────────────────┐
                         │   Raspberry Pi (on robot)     │
                         │───────────────────────────────│
                         │ - Hosts local Flask server    │
                         │ - Exposed via Cloudflare      │
                         │   Tunnel for public access    │
                         │ - Receives control mode cmds  │
                         │ - Processes joystick data     │
                         │ - Executes robot logic        │
                         └───────────┬───────────────────┘
                                     │ GPIO Control
                                     ▼
                ┌──────────────────────────────────────────────────┐
                │                ROBOT CHASSIS                     │
                │──────────────────────────────────────────────────│
                │  • Motor Driver (L298N)                          │
                │  • Drive Motors                                  │
                │                                                  │
                │  Control Mode Hardware:                          │
                │    1) IR Sensors → Line Following                │
                │    2) Ultrasonic Sensor + Servo → Pathfinding    │
                │    3) Joystick Data (via RPi) → Manual Control   │
                │                                                  │
                │  Power Source: Power Bank for Raspberry Pi       │
                └──────────────────────────────────────────────────┘


           Off-Board Components (Powered by Computer)
           ┌──────────────────────────────┐
           │ Arduino Uno R3 + HW-504      │
           │  - Reads joystick X/Y        │
           │  - Sends coordinates via USB │
           └──────────────────────────────┘
```


## Power Distribution Diagram

```

    ┌──────────────────────────────────────────────────────────────┐
    │                    ROBOT CHASSIS                             │
    │                                                              │
    │  [10,000mAh Power Bank] ──► Raspberry Pi 3 (5V/2.5A)         │
    │         │                        │                           │
    │         │                        └──► Servo Motor (5V)       │
    │         │                        └──► Status LEDs (GPIO)     │
    │         │                        └──► Infrared Sensors (5V)  │
    │         │                        └──► Ultrasonic Sensor (5V) │
    │         │                                                    │
    │  [2x 3.7V Batteries] ──► L298N Motor Controller              │
    │                               │                              │
    │                               ├──► DC Motor 1                │
    │                               └──► DC Motor 2                │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────┐
    │                 REMOTE CONTROL UNIT                     │
    │                                                         │
    │  [Computer USB Port] ──► Arduino Uno R3 (5V)            │
    │                               │                         │
    │                               └──► Joystick Module (5V) │
    └─────────────────────────────────────────────────────────┘
```


