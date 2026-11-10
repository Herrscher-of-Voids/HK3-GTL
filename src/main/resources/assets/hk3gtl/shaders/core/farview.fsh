#version 150
uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform vec2 ChunkOrigin;
uniform vec3 CameraOrigin;
uniform float FarLimit;
uniform float NearLimit;
in vec3 worldPosition;
in vec4 vertexColor;
in vec2 faceUV;
out vec4 fragColor;
void main() {
    vec2 cell=floor(worldPosition.xz/16.0)-ChunkOrigin;
    if(all(greaterThanEqual(cell,vec2(0.0)))&&all(lessThan(cell,vec2(128.0)))
            &&distance(worldPosition,CameraOrigin)<NearLimit&&texelFetch(Sampler1,ivec2(cell),0).r>0.5)discard;
    if(distance(worldPosition,CameraOrigin)>FarLimit)discard;
    int slot=int(round(vertexColor.r*255.0))+int(round(vertexColor.g*255.0))*256;
    vec2 tile=vec2(slot%32,slot/32);
    float footprint=max(length(dFdx(faceUV)*32.0),length(dFdy(faceUV)*32.0));
    float lod=clamp(log2(max(1.0,footprint)),0.0,5.0);
    float inset=0.5*exp2(lod)/32.0;
    vec2 uv=(tile+mix(vec2(inset),vec2(1.0-inset),fract(faceUV)))/32.0;
    vec4 material=textureLod(Sampler0,uv,lod);
    if(material.a<0.1)discard;
    fragColor=vec4(material.rgb*vertexColor.b,material.a);
}
