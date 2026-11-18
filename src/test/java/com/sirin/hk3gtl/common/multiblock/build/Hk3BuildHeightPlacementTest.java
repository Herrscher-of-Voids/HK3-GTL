package com.sirin.hk3gtl.common.multiblock.build;

public final class Hk3BuildHeightPlacementTest {
    public static void main(String[] args) {
        String low = Hk3BuildHeightPlacement.rejection(-64, 320, -60, -29, 353);
        require(low != null && low.contains("Y=-89～293") && low.contains("Y=-35～-34"), "原版建高中的W01低位放置");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, -35, -29, 353) == null, "原版最低有效位置");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, -34, -29, 353) == null, "原版最高有效位置");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, -36, -29, 353) != null, "低于下限一格");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, -33, -29, 353) != null, "超过上限一格");
        String tooTall = Hk3BuildHeightPlacement.rejection(0, 256, 29, -29, 353);
        require(tooTall.contains("完整建筑高383格") && tooTall.contains("本维度放不下"), "过矮维度不建议无效位置");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, -64, 0, 383) == null, "恰好占满维度高度");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, 0, -64, 320).contains("本维度放不下"), "比维度高一格");
        require(Hk3BuildHeightPlacement.rejection(-64, 320, Integer.MAX_VALUE, 0, 100).contains("2147483747"), "高度加法不溢出");
        require(Hk3BuildHeightPlacement.rejection(-64, 1024, -60, -29, 353).contains("Y=-35～670"), "增强版实际建高提示");
        require(Hk3BuildHeightPlacement.rejection(-64, 1024, 670, -29, 353) == null, "增强版最高有效位置");
        require(Hk3BuildHeightPlacement.rejection(-64, 1024, 671, -29, 353) != null, "增强版超过上限一格");
        System.out.println("Hk3BuildHeightPlacementTest: 12项放置与提示检查通过");
    }
    private static void require(boolean value, String label) {
        if (!value) throw new AssertionError(label);
    }
}
