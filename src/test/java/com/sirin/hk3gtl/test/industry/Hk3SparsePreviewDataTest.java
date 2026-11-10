package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.multiblock.pattern.*;

/** 用实际资源确认奇观与1145格舰体完整坐标、材料及层数，不接受单控制器占位。 */
public final class Hk3SparsePreviewDataTest {
    public static void main(String[] args) {
        check(Hk3SparsePreviewData.machines().size()==56,"五十二正式形态和四座独立建筑均需自家预览");
        for(String id:Hk3SparsePreviewData.machines())check(id.startsWith("hk3gtl:"),"不能接管其他模组");
        check(!Hk3SparsePreviewData.supported("gtceu:assembly_line"),"原版GT预览保持独立");
        for(String id:new String[]{"hk3gtl:omnia_autonomous_industrial_matrix","hk3gtl:void_anchor_ring","hk3gtl:hyperion_flagship"}) {
            var data=Hk3SparsePreviewData.load(id);var layout=data.layout();var index=new Hk3W01PreviewIndex(layout);
            long total=0;for(int y=0;y<layout.height();y++)total+=index.countLayer(y);
            check(total==layout.cells().length&&total>1_000_000,"必须呈现全部实体");
            for(long cell:layout.cells())check(index.stateAt(Hk3W01HallLayout.x(cell),Hk3W01HallLayout.y(cell),Hk3W01HallLayout.z(cell))
                    ==Hk3W01HallLayout.state(cell),"完整坐标与状态逐一回读");
            check(index.stateAt(layout.controllerX(),layout.controllerY(),layout.controllerZ())>=0,"主控不可缺格");
            if(id.endsWith("hyperion_flagship"))check(layout.width()==1145,"不能裁掉超过1024格的舰体");
            if(id.contains("omnia"))check(total==6072490,"必须使用相邻接口的新蓝图");
            System.out.println(id+" 自家预览完整回读："+total);
        }
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
