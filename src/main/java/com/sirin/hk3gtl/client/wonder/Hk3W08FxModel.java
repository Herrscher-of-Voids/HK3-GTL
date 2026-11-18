package com.sirin.hk3gtl.client.wonder;

public record Hk3W08FxModel(Data data, Material[] materials, Part[] parts) {
    public record Data(float[] star_center,float[] controller_blueprint,int[] blueprint_to_export_offset_xyz,float star_radius,float corona_radius) {}
    public record Material(boolean transparent,boolean emissive) {}
    public record Mask(float radial_min,float radial_max,float axial_min,float axial_max) {}
    public record Metadata(float[] motion_axis,Mask effect_mask,float cube_sphere_radius) {}
    public record Part(String id,int[] origin,int[] size,int[][][] starts,int[][][] lengths,int[][][] spans,Metadata metadata) {}
    public static Hk3W08FxModel load(){
        return Hk3CompactScene.load("w08_a5",Hk3W08FxModel.class);
    }
}
