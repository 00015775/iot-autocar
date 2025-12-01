# testing IR sensor

from gpiozero import DigitalInputDevice
from time import sleep


sensor = DigitalInputDevice(20, pull_up=False) 

while True:
  if sensor.value == 0:
    print("Object detected!")
  sleep(0.1)
  if sensor.value == 1:
    print("No object detected.")

"""

sensor.value = [
    0: no object is detected within the range defined with sensitivity potentiometer,
    1: object is detected/seen within the range defined with sensitivity potentiometer      
    ]

This IR sensor or to be precise MH Infrared Obstacle Sensor Module
just like Utrasonic Sensor detects the distance based on the light, the white LED
emits the light while the Black one receives the bounced back light. The closer the object
the lighter the bounced light will be, and the farther the object
the dimmer the bounced light will be. IR sensor is better fitted for close range objects.

NOTES: IR sensor cannot detect the black or transparent objects. If we can use 
black duct tape to make it follow the line, but we have to put the module facing downwards


The range of distance can be adjusted from the module itself:
* Turn the sensitivity potentiometer counter-clockwise to reduce sensitivity.
* Turn the sensitivity potentiometer clockwise to increase sensitivity.

Pins:
GND - GND
VCC - 3.3V or 5V
OUT - Any GPIO pins

Reference: 
Information learned from https://circuitdigest.com/microcontroller-projects/interfacing-ir-sensor-module-with-arduino

The module itself: https://einstronic.com/product/infrared-obstacle-sensor-module/

"""