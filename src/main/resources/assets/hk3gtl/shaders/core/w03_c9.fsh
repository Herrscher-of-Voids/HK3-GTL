#version 150
uniform sampler2D Sampler0;
in vec4 vertexColor;
in vec2 tileUV;
flat in int tile;
out vec4 fragColor;
void main(){
    vec2 uv=clamp(vec2(fract(tileUV.x),1.0-fract(tileUV.y)),0.001,0.999);
    vec2 origin=vec2(tile%16,tile/16);
    vec4 color=texture(Sampler0,(origin+uv)/vec2(16.0,8.0));
    if(color.a<0.12)discard;
    fragColor=vec4(color.rgb*vertexColor.rgb,1.0);
}
