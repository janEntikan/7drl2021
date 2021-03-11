from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Wait, Sequence
from panda3d.core import NodePath


class Item():
    def __init__(self):
        pass

    def use(self):
        pass


class Syringe(Item):
    def __init__(self):
        Item.__init__(self)
        self.description = choice("")


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
            self.clip[1] = self.next_bullet+1
        else:
            self.clip[0] = self.next_bullet+1
        base.hudgun.play("reload")
        base.task_mgr.doMethodLater(0.4, self.set_hud_bullets, name="reload")

    def fire(self, aimed):
        if not self.clip[0]-1 == aimed.color:
            aimed.hurt()
        self.clip[0] = self.clip[1]
        self.clip[1] = 0
        base.hudgun.play("fire")
        base.sequence_player.wait = 0.7
        self.activate(self, aimed)
        base.task_mgr.doMethodLater(0.2, self.set_hud_bullets, name="fire")