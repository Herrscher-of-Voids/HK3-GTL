#version 150
in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV1;
in ivec2 UV2;
in vec3 Normal;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
out vec4 vertexColor;
out vec2 flowCoord;
flat out int mode;
flat out float flowWidth;
flat out float intensity;
flat out float phase;
flat out float speed;
void main(){
    gl_Position=ProjMat*ModelViewMat*vec4(Position,1.0);
    vertexColor=Color;
    flowCoord=UV0;
    mode=UV1.x&3;
    flowWidth=float(UV1.x/4)*.01;
    intensity=float(UV1.y)*.001;
    phase=float(UV2.x)*.001;
    speed=float(UV2.y)*.0001;
}
