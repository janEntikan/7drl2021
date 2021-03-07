from direct.actor.Actor import Actor
from panda3d.core import Vec3
from map import Room


def round_vec3(vec3):
    for v, value in enumerate(vec3):
        vec3[v] = int(value)
    return vec3


class Interface(): # takes care of player logic and ai response
    def update(self):
        player = base.player
        context = base.device_listener.read_context('ew')
        current = player.root.get_pos()
        new_pos = None
        time = 0.33

        if int(context["move"].x):         
            new_pos = Vec3(current.x+int(context["move"].x), current.y, 0)
        elif int(context["move"].y):
            new_pos = Vec3(current.x, current.y+int(context["move"].y), 0)
        else:
            player.root.loop("idle")

        if new_pos:
            wx, wy, wz = round_vec3(new_pos/9)
            destination_room = base.rooms[(wx,-wy)]            
            x, y, z = new_pos
            destination_tile = destination_room.tiles[-int((y%9))][int((x%9))]
            if destination_tile.char == "#":
                return
            elif destination_tile.char == "=":
                if not destination_tile.open:
                    destination_tile.activate()
                    return
            if not player.root.getCurrentAnim() == "walk":
                player.root.loop("walk")

            movement = player.root.posInterval(time, new_pos, startPos=current)
            player.root.look_at(new_pos)
            base.sequence_player.add_to_sequence(movement)


class Creature():
    def __init__(self, name, model):
        self.name = name
        self.world_pos = [0,0]
        self.root = model
        self.root.setLODAnimation(2, 1, 0.0075)
        self.root.loop("idle")
        self.root.reparent_to(render)


class Player(Creature):
    def __init__(self):
        Creature.__init__(
            self, "player", 
            Actor("assets/models/player.bam")
        )

        chest = self.root.find("**/torso")
        chest.set_color((0,0.1,0.1,1))
        legs = self.root.find("**/legs")
        legs.set_color((0.02,0.02,0.02,1))
        #arms = self.root.find("**/arms")
        #arms.set_color((0.1,0.1,0.1,1))
