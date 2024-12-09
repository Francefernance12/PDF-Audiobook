import vlc

class MP3Player:
    def __init__(self):
        self.player = None
        self.is_playing = False

    def play_mp3(self, output):
        if self.player:
            self.stop()
        self.player = vlc.MediaPlayer(output)
        self.player.play()
        self.is_playing = True

    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None
            self.is_playing = False
    
    def is_audio_playing(self):
        return self.is_playing
