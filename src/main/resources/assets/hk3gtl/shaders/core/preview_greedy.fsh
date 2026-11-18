#version 150
uniform sampler2D Sampler0;
uniform vec4 SpriteBounds;
uniform int Connected;
uniform vec3 CtmU0;
uniform vec3 CtmU1;
uniform vec3 CtmU2;
uniform vec3 CtmU3;
uniform vec3 CtmV0;
uniform vec3 CtmV1;
uniform vec3 CtmV2;
uniform vec3 CtmV3;
in vec4 vertexColor;
in vec2 faceUV;
out vec4 fragColor;
void main() {
    if (Connected != 0) {
        vec2 quarter = fract(faceUV) * 2.0;
        int quadrant = int(quarter.x) + int(quarter.y) * 2;
        vec3 mapU, mapV;
        if (quadrant == 0) { mapU = CtmU0; mapV = CtmV0; }
        else if (quadrant == 1) { mapU = CtmU1; mapV = CtmV1; }
        else if (quadrant == 2) { mapU = CtmU2; mapV = CtmV2; }
        else { mapU = CtmU3; mapV = CtmV3; }
        vec3 local = vec3(1.0, fract(quarter));
        vec2 uv = vec2(dot(mapU, local), dot(mapV, local));
        vec2 dx = dFdx(faceUV) * 2.0, dy = dFdy(faceUV) * 2.0;
        fragColor = textureGrad(Sampler0, uv,
                vec2(dot(mapU.yz, dx), dot(mapV.yz, dx)),
                vec2(dot(mapU.yz, dy), dot(mapV.yz, dy))) * vertexColor;
        return;
    }
    vec2 span = SpriteBounds.zw - SpriteBounds.xy;
    vec2 uv = SpriteBounds.xy + fract(faceUV) * span;
    fragColor = textureGrad(Sampler0, uv, dFdx(faceUV) * span, dFdy(faceUV) * span) * vertexColor;
}
