from direct.interval.LerpInterval import LerpFunc
from random import randint, uniform, choice
from panda3d.core import NodePath


class Tile():
    def __init__(self, props=None, pos=(0,0), char="#"):
        self.props = props
        self.made = False
        self.pos = pos
        self.root = NodePath("tile")
        self.unlit = NodePath("tile_unlit")
        self.root.set_pos(pos[0], -pos[1], 0)
        self.unlit.set_pos(pos[0], -pos[1], 0)

        self.char = char
        self.surrounding = [
            [None,None,None],
            [None,self,None],
            [None,None,None],
        ]    

    def get_surrounding_tiles(self):
        for sy in range(3):
            for sx in range(3):
                x = self.pos[0]-1+sx
                y = self.pos[1]-1+sy
                self.surrounding[sy][sx] = base.map.tiles[x,y]

    def make_mesh(self):
        self.make_walls()

    def make_walls(self):
        f = base.map.tile_set["floor_"+str(self.props.floor)].copy_to(self.root)
        light = self.pos[0]%2 == 1 and self.pos[1]%2 == 1
        vent = self.pos[0]%4 == 1 and self.pos[1]%4 == 1 

        for angle, offset in enumerate(((0,1), (1,0), (2,1), (1,2))):
            if self.surrounding[offset[1]][offset[0]]:
                neighbour = self.surrounding[offset[1]][offset[0]]
                if neighbour.char == "#":
                    wall_type = "wall_"+str(self.props.wall)
                    w = base.map.tile_set[wall_type].copy_to(self.root)
                    heading = -angle*90 
                    w.set_h(heading)
                    if light:
                        l = base.map.tile_set["light"].copy_to(self.unlit)
                        l.set_h(heading)
                    if not randint(0,8):
                        p = randint(0,4)
                        l = base.map.tile_set["wall_prop_"+str(p)].copy_to(self.unlit)
                        l.set_h(heading)                        


class Door(Tile):
    def __init__(self, props, pos, direction):
        Tile.__init__(self, props, pos, char="=")
        self.direction = direction
        self.open = False

    def make_mesh(self):
        f = base.map.tile_set["floor_0"].copy_to(self.root)
        doorway = base.map.tile_set["doorway"].copy_to(base.map.static)
        doorway.set_pos(self.pos[0],-self.pos[1],0)
        doorway.set_h(90*(self.direction in "ns"))
        self.door = base.map.tile_set["door"].copy_to(base.map.dynamic)
        self.door.set_pos(self.pos[0],-self.pos[1],0)
        self.door.set_h(90*(self.direction in "ns"))
        self.open_door(1)

    def activate(self):
        lerp = LerpFunc(
            self.open_door, fromData=1, 
            toData=0, duration=0.25,
        )
        base.sequence_player.add_to_sequence(lerp)
        base.map.build(self.direction)
        self.open = True
    
    def open_door(self, value):
        chars = self.door.find_all_matches('**/+Character')
        for char in chars:
            char.node().get_bundle(0).freeze_joint("closed", value)

