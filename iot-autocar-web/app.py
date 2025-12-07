"""
Flask Web Interface for Raspberry Pi Robot Control
Run this on Raspberry Pi: python3 app.py
Access from browser: http://[PI_IP]:5000

Requirements:
pip install flask flask-socketio eventlet gpiozero pyserial pyttsx3
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from gpiozero import Robot, OutputDevice, LineSensor, DistanceSensor, Servo
import threading
import time
import pyttsx3
from collections import deque
import statistics

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'robot_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ===== HARDWARE SETUP ===== 
# Reference: https://gpiozero.readthedocs.io/en/stable/recipes.html

# L298N Enable pins
ena = OutputDevice(12)
enb = OutputDevice(13)
ena.on()
enb.on()

# Robot motor control (IN1, IN2, IN3, IN4)
robot = Robot(left=(7, 8), right=(9, 10))

# Ultrasonic sensor (HC-SR04)
# Reference: https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04
ultra = DistanceSensor(echo=26, trigger=16)

# IR sensors (MH Infrared Obstacle Sensor Module)
# Reference: https://projects.raspberrypi.org/en/projects/rpi-python-line-following/6
left_ir = LineSensor(17)
right_ir = LineSensor(27)

# Servo motor (SG90)
# Reference: https://gpiozero.readthedocs.io/en/stable/api_output.html#servo
servo = Servo(19)

# Text-to-Speech engine
# Reference: https://pyttsx3.readthedocs.io/en/latest/
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Speed of speech

# ===== GLOBAL STATE =====
robot_state = {
    'mode': 'manual',  # 'manual' or 'autonomous'
    'speed': 50,  # PWM speed percentage (0-100)
    'servo_angle': 90,
    'ultrasonic_distance': 0,
    'ir_left': 0,
    'ir_right': 0,
    'is_moving': False,
    'last_movement': 'stop'
}

# Distance history for statistics (store last 100 readings)
distance_history = deque(maxlen=100)

# Thread control
running = True
autonomous_active = False

# ===== HELPER FUNCTIONS =====

def set_servo_angle(angle):
    """Set servo to specific angle (0-180 degrees)"""
    # Reference: https://randomnerdtutorials.com/raspberry-pi-pico-servo-motor-micropython/
    angle = max(0, min(180, angle))
    servo.value = (angle - 90) / 90  # Convert 0-180 to -1 to 1
    robot_state['servo_angle'] = angle
    time.sleep(0.05)

def get_distance():
    """Get distance from ultrasonic sensor in cm"""
    try:
        dist = ultra.distance * 100  # Convert meters to cm
        return round(dist, 1)
    except:
        return 0

def speak(text):
    """Non-blocking text-to-speech"""
    def _speak():
        tts_engine.say(text)
        tts_engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def calculate_statistics():
    """Calculate statistics from distance history"""
    # Reference: https://docs.python.org/3/library/statistics.html
    if len(distance_history) < 5:
        return None
    
    return {
        'mean': round(statistics.mean(distance_history), 1),
        'median': round(statistics.median(distance_history), 1),
        'min': round(min(distance_history), 1),
        'max': round(max(distance_history), 1),
        'stdev': round(statistics.stdev(distance_history), 1) if len(distance_history) > 1 else 0
    }

# ===== MOTOR CONTROL =====
# Reference: https://projects.raspberrypi.org/en/projects/physical-computing/14

def move_robot(direction, speed_percent=50):
    """Control robot movement with speed control"""
    speed = speed_percent / 100.0  # Convert to 0.0-1.0 range
    
    if direction == 'forward':
        robot.forward(speed)
    elif direction == 'backward':
        robot.backward(speed)
    elif direction == 'left':
        robot.left(speed)
    elif direction == 'right':
        robot.right(speed)
    elif direction == 'stop':
        robot.stop()
    
    robot_state['last_movement'] = direction
    robot_state['is_moving'] = (direction != 'stop')

# ===== SENSOR MONITORING THREAD =====

def sensor_monitor():
    """Continuously monitor sensors and emit updates"""
    global running
    
    while running:
        try:
            # Read sensors
            dist = get_distance()
            ir_l = int(left_ir.value)
            ir_r = int(right_ir.value)
            
            # Update state
            robot_state['ultrasonic_distance'] = dist
            robot_state['ir_left'] = ir_l
            robot_state['ir_right'] = ir_r
            
            # Add to history for statistics
            distance_history.append(dist)
            
            # Emit sensor data to all connected clients
            socketio.emit('sensor_update', {
                'distance': dist,
                'ir_left': ir_l,
                'ir_right': ir_r,
                'servo_angle': robot_state['servo_angle'],
                'statistics': calculate_statistics()
            })
            
            time.sleep(0.1)  # Update rate: 10 Hz
        except Exception as e:
            print(f"Sensor monitor error: {e}")
            time.sleep(0.5)

# ===== AUTONOMOUS MODE =====

def autonomous_mode():
    """Autonomous obstacle avoidance logic"""
    global autonomous_active
    
    FRONT_THRESHOLD = 25  # cm
    REVERSE_TIME = 0.4
    TURN_TIME = 0.55
    
    while autonomous_active:
        try:
            dist = get_distance()
            ir_l = int(left_ir.value)
            ir_r = int(right_ir.value)
            
            # Check for obstacles
            if ir_l == 0 or ir_r == 0 or dist < FRONT_THRESHOLD:
                robot.stop()
                speak("Object detected")
                socketio.emit('status', {'message': 'Obstacle detected! Scanning...'})
                
                # Perform servo sweep
                speak("Scanning environment")
                best_angle = sweep_and_find_path()
                
                # Return servo to center
                set_servo_angle(90)
                
                # Reverse and turn
                robot.backward(0.5)
                time.sleep(REVERSE_TIME)
                robot.stop()
                
                if best_angle < 80:
                    robot.left(0.5)
                    time.sleep(TURN_TIME)
                elif best_angle > 100:
                    robot.right(0.5)
                    time.sleep(TURN_TIME)
                
                robot.stop()
                speak("Clear path found")
                socketio.emit('status', {'message': f'Clear path at {best_angle}°'})
            else:
                # Move forward
                speed = robot_state['speed'] / 100.0
                robot.forward(speed)
            
            time.sleep(0.05)
        except Exception as e:
            print(f"Autonomous mode error: {e}")
            time.sleep(0.5)

def sweep_and_find_path():
    """Sweep servo 0-180 and find best direction"""
    # Reference: https://www.geeksforgeeks.org/python/python-max-function/
    
    distance_map = {}
    angles = list(range(0, 181, 10))  # Sweep in 10-degree steps
    
    for angle in angles:
        set_servo_angle(angle)
        time.sleep(0.1)
        dist = get_distance()
        distance_map[angle] = dist
        
        # Emit sweep data for visualization
        socketio.emit('sweep_data', {
            'angle': angle,
            'distance': dist
        })
    
    # Find angle with maximum distance
    best_angle = max(distance_map, key=distance_map.get)
    return best_angle

# ===== FLASK ROUTES =====

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

# ===== SOCKETIO EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('robot_state', robot_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('set_mode')
def handle_mode(data):
    """Switch between manual and autonomous mode"""
    global autonomous_active
    
    mode = data.get('mode', 'manual')
    robot_state['mode'] = mode
    
    if mode == 'autonomous':
        autonomous_active = True
        threading.Thread(target=autonomous_mode, daemon=True).start()
        speak("Autonomous mode activated")
    else:
        autonomous_active = False
        robot.stop()
        speak("Manual mode activated")
    
    emit('robot_state', robot_state, broadcast=True)

@socketio.on('move')
def handle_move(data):
    """Handle manual movement commands"""
    if robot_state['mode'] == 'manual':
        direction = data.get('direction', 'stop')
        move_robot(direction, robot_state['speed'])
        emit('robot_state', robot_state, broadcast=True)

@socketio.on('set_speed')
def handle_speed(data):
    """Set motor speed (0-100%)"""
    speed = int(data.get('speed', 50))
    robot_state['speed'] = max(0, min(100, speed))
    emit('robot_state', robot_state, broadcast=True)

@socketio.on('set_servo')
def handle_servo(data):
    """Set servo angle (0-180 degrees)"""
    angle = int(data.get('angle', 90))
    set_servo_angle(angle)
    emit('robot_state', robot_state, broadcast=True)

@socketio.on('servo_sweep')
def handle_servo_sweep():
    """Perform servo sweep and return data"""
    speak("Performing servo sweep")
    threading.Thread(target=sweep_and_find_path, daemon=True).start()

# ===== MAIN =====

if __name__ == '__main__':
    print("Starting Flask Robot Control Server...")
    print("Access at: http://[YOUR_PI_IP]:5000")
    
    # Start sensor monitoring thread
    sensor_thread = threading.Thread(target=sensor_monitor, daemon=True)
    sensor_thread.start()
    
    try:
        # Run Flask-SocketIO server
        # Reference: https://flask-socketio.readthedocs.io/en/latest/
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        running = False
        autonomous_active = False
        robot.stop()
        ena.off()
        enb.off()
        print("Cleanup complete")

"""
References:
- Flask: https://flask.palletsprojects.com/
- Flask-SocketIO: https://flask-socketio.readthedocs.io/
- GPIOZero: https://gpiozero.readthedocs.io/
- pyttsx3: https://pyttsx3.readthedocs.io/
- Python Statistics: https://docs.python.org/3/library/statistics.html
"""

