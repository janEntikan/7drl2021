from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Wait, Sequence
from panda3d.core import NodePath
from random import randint

class Item():
    def __init__(self):
        pass

    def use(self):
        pass


class Healthpack(Item):
    def __init__(self, pos):
        Item.__init__(self)
        self.model = base.icons["medpack"].copy_to(render)
        self.model.set_pos(pos[0],-pos[1],0)
        base.map.items.append(self)
        self.model.set_scale(0.2)

    def activate(self):
        base.player.hp = 2
        base.hudgun.find("**/hand_healthy").show()
        base.hudgun.find("**/hand_hurt").hide()
        base.map.items.remove(self)
        self.model.detach_node()
        base.sound.play("take")

class Weapon():
    def __init__(self):
        self.name = "plasmarifle"
        self.damage = 1
        self.next_bullet = 0
        self.clip = [0,0]
        self.two_handed = True
        self.icon = base.icons["plasmarifle"]
        self.muzzle = self.icon.find("**/muzzle*")
        self.muzzle.hide()
        self.hold_node = NodePath(self.name)
        

    def bullet(self):
        pass

    def is_twohand(self, string):
        if self.two_handed:
            string+="_twohanded"
        else:
            string+="_onehanded"
        return string

    def flash(self, user, on=True):
        if on: self.muzzle.show()
        else:  self.muzzle.hide()

    def activate(self, user, aimed):
        flash_sequence = Sequence(
            Wait(0.15),
            Func(self.flash, user, True),
            Func(
                base.linefx.draw_bullet, 
                self.muzzle,
                aimed.root.get_pos(),
                self.clip[0],
            ),
            Wait(0.15),
            Func(
                base.linefx.remove_bullet,
            ),
            Func(self.flash, user, False),
        )
        base.sequence_player.add_to_sequence(flash_sequence)

    def hold(self, user):
        self.icon.clear_transform()
        self.hold_node.reparent_to(user.root)
        self.icon.reparent_to(self.hold_node)
        user.root.expose_joint(self.hold_node, "modelRoot", "hand.r")
        self.icon.set_hpr(20,90,-90)

    def set_hud_bullets(self, task=None):
        hudgun = base.hudgun
        indicators = (
            hudgun.find("**/indicator_pink"),
            hudgun.find("**/indicator_cyan"),
        )
        bullets = (
            hudgun.find("**/chamber_bullet_a_pink"), 
            hudgun.find("**/chamber_bullet_a_cyan"),
            hudgun.find("**/chamber_bullet_b_pink"),
            hudgun.find("**/chamber_bullet_b_cyan"),
        )
        for bullet in bullets:
            bullet.hide()
        for indicator in indicators:
            indicator.hide()

        if self.clip[0] == 1:
            bullets[0].show()
            indicators[0].show()
        elif self.clip[0] == 2:
            bullets[1].show()
            indicators[1].show()
        if self.clip[1] == 1:
            bullets[2].show()
        elif self.clip[1] == 2:
            bullets[3].show()

    def reload(self):
        if self.clip[0] > 0:
            if self.clip[1] > 0:
                self.clip[0] = self.clip[1]
            self.clip[1] = self.next_bullet+1
        else:
            self.clip[0] = self.next_bullet+1
        base.hudgun.play("reload")
        base.task_mgr.doMethodLater(0.4, self.set_hud_bullets, name="reload")

    def fire(self, aimed):
        if not self.clip[0]-1 == aimed.color:
            aimed.hurt()
            base.sound.play("impact1")
        base.hudgun.play("fire")
        base.sequence_player.wait = 0.7
        self.activate(self, aimed)
        self.clip[0] = self.clip[1]
        self.clip[1] = 0
        base.task_mgr.doMethodLater(0.2, self.set_hud_bullets, name="fire")
