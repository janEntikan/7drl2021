from math import hypot
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Wait, Sequence
from random import uniform
from direct.actor.Actor import Actor
from panda3d.core import Vec3
from items import *


class Interface(): # takes care of player logic and ai response
    def update(self):
        player = base.player
        context = base.device_listener.read_context('ew')
        current = player.root.get_pos()
        new_pos = None
        turn_over = False
        time = base.turn_speed
        if int(context["move"].x):         
            new_pos = Vec3(current.x+int(context["move"].x), current.y, 0)
        elif int(context["move"].y):
            new_pos = Vec3(current.x, current.y+int(context["move"].y), 0)
        if new_pos:
            x, y = int(new_pos.x), -int(new_pos.y)
            destination_tile = base.map.tiles[x, y]
            if destination_tile.char == "#":
                return
            elif destination_tile.char == "=":
                if not destination_tile.open:
                    destination_tile.activate()
                    return
            player.animate("walk", False)
            player.move_to(new_pos)
            base.map.set(new_pos)
            turn_over = True
        elif context["fire"]:
            turn_over = player.fire()
        else:
            player.aim()
            player.stop()
        if turn_over:
            for enemy in base.map.enemies:
                enemy.update()
        else:
            for enemy in base.map.enemies:
                enemy.reset()


class Creature():
    def __init__(self, name, model, pos):
        self.name = name
        self.root = model
        self.root.set_pos(pos)
        self.root.setLODAnimation(2, 1, 0.0075)
        self.root.loop("idle")
        self.root.reparent_to(render)
        
    def stop(self):
        if not self.root.getCurrentAnim() == "idle":
            self.root.loop("idle")

    def move_to(self, pos):
        movement = self.root.posInterval(
            base.turn_speed, pos, startPos=self.root.get_pos()
        )
        self.root.look_at(pos)
        base.sequence_player.add_to_sequence(movement)


class Player(Creature):
    def __init__(self, pos):
        Creature.__init__(
            self, "player", 
            Actor("assets/models/creatures/humanoid.bam"),
            pos
        )
        self.inventory = []
        self.weapon = Weapon()
        self.weapon.hold(self)
        self.aim_select = 0
        self.aimed = None
        self.crosshair = base.icons["crosshair"]
        self.crosshair.set_scale(0.5)
        self.color()

    def color(self):
        chest = self.root.find("**/torso")
        chest.set_color((0,0.1,0.1,1))
        legs = self.root.find("**/legs")
        legs.set_color((0.02,0.02,0.02,1))
        arms = self.root.find("**/arms")
        arms.set_color((0.1,0.1,0.1,1))

    def aim(self):
        for enemy in base.map.enemies:
            vector = self.root.getPos() - enemy.root.getPos()
            enemy.distance = vector.get_xy().length()
        base.map.enemies.sort(key=lambda x: x.distance, reverse=False)
        try:
            self.aimed = base.map.enemies[self.aim_select]
            self.crosshair.reparent_to(self.aimed.root)
            self.crosshair.set_z(0.01)
            self.crosshair.show()
        except:
            return

    def fire(self):
        self.aim()
        if self.aimed:
            self.root.look_at(self.aimed.root)
            self.animate("fire", False)
            self.crosshair.hide()
            base.sequence_player.wait = 1
            self.weapon.activate(self,self.aimed)
            self.aimed.hurt()
        self.aimed = None
        return True

    def animate(self, animation, loop=True):
        if self.weapon:
            n = self.weapon.is_twohand(animation)
            if not self.root.getCurrentAnim() == n:
                if loop:
                    self.root.loop(n)
                else:
                    self.root.play(n)


class Enemy(Creature):
    def __init__(self, name, model, pos):
        Creature.__init__(self, name, model, pos)
        self.goto = None
        self.wait = True
        self.alive = True
        self.hp = 1

    def hurt(self):
        self.hp -= 1
        self.wait = True
        if self.hp > 0:
            self.root.play("hurt")
        else:
            self.alive = False
            self.root.play("die")

    def reset(self):
        if self.alive:
            self.stop()

    def detach(self, task):
        self.root.detach_node()

    def update(self):
        if not self.alive:
            base.map.enemies.remove(self)
            base.task_mgr.doMethodLater(3, self.detach, "ok")
            return
        if not self.wait:
            self.root.loop("move")
            x,y,z = self.root.get_pos()
            a = base.map.tiles[int(x),int(-y)]
            x,y,z = base.player.root.get_pos()
            b = base.map.tiles[int(x),int(-y)]
            self.next_tile = base.map.flow_field(a,b)
            x,y = self.next_tile.pos
            self.move_to((x,-y,0))
        else:
            self.wait = False


class Worm(Enemy):
    def __init__(self, type, pos):
        Enemy.__init__(
            self, "worm",
            Actor("assets/models/creatures/worm.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.5,0.9))

