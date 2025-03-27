# Kivy
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
# Other
from threading import Thread
import traceback
import os
# Local imports
from app import GoogleTTS, MP3Player, loadPDF


"""Intro splash screen"""
class SplashScreen(Screen):
    # splash screen appears for 3 seconds
    def on_enter(self, *args):
        Clock.schedule_once(self.switch_to_main, 3)

    # Eventually switch to main screen
    def switch_to_main(self, *args):
        self.manager.current = "main"


"""The file selector popup"""
class FileSelectorPopup(Popup):
    # File loader Object
    load = ObjectProperty(None)


"""Main screen"""
class MainScreen(Screen):
    # Labels
    file_path = StringProperty("No file selected")
    file_select_state = StringProperty("Tap the button below to choose a PDF file and generate an audiobook.")

    def open_file(self):
        # Open the file selector popup
        popup = FileSelectorPopup()
        # Set the load callback with the popup instance
        popup.load = lambda path, selection: self.load_file(path, selection, popup)
        popup.open()
    
    # Temporarily disabled
    # # Dynamic Button
    # def create_audiobook_button(self):
    #     # Get the container and buttons
    #     audiobook_button_container = self.ids.audiobook_button
    #     choose_file_button = self.ids.choose_file_button

    #     # Avoid duplicates
    #     if any(isinstance(child, Button) for child in audiobook_button_container.children):
    #         return

    #     # Dynamic button creation
    #     audiobook_button_layout = Button(
    #         text='Audiobook Player',
    #         size_hint_x=1,
    #         pos_hint={'center_x': 0.5, 'center_y': 0.5},
    #         background_color=(0, 0, 0, 0), # blue background (#1C4983)
    #         background_normal='',
    #         color=(232/255, 241/255, 255/255, 1),  # Light text (#e8f1ff)
    #         padding=[24, 16],
    #         font_size="20sp",
    #         font_name="./app/Fonts/Roboto_SemiCondensed-Medium.ttf"
    #     )

    #     # Create new canvas
    #     audiobook_button_layout.canvas.before.clear()
    #     with audiobook_button_layout.canvas.before:
    #         Color(46/255, 93/255, 159/255, 1) 
    #         rectangle = RoundedRectangle(pos=audiobook_button_layout.pos, 
    #                          size=audiobook_button_layout.size, 
    #                          radius=[15, 15, 15, 15])
        
    #     # bind position and size to the button and text
    #     audiobook_button_layout.bind(pos=lambda instance, value: setattr(rectangle, 'pos', value))
    #     audiobook_button_layout.bind(size=lambda instance, value: setattr(rectangle, 'size', value))
        
    #     # add button to container
    #     audiobook_button_container.add_widget(audiobook_button_layout)

    #     # adjust size hint
    #     choose_file_button.size_hint_x = 0.5
    #     audiobook_button_container.size_hint_x = 0.5

    #     # onpress listener
    #     audiobook_button_layout.on_press = self.switch_to_screen
        

    # Load the selected PDF file
    def load_file(self, path, selection, popup):
        print("Loading file")

        # Check if selection is empty
        if not selection:
            print(f"No file selected from {path}")
            return

        try:
            # Create audiobook button once PDF selected
            # self.create_audiobook_button()

            # Change string property after selecting path
            full_file_path = os.path.join(path, selection[0])
            self.file_path = selection[0]
            self.file_select_state = "Load another PDF file to generate an audiobook."
            print(f"Attempting to load: {self.file_path}")
            
            # Dismiss selector popup
            popup.dismiss()
            
            # extract text from pdf
            pdf_content = loadPDF(self.file_path)
            if not pdf_content:
                print("Error: Could not extract text from PDF")
                return 
            # Change Label
            fix_file_path = full_file_path.replace('\\', '/')
            self.file_path = f"Recent file: {fix_file_path.split('/')[-1] if '/' in fix_file_path else fix_file_path.split('//')[-1]}"


            # display text count
            print(f"Successfully loaded PDF with {len(pdf_content)} characters")

            # changing text string property from TextScreen to PDF content
            text_screen = self.manager.get_screen("text")
            text_screen.text = pdf_content
            text_screen.has_pdf = True

            # remove old mp3
            if os.path.exists("output.mp3"):
                os.remove("output.mp3")

            # Switch to text screen
            self.switch_to_screen()

        except Exception as e:
            print(f"Error loading file: {str(e)}")
            traceback.print_exc()

    # switch to text screen
    def switch_to_screen(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = "text"


"""Loading waiting popup"""
class loading_tts_popup(Popup):
    pass


"""PDF viewer"""
class TextScreen(Screen):
    # Instances
    google_tts = GoogleTTS()
    mp3_player = MP3Player()

    # booleans
    text = StringProperty("")
    has_pdf = BooleanProperty(False)
    play_button_disabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(TextScreen, self).__init__(**kwargs)
        self.popup = loading_tts_popup()

    # checks if mp3 exists, Used for the kivy lang and create_tts function
    def check_audio_exists(self):
        if os.path.exists("output.mp3"):
            return True
        else:
            return False
    
    def check_thread_done(self, dt):
        if not self.play_thread.is_alive():
            self.popup.dismiss()
            self.play_button_disabled = False
            self.play_audio()
            print("Audio created, audio playing")
            return False  # stops the clock schedule
        return True  # keeps checking
    
    # Creates mp3 from google tts API
    def create_tts(self):
        print("Creating Audio")
        # disables play button to prevent multiple threads
        self.play_button_disabled = True

        # creates mp3
        if not self.check_audio_exists():
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
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = "main"


"""Initialize App"""
class AudioBookApp(App):
    def build(self):
        # Window properties
        from kivy.config import Config
        Config.set('graphics', 'resizable', '0')
        Config.set('graphics', 'width', 812)
        Config.set('graphics', 'height', 600)

        # load KV File
        self.load_kv("styles.kv")

        # screens
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(TextScreen(name="text"))
        return sm
    
    # Once the app is either closed, or exited
    def on_stop(self):
        print("App stopped")
        if os.path.exists("output.mp3"):
            os.remove("output.mp3")
            print("output.mp3 deleted")
        print("Bye")

"""Runs app"""
if __name__ == '__main__':
    AudioBookApp().run()
