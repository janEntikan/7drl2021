from direct.showbase.ShowBase import ShowBase
from direct.showbase.Transitions import Transitions
from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import Parallel 
from direct.interval.IntervalGlobal import Func 
from direct.interval.IntervalGlobal import Wait

from panda3d.core import load_prc_file
from panda3d.core import Filename
from panda3d.core import CardMaker
from panda3d.core import LineSegs
from panda3d.core import NodePath
from panda3d.core import PointLight
from panda3d.core import VBase4
from panda3d.core import OrthographicLens
from panda3d.core import FrameBufferProperties
from panda3d.core import WindowProperties
from panda3d.core import GraphicsPipe
from panda3d.core import SamplerState

from keybindings.device_listener import add_device_listener
from keybindings.device_listener import SinglePlayerAssigner

from map import Map, Room
from creature import Interface, Player


load_prc_file(
    Filename.expand_from('$MAIN_DIR/config.prc')
)


class LineEffects():
    def __init__(self):
        self.linesegs = LineSegs("lines")
        self.bullet = None

    def remove_bullet(self):
        if self.bullet:
            self.bullet.detach_node()

    def draw_bullet(self, a, b):
        self.linesegs.move_to(a)
        self.linesegs.draw_to(b)
        lines = self.linesegs.create()
        self.bullet = render.attach_new_node(lines)
        impact = base.icons["impact"]
        impact = impact.copy_to(self.bullet)
        impact.set_pos(b)


class SequencePlayer():
    def __init__(self):
        self.wait = base.turn_speed
        self.parallel = None

    def end(self):
        self.wait = base.turn_speed
        self.parallel = None

    def hold(self, time):
        self.wait = time
        self.add_to_sequence()

    def add_to_sequence(self, *kwargs):
        if not self.parallel:
            self.parallel = Parallel()
        for item in kwargs:
            self.parallel.append(item)
        func = Sequence(Wait(self.wait), Func(self.end))
        self.parallel.append(func)
        self.parallel.start()


class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        add_device_listener(
            config_file='keybindings.toml',
            assigner=SinglePlayerAssigner(),
        )
        base.disableMouse() 
        self.linefx = LineEffects()
        self.cardmaker = CardMaker("card")
        self.cardmaker.set_frame(-1,1,-1,1)
        self.turn_speed = 0.3 #length of turn animation in seconds
        self.sequence_player = SequencePlayer()
        self.transition = Transitions(loader)
        self.interface = Interface()
        card, scene, camera = self.make_render_card()
        self.turn_speed = 0.3 #length of turn animation in seconds
        self.load_icons()
        self.map = Map()
        self.player = Player((1,-1,0))
        Room(0,0)

        camera.reparent_to(self.player.root)
        camera.set_pos(10,-12,10)
        camera.look_at(self.player.root)
        camera.setCompass()
        # FOV
        render.setShaderAuto()
        self.l = PointLight("caster")
        self.l.set_color((1,1,1,1))
        self.l.setScene(self.map.static)
        self.l.set_max_distance(1)
        self.l.set_specular_color((0,0,0,0))
        self.l.setShadowCaster(True)
        self.l.showFrustum()
        self.l.set_attenuation((0,1,0))
        for i in range(6):
            self.l.getLens().setNearFar(0.2, 10)
        self.l_np = render.attach_new_node(self.l)
        self.l_np.reparent_to(self.player.root)
        self.l_np.set_z(1)
        self.map.static.set_light(self.l_np)

        base.task_mgr.add(self.update)

    def make_render_card(self, ortho_size=[8,5], resolution=[256,256]):
        scene = NodePath("Scene")
        buffer = base.win.make_texture_buffer("Buffer", resolution[0], resolution[1])
        texture = buffer.get_texture()
        texture.set_magfilter(SamplerState.FT_nearest)
        texture.set_minfilter(SamplerState.FT_nearest)
        buffer.set_sort(-100)
        buffer.set_clear_color_active(True)
        s = (1/255)
        buffer.set_clear_color(VBase4(s, s, s, 1))
        camera = base.make_camera(buffer)
        lens = OrthographicLens()
        lens.set_film_size(ortho_size[0], ortho_size[1])
        lens.set_near(10)
        lens.set_far(40)
        camera.node().set_lens(lens)
        camera.reparent_to(scene)
        card = render2d.attach_new_node(self.cardmaker.generate())
        card.set_texture(texture)
        return card, scene, camera

    def load_icons(self):
        model = loader.load_model("assets/models/icons.bam")
        self.icons = {}
        for child in model.get_children():
            child.clear_transform()
            child.detach_node()
            self.icons[child.name] = child

    def update(self, task):
        self.dt = globalClock.get_dt()
        if not self.sequence_player.parallel:
            self.interface.update()
        return task.cont



if __name__ == "__main__":
    base = Base()
    base.run()