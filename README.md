#yaR

## Overview

The yaR project consists of two main components: the yaR-server, a Django-based server application, and the yaR-client, designed to run on a Raspberry Pi device. This project facilitates an IoT system where the Raspberry Pi interacts with various sensors and communicates with the Django server for processing and responding to data.

## yaR-server Setup

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)
- Virtualenv (optional but recommended for creating a virtual environment)

### Installation

1. Clone the repository to your local machine.
2. Navigate to the `yaR-server` directory.
3. Create a virtual environment (optional):
python3 -m venv venv
source venv/bin/activate

4. Install the required dependencies:
pip install -r requirements.txt

5. Set up environment variables:
- GEMINI_API_KEY: Your Gemini API key.
- GOOGLE_APPLICATION_CREDENTIALS: Path to your Google credentials JSON service account file.

These can be set in your shell or through a `.env` file in the `yaR-server` directory.
6. Initialize the database (make sure you are in the directory containing `manage.py`):
python manage.py migrate


7. Start the server:
python manage.py runserver


## yaR-client Setup (Raspberry Pi)

### Hardware Requirements
- Raspberry Pi (tested on Raspberry Pi 3 and 4)
- Camera sensor compatible with the Raspberry Pi
- Audio HAT with speaker
- Button connected to GPIO pin 4 and ground

### Software Installation

1. Clone the repository to your Raspberry Pi.
2. Navigate to the `yaR-client` directory.
3. Install necessary Python packages (it's recommended to use a virtual environment):
pip install -r requirements.txt

4. Make sure to enable the camera and configure the GPIO pins according to your setup.

### Running the yaR-client

To run the yaR-client application, execute:
python main.py


Ensure that your server is running and accessible from the Raspberry Pi for the client to communicate properly.

## Notes

- For the Django server, you must place your Gemini API key and Google credentials JSON service account file as described in the setup. These are critical for the server's functionality.
- For the Raspberry Pi setup, ensure that all hardware components are properly connected and configured before running the client application.

For further assistance or contributions, please open an issue or submit a pull request.


