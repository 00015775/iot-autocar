# pip install pyserial OR python3 -m pip install pyserial

"""
Step 2: Computer receives coordinates and sends them to RPi

The order of running the code:

  1. Upload the hw-504-joystick-send-values.ino to Arduino.

  2. Run pi-receiver.py on the Raspberry Pi first, and it will start listening on the specified port and wait for a connection.

  3. Next, run computer-bridge.py on the computer. It will connect to the Raspberry Pi and start reading from the Arduino.
        Once the double-press on the joystick is done, the Pi will start receiving and printing the joystick data.
      
"""

import serial
import socket

# --- config ---
SERIAL_PORT = '/dev/cu.usbmodem1101'  # Serial port shown at the top in Arduino IDE
BAUD_RATE = 9600

RPi_IP = 'jamescameronpi3.local'  # Dynamic Raspberry Pi IP, if it fails then use a static IP address
RPi_PORT = 5005

# --- setup ---
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((RPi_IP, RPi_PORT))

print("Bridge running...")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("X:"):  # joystick coordinates
            sock.sendall((line + "\n").encode('utf-8'))
        elif line.startswith("SENDING_ON"):
            print("[INFO] Sending enabled")
        elif line.startswith("SENDING_OFF"):
            print("[INFO] Sending disabled")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    sock.close()
    ser.close()


"""

Reference:
Code adapted from https://projects.raspberrypi.org/en/projects/nix-python-reading-serial-data/0

"""