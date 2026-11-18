package com.sirin.hk3gtl.client.wonder;

public record Hk3W10FxModel(Data data,Material[] materials,Part[] parts) {
    public record Bounds(int[] min,int[] max) {}
    public record Effects(float[][] beam_origins,float[] center,float[] jet_y_range,float void_radius) {}
    public record Data(int[] sizeXYZ,int[] blueprint_to_export_offset_xyz,int[] controller_blueprint,Bounds bounds,Effects effects) {}
    public record Material(boolean transparent,boolean emissive) {}
    public record Metadata(float[] motion_axis,float[] pivot,float motion_speed,String visual) {}
    public record Part(String id,int[] origin,int[] size,int[][][] starts,int[][][] lengths,int[][][] spans,Metadata metadata) {}
    public static Hk3W10FxModel load(){
        return Hk3CompactScene.load("w10_a3",Hk3W10FxModel.class);
    }
}
