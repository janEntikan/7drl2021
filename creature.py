
class Creature():
    def __init__(self, name, model):
        self.name = name
        self.root = model
        self.root.setLODAnimation(2, 1, 0.005)
        self.root.loop("idle")
        #self.root.loop("walk")


