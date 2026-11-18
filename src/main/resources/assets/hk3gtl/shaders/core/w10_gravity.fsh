#version 150
uniform vec4 ColorModulator;
uniform int LensPass;
uniform float LensStrength;
uniform float Time;
uniform float Seed;
in vec4 vertexColor;
out vec4 fragColor;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+Seed*41.0)*43758.5453);}
void main(){
    if(LensPass!=0){
        vec2 q=(vertexColor.rg-.5)*2.0;
        vec2 warped=q-q*(.11*LensStrength)/max(dot(q,q),.004);
        vec2 cell=floor(warped*120.0),local=fract(warped*120.0);
        float star=step(.997,hash(cell))*step(.45,local.x)*step(.45,local.y);
        float fade=1.0-smoothstep(.7,1.0,length(q));
        if(star*fade<.01)discard;
        vec3 color=mix(vec3(.24,.27,.34),vec3(.58,.48,.31),hash(cell+3.0));
        fragColor=vec4(color*(.8+.2*sin(Time*.3+hash(cell)*6.2831853)),star*fade*.85)*ColorModulator;
    }else{
        fragColor=vertexColor*ColorModulator;
    }
}
