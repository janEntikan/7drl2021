from panda3d.core import TextNode
from panda3d.core import TextFont
from random import choice, shuffle


class Texts():
    def __init__(self, camera):
        self.root = camera.attach_new_node("texts")
        self.root.set_y(7)
        self.font = loader.load_font("assets/fonts/pressstart2p.ttf")
        self.font.set_pixels_per_unit(10)
        self.font.set_render_mode(TextFont.RMPolygon)
        self.font.set_point_size(10)
        self.titlefont = loader.load_font("assets/fonts/probe.ttf")
        self.titlefont.set_pixels_per_unit(10)
        self.titlefont.set_render_mode(TextFont.RMPolygon)
        self.titlefont.set_point_size(10)
        self.tips = [
            "Load a cyan bullet with C!",
            "Select aim with X!",
            "Load a violet bullet with V!",
            "Slugs are strong but slow!",
            "Worms are fast but weak!",
            "Cyan bullets kill cyan enemies!",
            "Violet bullets kill violet enemies!",
            "Can you find the medipacks?",
        ]
        self.next_tips = self.tips[:]
        shuffle(self.next_tips)

        self.make_title()

    def deactivate(self):
        self.text.detach_node()

    def make_instructions(self):
        self.text = self.root.attach_new_node("instructions")
        text = self.make_textnode(self.text,
            "Your rifle can hold two bullets.\n"
            "Load a CYAN bullet with C\n"
            "Load a VIOLET bullet with V\n"
            "X to scroll targets\n"
            "Space to fire\n"
            "Find a way out!\n\n"
            "FIRE to continue!"
        )
        text.set_scale(0.17)
        text.node().set_align(3)
        text.set_z(2)
        text.set_x(-2.70)

    def make_end(self):
        self.text = self.root.attach_new_node("end")
        start = self.make_textnode(self.text,
            "RUNNING TO CONSOLE.\n"
            "SHORT BREATH.\n"
            "HIT COMMAND BUTTON.\n"
            "AIRLOCK OPEN BECOMES.\n"
            "WORM FLY OUT AND PERISH.\n"
            "MINING STATION LIFT OFF.\n"
            "FLY AWAY FROM ASTEROID.\n"
            "YOU LIVE SEE ANOTHER DAY.\n"
            "YOU'RE ADVENTURE\n"
            "ONLY JUST BEGIN!\n\n\n"
            "THE END\n\n"
            "THANKS FOR PLAYING",
            (0.1,0.1,0.5,1),
        )
        start.set_scale(0.20)
        start.set_z(1.5)

    def make_gameover(self):
        self.text = self.root.attach_new_node("game over")
        title = self.make_textnode(
            self.text, "GAME OVER", (1,0.15,0.15,1), True
        )
        title.set_z(0)
        title.set_scale(0.5)
        start = self.make_textnode(self.text, "Press FIRE to restart")
        start.set_scale(0.17)
        start.set_z(-0.3)
        tip = self.make_textnode(self.text, self.next_tips[0])
        self.tips = self.next_tips[1:]
        if len(self.next_tips) == 0:
            self.next_tips = self.tips
            shuffle(self.next_tips)
        tip.set_scale(0.16)
        tip.set_z(-2.2)

    def make_title(self):
        self.text = self.root.attach_new_node("title")
        name = self.make_textnode(self.text, "Hendrik-jan's")
        name.set_z(1.4)
        name.set_scale(0.17)
        title = self.make_textnode(
            self.text, "EVIL\nEVIL\nWOYEMS", (1,0.15,1,1), True
        )
        title.set_z(1)
        title.set_scale(0.5)
        start = self.make_textnode(self.text, "Press SPACE to start")
        start.set_scale(0.16)
        start.set_z(-0.4)
        credit = self.make_textnode(self.text, "special thanks to:\nschwarzbaer rdb tizilogic")
        credit.set_scale(0.17)
        credit.node().set_align(3)
        credit.set_z(-2)
        credit.set_x(-2.70)

    def make_textnode(self, root, text_string, color=(1,1,1,1), title=False):
        if title:
            font = self.titlefont
        else:
            font = self.font
        text = TextNode("text")
        text.set_font(font)
        text.set_align(2)
        text.set_text_color((0,0,0,1))
        text.set_shadow(0.1,0.1)
        text.set_shadow_color(color)
        text.text = text_string
        text_np = root.attach_new_node(text)
        text_np.set_scale(1)
        return text_np
