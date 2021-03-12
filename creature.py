from math import hypot
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Wait, Sequence
from random import randint, uniform
from direct.actor.Actor import Actor
from panda3d.core import Vec3
from items import *


class Interface(): # takes care of player logic and ai response
    def update(self, context):
        player = base.player
        turn_over = False
        if player.alive:
            current = player.root.get_pos()
            new_pos = None
            time = base.turn_speed
            if context["aim"]:
                player.next_aim()
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
                for item in base.map.items:
                    if item.model.get_pos() == new_pos:
                        item.activate()

                if destination_tile.char in "#P":
                    return
                elif destination_tile.char == "=":
                    if not destination_tile.open:
                        base.sound.play("door")
                        destination_tile.activate()
                        return                
                base.sound.play("step")
                player.animate("walk", True)
                player.move_to(new_pos)
                player.root.set_x(x)
                player.root.set_y(-y)
                base.map.set(new_pos)
                turn_over = True
            elif context["fire"]:
                turn_over = player.fire()
            elif context["reload_violet"]:
                turn_over = player.reload(0)
            elif context["reload_cyan"]:
                turn_over = player.reload(1)
            else:
                player.stop()
        if turn_over:
            player.aim()
            for enemy in base.map.enemies:
                enemy.update()
            base.sequence_player.finalize()
            player.aim()
        else:
            for enemy in base.map.enemies:
                enemy.reset()


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
        self.weapon = Weapon()
        self.weapon.hold(self)
        self.hp = 2
        self.aim_select = 0
        self.aimed = None
        self.crosshair = base.icons["crosshair"]
        self.crosshair.set_scale(0.5)
        self.color()

    def reset(self):
        self.hp = 2
        self.aim_select = 0
        self.aimed = None
        self.alive = True
        self.weapon.clip = [0,0]
        self.animate("idle",True)
        try:
            base.hudgun.find("**/hand_healthy").show()
            base.hudgun.find("**/hand_hurt").hide()
            self.weapon.set_hud_bullets()
        except:
            pass

    def color(self):
        hair = self.root.find("**/hair")
        hair.clear_color()
        chest = self.root.find("**/torso")
        chest.set_color((0.1,0.4,0.1,1))
        legs = self.root.find("**/legs")
        legs.set_color((0.02,0.02,0.02,1))
        #arms = self.root.find("**/arms")
        #arms.set_color((0.1,0.2,0,1))

    def hurt_hand(self):
        base.hudgun.find("**/hand_healthy").hide()
        base.hudgun.find("**/hand_hurt").show()

    def oof(self):
        base.transition.setFadeColor(*(0.2,0,0))
        base.transition.fadeOut(0)
        base.transition.fadeIn(0.05)

    def hurt(self, amt, attacker, delay):
        self.hp -= amt
        if self.hp > 0:
            base.sequence_player.add_to_sequence(
                Sequence(
                    Wait(0.2+delay),
                    Func(self.oof),
                    Func(self.root.play, "hurt"),
                    Func(self.root.look_at, attacker.root),
                    Func(self.hurt_hand),
                )
            )
        else:
            self.alive = False
            base.sound.play("die")
            base.sequence_player.add_to_sequence(
                Sequence(
                    Wait(0.2+delay),
                    Func(self.oof),
                    Func(base.game_over),
                    Func(self.root.play, "die"),
                    Func(self.root.look_at, attacker.root),
                    Wait(0.5),
                )
            )
        base.sequence_player.hold(1)

    def end(self, pos):
        movement = self.root.posInterval(
            5, pos, startPos=self.root.get_pos()
        )
        base.sequence_player.add_to_sequence(
            Sequence(
                movement,
                Func(base.win_game),
                Func(self.root.play, "idle"),
            )
        )
        base.sequence_player.finalize()
        self.alive = False

    def aim(self):
        visable = []
        for enemy in base.map.enemies:
            if enemy.alive:
                p1 = self.root.get_pos()
                p2 = enemy.root.get_pos()
                p2.x = round(p2.x)
                p2.y = round(p2.y)
                vector = p1 - p2
                enemy.distance = vector.get_xy().length()
                if enemy.distance < 50:
                    if enemy.distance < 5:
                        if base.map.scan(p1, p2, vector):
                            visable.append(enemy)
                            enemy.root.show()
                            enemy.last_seen = self.root.get_pos()
                        else:
                            enemy.root.hide()
                else:
                    base.map.enemies.remove(enemy)
                    enemy.detach()
        base.map.enemies.sort(key=lambda x: x.distance, reverse=False)

        if len(visable) > 0:
            if self.aim_select >= len(visable):
                self.aim_select = 0
            self.aimed = visable[self.aim_select]
            self.root.look_at(self.aimed.root)
            self.crosshair.reparent_to(self.aimed.root)
            self.crosshair.set_scale(render, 0.5)
            self.crosshair.set_z(0.01)
            self.crosshair.show()
        else:
            self.crosshair.hide()
            self.aimed = None

    def next_aim(self):
        self.aim_select += 1
        self.aim()

    def reload(self, bullet):
        self.weapon.next_bullet = bullet
        self.weapon.reload()
        base.sound.play("reload")
        self.animate("reload", False)
        base.sequence_player.hold(0.6)
        return True

    def fire(self):
        if self.aimed:
            if self.weapon.clip[0] > 0:
                base.sound.play("laser")
                self.weapon.fire(self.aimed)
                self.root.look_at(self.aimed.root)
                self.animate("fire", False)

            else:
                return False
        else:
            return False
        return True

    def animate(self, animation, loop=True):
        if self.weapon:
            n = self.weapon.is_twohand(animation)
            if loop:
                if not self.root.getCurrentAnim() == n:
                    self.root.loop(n)
            else:
                self.root.play(n)


class Enemy(Creature):
    def __init__(self, name, model, pos):
        Creature.__init__(self, name, model, pos)
        self.color = randint(0,1)
        l = self.root.find("**/l")
        d = self.root.find("**/d")
        if self.color == 0:
            l.set_color(0.01,1,1,1)
            d.set_color(0.005,0.5,0.5,1)
        elif self.color == 1:
            l.set_color(1,0.01,1,1)
            d.set_color(0.5,0.005,0.5,1)
        self.last_seen = None
        self.wait = True
        self.hurtsound = "woo1"
        self.diesound = "kill1"
        self.attacksound = "woo6"

    def hurt(self):
        self.root.look_at(base.player.root)
        self.hp -= 1
        self.wait = True
        if self.hp > 0:
            self.root.play("hurt")
            base.sound.play(self.hurtsound)
        else:
            base.sound.play(self.diesound)
            self.alive = False
            self.root.play("die")

    def reset(self):
        if self.alive:
            self.stop()

    def detach(self, task=None):
        self.root.detach_node()

    def attack(self):
        base.sound.play(self.attacksound)
        delay = uniform(0,0.2)
        base.sequence_player.add_to_sequence(
            Sequence(
                Wait(delay),
                Func(base.sound.play, "impact"+str(randint(1,4))),
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
        if self.distance <= 1:
            self.attack()
            return
        if randint(0,self.speed):
            self.wait = True
        if not self.wait and self.last_seen:
            self.root.loop("move")
            x,y,z = self.root.get_pos()
            a = base.map.tiles[round(x),round(-y)]
            x,y,z = self.last_seen
            b = base.map.tiles[int(x),int(-y)]
            self.next_tile = base.map.flow_field(a,b)
            x,y = self.next_tile.pos
            px,py,pz = self.last_seen
            if px == x and -py == y:
                self.last_seen = None
            else:
                o = 0.2
                x += uniform(-o,o)
                y += uniform(-o,o)
                self.move_to((x,-y,0))
        else:
            self.wait = False

class Worm(Enemy):
    def __init__(self, pos):
        Enemy.__init__(
            self, "worm",
            Actor("assets/models/creatures/worm.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.5,0.9))
        self.hp = 1
        self.speed = 2

        self.hurtsound = "woo1"
        self.diesound = "kill4"
        self.attacksound = "woo2"



class Slug(Enemy):
    def __init__(self, pos):
        Enemy.__init__(
            self, "slug",
            Actor("assets/models/creatures/slug.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.5,0.9))
        self.hp = 3
        self.speed = 5

        self.hurtsound = "woo3"
        self.diesound = "kill1"
        self.attacksound = "woo4"



class Centipede(Enemy):
    def __init__(self, pos):
        Enemy.__init__(
            self, "centipede",
            Actor("assets/models/creatures/centipede.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.6,0.9))
        self.speed = 2
        self.hp = 2

        self.hurtsound = "woo4"
        self.diesound = "kill2"
        self.attacksound = "woo5"



class Blob(Enemy):
    def __init__(self, pos):
        Enemy.__init__(
            self, "blob",
            Actor("assets/models/creatures/blob.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.05,0.2))
        self.hp = 1
        self.speed = 2
        self.hurtsound = "woo5"
        self.diesound = "kill3"
        self.attacksound = "woo6"



class Jelly(Enemy):
    def __init__(self, pos):
        Enemy.__init__(
            self, "jelly",
            Actor("assets/models/creatures/jelly.bam"),
            pos,
        )
        self.root.set_scale(uniform(0.5,0.9))
        self.hp = 3
        self.speed = 4
        self.hurtsound = "squeel"
        self.diesound = "kill4"
        self.attacksound = "scream"
