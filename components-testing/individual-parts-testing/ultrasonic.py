# testing ultrasonic sensor

from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo=26, trigger=16)
while True:
    print('Distance: ', sensor.distance * 100)
    sleep(0.1)

"""
Make sure to use voltage divider with two resistors for pin connected to Echo. 
Otherwise the program will not work and Pi can be damaged!

Pins: 
VCC - 5V 
TRIG - Any GPIO pins
ECHO - Any GPIO pins
GND - GND

Resistor:
I was not able to find 330 and 470 omh resistors from Arduino Kit,
instead I used 5-band 1K Ohms (Brown, Black, Black, Brown, Brown)
With this setups, everything worked.

Reference:
Code adapted from https://projects.raspberrypi.org/en/projects/physical-computing/12
Code adapted from https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04

"""
