#version 150
uniform vec4 ColorModulator;
uniform float SceneTime;
in vec4 vertexColor;
in vec2 flowCoord;
flat in int mode;
flat in float flowWidth;
flat in float intensity;
flat in float phase;
flat in float speed;
out vec4 fragColor;
void main(){
    vec4 color=vertexColor*ColorModulator;
    float across=abs(flowCoord.y);
    if(mode==0){
        color.rgb*=intensity;
    }else if(mode==2){
        float feather=pow(1.0-smoothstep(0.0,1.0,across),1.5);
        float pulse=.94+.06*sin(SceneTime*.37+phase);
        color.rgb*=intensity;
        color.a*=feather*pulse;
    }else{
        float soft=mode==3?1.0:0.0;
        float travel=floor(flowCoord.x/1.25)*1.25;
        float front=floor(pow(.5+.5*sin(travel*.11-SceneTime*(1.1+speed*6.0)+phase),8.0)*3.99)/3.0;
        float fine=floor((.5+.5*sin(travel*.29-SceneTime*(.6+speed*2.7)+phase*1.7))*2.99)/2.0;
        float lane=1.0-floor(clamp(across,0.0,.999)*3.0)/3.0;
        float base=.66+.12*fine;
        float peak=.48+clamp(flowWidth*.08,0.0,.35);
        float feather=1.0-smoothstep(.02,1.0,across);
        float shade=mix(.88+.12*lane,1.0,soft);
        vec3 warm=mix(color.rgb,vec3(1.0,.79,.96)*ColorModulator.rgb,front*.12*(1.0-soft));
        color.rgb=warm*intensity*(base+front*peak)*shade;
        color.a*=mix(1.0,feather,soft);
    }
    fragColor=color;
}
