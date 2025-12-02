# connect L298N and IR sensor

"""

 IN1, IN2 = 7, 8
 IN3, IN4 = 9, 10
 ENA, ENB = 13, 12

OUT(right)=17, OUT(left)=27; IR sensors; PWM enabled GPIOs

Both RPi and L298N must have a common ground! Connect RPi GND to L298N GND powered from battery
Instead of connecting GND, VCC to each of IR sensors, connect only a single GND, VCC from RPi to breadboard
then distribute from there to IR sensors connected to breadboard

"""


from gpiozero import Robot, LineSensor, OutputDevice
from time import sleep

# Without enabling ENA/ENB, motor does not move
ena = OutputDevice(12)
enb = OutputDevice(13)
ena.on()
enb.on()

# Motor pins going to L298N IN1–IN4
robot = Robot(left=(7, 8), right=(9, 10))

# IR sensors
left_sensor = LineSensor(17)
right_sensor = LineSensor(27)

try:
    while True:
        left = int(left_sensor.value)  
        right = int(right_sensor.value)

        if left == 0 or right == 0:
            # Object detected
            robot.stop()
        else:
            # No object
            robot.forward()

        sleep(0.01)

except KeyboardInterrupt:
    robot.stop()
    ena.off()
    enb.off()


"""

Reference:
Code adapted from https://projects.raspberrypi.org/en/projects/rpi-python-line-following/6

"""

