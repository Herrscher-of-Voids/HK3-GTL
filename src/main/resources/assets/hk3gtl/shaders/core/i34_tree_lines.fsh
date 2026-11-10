#version 150
uniform float Power;
in vec3 tint;
out vec4 fragColor;
void main(){
    vec3 srgb=mix(tint*12.92,1.055*pow(tint,vec3(1.0/2.4))-.055,step(vec3(.0031308),tint));
    fragColor=vec4(srgb,.72*Power);
}
