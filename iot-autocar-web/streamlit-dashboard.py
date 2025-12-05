# pip install streamlit or python -m pip install streamlit
import streamlit as st
import socket
import threading
import time
from gpiozero import Robot, OutputDevice, LineSensor, DistanceSensor, Servo
import pandas as pd

# --- Robot setup ---
ena = OutputDevice(12)
enb = OutputDevice(13)
ena.on()
enb.on()
robot = Robot(left=(7, 8), right=(9, 10))

left_ir = LineSensor(17)
right_ir = LineSensor(27)
servo = Servo(19)

def set_servo_deg(deg):
    deg = max(0, min(180, deg))
    servo.value = (deg - 90) / 90
    time.sleep(0.03)
    return deg

ultra = DistanceSensor(echo=26, trigger=16)

# --- TCP connection setup ---
HOST = ''
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)
st.info("Waiting for joystick connection...")
conn, addr = sock.accept()
st.success(f"Connected to {addr}")

# --- Shared state ---
joystick = {"X": 0, "Y": 0, "SW": 0}
mode = "manual"
last_switch_time = 0
SW_DEBOUNCE = 0.5
FRONT_THRESHOLD = 25
REVERSE_TIME = 0.4
TURN_TIME = 0.55
DEADZONE = 100
servo_history = []

# --- Helper functions ---
def parse_data(data_str):
    try:
        parts = data_str.split('|')
        for part in parts:
            key, val = part.split(':')
            joystick[key] = int(val)
    except:
        pass

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
    return 'stop'

def get_distance():
    time.sleep(0.05)
    return ultra.distance * 100

def sweep_environment():
    angles = list(range(90, -1, -5)) + \
             list(range(0, 181, 5)) + \
             list(range(180, 89, -5))
    
    distance_map = {}
    for angle in angles:
        dist_cm = ultra.distance * 100
        distance_map[angle] = dist_cm
        set_servo_deg(angle)
        servo_history.append({"angle": angle, "distance": dist_cm})
    best_angle = max(distance_map, key=distance_map.get)
    return best_angle

def reverse_and_turn(best_angle):
    robot.backward()
    time.sleep(REVERSE_TIME)
    robot.stop()
    time.sleep(0.1)
    if best_angle < 80:
        robot.left()
    elif best_angle > 100:
        robot.right()
    time.sleep(TURN_TIME)
    robot.stop()

# --- Thread for receiving joystick data ---
def joystick_thread():
    global mode, last_switch_time
    while True:
        try:
            data = conn.recv(1024)
            if data:
                lines = data.decode('utf-8').strip().split('\n')
                for line in lines:
                    parse_data(line)
        except:
            pass
        # --- Mode switch ---
        current_time = time.time()
        if joystick.get("SW", 0) == 1 and (current_time - last_switch_time) > SW_DEBOUNCE:
            last_switch_time = current_time
            if mode == "manual":
                mode = "auto"
            else:
                mode = "manual"

threading.Thread(target=joystick_thread, daemon=True).start()

# --- Streamlit UI ---
st.title("Raspberry Pi Robot Dashboard")

# Mode
st.subheader("Mode Control")
mode_toggle = st.button(f"Switch Mode (Current: {mode.upper()})")
if mode_toggle:
    mode = "auto" if mode == "manual" else "manual"

# Sensor Data
st.subheader("Sensors")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("IR Left", "RED" if left_ir.value==0 else "GREEN")
with col2:
    st.metric("IR Right", "RED" if right_ir.value==0 else "GREEN")
with col3:
    st.metric("Ultrasonic (cm)", f"{get_distance():.1f}")

st.metric("Servo Angle", f"{servo.value*90 + 90:.0f}")

# Actuator Control
st.subheader("Actuators")
colf, colb, coll, colr, cols = st.columns(5)
if colf.button("Forward"):
    robot.forward(0.5)
if colb.button("Backward"):
    robot.backward(0.5)
if coll.button("Left"):
    robot.left(0.5)
if colr.button("Right"):
    robot.right(0.5)
if cols.button("Stop"):
    robot.stop()

servo_deg = st.slider("Servo Angle", 0, 180, 90)
set_servo_deg(servo_deg)

# Visualize servo sweep
st.subheader("Servo Sweep History")
if servo_history:
    df_servo = pd.DataFrame(servo_history)
    st.line_chart(df_servo.set_index("angle")["distance"])

# Joystick visualization
st.subheader("Joystick")
st.text(f"X: {joystick['X']}, Y: {joystick['Y']}, SW: {joystick['SW']}")

# Auto mode behavior
if mode == "auto":
    front_dist = get_distance()
    if left_ir.value==0 or right_ir.value==0 or front_dist < FRONT_THRESHOLD:
        best_angle = sweep_environment()
        set_servo_deg(90)
        reverse_and_turn(best_angle)
    else:
        robot.forward(0.5)

st.text("Dashboard updating in real-time...")
time.sleep(0.1)
