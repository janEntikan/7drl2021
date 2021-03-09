from random import randint, uniform, choice
from collections import defaultdict
from direct.actor.Actor import Actor
from mazegen import Maze
from tiles import *
from creature import *


DIRS = [(0,-1),(1, 0),(0, 1),(-1,0)]
LOCS = [(4, 0),(8, 4),(4, 8),(0, 4)]
OPPOSITE = {
    "n":"s",
    "e":"w",
    "s":"n",
    "w":"e",
}


class Props():
    def __init__(self):
        self.floor = randint(0,3)
        self.wall = 0

class Room():
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = [self.x,self.y,9,9]
        self.props = Props()
        self.root = base.map.static.attach_new_node("room")
        self.unlit = base.map.unlit.attach_new_node("room")
        self.construct()

    def construct(self):
        self.generate()
        self.make_doors()
        self.finalize()
        base.map.enemies.append(Worm("fat",(self.x+4, -(self.y+4), 0)))

    def make_door(self, direction="n"):
        d = "nesw".index(direction)
        x = LOCS[d][0]+self.x
        y = LOCS[d][1]+self.y
        base.map.tiles[x,y] = Door(self.props, [x,y], direction)

    def make_doors(self):
        for door in base.map.new_doors:
            self.make_door(door)

    def connect_doors(self):
        for door in base.map.doors:
            d = "nesw".index(door)
            x = LOCS[d][0]+self.x
            y = LOCS[d][1]+self.y
            w = int(self.rect[2]/2)+self.rect[0]
            h = int(self.rect[3]/2)+self.rect[1]
            self.draw_line(x,y,w,h," ")

    def draw(self, x, y, char):
        base.map.tiles[x,y] = Tile(self.props, [x, y], char)

    def draw_line(self, x1, y1, x2, y2, char):
        self.draw(x1, y1, char)
        while True:
            if   x1 < x2: x1 += 1
            elif x1 > x2: x1 -= 1
            elif y1 < y2: y1 += 1
            elif y1 > y2: y1 -= 1
            else: return
            self.draw(x1, y1, char)

    def draw_square(self, rect):
        for y in range(rect[3]):
            for x in range(rect[2]):
                self.draw(rect[0]+x, rect[1]+y, " ")
               
    def generate(self):
        self.connect_doors()
        x, y, w, h = self.rect
        w = randint(1,self.rect[2]-2)
        h = randint(1,self.rect[3]-2)
        x += (self.rect[2]//2)-(w//2)
        y += (self.rect[3]//2)-(h//2)
        self.draw_square((x,y,w,h))

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
                        t.unlit.reparent_to(self.unlit)
        self.root.flatten_strong()
        self.unlit.flatten_strong()


class Map(Maze):
    def __init__(self):
        Maze.__init__(self, 32)
        self.tiles = defaultdict(Tile)
        self.static = render.attach_new_node("map-static")
        self.unlit = render.attach_new_node("map-unlit")
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

    def build(self, direction):
        self.move(direction)
        p = self.pos(8)
        if not p in self.rooms:
            self.rooms[p] = Room(*p)
        self.move(OPPOSITE[direction])
