package com.sirin.hk3gtl.common.farview;

import net.minecraftforge.common.ForgeConfigSpec;

public final class Hk3FarViewConfig {
    public static final ForgeConfigSpec SPEC;
    public static final ForgeConfigSpec.BooleanValue ENABLED;
    public static final ForgeConfigSpec.IntValue DISTANCE,GPU_MIB;
    static {
        var b=new ForgeConfigSpec.Builder();
        ENABLED=b.comment("本模组巨构原生远景；不加载真实区块，不绘制实体。可关闭以节省显存。")
                .define("enabled",true);
        DISTANCE=b.comment("巨构外观最远可见距离（方块）；真实地形视距和模拟距离不变。")
                .defineInRange("distance",2048,256,4096);
        GPU_MIB=b.comment("远景顶点缓存上限MiB，按需使用而非预分配；过低会省略超额批次。优先保留近处，后台分帧上传。")
                .defineInRange("gpuMiB",64,8,128);
        SPEC=b.build();
    }
    private Hk3FarViewConfig() {}
}
