"""Simple Maze generator."""
from dataclasses import dataclass, field
from math import ceil, sqrt
from random import choice
from typing import Any, Dict

_DIRS = {'n': (0, -1), 'e': (1, 0), 's': (0, 1), 'w': (-1, 0)}
_REVERSE = {'n': 's', 'e': 'w', 's': 'n', 'w': 'e'}
_REPR = {(False, False, False): 'G', (True, False, False): 'S', (False, True, False): 'E', (False, False, True): 'D'}


@dataclass
class Room:
    x: int = 0
    y: int = 0
    num: int = -1
    is_start: bool = False
    is_end: bool = False
    is_dead_end: bool = False
    neighbors: Dict[str, Any] = field(default_factory=dict)

    @property
    def room_key(self):
        return self.x, self.y

    def connect(self, other, direction):
        self.neighbors[direction] = other
        other.neighbors[_REVERSE[direction]] = self


class Maze:
    """
    This class generates a maze of connected rooms with exactly one possible
    path from start to end with single dead end rooms added in at random.
    The maze is made up of the number of `cells` passed to the constructor
    out of which `dead_end_prct` become dead end cells/rooms.
    """
    def __init__(self, cells, dead_end_prct=0.2):
        if dead_end_prct < 0 or dead_end_prct >= 1:
            raise ValueError('Bad JanEntikan!! I will not allow me to make too much dead ends')
        if cells < 2:
            raise ValueError('Almost got me there you silly...')
        if cells > 600:
            raise ValueError('Not even I can do magic!!')
        self._cells = cells - int(cells * dead_end_prct)
        self._dead_ends = cells - self._cells
        self._rooms = {}
        self._current_room = 0, 0
        while not self._generate():
            pass

    def _generate(self):
        path_cells_remaining = self._cells - 1
        current_room = Room(is_start=True)
        history = [current_room.room_key]
        rooms = {}

        def valid_moves():
            mvs = []
            for k in _DIRS:
                x, y = _DIRS[k]
                room_key = current_room.x + x, current_room.y + y
                if room_key not in rooms:
                    mvs.append(k)
            return mvs
        
        failed = 0

        was_success = True
        while not current_room.is_end:
            possible_moves = valid_moves()
            if not possible_moves:
                k = history.pop()
                current_room = rooms.pop(k)
                path_cells_remaining += 1
                failed += 1
                if not was_success:
                    droplist = []
                    for k in current_room.neighbors:
                        n = current_room.neighbors[k]
                        if n.num > current_room.num:
                            droplist.append(k)
                    while droplist:
                        current_room.neighbors.pop(droplist.pop())
                was_success = False
                if failed > 100:
                    return False
                continue
            direction = choice(possible_moves)
            old_key = current_room.room_key
            rooms[old_key] = current_room
            history.append(old_key)
            path_cells_remaining -= 1
            current_room = Room(x=current_room.x + _DIRS[direction][0], 
                                y=current_room.y + _DIRS[direction][1],
                                num=self._cells - path_cells_remaining - 2, 
                                is_end=False if path_cells_remaining > 0 else True)
            rooms[old_key].connect(current_room, direction)
            was_success = True
        rooms[current_room.room_key] = current_room
        current_room.num = -1

        dead_ends_remaining = self._dead_ends
        while dead_ends_remaining > 0:
            k = choice(list(rooms.keys()))
            current_room = rooms[k]
            if current_room.is_dead_end:
                continue
            possible_moves = valid_moves()
            if not possible_moves:
                continue
            direction = choice(possible_moves)
            dead_ends_remaining -= 1
            dead_end = Room(x=current_room.x + _DIRS[direction][0], 
                            y=current_room.y + _DIRS[direction][1],
                            num=-2,
                            is_dead_end=True)
            current_room.connect(dead_end, direction)
            rooms[dead_end.room_key] = dead_end
        self._rooms = rooms
        return True

    def move(self, direction):
        if direction in self.current_room.neighbors:
            new_room = self.current_room.neighbors[direction]
            self._current_room = new_room.x, new_room.y
        else:
            raise ValueError('Cannot move in that direction')

    def plot(self):
        xmin = 1
        xmax = -1
        ymin = 1
        ymax = -1
        for room in self._rooms.values():
            xmin = min(xmin, room.x)
            xmax = max(xmax, room.x)
            ymin = min(ymin, room.y)
            ymax = max(ymax, room.y)
        s = ''
        for y in range(ymin, ymax + 1):
            for x in range(xmin, xmax + 1):
                if (x, y) in self._rooms:
                    room = self._rooms[(x, y)]
                    if room.num > -1:
                        s += ' ' + f'{room.num:02d}'[-2:] + ' '
                    else:
                        s += '!' + _REPR[(room.is_start, room.is_end, room.is_dead_end)] * 2 + '!'
                else:
                    s += '    '
                s += ' '
            s += '\n'
        print(s)

    @property
    def doors(self):
        return list(self.current_room.neighbors.keys())

    @property
    def new_doors(self):
        mvs = []
        if self.current_room.is_dead_end:
            return mvs
        for k in self.current_room.neighbors:
            if self.current_room.neighbors[k].num - self.current_room.num != -1:
                mvs.append(k)
        return mvs

    @property
    def current_room(self):
        return self._rooms[self._current_room]
