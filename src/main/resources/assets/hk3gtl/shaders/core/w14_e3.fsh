#version 150
uniform sampler2D Sampler0;
uniform float Glow;
uniform vec2 AtlasGrid;
in vec4 vertexColor;
in vec2 tileUV;
flat in int tile;
out vec4 fragColor;
void main(){
    vec2 uv=clamp(vec2(fract(tileUV.x),1.0-fract(tileUV.y)),.001,.999);
    int columns=int(AtlasGrid.x);vec2 origin=vec2(tile%columns,tile/columns);
    vec4 color=texture(Sampler0,(origin+uv)/AtlasGrid);
    if(color.a<.12)discard;
    fragColor=vec4(color.rgb*vertexColor.rgb*Glow,color.a*vertexColor.a);
}
