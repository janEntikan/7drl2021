from direct.showbase.ShowBase import ShowBase
from direct.showbase.Transitions import Transitions
from direct.interval.IntervalGlobal import Sequence, Func
from direct.actor.Actor import Actor

from panda3d.core import load_prc_file
from panda3d.core import Filename
from panda3d.core import CardMaker
from panda3d.core import NodePath
from panda3d.core import VBase4
from panda3d.core import OrthographicLens
from panda3d.core import FrameBufferProperties
from panda3d.core import WindowProperties
from panda3d.core import GraphicsPipe
from panda3d.core import SamplerState

from keybindings.device_listener import add_device_listener
from keybindings.device_listener import SinglePlayerAssigner

from stars import create_star_sphere_geom_node
from map import Room, Medical
from creature import Interface, Creature


load_prc_file(
    Filename.expand_from('$MAIN_DIR/config.prc')
)


class SequencePlayer():
    def __init__(self):
        self.sequence = None
        self.sequence_end = Func(self.end_sequence)

    def add_to_sequence(self, *kwargs):
        if not self.sequence:
            self.sequence = Sequence()
        while self.sequence_end in self.sequence:
            self.sequence.remove(self.sequence_end)
        for item in kwargs:
            self.sequence.append(item)
        self.sequence.append(self.sequence_end)
        self.sequence.start()

    def end_sequence(self):
        if self.sequence:
            self.sequence.finish()
            self.sequence = None



class Base(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        add_device_listener(
            config_file='keybindings.toml',
            assigner=SinglePlayerAssigner(),
        )
        base.disableMouse() 

        self.cardmaker = CardMaker("card")
        self.cardmaker.set_frame(-1,1,-1,1)
        self.sequence_player = SequencePlayer()
        self.transition = Transitions(loader)
        self.interface = Interface()
        card, scene, camera = self.make_render_card()

        self.map = Medical()
        self.player = Creature(
            "player", Actor("assets/models/player.bam")
        )
        start_leaf = self.map.random_leaf()
        x, y, w, h = start_leaf.rect
        x = x + int(w/2)
        y = y + int(h/2)
        self.player.root.set_pos(x, y, 0)
        room = Room(self.map, start_leaf)
        room.construct()

        #camera.set_pos(room.root.get_x()+10, room.root.get_y()-12, 10)

        room.root.reparent_to(scene)
        self.player.root.reparent_to(scene)
        self.player.root.set_pos(room.root, (1,-1,0))


        camera.reparent_to(self.player.root)
        camera.set_pos(10,-12,10)
        camera.look_at(self.player.root)
        camera.setCompass()
        
        stars = create_star_sphere_geom_node(60, 1000)
        self.stars = camera.attach_new_node(stars)
        self.stars.set_scale(30)
        def rotate_sky(task):
            self.stars.set_r(
                self.stars,
                globalClock.dt * 360 / 6000,
            )
            return task.cont
        base.task_mgr.add(rotate_sky)
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
        camera.node().set_lens(lens)
        camera.reparent_to(scene)
        card = render2d.attach_new_node(self.cardmaker.generate())
        card.set_texture(texture)
        return card, scene, camera

    def update(self, task):
        self.dt = globalClock.get_dt()
        if not self.sequence_player.sequence:
            self.interface.update()
        return task.cont



if __name__ == "__main__":
    base = Base()
    base.run()