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
from panda3d.core import AmbientLight
from panda3d.core import VBase4
from panda3d.core import OrthographicLens
from panda3d.core import FrameBufferProperties
from panda3d.core import WindowProperties
from panda3d.core import GraphicsPipe
from panda3d.core import SamplerState
from panda3d.core import DepthOffsetAttrib
from panda3d.core import LightRampAttrib

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
        a = a.get_pos(render)
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
        self.bg_color = VBase4(0, 0, 0, 1)

        card, scene, camera, self.buffer = self.make_render_card()
        self.load_icons()
        self.map = Map()
        p = self.map.pos(8)
        self.map.rooms[p] = Room(*p)
        self.player = Player((p[0]+4,-p[1]-4,0))

        camera.reparent_to(self.player.root)
        camera.set_pos(4,-4,8)
        camera.look_at(self.player.root)
        camera.set_compass()
        self.innitialize_fov()
        base.task_mgr.add(self.update)

    def innitialize_fov(self):
        render.set_shader_auto()
        target_np = self.map.static
        target_np.set_attrib(LightRampAttrib.make_single_threshold(0.0, 1.0))
        self.fov_point = PointLight("caster")
        self.fov_point.set_shadow_caster(True, 256, 256, -1000)
        self.fov_point.set_camera_mask(0b001)
        self.player.root.hide(0b001)
        self.fov_point.set_scene(target_np)
        self.fov_point.set_initial_state(
            self.fov_point.get_initial_state().add_attrib(
                DepthOffsetAttrib.make(-6)
            )
        )
        self.fov_point.set_lens_active(4, False)
        self.fov_point.set_lens_active(5, False)
        for i in range(6):
            self.fov_point.get_lens(i).set_near_far(0.2, 10)
        self.fov_point_np = self.player.root.attach_new_node(self.fov_point)
        self.fov_point_np.set_z(0.5)
        self.fov_point.set_color(VBase4(1,1,1,1)-self.bg_color)
        target_np.set_light(self.fov_point_np)


    def make_render_card(self, ortho_size=[8,5], resolution=[256,256]):
        scene = NodePath("Scene")
        buffer = base.win.make_texture_buffer("Buffer", resolution[0], resolution[1])
        texture = buffer.get_texture()
        texture.set_magfilter(SamplerState.FT_nearest)
        texture.set_minfilter(SamplerState.FT_nearest)
        buffer.set_sort(-100)
        buffer.set_clear_color_active(True)
        buffer.set_clear_color(self.bg_color)
        camera = base.make_camera(buffer)
        lens = OrthographicLens()
        lens.set_film_size(ortho_size[0], ortho_size[1])
        lens.set_near(5)
        lens.set_far(40)
        camera.node().set_lens(lens)
        camera.reparent_to(scene)
        card = render2d.attach_new_node(self.cardmaker.generate())
        card.set_texture(texture)
        return card, scene, camera, buffer

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