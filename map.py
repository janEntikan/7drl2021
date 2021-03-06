from random import randint, uniform, choice
from bsp import BSP, get_segment_rects


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

    def get_surrounding(self):
        for sy in range(3):
            for sx in range(3):
                x = self.pos[0]-1+sx
                y = self.pos[1]-1+sy
                try:
                    t = self.room.tiles[y][x]
                    self.surrounding[sy][sx] = t
                except IndexError:
                    self.surrounding[sy][sx] = Tile(self.room, (x,y), "=")

    def make_mesh(self):
        if not self.char in "#":
            self.make_walls()
        #else: # Cover walls with a ceiling
        #    f = self.room.map.tile_set["ceiling"].copy_to(self.root)
        self.root.flatten_strong() 
        if self.char == "=":
            door = self.room.map.tile_set["doorway"].copy_to(self.root)
            door.set_pos(self.pos[0],-self.pos[1],0)
            if self.pos[1] == 0 or self.pos[1] == self.room.leaf.rect[3]:
                door.set_h(90)

    def make_walls(self):
        f = self.room.map.tile_set["floor_a"].copy_to(self.root)
        if self.char == "=": 
            return
        for angle, offset in enumerate(((0,1), (1,0), (2,1), (1,2))):
            if self.surrounding[offset[1]][offset[0]]:
                neighbour = self.surrounding[offset[1]][offset[0]]
                if neighbour.char == "#":
                    wall_type = "wall_a"
                    w = self.room.map.tile_set[wall_type].copy_to(self.root)
                    heading = -angle*90 
                    w.set_h(heading)
        # TODO: use instance instead of copy/flatten
        # TODO: Different walls and props and things


class Room():
    def __init__(self, map, bsp_leaf):
        self.map = map
        self.leaf = bsp_leaf
        self.root = render.attach_new_node("room")
        self.root.set_pos(self.leaf.rect[0], -self.leaf.rect[1], 0)
        self.tiles = []

    def construct(self):
        self.fill()
        self.generate()
        self.finalize()
        self.print()

    def generate(self):
        for y in range(self.leaf.rect[3]-1):
            for x in range(self.leaf.rect[2]-1):
                tile = self.tiles[y+1][x+1]
                tile.char = " "

    def fill(self):
        for y in range(self.leaf.rect[3]+1):
            self.tiles.append([])
            for x in range(self.leaf.rect[2]+1):
                global_pos = [self.leaf.rect[0]+x, self.leaf.rect[1]+y]
                if global_pos in self.leaf.root.all_doors:
                    self.tiles[y].append(Tile(self,[x,y], "="))
                else:
                    self.tiles[y].append(Tile(self,[x,y], "#"))

    def finalize(self):
        for y in range(self.leaf.rect[3]+1):
            for x in range(self.leaf.rect[2]+1):
                self.tiles[y][x].get_surrounding()
                self.tiles[y][x].make_mesh()

    def print(self):
        for y in range(self.leaf.rect[3]+1):
            s = ""
            for x in range(self.leaf.rect[2]+1):
                s += self.tiles[y][x].char
            print(s)

class Map():
    def __init__(self, size=64):
        self.segment_rects = get_segment_rects()
        self.segment_bsp = []
        self.doors = []
        for rect in self.segment_rects:
            for r, value in enumerate(rect):
                rect[r] = int(value*(size/3))
            self.segment_bsp.append(BSP(rect))

    def load_tile_set(self, name="background"):
        self.tile_set = {}
        tile_set_root = loader.load_model("assets/models/"+name+".bam")
        for child in tile_set_root.get_children():
            self.tile_set[child.name] = child
            child.detach_node()
            child.clear_transform()

    def random_leaf(self):
        return choice(choice(self.segment_bsp).leafs)


class Medical(Map):
    def __init__(self):
        Map.__init__(self)
        self.load_tile_set()

        