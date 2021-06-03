import RPi.GPIO as GPIO
import pigpio
from gpiozero import DistanceSensor
from gpiozero import LED
from gpiozero import Buzzer
import time

servo = 18
pwm = pigpio.pi()
pwm.set_mode(servo, pigpio.OUTPUT)
pwm.set_PWM_frequency( servo, 50 )

sensor = DistanceSensor(echo=24, trigger=23, max_distance=1)

led_red = LED(22)
led_yellow = LED(27)
led_green = LED(17)
bz = Buzzer(4)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def mouth(open):
  #   0 = closed =  45 deg = 1000
  # 100 = open   = -45 deg = 2000
  pulse = int( translate(open, 0, 100, 1000, 2000) )
  pwm.set_servo_pulsewidth( servo, pulse )
    
previous_distance = 1.0
openness_variable = 2
is_closed = False

while True:
    
new_distance = sensor.distance
    print(new_distance)
    
if not is_closed and previous_distance - new_distance > 0.2:
        print("Too fast!")
        is_closed = True
        openness_variable = 0
        openness = int( translate(openness_variable, .5, 2, 0, 100 ) )
        mouth(open=openness)
        led_red.on()
        led_green.off()
        led_yellow.off()
        for i in range(0, 20):
            print(i)
            led_red.on()
            bz.on()
            time.sleep(0.05)
            led_red.off()
            bz.off()
            time.sleep(0.05)
        led_red.on()
    elif not is_closed and previous_distance - new_distance > 0.1:
        print("Detecting you")
        # decrease angle a little bit to stress you
        if openness_variable >= 0.05:
            openness_variable = openness_variable - 0.05
            openness = int( translate(openness_variable, .5, 2, 0, 100 ) )
            mouth(open=openness)
        led_red.off()
        led_green.off()
        led_yellow.on()
        bz.on()
        time.sleep(0.02)
        bz.off()
    elif previous_distance == 1.0 and new_distance == 1.0:
        print("Not detecting you. Restarting.")
        is_closed = False
        openness_variable = 2
        openness = int( translate(openness_variable, .5, 2, 0, 100 ) )
        mouth(open=openness)
        led_red.off()
        led_green.on()
        led_yellow.off()
    previous_distance = new_distance
    time.sleep(1)
