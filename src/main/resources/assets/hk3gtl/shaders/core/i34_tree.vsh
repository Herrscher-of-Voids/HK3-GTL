#version 150
in vec3 Position;
in vec4 Color;
in vec2 UV0;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform vec2 Viewport;
out vec2 coord;
out float phase;
out float halo;
void main(){
    vec4 p=ModelViewMat*vec4(Position,1.0);
    halo=step(.65,Color.b);
    coord=sign(UV0);
    phase=abs(UV0.y)-1.0;
    float size=abs(UV0.x);
    if(halo>.5){
        p.xy+=coord*vec2(size,25.0)*.45;
        gl_Position=ProjMat*p;
    }else{
        gl_Position=ProjMat*p;
        float pixels=clamp(size*520.0/max(1.0,-p.z),1.0,26.0);
        gl_Position.xy+=coord*pixels/Viewport*gl_Position.w;
    }
}
