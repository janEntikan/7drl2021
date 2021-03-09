from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Wait, Sequence

from random import uniform
from direct.actor.Actor import Actor
from panda3d.core import Vec3
from math import hypot


def round_vec3(vec3):
    new = Vec3()
    for v, value in enumerate(vec3):
        new[v] = round(value)
    return new

def towards(a, b):
    try:
        sx, sy, sz = a
        fx, fy, fz = b
        dx, dy = sx - fx, sy - fy
        dist = hypot(dx, dy)
        dx, dy = dx/dist, dy/dist
    except ZeroDivisionError:
        dx, dy = 0,0
    return Vec3(dx, dy, 0)


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

class Weapon():
    def __init__(self):
        self.name = "spreadblaster"
        self.damage = 10
        self.two_handed = True
        self.icon = base.icons["plasmarifle"]


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
        self.hold(self.weapon.icon)
        self.aim_select = 0
        self.aimed = None
        self.crosshair = base.icons["crosshair"]
        self.crosshair.set_scale(0.5)
        self.muzzle = self.root.find("**/muzzle") 
        self.muzzle.hide()
        self.color()

    def color(self):
        chest = self.root.find("**/torso")
        chest.set_color((0,0.1,0.1,1))
        legs = self.root.find("**/legs")
        legs.set_color((0.02,0.02,0.02,1))
        #arms = self.root.find("**/arms")
        #arms.set_color((0.1,0.1,0.1,1))

    def flash(self, on=True):
        if on: self.muzzle.show()
        else:  self.muzzle.hide()

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
            flash_sequence = Sequence(
                Wait(0.2),
                Func(self.flash, True),
                Func(
                    base.linefx.draw_bullet, 
                    self.muzzle.get_pos(render), 
                    self.aimed.root.get_pos()
                ),
                Wait(0.15),
                Func(
                    base.linefx.remove_bullet,
                ),
                Func(self.flash, False),
            )
            base.sequence_player.add_to_sequence(flash_sequence)
            self.aimed.hurt()
        self.aimed = None
        return True

    def set_twohand(self, string):
        if self.weapon:
            if self.weapon.two_handed:
                string+="_twohanded"
            else:
                string+="_onehanded"
        return string

    def animate(self, animation, loop=True):
        n = self.set_twohand(animation)
        if not self.root.getCurrentAnim() == n:
            if loop:
                self.root.loop(n)
            else:
                self.root.play(n)

    def hold(self, item=None):
        old_item = self.root.find("**/holding")
        if old_item: old_item.remove_node()
        if item:
            hold_node = self.root.attach_new_node("holding")
            i = item.copy_to(hold_node)
            self.root.expose_joint(hold_node, "modelRoot", "hand.r")
            i.set_hpr(0,90,-90)
            i.set_scale(0.05)


class Enemy(Creature):
    def __init__(self, name, model, pos):
        Creature.__init__(self, name, model, pos)
        self.goto = None
        self.wait = True
        self.alive = True
        self.hp = 3

    def hurt(self):
        self.hp -= 1
        self.wait = False
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
        self.wait = not self.wait
        if not self.wait:
            seen = self.scan(base.player.root.get_pos())
            if seen:
                self.goto = seen
            if self.goto:
                self.root.loop("move")
                inc = towards(self.root.get_pos(),self.goto)
                inc = round_vec3(inc)
                self.move_to(self.root.get_pos()-inc)

    def scan(self, target_pos):
        pos_s = self.root.get_pos()
        pos_p = target_pos
        inc = towards(pos_s, pos_p)
        while True:
            pos_s -= inc
            px, py = round(pos_p.x),round(pos_p.y)
            sx, sy = round(pos_s.x),round(pos_s.y)
            t = base.map.tiles[sx, -sy]
            if t.char == "#":
                return None
            elif sx == px and sy == py:
                return target_pos


class Worm(Enemy):
    def __init__(self, type, pos):
        Enemy.__init__(
            self, "worm",
            Actor("assets/models/creatures/worm.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.5,0.9))

