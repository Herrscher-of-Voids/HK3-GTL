#version 150
in vec3 Position;
in vec4 Color;
in vec2 UV0;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform vec3 TileOrigin;
out vec3 worldPosition;
out vec4 vertexColor;
out vec2 faceUV;
void main() {
    gl_Position=ProjMat*ModelViewMat*vec4(Position,1.0);
    worldPosition=Position+TileOrigin;
    vertexColor=Color;
    faceUV=UV0;
}
