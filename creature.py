class Interface(): # takes care of player logic and ai response
    def update(self):
        player = base.player
        context = base.device_listener.read_context('ew')
        movement = None
        current = player.root.get_pos()
        time = 0.33

        if int(context["move"].x):         
            new = (current.x+int(context["move"].x), current.y, 0)
            movement = player.root.posInterval(time, new, startPos=current)
            player.root.look_at(new)
        elif int(context["move"].y):
            new = (current.x, current.y+int(context["move"].y), 0)
            movement = player.root.posInterval(time, new, startPos=current)
            player.root.look_at(new)

        if movement:
            if not player.root.getCurrentAnim() == "walk":
                player.root.loop("walk")
            base.sequence_player.add_to_sequence(movement)
        else:
            player.root.loop("idle")


class Creature():
    def __init__(self, name, model):
        self.name = name
        self.root = model
        self.root.setLODAnimation(2, 1, 0.0075)
        self.root.loop("idle")


