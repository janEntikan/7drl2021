from direct.interval.LerpInterval import LerpFunc
from random import randint, uniform, choice
from panda3d.core import NodePath


DIRS = [(0,1),(1, 0),(0,-1),(-1,0)]
ITEM_SPOTS = [
    [True,True,True,False],
    [True,True,False,True],
    [True,False,True,True],
    [False,True,True,True],
]
PROP_SPOT = [
    [True,True,True,True],
]


class Props():
    def __init__(self):
        self.floor = randint(0,3)
        self.wall = randint(0,2)
        self.prop = randint(0,2)
        self.prop_angle = randint(0,3)


class Tile():
    def __init__(self, props=None, pos=(0,0), char="#"):
        if not props:
            self.props = Props()
        else:
            self.props = props
        self.made = False
        self.pos = pos
        self.root = NodePath("tile")
        self.unlit = NodePath("tile_unlit")
        self.backsides = NodePath("tile_backsides")
        self.root.set_pos(pos[0], -pos[1], 0)
        self.unlit.set_pos(pos[0], -pos[1], 0)
        self.char = char
        self.access = [True,True,True,True]
        self.neighbors = []

    def get_access(self):
        for d, dir in enumerate(DIRS):
            x = self.pos[0]+dir[0]
            y = self.pos[1]+dir[1]
            tile = base.map.tiles[x,y]
            if tile.char in "#":
                self.access[d] = False

    def add_prop(self):
        name = "block_prop_"+str(self.props.prop)
        p = base.map.tile_set[name].copy_to(self.unlit)
        p.set_h(self.props.prop_angle*90)

    def make_mesh(self):
        self.make_walls()
        if self.char == "P":
            self.add_prop()

    def make_walls(self):
        if not self.props:
            floor = "floor_0"
        else:
            floor = "floor_"+str(self.props.floor)
        f = base.map.tile_set[floor].copy_to(self.unlit)
        light = self.pos[0]%2 == 1 and self.pos[1]%2 == 1
        for angle, access in enumerate(self.access):
            if not access:
                wall_type = "wall_"+str(self.props.wall)
                w = base.map.tile_set[wall_type].copy_to(self.root)
                heading = (angle+1)*90 
                w.set_h(heading)
                if light:
                    l = base.map.tile_set["light"].copy_to(self.unlit)
                    l.set_h(heading)
                if not randint(0,8):
                    p = randint(0,3)
                    try:
                        l = base.map.tile_set["wall_prop_"+str(p)].copy_to(self.unlit)
                        l.set_h(heading)                        
                    except:
                        pass

class Ending(Tile):
    def __init__(self, props, pos, direction):
        Tile.__init__(self, props, pos, char="e")

    def make_mesh(self):
        self.make_walls()

    def make_walls(self):
        f = base.map.tile_set["floor_0"].copy_to(self.unlit)
        light = self.pos[0]%2 == 1 and self.pos[1]%2 == 1
        for angle, access in enumerate(self.access):
            if not access:
                w = base.map.tile_set[ "wall_0"].copy_to(self.root)
                heading = (angle+1)*90 
                w.set_h(heading)
                l = base.map.tile_set["light"].copy_to(self.unlit)
                l.set_h(heading) 

class Door(Tile):
    def __init__(self, props, pos, direction):
        Tile.__init__(self, props, pos, char="=")
        self.direction = direction
        self.open = False

    def make_mesh(self):
        doorway = base.map.tile_set["doorway"].copy_to(self.root)
        doorway.set_h(90*(self.direction in "ns"))
        self.door = base.map.tile_set["door"].copy_to(base.map.dynamic)
        self.door.set_pos(self.pos[0],-self.pos[1],0)
        self.door.set_h(90*(self.direction in "ns"))
        self.open_door(1)

    def activate(self):
        lerp = LerpFunc(
            self.open_door, fromData=1, 
            toData=0, duration=1,
        )
        base.sequence_player.add_to_sequence(lerp)
        base.sequence_player.finalize()
        base.map.build(self.direction)
        self.open = True
    
    def open_door(self, value):
        chars = self.door.find_all_matches('**/+Character')
        for char in chars:
            char.node().get_bundle(0).freeze_joint("closed", value)

