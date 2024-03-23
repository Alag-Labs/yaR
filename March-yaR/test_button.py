import RPi.GPIO as GPIO
import time

# Using BCM numbering, not the physical pin number
GPIO.setmode(GPIO.BCM)
button_pin = 2

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
print('starting')
try:
    while True:
        if not GPIO.input(button_pin):
            print("Button pressed")
            time.sleep(1)
        else:
            time.sleep(0.2)
            
except KeyboardInterrupt:
    GPIO.cleanup()

