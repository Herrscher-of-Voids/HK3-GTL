#version 150
in vec3 Position;
in vec4 Color;
in vec2 UV0;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
out vec4 vertexColor;
out vec2 tileUV;
flat out int tile;
void main(){
    gl_Position=ProjMat*ModelViewMat*vec4(Position,1.0);
    vertexColor=Color;
    tile=int(floor(UV0.x/2048.0));
    tileUV=vec2(UV0.x-float(tile)*2048.0,UV0.y);
}
