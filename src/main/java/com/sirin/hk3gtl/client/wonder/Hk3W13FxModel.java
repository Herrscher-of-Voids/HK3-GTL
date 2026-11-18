package com.sirin.hk3gtl.client.wonder;

import com.google.gson.Gson;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public record Hk3W13FxModel(Data data,Material[] materials,Part[] parts,Layer[] layers){
    private static Data metadata;
    public record Data(int[] sizeXYZ,int[] blueprint_to_export_offset_xyz,int[] controller_blueprint,
                       int[] atlas_grid,String[] palette,long[] material_counts,Cable[] rig){}
    public record Cable(float[][] rest,float[] lengths,float[][] units,float[][] quaternions,float budget){}
    public record Material(boolean transparent,boolean emissive){}
    public record Metadata(int mode,int cable,int segment,float[] rest_matrix){}
    public record Part(String id,float[] origin,int[] size,int[][][] starts,int[][][] lengths,int[][][] spans,Metadata metadata){}
    public record Layer(int y,int[][] rectangles){}
    public static Hk3W13FxModel load(){
        return Hk3CompactScene.load("w13_t2_m1",Hk3W13FxModel.class);
    }
    public static Data loadMetadata(){
        if(metadata!=null)return metadata;
        try(var stream=Minecraft.getInstance().getResourceManager().open(new ResourceLocation("hk3gtl","models/scene/w13_t2_m1_meta.json"));
            var reader=new InputStreamReader(stream,StandardCharsets.UTF_8)){
            metadata=new Gson().fromJson(reader,Data.class);return metadata;
        }catch(IOException failure){throw new IllegalStateException("W13预览元数据读取失败",failure);}
    }
    static void clearMetadata(){metadata=null;}
}
