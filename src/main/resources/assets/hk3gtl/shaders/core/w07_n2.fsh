#version 150
uniform sampler2D Sampler0;
uniform sampler2D Sampler1;
uniform int PortsCount;
uniform float Glow;
uniform vec2 AtlasGrid;
in vec4 vertexColor;
in vec2 tileUV;
flat in int tile;
in vec3 referenceCell;
out vec4 fragColor;
ivec3 portAt(int index){
    int at=index*2;
    ivec4 first=ivec4(round(texelFetch(Sampler1,ivec2(at%1024,at/1024),0)*255.0));
    ivec4 second=ivec4(round(texelFetch(Sampler1,ivec2((at+1)%1024,(at+1)/1024),0)*255.0));
    return ivec3(first.r|(first.g<<8),first.b|(first.a<<8),second.r|(second.g<<8));
}
bool less(ivec3 a,ivec3 b){return a.x<b.x||(a.x==b.x&&(a.y<b.y||(a.y==b.y&&a.z<b.z)));}
bool interfaceAt(vec3 point){
    ivec3 p=ivec3(floor(point));int low=0,high=PortsCount-1;
    while(low<=high){int middle=(low+high)/2;ivec3 q=portAt(middle);if(all(equal(p,q)))return true;if(less(q,p))low=middle+1;else high=middle-1;}
    return false;
}
void main(){
    if(interfaceAt(referenceCell))discard;
    vec2 uv=clamp(vec2(fract(tileUV.x),1.0-fract(tileUV.y)),.001,.999);
    int columns=int(AtlasGrid.x);vec2 origin=vec2(tile%columns,tile/columns);
    vec4 color=texture(Sampler0,(origin+uv)/AtlasGrid);
    if(color.a<.12)discard;
    fragColor=vec4(color.rgb*vertexColor.rgb*Glow,color.a*vertexColor.a);
}
