from panda3d.core import Shader
from random import random

instancing_shader = Shader.make(Shader.SL_GLSL, """
#version 150
in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;
in mat4x3 p3d_InstanceMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform vec4 p3d_ColorScale;
out vec2 texcoord;
out vec4 color;
void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * vec4(p3d_InstanceMatrix * p3d_Vertex, 1);
  texcoord = p3d_MultiTexCoord0;
  color = p3d_Color * p3d_ColorScale;
}
""", """
#version 150
in vec2 texcoord;
in vec4 color;
out vec4 p3d_FragColor;
uniform sampler2D p3d_Texture0;
void main() {
  p3d_FragColor = texture(p3d_Texture0, texcoord);
  p3d_FragColor *= color;
}
""")

if __name__ == "__main__":
    inst = InstancedNode("inst")
    #inst.instances.append(pos=(2, 0, 0), hpr=(30, 0, 0))
    inst.instances.append(pos=(12, 0, 0), hpr=(30, 0, 0))
    inst.instances.append(pos=(22, 0, 0), hpr=(30, 0, 0))
    inst.instances.append(pos=(32, 0, 0), hpr=(30, 0, 0))
    inst.set_bounds_type(BoundingVolume.BT_best)
    inst_path = render.attach_new_node(inst)
    #inst_path.show_bounds()

    sattr = ShaderAttrib.make(instancing_shader)
    # Comment this out to get regular instancing
    sattr = sattr.set_flag(ShaderAttrib.F_hardware_instancing, True)
    inst_path.set_attrib(sattr)

    # Load the node that is to be instanced
    panda = loader.load_model("panda")
    panda.reparent_to(inst_path)
    panda.flatten_strong() # flattening highly recommended
    #panda.show_tight_bounds()
    #panda.show_bounds()

    # Test that nested instancing works, by giving each panda a baby panda.
    # I don't think this is as efficient as simply having a single InstancedNode
    # with a giant list of instances, though, but it should nonetheless DTRT.
    if False:
        inst2 = InstancedNode("inst2")
        inst2.instances.append(pos=(0, 0, 0))
        inst2.instances.append(pos=(0, -2.5, 0), hpr=(0, 0, 0), scale=0.3)
        inst2_path = inst_path.attach_new_node(inst2)
        panda.reparent_to(inst2_path)

    def spawn_instance():
        inst.instances.append(pos=(random() * 50, random() * 50, 0), hpr=(30, 0, 0), scale=random() + 0.5)

    base.accept('a', spawn_instance)
    base.accept('o', base.oobe_cull)

    base.trackball.node().set_pos(0, 50, 0)

    base.run()
