import sys
from direct.showbase.ShowBase import ShowBase
from direct.showbase.Transitions import Transitions
from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import Parallel
from direct.interval.IntervalGlobal import Func
from direct.interval.IntervalGlobal import Wait
from direct.actor.Actor import Actor
from direct.filter.FilterManager import FilterManager
from panda3d.core import load_prc_file
from panda3d.core import Filename
from panda3d.core import CardMaker
from panda3d.core import LineSegs
from panda3d.core import NodePath
from panda3d.core import PointLight
from panda3d.core import AmbientLight

from panda3d.core import Shader
from panda3d.core import Texture
from panda3d.core import VBase4
from panda3d.core import OrthographicLens
from panda3d.core import FrameBufferProperties
from panda3d.core import WindowProperties
from panda3d.core import GraphicsPipe
from panda3d.core import SamplerState
from panda3d.core import DepthOffsetAttrib

from keybindings.device_listener import add_device_listener
from keybindings.device_listener import SinglePlayerAssigner

from text import Texts
from map import Map, Room
from sound import SoundManager
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

    def draw_bullet(self, a, b, color):
        if color == 1:
            color = (1,0,1,1)
        elif color == 2:
            color = (0,1,1,1)
        else:
            color = (1,1,1,1)
        self.linesegs.set_color(color)
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

    def finalize(self):
        if not self.parallel:
            self.parallel = Parallel()
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
        self.sound = SoundManager()
        self.linefx = LineEffects()
        self.cardmaker = CardMaker("card")
        self.cardmaker.set_frame(-1,1,-1,1)
        self.turn_speed = 0.3 #length of turn animation in seconds
        self.sequence_player = SequencePlayer()
        self.transition = Transitions(loader)
        self.interface = Interface()
        self.bg_color = VBase4(0, 0, 0, 1)
        self.innitialize_fov()

        card, scene, camera, self.buffer = self.make_render_card()
        card.set_x(-0.25)
        self.camera = camera
        self.load_icons()

        self.texts = Texts(camera)
        self.pause = True
        self.gameover = False
        self.won = False

        self.player = Player((0,0,0))
        self.map = Map()
        self.map.new_game()

        camera.reparent_to(self.player.root)
        camera.set_pos(4,-4,8)
        camera.look_at(self.player.root)
        camera.set_compass()
        base.task_mgr.add(self.update)

        card, scene, camera, buffer = self.make_render_card([3,7],[64,256],(0,100))
        self.hudgun = Actor("assets/models/hand.bam")
        self.hudgun.reparent_to(scene)
        self.hudgun.find("**/hand_healthy").show()
        self.hudgun.find("**/hand_hurt").hide()
        self.hudgun.setLODAnimation(1, 0.1, 0.005)
        self.player.weapon.set_hud_bullets()
        camera.look_at(self.hudgun)
        camera.set_pos(0.5,-1.5,10)
        camera.set_p(-90)
        card.set_scale(1/4,1,1)
        card.set_x(1-(1/4))
        self.quad = None
        self.setup_post_effect()

    def game_over(self):
        self.pause = True
        self.gameover = True
        self.texts.make_gameover()

    def win_game(self):
        self.pause = True
        self.won = True
        self.texts.make_end()

    def innitialize_fov(self):
        render.set_shader_auto()
        self.fov_point = PointLight("caster")
        self.fov_point.set_shadow_caster(True, 256*2, 256*2, -1000)
        self.fov_point.set_camera_mask(0b001)
        self.fov_point.set_lens_active(4, False)
        self.fov_point.set_lens_active(5, False)
        for i in range(6):
            self.fov_point.get_lens(i).set_near_far(0.5, 10)
        self.fov_point_np = render.attach_new_node(self.fov_point)
        self.fov_point_np.set_z(0.5)
        self.fov_point.set_color(VBase4(1,1,1,1))


    def make_render_card(self, ortho_size=[8,5], resolution=[256,256], nearfar=(5,40)):
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
        lens.set_near(nearfar[0])
        lens.set_far(nearfar[1])
        camera.node().set_lens(lens)
        camera.reparent_to(scene)
        card = render2d.attach_new_node(self.cardmaker.generate())
        card.set_texture(texture)
        return card, scene, camera, buffer

    def setup_post_effect(self):
        self.manager = FilterManager(base.win, base.cam2d)
        tex = Texture()
        #tex = loader.load_texture("assets/noise.png")
        self.quad = self.manager.renderSceneInto(colortex=tex)
        self.quad.setShader(Shader.load(Shader.SL_GLSL, "crt.vert","crt.frag"))
        self.quad.setShaderInput("iResolution", (1920,1080))
        #self.quad.setShaderInput("iChannel0", tex)
        base.accept("window-event", self.on_window_event)

    def on_window_event(self, win):
        base.windowEvent(win)
        self.quad.setShaderInput("iResolution", (base.win.getXSize(), base.win.getYSize()))

    def load_icons(self):
        model = loader.load_model("assets/models/icons.bam")
        self.icons = {}
        for child in model.get_children():
            child.clear_transform()
            child.detach_node()
            self.icons[child.name] = child

    def update(self, task):
        self.dt = globalClock.get_dt()
        context = base.device_listener.read_context('ew')
        if context["quit"]:
            sys.exit()
        if not self.pause:
            if not self.sequence_player.parallel:
                self.interface.update(context)
        else:
            if self.won:
                return task.cont
            if context["select"]:
                self.texts.deactivate()
                self.pause = False
                if self.gameover:
                    base.sound.stop("die")
                    self.gameover = False
                    self.map.destroy()
                    self.map.new_game()
                else:
                    base.sound.music["opening"].stop()
                    base.sound.music["background"].play()
        return task.cont

if __name__ == "__main__":
    base = Base()
    base.run()
