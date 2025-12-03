
"""
Step 3: RPi receives coordinates and stores them in dictionary for later use

The order of running the code:

  1. Upload the hw-504-joystick-send-values.ino to Arduino.

  2. Run pi-receiver.py on the Raspberry Pi first, and it will start listening on the specified port and wait for a connection.

  3. Next, run computer-bridge.py on the computer. It will connect to the Raspberry Pi and start reading from the Arduino.
        Once the double-press on the joystick is done, the Pi will start receiving and printing the joystick data.
      
"""

import socket

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

try:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        lines = data.decode('utf-8').strip().split('\n')
        for line in lines:
            parse_data(line)
            print("Joystick state:", joystick)
            # Example usage
            if joystick['X'] == 0 and joystick['Y'] == 0 and joystick['SW'] == 1:
                print("Button pressed at origin! Move car accordingly.")
finally:
    conn.close()
    sock.close()


"""

Reference:
Code adapted from https://forums.raspberrypi.com/viewtopic.php?t=106468
Code adapted from https://stackoverflow.com/questions/21866762/sending-serial-communication-from-raspberry-pi
Code adapted from https://raspberrypi.stackexchange.com/questions/935/how-do-i-get-the-data-from-the-serial-port

"""