
"""
THIS CODE WAS TESTED TO CHECK THE REMOTE CONTROL OF L298N

(OPTIONAL): RPi receives coordinates and stores them in dictionary for later use

The order of running the code:

  1. Upload the hw-504-joystick-send-values.ino to Arduino.

  2. Run pi-receiver.py on the Raspberry Pi first, and it will start listening on the specified port and wait for a connection.

  3. Next, run computer-bridge.py on the computer. It will connect to the Raspberry Pi and start reading from the Arduino.
        Once the double-press on the joystick is done, the Pi will start receiving and printing the joystick data.
        
"""

import socket
from gpiozero import Robot, OutputDevice


# ---- L298N and DC hobby motor Setup ----
# ENA/ENB control the speed of motors, without enabling them motor does not work
ena = OutputDevice(12)
enb = OutputDevice(13)
ena.on()
enb.on()

# Motor pins: left=(IN1, IN2), right=(IN3, IN4)
robot = Robot(left=(7, 8), right=(9, 10))

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

try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        lines = data.decode('utf-8').strip().split('\n')
        for line in lines:
            parse_data(line)
            movement = get_movement(joystick['X'], joystick['Y'])
            
            # control the robot
            if movement == 'forward':
                robot.forward(0.5) # drive at the half speed to preserve the energy
            elif movement == 'backward':
                robot.backward(0.5)
            elif movement == 'left':
                robot.left(0.5)
            elif movement == 'right':
                robot.right(0.5)
            else:
                robot.stop()
finally:
    conn.close()
    sock.close()
    robot.close()
    ena.off()
    enb.off()


"""

Reference:
Code adapted from https://forums.raspberrypi.com/viewtopic.php?t=106468
Code adapted from https://stackoverflow.com/questions/21866762/sending-serial-communication-from-raspberry-pi
Code adapted from https://raspberrypi.stackexchange.com/questions/935/how-do-i-get-the-data-from-the-serial-port

"""