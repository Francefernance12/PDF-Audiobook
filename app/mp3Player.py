import vlc

class MP3Player:
    def __init__(self):
        # player is the vlc media player
        self.player = None
        self.is_playing = False

    # output is the path to the mp3 file
    def play_mp3(self, output):
        if self.player:
            self.stop()
        self.player = vlc.MediaPlayer(output)
        self.player.play()
        self.is_playing = True

    # stop audio
    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None
            self.is_playing = False
    
    # check if audio is playing
    def is_audio_playing(self):
        return self.is_playing
