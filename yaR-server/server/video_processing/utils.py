import os


def is_app_engine():
    return os.getenv("GAE_ENV", "").startswith("standard")


def get_directory(base_directory):
    if is_app_engine():
        return os.path.join("/tmp", base_directory)
    else:
        return base_directory


def save_video_file(video_file, board_token, directory="uploads"):
    directory = get_directory(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    video_file_path = os.path.join(directory, f"video-{board_token}.mp4")
    with open(video_file_path, "wb") as f:
        for chunk in video_file.chunks():
            f.write(chunk)
    return video_file_path


import os
import wave


def save_audio_file(uploaded_audio, board_token, directory="audio"):
    directory = get_directory(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    audio_file_path = os.path.join(directory, f"audio-{board_token}.wav")
    with open(audio_file_path, "wb") as wf:
        for chunk in uploaded_audio.chunks():
            wf.write(chunk)

    return audio_file_path


import cv2
from imutils import paths


def extract_frames(video_file_path, directory="frames"):
    directory = get_directory(directory)
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        raise Exception("Error opening video file")
    if not os.path.exists(directory):
        os.makedirs(directory)
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(directory, f"frame-{frame_count}.jpg")
        cv2.imwrite(frame_path, frame)
        frame_count += 1
    cap.release()
    return directory


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def find_least_blurry_frame(directory):
    highest_focus_measure = 0
    least_blurry_image_path = None

    for image_path in paths.list_images(directory):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = variance_of_laplacian(gray)
        if fm > highest_focus_measure:
            highest_focus_measure = fm
            print(least_blurry_image_path)
            least_blurry_image_path = image_path
    if least_blurry_image_path is None:
        raise Exception("No frames found")
    return least_blurry_image_path


def extract_and_find_least_blurry_frame(video_file_path, directory="frames"):
    directory = get_directory(directory)
    cap = cv2.VideoCapture(video_file_path)
    if not cap.isOpened():
        raise Exception("Error opening video file")
    if not os.path.exists(directory):
        os.makedirs(directory)

    highest_focus_measure = 0
    least_blurry_frame_path = None
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fm = variance_of_laplacian(gray)
        if fm > highest_focus_measure:
            highest_focus_measure = fm
            least_blurry_frame_path = os.path.join(
                directory, f"frame-{frame_count}.jpg"
            )
            cv2.imwrite(least_blurry_frame_path, frame)
        frame_count += 1

    cap.release()

    if least_blurry_frame_path is None:
        raise Exception("No frames found")

    return least_blurry_frame_path


from google.cloud import speech


def convert_speech_to_text(audio_file_path):
    client = speech.SpeechClient()

    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript
    print(transcript)

    return transcript


import google.generativeai as genai
import pathlib
import google.ai.generativelanguage as glm


def image_to_text(image_path, prompt, stream=True):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro-vision")
    if stream:
        response_generator = model.generate_content(
            glm.Content(
                parts=[
                    glm.Part(text=prompt),
                    glm.Part(
                        inline_data=glm.Blob(
                            mime_type="image/jpeg",
                            data=pathlib.Path(image_path).read_bytes(),
                        )
                    ),
                ],
            ),
            stream=True,
        )

        for chunk in response_generator:
            yield chunk.text
    else:
        response = model.generate_content(
            glm.Content(
                parts=[
                    glm.Part(text=prompt),
                    glm.Part(
                        inline_data=glm.Blob(
                            mime_type="image/jpeg",
                            data=pathlib.Path(image_path).read_bytes(),
                        )
                    ),
                ],
            )
        )

        return response.text


import requests
from google.cloud import texttospeech


def convert_text_to_speech(input_text, board_token, directory="response"):
    directory = get_directory(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    output_file = os.path.join(directory, f"response-{board_token}.mp3")

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Studio-O"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        effects_profile_id=["small-bluetooth-speaker-class-device"],
        pitch=0,
        speaking_rate=1,
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    chunk_size = 1024
    for i in range(0, len(response.audio_content), chunk_size):
        yield response.audio_content[i : i + chunk_size]


import time


def get_time(starting_time):
    return time.time() - starting_time


from google.cloud import vision
import io


def ocr(image_path):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description.strip()
    else:
        return ""
