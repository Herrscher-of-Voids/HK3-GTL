package com.sirin.hk3gtl.common.farview;

/** 已缓存但超出绘制半径的区块不能抹去远景；未加载区块不能产生遮罩。 */
public final class Hk3FarViewMaskTest {
    public static void main(String[] args) {
        check(Hk3FarViewMask.covered(true,0,0,8),"近处已加载区块应隐藏远景");
        check(!Hk3FarViewMask.covered(false,0,0,8),"未加载近处不能隐藏远景");
        check(!Hk3FarViewMask.covered(true,8,0,8),"超出实际绘制距离的缓存不能隐藏远景");
        check(!Hk3FarViewMask.covered(true,6,6,8),"角落超出绘制半径不能隐藏远景");
        check(Hk3FarViewMask.covered(true,-4,-4,8),"负坐标近处遮罩应对称");
        System.out.println("原生远景近远区块遮罩边界通过；实际游戏绘制另验。");
    }
    private static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
}
