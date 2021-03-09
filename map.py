from random import randint, uniform, choice
from direct.interval.LerpInterval import LerpFunc
from collections import defaultdict
from panda3d.core import NodePath
from direct.actor.Actor import Actor
from mazegen import Maze
from creature import Worm


DIRS = [(0,-1),(1, 0),(0, 1),(-1,0)]
LOCS = [(4, 0),(8, 4),(4, 8),(0, 4)]
OPPOSITE = {
    "n":"s",
    "e":"w",
    "s":"n",
    "w":"e",
}

class Tile():
    def __init__(self, room=None, pos=(0,0), char="#"):
        self.made = False
        self.room = room
        self.pos = pos
        self.root = NodePath("tile")
        self.root.set_pos(pos[0], -pos[1], 0)
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
        f = base.map.tile_set["floor_0"].copy_to(self.root)
        light = self.pos[0]%2 == 1 and self.pos[1]%2 == 1 
        vent = self.pos[0]%4 == 1 and self.pos[1]%4 == 1 

        for angle, offset in enumerate(((0,1), (1,0), (2,1), (1,2))):
            if self.surrounding[offset[1]][offset[0]]:
                neighbour = self.surrounding[offset[1]][offset[0]]
                if neighbour.char == "#":
                    wall_type = "wall_0"
                    w = base.map.tile_set[wall_type].copy_to(self.root)
                    heading = -angle*90 
                    w.set_h(heading)
                    if light:
                        l = base.map.tile_set["light"].copy_to(self.root)
                        l.set_h(heading)
                    if not randint(0,16):
                        l = base.map.tile_set["wall_prop_0"].copy_to(self.root)
                        l.set_h(heading)                        


class Door(Tile):
    def __init__(self, room, pos, direction, open=False):
        Tile.__init__(self, room, pos, char="=")
        self.direction = direction
        self.open = open

    def make_mesh(self):
        f = base.map.tile_set["floor_0"].copy_to(self.root)
        doorway = base.map.tile_set["doorway"].copy_to(base.map.static)
        doorway.set_pos(self.pos[0],-self.pos[1],0)
        doorway.set_h(90*(self.direction in "ns"))
        self.door = base.map.tile_set["door"].copy_to(base.map.dynamic)
        self.door.set_pos(self.pos[0],-self.pos[1],0)
        self.door.set_h(90*(self.direction in "ns"))
        self.open_door(int(not self.open))

    def activate(self):
        self.open = True
        lerp = LerpFunc(
            self.open_door, fromData=1, 
            toData=0, duration=0.25,
        )
        base.sequence_player.add_to_sequence(lerp)
        base.map.move(self.direction)
        p = base.map.pos(8)
        if not p in base.map.rooms:
            base.map.rooms[p] = Room(*p)
        base.map.move(OPPOSITE[self.direction])

    def open_door(self, value):
        chars = self.door.find_all_matches('**/+Character')
        for char in chars:
            char.node().get_bundle(0).freeze_joint("closed", value)


class Room():
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = [self.x,self.y,9,9]
        self.root = base.map.static.attach_new_node("room")
        self.construct()

    def construct(self):
        self.generate()
        self.make_doors()
        self.finalize()
        base.map.enemies.append(Worm("fat",(self.x+4, -(self.y+4), 0)))

    def make_door(self, direction="n", open=False):
        print("making door", direction)
        d = "nesw".index(direction)
        x = LOCS[d][0]+self.x
        y = LOCS[d][1]+self.y
        base.map.tiles[x,y] = Door(self, [x,y], direction, open=open)

    def make_doors(self):
        for door in base.map.new_doors:
            self.make_door(door)

    def generate(self):
        for y in range(self.rect[3]-2):
            for x in range(self.rect[2]-2):
                if randint(0,9):
                    tx, ty = self.x+x+1,self.y+y+1
                    base.map.tiles[tx,ty] = Tile(self, [tx, ty], " ")

    def finalize(self):
        for y in range(self.rect[3]):
            for x in range(self.rect[2]):
                t = base.map.tiles[self.x+x,self.y+y]
                if not t.char == "#":
                    if not t.made:
                        t.made = True
                        t.get_surrounding_tiles()
                        t.make_mesh()
                        t.root.reparent_to(self.root)
        self.root.flatten_strong()


class Map(Maze):
    def __init__(self):
        Maze.__init__(self, 32)
        self.tiles = defaultdict(Tile)
        self.static = render.attach_new_node("map-static")
        self.dynamic = render.attach_new_node("map-dynamic")
        self.enemies = []
        self.rooms = {}
        self.load_tile_set()

    def pos(self, size):
        return self.current_room.x*8, self.current_room.y*8

    def set(self, pos):
        x, y, z = pos
        x = int(x)//8
        y = -int(y)//8
        self._current_room = x, y

    def load_tile_set(self, name="medical"):
        self.tile_set = {}
        tile_set_root = loader.load_model("assets/models/decks/"+name+".bam")
        for child in tile_set_root.get_children():
            self.tile_set[child.name] = child
            child.detach_node()
            child.clear_transform()
        self.tile_set["door"] = Actor("assets/models/decks/doors.bam")
