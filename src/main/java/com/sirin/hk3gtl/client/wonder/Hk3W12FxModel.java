package com.sirin.hk3gtl.client.wonder;

public record Hk3W12FxModel(Data data,Material[] materials,Part[] parts) {
    public record Bounds(int[] min,int[] max) {}
    public record Effects(float[][] beam_origins,float[][] tower_origins,float[][] lance_directions,float[] lance_energy_radii,float[] center) {}
    public record Data(int[] sizeXYZ,int[] blueprint_to_export_offset_xyz,int[] controller_blueprint,Bounds bounds,Effects effects) {}
    public record Material(boolean transparent,boolean emissive) {}
    public record Metadata(float[] motion_axis,float[] pivot,float motion_speed,String visual) {}
    public record Part(String id,int[] origin,int[] size,int[][][] starts,int[][][] lengths,int[][][] spans,Metadata metadata) {}
    public static Hk3W12FxModel load(){
        return Hk3CompactScene.load("w12_a3",Hk3W12FxModel.class);
    }
}
