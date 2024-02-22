import threading
import wave
import pyaudio
import picamera
import RPi.GPIO as GPIO
from request_handler import upload_video_and_handle_response
import time
import os

import pygame


def play_audio(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


class AudioRecorder:
    def __init__(self, filename, channels=1, rate=44100, frames_per_buffer=1024):
        self.filename = filename
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.pyaudio_instance = pyaudio.PyAudio()
        self.frames = []
        self.button_pin = 4

    def record(self):
        self.is_recording = True
        stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
        )
        while self.is_recording:
            if GPIO.input(self.button_pin):
                self.frames.append(stream.read(self.frames_per_buffer))
            else:
                self.is_recording = False

        stream.stop_stream()
        stream.close()

    def save(self):
        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.pyaudio_instance.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b"".join(self.frames))


def record_video(filename, duration):
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.start_recording(filename, format="h264")
        camera.wait_recording(duration)
        camera.stop_recording()


def main():

    GPIO.setmode(GPIO.BCM)
    button_pin = 4
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    token = os.getenv("LOOKOUT_TOKEN")

    try:
        while True:
            button_state = GPIO.input(button_pin)
            if button_state == True:
                video_filename = "video.mp4"
                audio_filename = "audio.wav"
                duration = 15

                audio_recorder = AudioRecorder(audio_filename)

                audio_thread = threading.Thread(target=audio_recorder.record)
                video_thread = threading.Thread(
                    target=record_video, args=(video_filename, duration)
                )

                audio_thread.start()
                video_thread.start()

                while GPIO.input(button_pin):
                    time.sleep(0.2)

                audio_thread.join()
                video_thread.join()

                audio_recorder.save()

                mp3_path = upload_video_and_handle_response(
                    video_filename, audio_filename, token
                )

                if mp3_path:
                    play_audio(mp3_path)
            time.sleep(0.2)
    except KeyboardInterrupt:
        GPIO.cleanup()

    GPIO.cleanup()


if __name__ == "__main__":
    main()
