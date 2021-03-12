#version 130
// Exactly nothing happens in vertex shading.

in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Color;

out vec4 vtx_color;
out vec2 texcoord;

void main()  {
  texcoord = p3d_Vertex.xz / 2.0 + 0.5;;
  vtx_color = p3d_Color;
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
