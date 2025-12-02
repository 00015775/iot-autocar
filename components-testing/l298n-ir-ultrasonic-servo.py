# testing L298N + IR sensor + Ultrasonic Sensor + Servo

"""

L298N and DC hobby motor wires and pins:
  Red wires - IN1, IN3
  Black wires - IN2, IN4

  IN1, IN2 = 7, 8
  IN3, IN4 = 9, 10
  ENA, ENB = 13, 12
  12+V (VC) - Connect to Power Supply Battery 2x3.7V
  GND - GND
  5+V (VCC) - no need to connect to it since DC motors require 6V each
  

IR sensor pins:
  GND - GND
  VCC - 5V
  OUT(right)=17, OUT(left)=27; IR sensors; PWM enabled GPIOs

  
HC-SR04 Ultrasonic sensor pins:
  VCC - 5V
  GND - GND
  TRIG - 16
  ECHO - 26
  Make sure to use voltage divider with two resistors for pin connected to Echo. 
  Otherwise the program will not work and Pi can be damaged!

  
Servo SG09 motor:
  YELLOW - VCC, 5V
  RED - 19; PWN enabled pins (BCM: 12,13,18,19) if any left.
  BROWN - GND


Both RPi and L298N must have a common ground! Connect RPi GND to L298N GND powered from battery
Instead of connecting GND, VCC to each of IR sensors, connect only a single GND, VCC from RPi to breadboard
then distribute from there to IR sensors connected to breadboard

"""


from gpiozero import Robot, LineSensor, OutputDevice, DistanceSensor, Servo
from time import sleep


# ---- L298N and DC hobby motor Setup ---- 
# Enable pins (must be HIGH to allow L298N to drive motors)
ena = OutputDevice(12)   # ENA
enb = OutputDevice(13)   # ENB
ena.on()
enb.on()

# L298N input pins: left=(IN1, IN2), right=(IN3, IN4)
robot = Robot(left=(7, 8), right=(9, 10))


# ---- IR sensor Setup (MH Infrared Obstacle Sensor Module) ---- 
left_ir = LineSensor(17)    # IR left
right_ir = LineSensor(27)   # IR right


# ---- HC-SR04 Ultrasonic sensor ---- 
ultra = DistanceSensor(echo=26, trigger=16)  # must have voltage divider for echo pin


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


# ---- Main Logic ----

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


# ---- Main Loop ----

try:
    while True:
        ir_left = int(left_ir.value)
        ir_right = int(right_ir.value)
        front_dist = ultra.distance * 100

        print(f"IR L={ir_left}, R={ir_right}, Dist={front_dist:.1f} cm")

        # Stop condition
        if ir_left == 0 or ir_right == 0 or front_dist < FRONT_THRESHOLD:
            print("\nObstacle detected! Stopping.")
            robot.stop()
            sleep(0.1)

            # Perform servo sweep
            best_angle = sweep_environment()

            # Return servo to center before moving
            set_servo_deg(90)

            # Reverse + turn toward chosen direction
            reverse_and_turn(best_angle)

        else:
            robot.forward()

        sleep(0.02)

except KeyboardInterrupt:
    print("Program stopped.")
    robot.stop()
    ena.off()
    enb.off()


"""



Reference:

Servo motor (SG90) logic:
  Code adapted from https://www.geeksforgeeks.org/python/python-max-function/
  Code adapted from https://randomnerdtutorials.com/raspberry-pi-pico-servo-motor-micropython/#:~:text=Calculating%20the%20Duty%20Cycle,(65535/100)%20=%201802

L298N and DC motor logic:
  Code adapted from https://projects.raspberrypi.org/en/projects/physical-computing/14

L298N + IR logic:
  Code adapted from https://projects.raspberrypi.org/en/projects/rpi-python-line-following/6

DistanceSensor (HC-SR04) logic:
  Code adapted from https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04

  
"""