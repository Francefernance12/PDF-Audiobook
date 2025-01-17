# PDF Audiobook
A mobile app that converts PDFs into audio books using Google's Text-to-Speech API.

## Features
- Select a PDF file from your device
- Convert the PDF content into an audio book
- Display the PDF content
- Play the audio book
- Stop the audio book

## Installation
1. Install Python 3.10.11 from the official website: https://www.python.org/downloads/
2. Install the required packages by running the command `pip install -r requirements.txt`

## Running the App
1. Run the command `python main.py`
2. The app should now be running on your device

## Important Note
- Required to have a Google Cloud Platform account to use the google tts api. Google tts credentials(e.g. googletts-cred.json) must be placed in the same directory as the app.
- VLC media player must be installed on the device. VLC media player can be downloaded from the official website: https://www.videolan.org/vlc/download.html
- As of right now, the app only supports pdf files that are 5000 total bytes or 3-4 pages. Else, the app will shorten the text to 5000 characters.
