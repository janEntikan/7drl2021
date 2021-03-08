from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.actor = Actor("worm.bam")
        self.actor.reparent_to(render)
        self.actor.loop("idle")

base = Base()
base.run()