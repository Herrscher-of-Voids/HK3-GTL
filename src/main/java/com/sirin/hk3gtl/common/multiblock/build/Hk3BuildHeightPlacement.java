package com.sirin.hk3gtl.common.multiblock.build;

/** 按维度实际建高计算控制器范围，不移动或裁切蓝图。 */
final class Hk3BuildHeightPlacement {
    private Hk3BuildHeightPlacement() {}

    static String rejection(int worldMin, int worldMaxExclusive, int controllerY, int minOffset, int maxOffset) {
        long low = (long) controllerY + minOffset, high = (long) controllerY + maxOffset;
        if (low >= worldMin && high < worldMaxExclusive) return null;
        long lowest = (long) worldMin - minOffset, highest = (long) worldMaxExclusive - 1 - maxOffset;
        String detail = "蓝图实际高度Y=" + low + "～" + high + "，本维度允许Y=" + worldMin + "～" + (worldMaxExclusive - 1) + "。";
        return lowest <= highest
                ? detail + "请将控制器放在Y=" + lowest + "～" + highest + "后重试；未放置方块，也未扣除材料。"
                : detail + "完整建筑高" + ((long) maxOffset - minOffset + 1) + "格，本维度放不下；请使用建高足够的维度。未放置方块，也未扣除材料。";
    }
}
