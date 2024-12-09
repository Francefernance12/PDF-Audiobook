from google.cloud import texttospeech
from app.pdf_utils import loadPDF
import os
from threading import Thread, Lock


class GoogleTTS:
    def __init__(self):
        # API Credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googletts-cred.json"
        # client object
        self.client = texttospeech.TextToSpeechClient()


    def synthesize_text(self, text):
        # TODO: Make sure the user is able to select a file from app by giving the text
        # synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        self.tts_config(synthesis_input)

    def tts_config(self, synthesis_input):
        # TODO: Make sure the user is able to select a voice
        # voice selection
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-C"
        )

        # TODO: Make sure the user is able to configure the audio
        # voice config
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
            effects_profile_id=["small-bluetooth-speaker-class-device"]
        )

        self.synthesize_speech(synthesis_input, voice, audio_config)

    def synthesize_speech(self, synthesis_input, voice, audio_config):
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        self.create_audio(response)
        
    def create_audio(self, response):
        # TODO: Make sure the user is able play the audio from the app instead of downloading it
        with open("output.mp3", "wb") as output:
            output.write(response.audio_content)
            print("Audio content written to file 'output.mp3'")
            # start_mp3_player = Thread(target=play_mp3, args=(output,))
            # start_mp3_player.start()
            # if os.path.exists("output.mp3"):
            #     os.remove("output.mp3")
