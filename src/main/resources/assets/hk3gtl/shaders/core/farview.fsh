#version 150
uniform sampler2D Sampler0;
uniform vec3 CameraOrigin;
uniform float FarLimit;
uniform int NativeMask;
uniform float NativeBaseY;
uniform float NativeSections[65];
in vec3 worldPosition;
in vec3 tilePosition;
in vec4 vertexColor;
in vec2 faceUV;
out vec4 fragColor;
void main() {
    vec3 delta=worldPosition-CameraOrigin;
    if(dot(delta,delta)>FarLimit*FarLimit)discard;
    if(NativeMask!=0){
        vec3 normal=normalize(cross(dFdx(tilePosition),dFdy(tilePosition)))*(gl_FrontFacing?1.0:-1.0);
        ivec3 section=ivec3(floor((tilePosition-normal*0.001)/16.0));
        int layer=section.y-int(NativeBaseY);
        if(section.x>=0&&section.x<4&&section.z>=0&&section.z<4&&layer>=0&&layer<65
                &&(int(NativeSections[layer])&(1<<(section.x*4+section.z)))!=0)discard;
    }
    int slot=int(round(vertexColor.r*255.0))+int(round(vertexColor.g*255.0))*256;
    vec2 tile=vec2(slot%32,slot/32);
    float footprint=max(length(dFdx(faceUV)*32.0),length(dFdy(faceUV)*32.0));
    float lod=clamp(log2(max(1.0,footprint)),0.0,5.0);
    float inset=0.5*exp2(ceil(lod))/32.0;
    vec2 uv=(tile+mix(vec2(inset),vec2(1.0-inset),fract(faceUV)))/32.0;
    vec4 material=textureLod(Sampler0,uv,lod);
    if(material.a<0.1)discard;
    fragColor=vec4(material.rgb*vertexColor.b,material.a);
}
