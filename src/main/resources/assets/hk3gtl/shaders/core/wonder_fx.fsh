#version 150
uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform int PortsCount;
uniform int VoidSurface;
uniform float Glow;
uniform float Time;
uniform vec2 ScrollUV;
uniform int CoreSurface;
uniform int Working;
uniform vec3 SceneSize;
in vec4 vertexColor;
in vec2 tileUV;
flat in int tile;
in vec3 referenceCell;
in vec3 currentCell;
in vec3 blueprintPosition;
out vec4 fragColor;
bool interfaceAt(vec3 point){
    ivec3 p=ivec3(floor(point)),size=ivec3(SceneSize);
    if(any(lessThan(p,ivec3(0)))||any(greaterThanEqual(p,size)))return false;
    int id=(p.y*size.z+p.z)*size.x+p.x,low=0,high=PortsCount-1;
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
    if(VoidSurface!=0){
        vec3 cell=floor(blueprintPosition*2.0);
        float line=step(.996,sin(cell.y*.13+cell.x*.029+cell.z*.031-Time*.12));
        fragColor=vec4(vec3(.0015,.0005,.0025)*line,1.0);
        return;
    }
    if(CoreSurface!=0&&Working!=0){fragColor=vec4(vec3(2.2),1.0);return;}
    vec2 shifted=tileUV+ScrollUV;
    vec2 uv=clamp(vec2(fract(shifted.x),1.0-fract(shifted.y)),0.001,0.999);
    vec2 origin=vec2(tile%16,tile/16);
    vec4 color=texture(Sampler0,(origin+uv)/vec2(16.0,8.0));
    if(color.a<0.12)discard;
    fragColor=vec4(color.rgb*vertexColor.rgb*Glow,color.a*vertexColor.a);
}
