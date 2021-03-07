from random import randint, uniform, choice
from direct.interval.LerpInterval import LerpFunc


DIRS = [(0,1),(1, 0),(0, -1),(-1,0)]
LOCS = [(4, 8),(8, 4),(4, 0),(0, 4)]


class Tile():
    def __init__(self, room, pos, char="#"):
        self.room = room
        self.pos = pos
        self.root = room.root.attach_new_node("tile")
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
                try:
                    t = self.room.tiles[y][x]
                    self.surrounding[sy][sx] = t
                except IndexError:
                    self.surrounding[sy][sx] = Tile(self.room, (x,y), " ")

    def make_mesh(self):
        if not self.char in "#":
            self.make_walls()
        self.root.flatten_strong() 

    def make_walls(self):
        f = base.tile_set["floor_a"].copy_to(self.root)
        if self.char == "=": 
            return
        light = self.pos[0]%2 == 1 and self.pos[1]%2 == 1 
        vent = self.pos[0]%4 == 1 and self.pos[1]%4 == 1 

        for angle, offset in enumerate(((0,1), (1,0), (2,1), (1,2))):
            if self.surrounding[offset[1]][offset[0]]:
                neighbour = self.surrounding[offset[1]][offset[0]]
                if neighbour.char == "#":
                    wall_type = "wall_a"
                    w = base.tile_set[wall_type].copy_to(self.root)
                    heading = -angle*90 
                    w.set_h(heading)
                    if light:
                        l = base.tile_set["light"].copy_to(self.root)
                        l.set_h(heading)
                    if vent and randint(0,1): 
                        l = base.tile_set["vent"].copy_to(self.root)
                        l.set_h(heading)
                    a = choice(["table", "terminal","chairs"])
                    if not randint(0,16):
                        l = base.tile_set[a].copy_to(self.root)
                        l.set_h(heading)                        


class Door(Tile):
    def __init__(self, room, pos, direction, open=False):
        Tile.__init__(self, room, pos, char="=")
        self.direction = direction
        self.open = open

    def make_mesh(self):
        if not self.char in "#":
            self.make_walls()
        self.root.flatten_strong() 
        doorway = base.tile_set["doorway"].copy_to(self.root)
        doorway.set_pos(self.pos[0],-self.pos[1],0)
        if not self.direction%2: doorway.set_h(90)
        self.door = base.tile_set["door"].copy_to(doorway)
        self.open_door(int(not self.open))

    def activate(self):
        self.open = True
        lerp = LerpFunc(
            self.open_door, fromData=1, 
            toData=0, duration=0.25,
        )
        base.sequence_player.add_to_sequence(lerp)
        dir = DIRS[self.direction]
        x = self.room.x+dir[0]
        y = self.room.y+dir[1]
        if not (x,y) in base.rooms:
            base.rooms[(x,y)] = Room(x,y,(self.direction+2)%4)

    def open_door(self, value):
        chars = self.door.find_all_matches('**/+Character')
        for char in chars:
            char.node().get_bundle(0).freeze_joint("closed", value)
        

class Room():
    def __init__(self, x, y, back_direction=None):
        self.x, self.y = x, y
        self.rect = [(x*9),(y*9),9,9]
        self.root = render.attach_new_node("room")
        self.root.set_pos(self.rect[0], -self.rect[1], 0)
        self.doors = [None,None,None,None]
        self.tiles = []
        self.back_direction = back_direction
        print(x, y, self.rect, self.back_direction)

        self.construct()

    def construct(self):
        self.fill()
        self.generate()
        self.make_doors()
        self.finalize()
        self.print()

    def make_door(self, d=0, open=False):
        x = LOCS[d][0]
        y = LOCS[d][1]
        self.tiles[y][x] = Door(self, [x,y], d, open=open)

    def make_doors(self):
        if not self.back_direction == None:
            self.make_door(self.back_direction, open=True)
            b = (self.back_direction+choice((-1,1,2)))%4
            self.make_door(b)
        else:
            self.make_door(randint(0,3))

    def generate(self):
        for y in range(self.rect[3]-2):
            for x in range(self.rect[2]-2):
                tile = self.tiles[y+1][x+1]
                tile.char = " "

    def fill(self):
        for y in range(self.rect[3]):
            self.tiles.append([])
            for x in range(self.rect[2]):
                self.tiles[y].append(Tile(self,[x,y], "#"))

    def finalize(self):
        for y in range(self.rect[3]):
            for x in range(self.rect[2]):
                self.tiles[y][x].get_surrounding_tiles()
                self.tiles[y][x].make_mesh()

    def print(self):
        for y in range(self.rect[3]):
            s = ""
            for x in range(self.rect[2]):
                s += self.tiles[y][x].char
            print(s)

