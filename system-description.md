# Project Overview

---

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

---

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

---

## System Description/Requirements (*High-level*)

I plan to build a multi-mode driving robot using the collection of hardware components I already have. The robot will operate in three distinct control modes. The first mode relies on **infrared line-following sensors** to detect and track a path(*duct tape*) laid out on the ground. The second mode uses an **ultrasonic distance sensor** mounted on a **servo motor**, by sweeping the sensor left and right, the robot continuously measures surrounding distances and chooses the direction that offers the farthest(*obstacle-free*) range. The third mode is a manual control mode operated through a **2-axis joystick (HW-504)** connected to an **Arduino Uno R3** on my computer. The Arduino reads the joystick's X and Y coordinates, then sends these values to the computer over USB serial, and the computer then forwards these X/Y coordinates to a Raspberry Pi over the local network. The Raspberry Pi, mounted on the robot chassis and powered by a power bank, receives the joystick commands and drives the motors accordingly. The joystick and the Arduino remain separate from the robot chassis(*off-board*) and receive power directly from the computer.

I also need the functionality to switch between these three control modes remotely. To accomplish this, I will develop a web application using **Flask**. This web app will be hosted at both the edge and cloud levels: locally on the Raspberry Pi, which will be exposed to the internet through a **Cloudflare Tunnel**, and also on **PythonAnywhere (*or any other free cloud-hosting servers*)** usings its free tier. From this interface, I should be able to select any of the robot's operating modes. In summary, the system integrates onboard sensors and compute on the Raspberry Pi with remote user controls and dual web-hosting, hence enabling flexible and accessibly robot operation from anywhere.

---

## High-level Overview

* *Robot-mounted*: **Raspberry Pi 3 (master controller)**, **L298N motor driver**, **2 DC motors**, **ultrasonic sensor** mounted on **servo**, **2 IR line sensors**, **LEDs/actuators**, **power bank (10,000 mAh) + two 3.7V batteries** (for motors via L298N / battery holder).
* *User workstation*: **Arduino Uno R3 + HW-504 joystick** connected by USB to PC. Arduino reads joystick X/Y and sends coordinates over serial to the PC.
* PC acts as a **bridge client**: reads serial from Arduino, and forwards joystick commands to the robot’s Flask server (Raspberry Pi) over the network (HTTP/WS).
* *Web app*: **Flask** hosted on Raspberry Pi (edge) and also on the cloud (PythonAnywhere free tier). **Cloudflare Tunnel** is used to expose the Pi-hosted endpoint to the internet.
* *Mode switching done via the web UI* — toggles robot between (1) IR Line follow, (2) Ultrasonic-path selection, (3) Joystick remote.

---

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

---

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

---

## Real-time communication 

In order to achieve a real-time we need more than just Flask. **[Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)** gives Flask applications access to low latency bi-directional communications between the clients and the server. The client-side can use any of the SocketIO client libraries in Javascript, Python, C++, Java and Swift, or any other compatible client to establish a permanent connection to the server. This approach works for both edge and cloud level hostings:  
* The Flask app hosted on the Raspberry Pi (local/edge)
* The same Flask app mirrored on PythonAnywhere (cloud)

In theory, the same `app.py` code being be uploaded on RPi and PythonAnywhere, should work similarly, by being real-time, low-latency and bi-directional.

```
Flask  ───► Flask-SocketIO (Python package)
                    ▲
                    └──► uses socket.io protocol (under the hood)
                    └──► works with the official socket.io JavaScript client
```

---

## Hardware Architecture (**High-level**)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ROBOT CHASSIS                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    RASPBERRY PI 3 B v1.2                     │   │
│  │  • Flask + Flask-SocketIO Web Server (Edge)                  │   │
│  │  • Mode Controller                                           │   │
│  │  • Motor Control Logic                                       │   │
│  │  • Network Communication Handler                             │   │
│  └────────┬─────────────┬──────────────┬────────────────────────┘   │
│           │             │              │                            │
│  ┌────────▼─────────────▼──────────────▼─────────┐                  │
│  │         L298N Motor Driver Board              │                  │
│  │  • Controls DC Motor Speed & Direction        │                  │
│  └────────┬──────────────────────────┬───────────┘                  │
│           │                          │                              │
│  ┌────────▼────────┐        ┌────────▼────────┐                     │
│  │  DC Motor (L)   │        │  DC Motor (R)   │                     │
│  │    3.7V         │        │    3.7V         │                     │
│  └─────────────────┘        └─────────────────┘                     │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │         Servo Motor (SG90)               │                       │
│  │  • Pan Ultrasonic Sensor                 │                       │
│  │  • Controlled by Raspberry Pi GPIO       │                       │
│  └────────┬─────────────────────────────────┘                       │
│           │                                                         │
│  ┌────────▼─────────────────────────────────┐                       │
│  │   Ultrasonic Distance Sensor (HC-SR04)   │                       │
│  │  • Measures distance (2cm - 400cm)       │                       │
│  │  • Used in Obstacle Avoidance Mode       │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │    IR Sensor (Left)  │  IR Sensor (Right)│                       │
│  │  • Detects black line on white surface   │                       │
│  │  • Used in Line Following Mode           │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │          LEDs & Status Indicators        │                       │
│  │  • Mode indication                       │                       │
│  │  • Status feedback                       │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │     Power Bank (10,000mAh)               │                       │
│  │  • Powers Raspberry Pi 3                 │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
│  ┌──────────────────────────────────────────┐                       │
│  │  2x 3.7V Batteries + Battery Holder      │                       │
│  │  • Powers Motors via L298N               │                       │
│  └──────────────────────────────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ WiFi Network
                              │ (Same LAN)
                              │
┌─────────────────────────────▼──────────────────────────────┐
│                     COMPUTER STATION                       │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Arduino Uno R3                          │  │
│  │  • Reads Joystick X/Y coordinates                    │  │
│  │  • Sends data via USB Serial                         │  │
│  └────────┬─────────────────────────────────────────────┘  │
│           │                                                │
│  ┌────────▼─────────────────────────────────────────────┐  │
│  │    2-Axis Joystick Module (HW-504)                   │  │
│  │  • X-axis: VRx → Arduino A0                          │  │
│  │  • Y-axis: VRy → Arduino A1                          │  │
│  │  • SW (button): Digital Pin                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Python Serial Reader Script                  │  │
│  │  • Reads from Arduino via Serial (USB)               │  │
│  │  • Sends joystick data to Raspberry Pi via HTTP/WS   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Web Browser Interface                      │  │
│  │  • Access Flask web app                              │  │
│  │  • Switch between modes                              │  │
│  │  • Monitor robot status                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│           USB Power → Arduino Uno R3                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## GPIO Pin Mapping Template (Raspberry Pi)

```
L298N Motor Driver:
• IN1 → GPIO 17 (Motor A direction)
• IN2 → GPIO 18 (Motor A direction)
• IN3 → GPIO 22 (Motor B direction)
• IN4 → GPIO 23 (Motor B direction)
• ENA → GPIO 12 (PWM - Motor A speed)
• ENB → GPIO 13 (PWM - Motor B speed)

IR Sensors:
• Left IR OUT → GPIO 24
• Right IR OUT → GPIO 25

Ultrasonic Sensor:
• TRIG → GPIO 5
• ECHO → GPIO 6

Servo Motor:
• PWM Signal → GPIO 27

LEDs (Status Indicators):
• LED1 (Mode 1) → GPIO 16
• LED2 (Mode 2) → GPIO 20
• LED3 (Mode 3) → GPIO 21
```

---

## Power Distribution Diagram

```
┌──────────────────────────────────────────┐
│         ROBOT POWER SYSTEM               │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐      │
│  │  Power Bank 10,000mAh          │      │
│  │  Output: 5V / 2A               │      │
│  └──────────┬─────────────────────┘      │
│             │                            │
│             │ Micro USB                  │
│             │                            │
│  ┌──────────▼─────────────────────┐      │
│  │    Raspberry Pi 3 Model B      │      │
│  │    Power: 5V / 2.5A            │      │
│  └────────────────────────────────┘      │
│                                          │
│  ┌────────────────────────────────┐      │
│  │  2x 3.7V Batteries (Series)    │      │
│  │  Total: 7.4V                   │      │
│  └──────────┬─────────────────────┘      │
│             │                            │
│             │                            │
│  ┌──────────▼─────────────────────┐      │
│  │      L298N Motor Driver        │      │
│  │  • Powers both DC motors       │      │
│  │  • 5V regulator for logic      │      │
│  └──────────┬──────────┬──────────┘      │
│             │          │                 │
│    ┌────────▼───┐  ┌───▼────────┐        │
│    │ DC Motor L │  │ DC Motor R │        │
│    └────────────┘  └────────────┘        │
│                                          │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│      COMPUTER STATION POWER              │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐      │
│  │         Computer USB Port      │      │
│  │         Output: 5V / 500mA     │      │
│  └──────────┬─────────────────────┘      │
│             │                            │
│             │ USB Cable                  │
│             │                            │
│  ┌──────────▼─────────────────────┐      │
│  │       Arduino Uno R3           │      │
│  │       Power: 5V                │      │
│  └────────────┬───────────────────┘      │
│               │                          │
│               │ 5V Pin                   │
│               │                          │
│  ┌────────────▼───────────────────┐      │
│  │    Joystick HW-504             │      │
│  │    Power: 5V                   │      │
│  └────────────────────────────────┘      │
│                                          │
└──────────────────────────────────────────┘
```

---

## Web Application Structure (*Template*)

```
project/
│
├── raspberry_pi/
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api_routes.py       # REST API endpoints
│   │   └── web_routes.py       # Web page routes
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── mode_controller.py    # Mode switching logic
│   │   ├── motor_controller.py   # Motor control
│   │   └── sensor_controller.py  # Sensor readings
│   │
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── line_follow.py      # Mode 1 implementation
│   │   ├── obstacle_avoid.py   # Mode 2 implementation
│   │   └── joystick_control.py # Mode 3 implementation
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── control.js     # Frontend JavaScript
│   │
│   └── templates/
│       ├── index.html         # Main control page
│       └── status.html        # Status monitoring
│
├── computer_station/
│   ├── serial_bridge.py       # Arduino serial reader
│   └── requirements.txt
│
├── arduino/
│   └── joystick_reader/
│       └── joystick_reader.ino # Arduino sketch
│
└── cloud/
    └── pythonanywhere/
        ├── flask_app.py       # Cloud Flask app
        └── requirements.txt
```

---

## Data Flow Summary

1. **Mode Selection**: User → Web Browser → Cloud/Edge Flask → Raspberry Pi → Mode Switch
2. **Line Following**: IR Sensors → Raspberry Pi GPIO → Motor Driver → Motors
3. **Obstacle Avoidance**: Ultrasonic + Servo → Raspberry Pi → Path Decision → Motors
4. **Joystick Control**: Joystick → Arduino → Serial → Python Script → HTTP → Raspberry Pi → Motors

---

## Deployment Architecture (*High-level*)

```
┌────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT LAYERS                       │
└────────────────────────────────────────────────────────────┘

Layer 1: CLOUD (PythonAnywhere)
┌──────────────────────────────────────────┐
│  • Domain: username.pythonanywhere.com   │
│  • Flask app in production mode          │
│  • Forwards commands to RPi via HTTP     │
│  • Acts as remote control interface      │
└──────────────────────────────────────────┘
                    ▼
Layer 2: TUNNEL (Cloudflare)
┌──────────────────────────────────────────┐
│  • Secure tunnel to local network        │
│  • No port forwarding needed             │
│  • Expose RPi Flask to internet          │
└──────────────────────────────────────────┘
                    ▼
Layer 3: EDGE (Raspberry Pi)
┌──────────────────────────────────────────┐
│  • Local Flask server (192.168.x.x:5000) │
│  • Direct hardware control               │
│  • Real-time sensor processing           │
│  • Mode execution engine                 │
└──────────────────────────────────────────┘
                    ▼
Layer 4: HARDWARE (Robot Chassis)
┌──────────────────────────────────────────┐
│  • Motors, sensors, servo                │
│  • GPIO-controlled components            │
│  • Physical robot operation              │
└──────────────────────────────────────────┘

Layer 5: CONTROL STATION (Computer)
┌──────────────────────────────────────────┐
│  • Arduino + Joystick                    │
│  • Python serial bridge                  │
│  • Sends joystick data to RPi            │
└──────────────────────────────────────────┘
```

---

## Safety & Error Handling

- **Emergency Stop**: Implement stop button in web interface
- **Network Monitoring**: Detect connection loss
- **Battery Monitoring**: Low battery warning via LEDs
- **Collision Detection**: Stop on obstacle < 10cm (Mode 2)

---

## Development Roadmap

### Phase 1: Hardware Setup
- Assemble robot chassis
- Connect motors to L298N
- Wire sensors to Raspberry Pi
- Test individual components

### Phase 2: Basic Software
- Install Raspberry Pi OS
- Set up Flask + Flask-SocketIO framework
- Implement GPIO control
- Test motor movements

### Phase 3: Mode Development
- Develop Mode 1 (Line Following)
- Develop Mode 2 (Obstacle Avoidance)
- Develop Mode 3 (Joystick Control)

### Phase 4: Web Application
- Create Flask web interface
- Implement mode switching
- Add status monitoring
- Test on local network

### Phase 5: Cloud Deployment
- Deploy to PythonAnywhere
- Set up Cloudflare Tunnel
- Test remote access
- Finalize documentation

---

## Testing Checklist

- [ ] Individual motor control
- [ ] IR sensor calibration
- [ ] Ultrasonic distance accuracy
- [ ] Servo sweep range
- [ ] Joystick data transmission
- [ ] Network communication
- [ ] Mode switching
- [ ] Emergency stop functionality
- [ ] Cloud accessibility
- [ ] Battery life under load


