from math import hypot
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Wait, Sequence
from random import randint, uniform
from direct.actor.Actor import Actor
from panda3d.core import Vec3
from items import *


class Interface(): # takes care of player logic and ai response
    def update(self):
        player = base.player
        turn_over = False
        if player.alive:
            context = base.device_listener.read_context('ew')
            current = player.root.get_pos()
            new_pos = None
            time = base.turn_speed
            if int(context["move"].x):         
                new_pos = Vec3(current.x+int(context["move"].x), current.y, 0)
            elif int(context["move"].y):
                new_pos = Vec3(current.x, current.y+int(context["move"].y), 0)
            if new_pos:
                x, y = int(new_pos.x), -int(new_pos.y)
                for enemy in base.map.enemies:
                    ex, ey, ez = enemy.root.get_pos()
                    if round(ex) == x and round(ey) == -y:
                        return
                destination_tile = base.map.tiles[x, y]
                if destination_tile.char == "#":
                    return
                elif destination_tile.char == "=":
                    if not destination_tile.open:
                        destination_tile.activate()
                        return
                player.animate("walk", False)
                player.move_to(new_pos)
                player.root.set_x(x)
                player.root.set_y(-y)
                base.map.set(new_pos)
                turn_over = True
            elif context["fire"]:
                turn_over = player.fire()
            elif context["reload"]:
                turn_over = player.reload()
            else:
                player.stop()
        if turn_over:
            for enemy in base.map.enemies:
                enemy.update()
            base.sequence_player.finalize()
        else:
            for enemy in base.map.enemies:
                enemy.reset()
        player.aim()


class Creature():
    def __init__(self, name, model, pos):
        self.name = name
        self.root = model
        self.root.set_pos(pos)
        self.root.setLODAnimation(1, 0.1, 0.0075)
        self.root.loop("idle")
        self.root.reparent_to(render)
        self.distance = 99999
        self.alive = True
        self.hp = 1
       
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
        self.hp = 2
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

    def hurt(self, amt, attacker, delay):
        self.hp -= amt
        if self.hp > 0:
            base.sequence_player.add_to_sequence(
                Sequence(
                    Wait(0.2+delay),
                    Func(self.root.play, "hurt"),
                    Func(self.root.look_at, attacker.root),
                )
            )
        else:
            self.alive = False
            base.sequence_player.add_to_sequence(
                Sequence(
                    Wait(0.2+delay),
                    Func(self.root.play, "die"),
                    Func(self.root.look_at, attacker.root),
                )
            )
        base.sequence_player.hold(1)

    def aim(self):
        visable = []
        for enemy in base.map.enemies:
            p1 = self.root.get_pos()
            p2 = enemy.root.get_pos()
            vector = p1 - p2
            enemy.distance = vector.get_xy().length()
            if enemy.distance < 50:
                if base.map.scan(p1, p2, vector):
                    visable.append(enemy)
                    enemy.root.show()
                else:
                    enemy.root.hide()
        base.map.enemies.sort(key=lambda x: x.distance, reverse=False)
        try:
            self.aimed = visable[self.aim_select]
            self.crosshair.reparent_to(self.aimed.root)
            self.crosshair.set_z(0.01)
            self.crosshair.show()
        except:
            self.crosshair.hide()
            self.aimed = None

    def reload(self):
        if self.weapon.clip[0]<self.weapon.clip[1]:
            self.weapon.clip[0] += 1
            self.animate("reload", False)
            base.sequence_player.hold(1)
            return True
        else:
            return False

    def fire(self):
        if self.aimed:
            if self.weapon.clip[0] > 0:
                self.weapon.clip[0] -= 1
                self.root.look_at(self.aimed.root)
                self.animate("fire", False)
                base.sequence_player.wait = 1
                self.weapon.activate(self,self.aimed)
                self.aimed.hurt()
            else:
                return False
        else:
            return False
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

    def attack(self):
        delay = uniform(0,0.2)
        base.sequence_player.add_to_sequence(
            Sequence(
                Wait(delay),
                Func(self.root.play, "attack"),
            )
        )
        self.root.look_at(base.player.root)
        base.sequence_player.wait = 1
        base.player.hurt(1, self, delay)

    def update(self):
        if not self.alive:
            base.map.enemies.remove(self)
            base.task_mgr.doMethodLater(3, self.detach, "ok")
            return
        if not self.wait:
            if randint(0,1):
                self.wait = True
            self.root.loop("move")
            x,y,z = self.root.get_pos()
            a = base.map.tiles[round(x),round(-y)]
            x,y,z = base.player.root.get_pos()
            b = base.map.tiles[int(x),int(-y)]
            self.next_tile = base.map.flow_field(a,b)
            x,y = self.next_tile.pos
            px,py,pz = base.player.root.get_pos()
            if px == x and -py == y:
                self.attack()
            else:
                o = 0.2
                x += uniform(-o,o)
                y += uniform(-o,o)
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

