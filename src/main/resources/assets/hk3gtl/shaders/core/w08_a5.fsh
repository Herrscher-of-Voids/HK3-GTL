#version 150
uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform int PortsCount;
uniform float Glow;
in vec4 vertexColor;
in vec2 tileUV;
flat in int tile;
in vec3 referenceCell;
in vec3 currentCell;
out vec4 fragColor;
bool interfaceAt(vec3 point){
    ivec3 p=ivec3(floor(point));
    if(any(lessThan(p,ivec3(0)))||any(greaterThanEqual(p,ivec3(512,477,512))))return false;
    int id=(p.y*512+p.z)*512+p.x,low=0,high=PortsCount-1;
    while(low<=high){
        int middle=(low+high)/2;
        ivec4 bytes=ivec4(round(texelFetch(Sampler1,ivec2(middle%1024,middle/1024),0)*255.0));
        int value=bytes.r|(bytes.g<<8)|(bytes.b<<16)|(bytes.a<<24);
        if(value==id)return true;
        if(value<id)low=middle+1;else high=middle-1;
    }
    return false;
}
void main(){
    if(interfaceAt(referenceCell)||interfaceAt(currentCell))discard;
    vec2 uv=clamp(vec2(fract(tileUV.x),1.0-fract(tileUV.y)),0.001,0.999);
    vec2 origin=vec2(tile%16,tile/16);
    vec4 color=texture(Sampler0,(origin+uv)/vec2(16.0,8.0));
    if(color.a<0.12)discard;
    fragColor=vec4(color.rgb*vertexColor.rgb*Glow,color.a*vertexColor.a);
}
