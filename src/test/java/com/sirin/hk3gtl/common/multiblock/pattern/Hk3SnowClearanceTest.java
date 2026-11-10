package com.sirin.hk3gtl.common.multiblock.pattern;

import net.minecraft.resources.ResourceLocation;
import java.util.Arrays;

/** 核验积雪豁免的边界与真实稀疏体素的暴露表面，不冒充游戏成型验收。 */
public final class Hk3SnowClearanceTest {
    public static void main(String[] args) {
        check(Hk3InterfacePredicates.isClearance(true,new ResourceLocation("minecraft","cave_air")),"空气被拒绝");
        check(Hk3InterfacePredicates.isClearance(false,new ResourceLocation("minecraft","snow")),"自然雪层被拒绝");
        check(Hk3InterfacePredicates.isClearance(false,new ResourceLocation("ae2","cable_bus")),"既有AE线路被拒绝");
        for (String id:new String[]{"minecraft:snow_block","minecraft:powder_snow","minecraft:water","minecraft:lava",
                "minecraft:stone","minecraft:tall_grass","other:snow"})
            check(!Hk3InterfacePredicates.isClearance(false,new ResourceLocation(id)),"错误放行障碍："+id);
        // 两列及另一Z切片相邻，材料编号不同；不能把下一层切片误当作头顶支撑。
        long[] cells={cell(0,0,0,5),cell(0,1,0,9),cell(0,2,0,7),cell(1,0,0,2),cell(1,2,0,3),cell(0,0,1,8)};
        Arrays.sort(cells);
        for (int i=0;i<cells.length;i++) {
            int at=(int)(cells[i]>>>16),x=at%2,y=at/2%3,z=at/6;
            boolean expected=y==2 || Arrays.stream(cells).noneMatch(c->(c>>>16)==((z*3+y+1)*2+x));
            check(Hk3SnowSurfaceIndex.exposed(cells,i,2,3)==expected,"除雪表面与逐格独立判断不同");
        }
        System.out.println("雪层与AE线缆放行，雪块/细雪/流体/实体障碍拒绝；稀疏表面边界通过。未进行实装测试。");
    }
    private static long cell(int x,int y,int z,int state) { return (long)((z*3+y)*2+x)<<16|state; }
    private static void check(boolean ok,String message) { if(!ok)throw new AssertionError(message); }
}
