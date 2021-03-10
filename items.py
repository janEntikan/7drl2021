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
        self.clip = [2,2]
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
