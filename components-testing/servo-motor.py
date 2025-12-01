# testing servo motor

from gpiozero import Servo
from time import sleep
 
myGPIO=19 # PWM enabled GPIO
 
servo = Servo(myGPIO)
 
while True:
    servo.mid()
    print("90 degree")
    sleep(0.5)
    servo.min()
    print("0 degree")
    sleep(1)
    servo.mid()
    print("90 degree")
    sleep(0.5)
    servo.max()
    print("180 degree")
    sleep(1)


"""
servo.value = [-1: 0 degree, 
               0: 90 degree,
               1: 180 degree]

Pins:
YELLOW - VCC, 5V
RED - Any GPIO pins, but use PWN enabled pins (BCM: 12,13,18,19) if any left.
BROWN - GND

Referece:
Code adapted from https://www.raspberrypi-spy.co.uk/2018/02/basic-servo-use-with-the-raspberry-pi/
Information learned from https://docs.arduino.cc/tutorials/generic/basic-servo-control/

If using external power supply for servo motor then read (both Power Supply and RPI/Arduino must have the COMMON GND): 
https://docs.arduino.cc/learn/electronics/servo-motors/

"""
