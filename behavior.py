# To prevent servo from flickering, wer’re using this hack:
# https://ben.akrin.com/?p=9158

# Imports hack
import RPi.GPIO as GPIO
import pigpio

# Imports ultrassonic sensor library
from gpiozero import DistanceSensor

# Imports time to use sleep and (hopefully) calculate the speed of approach
import time

# Imports fancy math to easily calculate median distance from multiple readings (for accuracy)
import statistics

# Settings for the servo
servo = 25 # GPIO 
pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_PWM_frequency( servo, 50 )

# Settings for the sensor
sensor = DistanceSensor(echo=21, trigger=18, max_distance=4)

# Custom function to replace the scaled() one, as I couldn’t get it to work:
# https://gpiozero.readthedocs.io/en/stable/api_tools.html
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

# Custom function to move the lid, where open is a value from 0 (closed) to 100 (opened)
def mouth(open):
  # Cheatsheet:
  #   0 = closed =  45 deg = 1000
  # 100 = open   = -45 deg = 2000
  pulse = int( translate(open, 0, 100, 1000, 2000) )
  pwm.set_servo_pulsewidth( servo, pulse )

# Creates empty list to house readings from the distance sensor
queue = []

# Infinite loop
while True:

  # If the queue has less than N items
  if len(queue) < 20:
  
    # Add one more readings from the sensor to it
    queue.append(sensor.distance)
    
    # Skip everything and start the iteration of the loop
    continue
  
  # If the queue has exactly N readings from the sensor
  else: 
    
    # Get the median reading (to remove outliers)
    distance = statistics.median(queue)
    print(distance)
    
    # Discard anything below 50 cm
    if distance < .5:
      distance = .5
    
    # Discard anything above 2 meters
    if distance > 2:
      distance = 2
    
    # Calculate how open the lid should be (from 0 to 100)
    openness = int( translate(distance, .5, 2, 0, 100 ) )
    
    # Make the lid move
    mouth(open=openness)
    
    # Wait for a bit
    time.sleep(.01)
    
    # Remove all 20 items from the queue
    queue.clear()

  #run each iteration around 20 times per second
  time.sleep(.01)
