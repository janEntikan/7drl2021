from random import randint, uniform, choice


def get_segment_rects():
    '''
    A 3x3 grid of rects, some take two places.
    S   > F
    112 > 152
    402 > 402
    433 > 673
    '''
    segment_rects = [
        [0,0,1,2],
        [1,0,2,1],
        [2,1,1,2],
        [0,2,2,1],
    ]
    for segment in segment_rects:
        if segment[2] > 1:
            if randint(0,1):
                segment[2] = 1
                new_segment = [segment[0]+1,segment[1],1,1]
                segment_rects.append(new_segment)

        if segment[3] > 1:
            if randint(0,1):
                segment[3] = 1
                new_segment = [segment[0],segment[1]+1,1,1]
                segment_rects.append(new_segment)
    return segment_rects


class BSP(): # Recursive Binary Space Partition Object
    def __init__(self, rect=[0,0,32,32], min_size=4, parent=None, root=None, vertical=False, first=True):
        self.first = first # first is always the top- or left-most leaf
        self.rect = rect
        self.min_size = min_size
        self.root = self if root == None else root
        self.parent = parent # To connect to if self.first
        self.children = []
        self.leafs = []
        self.vertical = vertical
        self.doors = []
        self.all_doors = []
        self.split()
        self.connect()

    def connect(self):
        x, y, w, h = self.rect
        if self.vertical:
            dx, dy = self.first*w, int(h/2)
        else:
            dx, dy = int(w/2), self.first*h

        self.doors.append((dx, dy))
        global_pos = [x+dx, y+dy]
        if global_pos not in self.root.all_doors:
            self.root.all_doors.append(global_pos)
       
    def split(self):
        x,y,w,h = self.rect
        # If wider, split vertically.
        if w > h:
            vertical = 1
        # If higher, split horizontally.
        elif h > w:
            vertical = 0
        # Else flip a coin
        else:
            vertical = randint(0,1)
        # Actually calculate the split
        if vertical:
            split = int(w/2)+randint(-3,3)
            rect_a = [x, y, split, h]
            rect_b = [x+split, y, w-split, h]
        else:
            split = int(h/2)+randint(-3,3)
            rect_a = [x, y, w, split]
            rect_b = [x, y+split, w, h-split]
        # If any result is smaller than minimal size, add to the root's leafs.
        # TODO: Add a random offset for more diverse room shapes.
        for rect in (rect_a, rect_b):
            if rect[2] < self.min_size or rect[3] < self.min_size:
                self.root.leafs.append(self)
                return
        # Else we make the recursive children.
        a = BSP(rect_a, self.min_size, self, self.root, vertical, True)
        b = BSP(rect_b, self.min_size, self, self.root, vertical, False)
        self.children.append(a)
        self.children.append(b)


if __name__ == "__main__":
    root = BSP([0,0,32,32], 5)
    grid = []
    for y in range(32):
        grid.append([])
        for x in range(32):
            grid[y].append(" ")

    for l, leaf in enumerate(root.leafs):
        x, y, w, h = leaf.rect
        for iy in range(h):
            for ix in range(w):
                if iy ==0 or ix == 0:
                    grid[iy+y][ix+x] = "#"

    for i in grid:
        print(str().join(i))