import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
from libcamera import controls
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

# Using BCM numbering, not the physical pin number
GPIO.setmode(GPIO.BCM)
button_pin = 2
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

picam2 = Picamera2()

print('Starting')
is_recording = False

try:
    while True:
        if not GPIO.input(button_pin):
            if not is_recording:
                print("Button pressed. Starting camera and recording...")
                picam2.start(show_preview=False)
                picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
                time.sleep(2)  # Delay to allow camera to start properly
                encoder = H264Encoder()
                output = FileOutput('video.h264')
                picam2.start_recording(encoder, output)
                is_recording = True
            else:
                print("Button pressed. Stopping recording and camera...")
                picam2.stop_recording()
                picam2.close()
                is_recording = False
            time.sleep(1)  # Debounce delay to avoid multiple button presses
        else:
            time.sleep(0.2)

except KeyboardInterrupt:
    if is_recording:
        picam2.stop_recording()
    picam2.close()
    GPIO.cleanup()