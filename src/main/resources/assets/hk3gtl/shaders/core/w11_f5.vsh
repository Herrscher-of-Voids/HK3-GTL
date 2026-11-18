#version 150
in vec3 Position;
in vec4 Color;
in vec2 UV0;
uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform mat4 PartTransform;
uniform vec3 ExportOffset;
out vec4 vertexColor;
out vec2 tileUV;
flat out int tile;
out vec3 referenceCell;
out vec3 currentCell;
void main(){
    gl_Position=ProjMat*ModelViewMat*vec4(Position,1.0);
    vertexColor=Color;
    tile=int(floor(UV0.x/2048.0));
    tileUV=vec2(UV0.x-float(tile)*2048.0,UV0.y);
    int face=tile%6;
    vec3 normal=face==0?vec3(1,0,0):face==1?vec3(-1,0,0):face==2?vec3(0,0,1):face==3?vec3(0,0,-1):face==4?vec3(0,-1,0):vec3(0,1,0);
    vec3 inside=Position-normal*.002;
    referenceCell=inside+ExportOffset;
    currentCell=(PartTransform*vec4(inside,1.0)).xyz+ExportOffset;
}
