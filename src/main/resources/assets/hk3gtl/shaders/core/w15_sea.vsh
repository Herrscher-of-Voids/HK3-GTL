#version 150
in vec3 Position;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform float Time;
uniform float Power;
out vec4 waterColor;
void main() {
    vec2 q = Position.xz / vec2(630.0,470.0);
    float r = length(q);
    float a = r == 0.0 ? 0.0 : atan(q.y,q.x);
    float drift = 0.5 * (sin(dot(Position.xz,vec2(.011,.017))+Time*.19) + cos(dot(Position.xz,vec2(.018,-.009))-Time*.23));
    float wave = smoothstep(.2,.95,sin(r*28.0-Time*.43+sin(a*4.0+r*5.0)*1.8+drift));
    vec3 color = vec3(.07,.095,.28)+vec3(.07,.195,.3)*(.5+drift*.25)+vec3(.1,.12,.2)*wave;
    waterColor = vec4(color,(.19+wave*.1)*(1.0-smoothstep(.88,1.0,r))*(.78+Power*.22));
    float h = 27.0 + sin(Position.x*.013+Time*.32)*3.0 + cos(Position.z*.017-Time*.25)*2.0;
    gl_Position = ProjMat * ModelViewMat * vec4(Position.x,h,Position.z,1.0);
}
