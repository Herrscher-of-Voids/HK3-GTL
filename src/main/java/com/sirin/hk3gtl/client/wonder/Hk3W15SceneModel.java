package com.sirin.hk3gtl.client.wonder;

import com.google.gson.Gson;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public record Hk3W15SceneModel(Data data,Material[] materials,Part[] parts,Layer[] layers){
    private static Data metadata;
    public record Data(int[] sizeXYZ,int[] blueprint_to_export_offset_xyz,int[] controller_blueprint,
                       int[] atlas_grid,String[] palette,long[] material_counts){}
    public record Material(boolean transparent,boolean emissive){}
    public record Part(int[] origin,int[] size,int[][][] starts,int[][][] lengths,int[][][] spans){}
    public record Layer(int y,int[][] rectangles){}
    public static Hk3W15SceneModel load(){
        return Hk3CompactScene.load("w15_b1",Hk3W15SceneModel.class);
    }
    public static Data loadMetadata(){
        if(metadata!=null)return metadata;
        try(var stream=Minecraft.getInstance().getResourceManager().open(new ResourceLocation("hk3gtl","models/scene/w15_b1_meta.json"));
            var reader=new InputStreamReader(stream,StandardCharsets.UTF_8)){
            metadata=new Gson().fromJson(reader,Data.class);return metadata;
        }catch(IOException failure){throw new IllegalStateException("W15预览元数据读取失败",failure);}
    }
    static void clearMetadata(){metadata=null;}
}
