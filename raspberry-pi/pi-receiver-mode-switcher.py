
"""
STEP 3: RPi receives coordinates and based on that changes mode and controls the motor

The order of running the code:

  1. Upload the hw-504-joystick-send-values.ino to Arduino.

  2. Run pi-receiver-mode-switcher.py on the Raspberry Pi first, and it will start listening on the specified port and wait for a connection.

  3. Next, run computer-bridge.py on the computer. It will connect to the Raspberry Pi and start reading from the Arduino.
        Once the double-press on the joystick is done, the Pi will start receiving and printing the joystick data.
      
"""

import socket
from gpiozero import Robot, OutputDevice, LineSensor, DistanceSensor, Servo
from time import sleep
import time


# --------- AUTONOMOUS MODE SETUP --------- #

# ---- L298N and DC hobby motor Setup ---- 
# Enable pins (must be HIGH to allow L298N to drive motors)
ena = OutputDevice(12)   # ENA
enb = OutputDevice(13)   # ENB
ena.on()
enb.on()

# L298N input pins: left=(IN1, IN2), right=(IN3, IN4)
robot = Robot(left=(7, 8), right=(9, 10))

# ---- HC-SR04 Ultrasonic sensor ---- 
ultra = None  # not created yet

def get_distance():
    global ultra
    if ultra is None:
        ultra = DistanceSensor(echo=26, trigger=16)
        sleep(0.2)  # allowing sensor to stabilize
    
    return ultra.distance * 100


# ---- IR sensor Setup (MH Infrared Obstacle Sensor Module) ---- 
left_ir = LineSensor(17)    # IR left
right_ir = LineSensor(27)   # IR right

# ---- Servo SG90 ----
servo = Servo(19)  # PWM pin (19, 12, 13, or 18)

# Helper function convert servo.value (-1..1) to degrees (0..180)
def set_servo_deg(deg):
    deg = max(0, min(180, deg))
    servo.value = (deg - 90) / 90   # maps 0..180 -> -1..1
    sleep(0.03)  # settling time


# ---- configurations ----
FRONT_THRESHOLD = 25     # in cm obstacle distance limit
REVERSE_TIME = 0.4       # time to move back and create some space 
TURN_TIME = 0.55         # time to rotate toward chosen direction


def sweep_environment():
    
    """Sweeps servo 90 -> 0 -> 180 -> 90, takes unique distance readings, returns best angle"""

    print("\n--- Performing 180 degree sweep ---")

    ANGLES_TO_SCAN = list(range(90, -1, -5)) + \
                     list(range(0, 181, 5)) + \
                     list(range(180, 89, -5))

    distance_map = {}

    for angle in ANGLES_TO_SCAN:
        if angle not in distance_map:   # avoid duplicates
            set_servo_deg(angle)
            sleep(0.05)
            dist_cm = ultra.distance * 100 # distance in cm
            distance_map[angle] = dist_cm
            print(f"Angle {angle} -> {dist_cm:.1f} cm")

    # Find angle with maximum distance
    best_angle = max(distance_map, key=lambda a: distance_map[a])
    best_distance = distance_map[best_angle]

    print(f"\n>> Best direction: {best_angle} degree, ({best_distance:.1f} cm)")

    return best_angle


def reverse_and_turn(best_angle):
    
    """Reverse slightly and turn robot toward the chosen direction"""

    print("\nReversing...")
    robot.backward()
    sleep(REVERSE_TIME)
    robot.stop()
    sleep(0.1)

    if best_angle < 80:
        print("Turning LEFT")
        robot.left()
    elif best_angle > 100:
        print("Turning RIGHT")
        robot.right()
    else:
        print("Forward direction is clear")
        return

    sleep(TURN_TIME)
    robot.stop()
    sleep(0.1)



# ------ MANUAL REMOTE CONTROL SETUP ------ #

# Joystick deadzone, basically ignoring small deviations near 512
DEADZONE = 100

# ---- TCP setup ----
HOST = ''  # listen on all interfaces
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
print("Waiting for connection...")

conn, addr = sock.accept()
print(f"Connected by {addr}")

joystick = {'X': 0, 'Y': 0, 'SW': 0}  # dictionary to store joystick state

def parse_data(data_str):
    """Parse incoming string into dictionary"""
    try:
        parts = data_str.split('|')
        for part in parts:
            key, val = part.split(':')
            joystick[key] = int(val)
    except Exception as e:
        print("Error parsing:", data_str, e)


def get_movement(x, y):
    x_centered = x - 512
    y_centered = y - 512

    if abs(x_centered) < DEADZONE and abs(y_centered) < DEADZONE:
        return 'stop'
    if y_centered > DEADZONE:
        return 'forward'
    elif y_centered < -DEADZONE:
        return 'backward'
    elif x_centered > DEADZONE:
        return 'right'
    elif x_centered < -DEADZONE:
        return 'left'
    else:
        return 'stop'


# --- Mode Switching Logic configs ---
mode = "manual"  # start in manual mode by default
last_switch_time = 0
SW_DEBOUNCE = 0.5  # seconds


# ------ MAIN LOGIC LOOP ------

# Make socket non-blocking via timeout
conn.settimeout(0.1)  # 100 milliseconds timeout

try:
    while True:
        # --- Try to receive any joystick data (non-blocking) ---
        try:
            data = conn.recv(1024)
            if data:
                lines = data.decode('utf-8').strip().split('\n')
                for line in lines:
                    parse_data(line)
        except OSError:
            # timeout or no data then continue
            pass

        # --- Mode switching (check joystick SW regardless of mode) ---
        current_time = time.time()
        if joystick.get('SW', 0) == 1 and (current_time - last_switch_time) > SW_DEBOUNCE:
            last_switch_time = current_time
            if mode == "manual":
                mode = "auto"
                print("\n>>> Switching to AUTONOMOUS mode")
            else:
                mode = "manual"
                print("\n>>> Switching to MANUAL mode")
            robot.stop()
            sleep(0.5)

        # --- Behavior depending on mode ---
        if mode == "manual":
            # joystick values were updated above (non-blocking)
            movement = get_movement(joystick['X'], joystick['Y'])
            if movement == 'forward':
                robot.forward(0.5)
            elif movement == 'backward':
                robot.backward(0.5)
            elif movement == 'left':
                robot.left(0.5)
            elif movement == 'right':
                robot.right(0.5)
            else:
                robot.stop()

        else:  # mode == "auto"

            front_dist = get_distance()
            ir_left = int(left_ir.value)
            ir_right = int(right_ir.value)

            print(f"IR L={ir_left}, R={ir_right}, Dist={front_dist:.1f} cm")

            if ir_left == 0 or ir_right == 0 or front_dist < FRONT_THRESHOLD:
                print("\nObstacle detected! Stopping.")
                robot.stop()
                sleep(0.1)

                best_angle = sweep_environment()
                set_servo_deg(90)
                reverse_and_turn(best_angle)
            else:
                robot.forward(0.5)

        # small loop delay
        sleep(0.02)
finally:
    print("Program stopped.")
    conn.close()
    sock.close()
    robot.close()
    ena.off()
    enb.off()


"""

Reference:

Serial Communication:
    Code adapted from https://forums.raspberrypi.com/viewtopic.php?t=106468
    Code adapted from https://stackoverflow.com/questions/21866762/sending-serial-communication-from-raspberry-pi
    Code adapted from https://raspberrypi.stackexchange.com/questions/935/how-do-i-get-the-data-from-the-serial-port

Servo motor (SG90) logic:
    Code adapted from https://www.geeksforgeeks.org/python/python-max-function/
    Code adapted from https://randomnerdtutorials.com/raspberry-pi-pico-servo-motor-micropython/#:~:text=Calculating%20the%20Duty%20Cycle,(65535/100)%20=%201802

L298N and DC motor logic:
    Code adapted from https://projects.raspberrypi.org/en/projects/physical-computing/14

L298N + IR logic:
    Code adapted from https://projects.raspberrypi.org/en/projects/rpi-python-line-following/6

DistanceSensor (HC-SR04) logic:
    Code adapted from https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04

HW-504 2-Axis joystick:
    Code adapted from https://lastminuteengineers.com/joystick-interfacing-arduino-processing/
    Information learned from https://docs.cirkitdesigner.com/component/fa55a084-79fb-4baa-914f-2151a791a6b0/joystick-module


"""