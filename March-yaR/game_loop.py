import RPi.GPIO as GPIO
import time
import subprocess
from picamera2 import Picamera2
from libcamera import controls
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from request_handler import upload_video_and_handle_response

import pygame


# Using BCM numbering, not the physical pin number
GPIO.setmode(GPIO.BCM)
button_pin = 2
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variables
video_path = 'video.h264'
audio_path = 'recording3.wav'
board_token = '123456'


picam2 = Picamera2()
picam2.start(show_preview=False)
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

print('Starting')
is_recording = False
audio_process = None  # Declare audio_process variable

def play_audio(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def record_audio():
    command = ["arecord", "-D", "dmic_sv", "-c2", "-r", "48000", "-f", "S32_LE", "-t", "wav", "-V", "mono", "-v", audio_path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

try:
    while True:
        if not GPIO.input(button_pin):
            if not is_recording:
                print("Button pressed. Starting camera and audio recording...")
                audio_process = record_audio()
                encoder = H264Encoder()
                output = FileOutput(video_path)
                picam2.start_recording(encoder, output)
                is_recording = True
                time.sleep(1)
            else:
                print("Button pressed. Stopping recording and camera...")
                picam2.stop_recording()
                # Actually close it to optimise
                # picam2.close()
                audio_process.terminate()
                audio_process.wait()
                if audio_process.returncode is not None:
                    print("Audio recording stopped successfully.")
                else:
                    print("There was an issue stopping the audio recording.")
                mp3_path = upload_video_and_handle_response(video_path, audio_path, board_token)
                if mp3_path:
                    play_audio(mp3_path)
                is_recording = False
                time.sleep(1)  # Debounce delay to avoid multiple button presses
        else:
            time.sleep(0.01)
except KeyboardInterrupt:
    if is_recording:
        picam2.stop_recording()
        picam2.close()
        audio_process.terminate()
        audio_process.wait()
    GPIO.cleanup()