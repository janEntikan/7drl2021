from panda3d.core import TextNode
from panda3d.core import TextFont


class Texts():
    def __init__(self, camera):
        self.root = camera.attach_new_node("texts")
        self.root.set_y(7)
        self.font = loader.load_font("assets/fonts/azeri.ttf")
        self.font.set_pixels_per_unit(10)
        self.font.set_render_mode(TextFont.RMPolygon)

        self.title = self.root.attach_new_node("title")
        name = self.make_textnode(self.title, "HENDRIK-JAN's")
        name.set_z(1.7)
        name.set_scale(0.4)
        title = self.make_textnode(self.title, "EVIL\nEVIL\nWOYEMS")        
        title.set_z(1)
        title.set_scale(0.7)
        title.node().set_text_color((1,0.15,1,1))
        
        credit = self.make_textnode(self.title, "with special thanks to:\nschwarzbaer\nrdb\ntizilogic")
        credit.set_scale(0.3)
        credit.node().set_align(3)
        credit.set_z(-1.3)
        credit.set_x(-2.4)

    def make_textnode(self, root, text_string):
        text = TextNode("text")
        text.set_font(self.font)
        text.set_align(2)        
        text.text = text_string
        text_np = root.attach_new_node(text)
        text_np.set_scale(1)
        return text_np
