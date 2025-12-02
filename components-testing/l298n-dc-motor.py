# testing L298N with DC motors

from gpiozero import Motor, OutputDevice, Robot
from time import sleep

ena = OutputDevice(12)
enb = OutputDevice(13)
ena.on()
enb.on()

# Robot(left=(forward=3, backward=2), right=(forward=21, backward=20))
robot = Robot(left=(7,8), right=(9,10))

robot.forward()
sleep(4)
robot.backward(0.5) # drive the half of the speed
sleep(4)
robot.reverse()
sleep(4)
robot.right()
sleep(4)
robot.left()
sleep(4)
robot.stop()


ena.off()
enb.off()

"""

ena for MotorA and enb for MotorB, can be referred as Right Motor and Left Motor if set up properly
these ena,enb provide control over speed, and needs to be on for wheels to work
speed is controlled:
   with ENA for right motor (MotorA)
   with ENB for left motor (MotorB)
the range of speed is 0.0 - 1.0


Pins:
OUT1-4 - Any GPIO pins
IN1-4 - Any GPIO pins
ENA/ENB - PWM enabled GPIO pins
12+V (VC) - Connect to Power Supply Battery 2x3.7V
GND - GND
5+V (VCC) - no need to connect to it since DC motors require 6V each


Reference:
Code adapted from https://projects.raspberrypi.org/en/projects/physical-computing/14
Information learned from https://lastminuteengineers.com/l298n-dc-stepper-driver-arduino-tutorial/

"""
