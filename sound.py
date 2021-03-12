class SoundManager():
    def __init__(self):
        self.sounds = {}
        self.load()
        self.music = {
            "background":loader.load_sfx("assets/music/background.ogg"),
            "opening":loader.load_sfx("assets/music/opening.ogg")
        }
        self.music["background"].setLoop(True)
        self.music["opening"].play()

    def load(self):
        sounds = [
            "die", "door", "impact1", "impact2", "impact3", "impact4",
            "kill1", "kill2", "kill3", "kill4", "laser", "no", "ok",
            "reload", "scream", "squeel", "step", "take", "woah", 
            "woo1", "woo2", "woo3", "woo4", "woo5", "woo6", "zoom",           
        ]
        for sound in sounds:
            self.sounds[sound] = loader.load_sfx("assets/sound/"+sound+".wav")

    def play(self, name):
        self.sounds[name].play()

    def stop(self, name):
        self.sounds[name].stop()