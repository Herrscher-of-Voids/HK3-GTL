package com.sirin.hk3gtl.client.farview;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.client.renderer.texture.MissingTextureAtlasSprite;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.client.model.data.ModelData;
import net.minecraftforge.client.extensions.common.IClientFluidTypeExtensions;
import com.mojang.blaze3d.platform.TextureUtil;
import org.lwjgl.opengl.GL30;
import java.util.*;

/** 读取真实静态烘焙面和材质；台阶、栅栏等保留模型形状，立方体才允许合面。 */
final class Hk3FarMaterials implements AutoCloseable {
    static final int PIXELS=32,GRID=32;
    private static final int MAX_MODELS=2048,MAX_FACES=32768,LOD_SLOTS=32;
    record Face(float[] vertices,int slot,int uAxis,int vAxis,Direction cull) {}
    record Material(boolean cube,boolean opaque,boolean translucent,List<Face> faces,boolean lod,Face[] sides) {
        Material(boolean cube,boolean opaque,boolean translucent,List<Face> faces,boolean lod){
            this(cube,opaque,translucent,faces,lod,new Face[6]);
            for(var face:faces)if(face.cull()!=null)sides[face.cull().ordinal()]=face;
        }
        Face side(Direction direction){return sides[direction.ordinal()];}
    }
    private record Lod(int color,Material[] materials) {}
    private final Map<Integer,Material> models=new HashMap<>();
    private final Map<Integer,Material> surfaces=new HashMap<>();
    private final Map<String,Integer> sprites=new HashMap<>();
    private final Map<String,Lod> lods=new LinkedHashMap<>();
    private final Map<Integer,Material> lodCache=new LinkedHashMap<>(16,.75f,true);
    private final Set<Integer> worldLimited=new HashSet<>();
    private static final Material EMPTY=new Material(false,false,false,List.of(),false);
    private DynamicTexture atlas;
    private ResourceLocation atlasLocation;
    private boolean dirty;
    private int modelFaces,limited;
    private boolean modelLimit,failureLogged,priority;
    void priority(boolean value){priority=value;}
    int limited(){return limited+(modelLimit?1:0);}
    Material get(int encoded){
        var previous=models.get(encoded);
        if(previous!=null&&!(priority&&worldLimited.remove(encoded)))return previous;
        var state=Block.stateById(encoded-1);
        if(state.isAir()||state.getRenderShape()==RenderShape.INVISIBLE&&state.getFluidState().isEmpty()){
            models.put(encoded,EMPTY);return EMPTY;
        }
        if(previous==null&&models.size()>=(priority?MAX_MODELS:MAX_MODELS/2)){modelLimit=true;return lod(state);}
        Material loaded;
        try{
            loaded=load(encoded);
        }catch(RuntimeException failure){
            loaded=lod(state);
            if(!failureLogged){failureLogged=true;com.mojang.logging.LogUtils.getLogger().warn("远景静态模型读取失败；后续同类错误不重复刷屏",failure);}
        }
        if(loaded.lod()){limited++;if(!priority)worldLimited.add(encoded);}
        else modelFaces+=loaded.faces().size();
        surfaces.remove(encoded);models.put(encoded,loaded);return loaded;
    }
    Material surface(int encoded){
        var material=get(encoded);
        return material.cube()||material==EMPTY?material:surfaces.computeIfAbsent(encoded,key->lod(Block.stateById(key-1)));
    }
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
            for(var q:quads){
                if(q.getSprite().contents().name().equals(MissingTextureAtlasSprite.getLocation()))return EMPTY;
                if(faces.size()>=faceLimit()-modelFaces)return lod(state);
                var face=face(q,state,direction);if(face==null)return lod(state);faces.add(face);cube&=unitFace(face,direction);
            }
        }
        var general=model.getQuads(state,null,RandomSource.create(42),ModelData.EMPTY,null);
        for(var q:general){
            if(q.getSprite().contents().name().equals(MissingTextureAtlasSprite.getLocation()))return EMPTY;
            if(faces.size()>=faceLimit()-modelFaces)return lod(state);
            var face=face(q,state,null);if(face==null)return lod(state);faces.add(face);
        }
        if(faces.isEmpty())return state.getRenderShape()==RenderShape.INVISIBLE&&!state.getFluidState().isEmpty()?lod(state):EMPTY;
        cube&=general.isEmpty()&&faces.size()==6;
        return new Material(cube,state.canOcclude(),ItemBlockRenderTypes.getChunkRenderType(state)==RenderType.translucent(),List.copyOf(faces),false);
    }
    private int faceLimit(){return (priority?MAX_FACES:MAX_FACES/2)-LOD_SLOTS*6;}
    private static int tint(BlockState state,int index){
        try{return Minecraft.getInstance().getBlockColors().getColor(state,null,null,index);}
        catch(RuntimeException unavailable){return 0xffffff;}
    }
    private Face face(BakedQuad quad,BlockState state,Direction cull) {
        var sprite=quad.getSprite();int color=quad.isTinted()?tint(state,quad.getTintIndex()):0xffffff;
        int slot=sprite(sprite,color);if(slot<0)return null;
        int[] raw=quad.getVertices();int stride=raw.length/4;
        float[] vertices=new float[20];
        for(int i=0;i<4;i++) {
            for(int axis=0;axis<3;axis++)vertices[i*5+axis]=Float.intBitsToFloat(raw[i*stride+axis]);
            vertices[i*5+3]=(Float.intBitsToFloat(raw[i*stride+4])-sprite.getU0())/(sprite.getU1()-sprite.getU0());
            vertices[i*5+4]=(Float.intBitsToFloat(raw[i*stride+5])-sprite.getV0())/(sprite.getV1()-sprite.getV0());
        }
        return new Face(vertices,slot,uvAxis(vertices,3),uvAxis(vertices,4),cull);
    }
    private Material lod(BlockState state){return lod(state,false);}
    private Material lod(BlockState state,boolean opaqueFluid){
        // 方块实体的粒子图不能代表动态几何，预算降级也不画假立方体。
        if(state.hasBlockEntity())return EMPTY;
        int id=Block.getId(state)*2+(opaqueFluid?1:0);var cached=lodCache.get(id);if(cached!=null)return cached;
        var mc=Minecraft.getInstance();var fluid=state.getFluidState();
        boolean liquid=state.getRenderShape()==RenderShape.INVISIBLE&&!fluid.isEmpty();
        TextureAtlasSprite sprite;int tint;boolean translucent;
        if(liquid){
            var extension=IClientFluidTypeExtensions.of(fluid);
            sprite=mc.getTextureAtlas(TextureAtlas.LOCATION_BLOCKS).apply(extension.getStillTexture());tint=extension.getTintColor();
            translucent=ItemBlockRenderTypes.getRenderLayer(fluid)==RenderType.translucent();
        }else{
            sprite=mc.getBlockRenderer().getBlockModelShaper().getBlockModel(state).getParticleIcon(ModelData.EMPTY);tint=tint(state,0);
            translucent=ItemBlockRenderTypes.getChunkRenderType(state)==RenderType.translucent();
        }
        if(sprite.contents().name().equals(MissingTextureAtlasSprite.getLocation()))return EMPTY;
        int pixel=sprite.getPixelRGBA(0,sprite.contents().width()/2,sprite.contents().height()/2);
        int color=((pixel&255)*((tint>>16)&255)/255)<<16|((pixel>>8&255)*((tint>>8)&255)/255)<<8|(pixel>>16&255)*(tint&255)/255;
        String key=sprite.contents().name()+":"+tint;var lod=lods.get(key);
        if(lod==null){
            if(lods.size()<LOD_SLOTS){
                int slot=GRID*GRID-LOD_SLOTS+lods.size();writeSprite(sprite,tint,slot);
                var faces=cubeFaces(slot);Material[] variants=new Material[4];
                for(int i=0;i<4;i++)variants[i]=new Material(true,(i&1)!=0,(i&2)!=0,faces,true);
                lod=new Lod(color,variants);lods.put(key,lod);
            }else lod=lods.values().stream().min(Comparator.comparingInt(candidate->colorDistance(color,candidate.color()))).orElseThrow();
        }
        // 达到静态模型预算后，透明与非完整块仅在远景中降级为粒子材质方块。
        int variant=(state.canOcclude()||opaqueFluid?1:0)|(translucent&&!opaqueFluid?2:0);var material=lod.materials()[variant];lodCache.put(id,material);
        if(lodCache.size()>256)lodCache.remove(lodCache.keySet().iterator().next());
        return material;
    }
    private static int colorDistance(int a,int b){
        int r=(a>>16&255)-(b>>16&255),g=(a>>8&255)-(b>>8&255),blue=(a&255)-(b&255);
        return r*r+g*g+blue*blue;
    }
    private static List<Face> cubeFaces(int slot){
        List<Face> faces=new ArrayList<>(6);int[] us={0,1,1,0},vs={0,0,1,1};
        for(var direction:Direction.values()){
            int axis=direction.getAxis().ordinal(),u=(axis+1)%3,v=(axis+2)%3;
            boolean positive=direction.getAxisDirection()==Direction.AxisDirection.POSITIVE;float[] vertices=new float[20];
            for(int i=0;i<4;i++){
                int corner=positive?i:3-i;vertices[i*5+axis]=positive?1:0;vertices[i*5+u]=us[corner];vertices[i*5+v]=vs[corner];
                vertices[i*5+3]=us[corner];vertices[i*5+4]=vs[corner];
            }
            faces.add(new Face(vertices,slot,u,v,direction));
        }
        return List.copyOf(faces);
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
    private int sprite(TextureAtlasSprite sprite,int tint) {
        String key=sprite.contents().name()+":"+tint;Integer previous=sprites.get(key);if(previous!=null)return previous;
        if(sprites.size()>=(priority?GRID*GRID-LOD_SLOTS:(GRID*GRID-LOD_SLOTS)/2))return -1;
        int slot=sprites.size();writeSprite(sprite,tint,slot);sprites.put(key,slot);return slot;
    }
    private void writeSprite(TextureAtlasSprite sprite,int tint,int slot){
        if(atlas==null) {
            atlas=new DynamicTexture(PIXELS*GRID,PIXELS*GRID,true);
            TextureUtil.prepareImage(atlas.getId(),5,PIXELS*GRID,PIXELS*GRID);
            atlasLocation=Minecraft.getInstance().getTextureManager().register("hk3gtl_far_materials",atlas);
        }
        int ox=slot%GRID*PIXELS,oy=slot/GRID*PIXELS;
        var image=atlas.getPixels();int w=sprite.contents().width(),h=sprite.contents().height();
        for(int x=0;x<PIXELS;x++)for(int y=0;y<PIXELS;y++) {
            int pixel=sprite.getPixelRGBA(0,x*w/PIXELS,y*h/PIXELS);
            int r=(pixel&255)*((tint>>16)&255)/255,g=((pixel>>8)&255)*((tint>>8)&255)/255,b=((pixel>>16)&255)*(tint&255)/255;
            image.setPixelRGBA(ox+x,oy+y,(pixel&0xff000000)|b<<16|g<<8|r);
        }
        dirty=true;
    }
    @Override public void close(){
        if(atlasLocation!=null){Minecraft.getInstance().getTextureManager().release(atlasLocation);atlasLocation=null;}
        else if(atlas!=null)atlas.close();
        atlas=null;models.clear();surfaces.clear();sprites.clear();lods.clear();lodCache.clear();worldLimited.clear();dirty=false;modelFaces=limited=0;modelLimit=failureLogged=priority=false;
    }
}
