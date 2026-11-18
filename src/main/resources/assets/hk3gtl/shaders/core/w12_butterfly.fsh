#version 150
in vec4 vertexColor;
in vec2 pixelUV;
out vec4 fragColor;
void main(){
    ivec2 p=ivec2(floor(pixelUV*16.0));
    int lo[11]=int[11](3,2,1,1,2,3,2,1,2,3,4);
    int hi[11]=int[11](5,6,6,6,7,7,6,6,6,5,5);
    int x=min(p.x,15-p.x),y=p.y-2;
    bool body=(p.x==7||p.x==8)&&p.y>=4&&p.y<=11;
    bool wing=y>=0&&y<11&&x>=lo[clamp(y,0,10)]&&x<=hi[clamp(y,0,10)];
    bool antenna=(x==6&&p.y>=2&&p.y<=3)||(x==5&&p.y==1);
    bool hole=(x==3&&(p.y==5||p.y==6||p.y==10));
    if((!body&&!wing&&!antenna)||hole||vertexColor.a<.03)discard;
    fragColor=vertexColor;
}
