package com.sirin.hk3gtl.client.farview;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.client.model.data.ModelData;
import com.mojang.blaze3d.platform.TextureUtil;
import org.lwjgl.opengl.GL30;
import java.util.*;

/** 读取真实静态烘焙面和材质；台阶、栅栏等保留模型形状，立方体才允许合面。 */
final class Hk3FarMaterials implements AutoCloseable {
    static final int PIXELS=32,GRID=32;
    record Face(float[] vertices,int slot,int uAxis,int vAxis,Direction cull) {}
    record Material(boolean cube,boolean opaque,boolean translucent,List<Face> faces) {
        Face side(Direction direction){return faces.stream().filter(f->f.cull==direction).findFirst().orElseThrow();}
    }
    private final Map<Integer,Material> models=new HashMap<>();
    private final Map<String,Integer> sprites=new HashMap<>();
    private DynamicTexture atlas;
    private boolean dirty;
    Material get(int encoded){return models.computeIfAbsent(encoded,this::load);}
    int texture() {
        if(dirty){atlas.upload();atlas.setFilter(true,true);GL30.glGenerateMipmap(GL30.GL_TEXTURE_2D);dirty=false;}
        return atlas.getId();
    }
    private Material load(int encoded) {
        var mc=Minecraft.getInstance();var state=Block.stateById(encoded-1);
        var model=mc.getBlockRenderer().getBlockModelShaper().getBlockModel(state);
        List<Face> faces=new ArrayList<>();boolean cube=true;
        for(Direction direction:Direction.values()) {
            var quads=model.getQuads(state,direction,RandomSource.create(42),ModelData.EMPTY,null);
            cube&=quads.size()==1;
            for(var q:quads){var face=face(q,state,direction);faces.add(face);cube&=unitFace(face,direction);}
        }
        var general=model.getQuads(state,null,RandomSource.create(42),ModelData.EMPTY,null);
        for(var q:general)faces.add(face(q,state,null));
        cube&=general.isEmpty()&&faces.size()==6;
        return new Material(cube,state.canOcclude(),ItemBlockRenderTypes.getChunkRenderType(state)==RenderType.translucent(),List.copyOf(faces));
    }
    private Face face(BakedQuad quad,net.minecraft.world.level.block.state.BlockState state,Direction cull) {
        var sprite=quad.getSprite();int tint=0xffffff;
        if(quad.isTinted())tint=Minecraft.getInstance().getBlockColors().getColor(state,null,null,quad.getTintIndex());
        int slot=sprite(sprite,tint);int[] raw=quad.getVertices();int stride=raw.length/4;
        float[] vertices=new float[20];
        for(int i=0;i<4;i++) {
            for(int axis=0;axis<3;axis++)vertices[i*5+axis]=Float.intBitsToFloat(raw[i*stride+axis]);
            vertices[i*5+3]=(Float.intBitsToFloat(raw[i*stride+4])-sprite.getU0())/(sprite.getU1()-sprite.getU0());
            vertices[i*5+4]=(Float.intBitsToFloat(raw[i*stride+5])-sprite.getV0())/(sprite.getV1()-sprite.getV0());
        }
        return new Face(vertices,slot,uvAxis(vertices,3),uvAxis(vertices,4),cull);
    }
    private static int uvAxis(float[] vertices,int uv) {
        for(int i=1;i<4;i++)if(Math.abs(vertices[i*5+uv]-vertices[uv])>.5f
                &&Math.abs(vertices[i*5+7-uv]-vertices[7-uv])<.01f) {
            for(int axis=0;axis<3;axis++)if(Math.abs(vertices[i*5+axis]-vertices[axis])>.5f)return axis;
        }
        return uv==3?0:1;
    }
    private static boolean unitFace(Face face,Direction direction) {
        float[] v=face.vertices;int axis=direction.getAxis().ordinal();
        float plane=direction.getAxisDirection()==Direction.AxisDirection.POSITIVE?1:0;
        for(int i=0;i<4;i++)for(int a=0;a<3;a++) {
            float n=v[i*5+a];
            if(a==axis?Math.abs(n-plane)>.0001f:Math.abs(n)>.0001f&&Math.abs(n-1)>.0001f)return false;
        }
        return true;
    }
    private int sprite(net.minecraft.client.renderer.texture.TextureAtlasSprite sprite,int tint) {
        String key=sprite.contents().name()+":"+tint;Integer previous=sprites.get(key);if(previous!=null)return previous;
        if(sprites.size()==GRID*GRID)throw new IllegalStateException("远景真实材质图集已满");
        if(atlas==null) {
            atlas=new DynamicTexture(PIXELS*GRID,PIXELS*GRID,false);
            TextureUtil.prepareImage(atlas.getId(),5,PIXELS*GRID,PIXELS*GRID);
            Minecraft.getInstance().getTextureManager().register("hk3gtl_far_materials",atlas);
        }
        int slot=sprites.size(),ox=slot%GRID*PIXELS,oy=slot/GRID*PIXELS;
        var image=atlas.getPixels();int w=sprite.contents().width(),h=sprite.contents().height();
        for(int x=0;x<PIXELS;x++)for(int y=0;y<PIXELS;y++) {
            int pixel=sprite.getPixelRGBA(0,x*w/PIXELS,y*h/PIXELS);
            int r=(pixel&255)*((tint>>16)&255)/255,g=((pixel>>8)&255)*((tint>>8)&255)/255,b=((pixel>>16)&255)*(tint&255)/255;
            image.setPixelRGBA(ox+x,oy+y,(pixel&0xff000000)|b<<16|g<<8|r);
        }
        sprites.put(key,slot);dirty=true;return slot;
    }
    @Override public void close(){if(atlas!=null){atlas.close();atlas=null;}models.clear();sprites.clear();dirty=false;}
}
