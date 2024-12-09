# Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
# Other
from threading import Thread, Lock
import traceback
import os
# Project Files
from app.pdf_utils import loadPDF
from app.google_tts import GoogleTTS
from app.mp3Player import MP3Player

# Intro splash screen
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_to_main, 3)

    def switch_to_main(self, *args):
        # Switch to the main screen
        self.manager.current = "main"


# The file selector popup
class FileSelectorPopup(Popup):
    # File loader Object
    load = ObjectProperty(None)

    def load(self, path, selection):
        if selection:
            print(f"Selected file(s): {selection}")
            print(f"From path: {path}")
        else:
            print("No file selected.")

# Main screen
class MainScreen(Screen):
    file_path = StringProperty("No file selected")
    main_text = StringProperty("Please select a PDF file")

    def open_file(self):
        # Open the file selector popup
        popup = FileSelectorPopup()
        # Set the load callback with the popup instance
        popup.load = lambda path, filename: self.load_file(path, filename, popup)
        popup.open()

    def load_file(self, path, filename, popup):
        print("Loading file")
        if not filename:
            print(f"No file selected from {path}")
            return

        try:
            # Load the selected PDF file
            self.file_path = filename[0]
            print(f"Attempting to load: {self.file_path}")
            
            # dismiss popup first
            popup.dismiss()
            
            # extract text
            pdf_content = loadPDF(self.file_path)
            if not pdf_content:
                print("Error: Could not extract text from PDF")
                return 
                
            # display text
            self.pdf_text = pdf_content
            print(f"Successfully loaded PDF with {len(pdf_content)} characters")

            # changing text from TextScreen to PDF content
            text_screen = self.manager.get_screen("text")
            text_screen.text = pdf_content
            text_screen.has_pdf = True

            if os.path.exists("output.mp3"):
                os.remove("output.mp3")

            # Switch to text screen
            self.manager.current = 'text'
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            traceback.print_exc()

    # switch to text screen
    def switch_to_screen(self, *args):
        self.manager.current = "text"


# Loading popup
class loading_tts_popup(Popup):
    pass

# Pdf viewer
class TextScreen(Screen):
    text = StringProperty("")
    # objects
    google_tts = GoogleTTS()
    mp3_player = MP3Player()
    # popup = loading_tts_popup()
    # booleans
    has_pdf = BooleanProperty(False)
    play_button_disabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(TextScreen, self).__init__(**kwargs)
        self.popup = loading_tts_popup()

    # checks if mp3 exists, Used for the kivy lang and create_tts function
    def check_file_exists(self):
        if os.path.exists("output.mp3"):
            return True
        else:
            return False
    
    # Creates mp3 from google tts API
    def create_tts(self):
        print("Creating Audio")
        # disables play button to prevent multiple threads
        self.play_button_disabled = True

        # creates mp3
        if not self.check_file_exists():
            try:
                # tell user that audio is being created
                self.popup.open()
                # start google tts
                self.play_thread = Thread(target=self.google_tts.synthesize_text, args=(self.text,))
                print("waiting for thread to finish")
                self.play_thread.daemon = True
                self.play_thread.start()
                Clock.schedule_interval(self.check_thread_done, 0.1)
            except Exception as e:
                print(f"Error creating audio: {str(e)}")
                traceback.print_exc()
                self.popup.dismiss()
                self.play_button_disabled = False

    def check_thread_done(self, dt):
        if not self.play_thread.is_alive():
            self.popup.dismiss()
            self.play_button_disabled = False
            self.play_audio()
            print("Audio created, audio playing")
            return False  # stops the clock schedule
        return True  # keeps checking

    # plays mp3 using vlc
    def play_audio(self):
        # disables play button to prevent multiple threads
        self.play_button_disabled = True
        try:
            self.mp3_player.play_mp3("output.mp3")
            print("Audio playing")
        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            traceback.print_exc()
        self.play_button_disabled = False

    def stop_audio(self):

        if self.mp3_player.is_audio_playing():
            self.mp3_player.stop()
            print("Audio stopped")
        else:
            print("Audio not playing")

    def switch_to_main(self, *args):
        self.stop_audio()  # Stop audio before switching screens
        self.manager.current = "main"


# Builds App
class AudioBookApp(App):
    def build(self):
        self.load_kv("styles.kv")  # Load the kv file explicitly
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(TextScreen(name="text"))
        return sm
    
    def on_stop(self):
        print("App stopped")
        os.remove("output.mp3")
        print("output.mp3 deleted")
        print("Bye")


if __name__ == '__main__':
    AudioBookApp().run()
