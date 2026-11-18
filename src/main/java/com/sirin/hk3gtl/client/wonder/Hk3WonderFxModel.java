package com.sirin.hk3gtl.client.wonder;

import com.google.gson.JsonObject;

public record Hk3WonderFxModel(Data data,Material[] materials,Part[] parts){
    public record Data(int[] sizeXYZ,int[] blueprint_to_export_offset_xyz,int[] controller_blueprint,JsonObject effects){}
    public record Material(boolean transparent,boolean emissive){}
    public record Metadata(float[] motion_axis,float[] pivot,float idle_speed,float running_speed,String motion_kind,float amplitude,float frequency){}
    public record Part(String id,int[] origin,int[] size,int[][][] starts,int[][][] lengths,int[][][] spans,Metadata metadata){}
    static String resource(String role){return role.equals("W05")?"w05_r3":"w06_author";}
    static Hk3WonderFxModel load(String role){
        return Hk3CompactScene.load(resource(role),Hk3WonderFxModel.class);
    }
}
