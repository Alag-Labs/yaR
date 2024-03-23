# REMEMBER TO RUN THIS COMMAND TO SEE IF THE MIC IS WORKING: arecord -D plughw:0 -c1 -r 48000 -f S32_LE -t wav -V mono -v file.wav

import subprocess
import time

def record_audio(duration=5):
    # Define the command as a string
    command = "arecord -D dmic_sv -c2 -r 48000 -f S32_LE -t wav -V mono -v recording.wav"
    
    # Start the command as a subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the specified duration
    time.sleep(duration)
    
    # Terminate the recording process
    process.terminate()
    
    # Wait for the process to terminate before continuing
    process.wait()
    
    # Check if the command was terminated successfully
    if process.returncode is not None:
        print("Recording stopped successfully.")
    else:
        print("There was an issue stopping the recording.")

if __name__ == "__main__":
    record_audio()

