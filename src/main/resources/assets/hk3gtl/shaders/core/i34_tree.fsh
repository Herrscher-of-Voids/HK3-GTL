#version 150
uniform float Time;
uniform float Power;
in vec2 coord;
in float phase;
in float halo;
out vec4 fragColor;
void main(){
    float r=length(coord);if(r>1.0)discard;
    float glow=exp(-r*r*7.5),core=exp(-r*r*70.0);
    float pulse=.72+.28*sin(Time*.8+phase);
    vec3 color=mix(vec3(1.0,.56,.16),vec3(1.0,.95,.75),core);
    float alpha=(glow*.35+core*.8)*pulse*Power;
    if(halo>.5){
        float t=min(r/.15,1.0);
        vec4 inner=mix(vec4(1.0,247.0/255.0,.8,.65),vec4(1.0,195.0/255.0,82.0/255.0,.2),t);
        vec4 outer=mix(vec4(1.0,195.0/255.0,82.0/255.0,.2),vec4(1.0,167.0/255.0,47.0/255.0,0.0),clamp((r-.15)/.85,0.0,1.0));
        vec4 gradient=r<.15?inner:outer;
        color=gradient.rgb*vec3(1.0,217.0/255.0,160.0/255.0);
        alpha=gradient.a*(.075+.009*sin(Time*.6+phase))*Power;
    }
    fragColor=vec4(color,alpha);
}
