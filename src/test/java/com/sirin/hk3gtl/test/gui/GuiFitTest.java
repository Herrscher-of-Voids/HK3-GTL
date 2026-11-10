package com.sirin.hk3gtl.test.gui;

import com.sirin.hk3gtl.common.gui.Hk3GuiFit;

/**
 * 【变更记录 #1】2026-09-23 12:09:00（内测5修订61）
 * 删除：无。新增：小视窗、宽窄屏及按钮命中坐标往返回归。修改：无。
 * 用途：保证底部支付按钮和滚动区域缩放后可命中；不冒充游戏渲染验收。
 * Verify viewport containment, pointer round trips and payment-button hit coordinates, not runtime rendering.
 */
public final class GuiFitTest {
    public static void main(String[] args) {
        int[][] viewports = {{320,240},{427,240},{640,360},{960,540},{2560,1440},{200,600},{900,160},{1,1}};
        for (int[] v : viewports) {
            var fit = Hk3GuiFit.centered(v[0],v[1],520,300,8);
            require(fit.scale()>0 && fit.scale()<=1,"positive downscale");
            require(fit.left()>=0 && fit.top()>=0,"nonnegative origin");
            require(fit.screenX(520)<=v[0]+1e-8 && fit.screenY(300)<=v[1]+1e-8,"contained panel");
            // 搜索、列表、详情滚动条以及两种支付按钮中心，单位为设计像素。
            // Design-pixel centers of search, list, detail scrollbar and both payment buttons.
            for (double[] p : new double[][]{{80,42},{60,69},{509,100},{217,283},{335,283},{452,283}}) {
                double x=fit.screenX(p[0]),y=fit.screenY(p[1]);
                require(fit.contains(x,y,520,300),"visible control is clickable");
                require(Math.abs(fit.x(x)-p[0])<1e-8 && Math.abs(fit.y(y)-p[1])<1e-8,"input round trip");
            }
            require(!fit.contains(fit.left()-1,fit.top(),520,300),"outside left rejected");
            require(!fit.contains(fit.screenX(520)+1,fit.screenY(300)+1,520,300),"outside bottom rejected");
        }
        require(Hk3GuiFit.centered(960,540,520,300,8).scale()==1,"large windows do not upscale");
        System.out.println("GUI fit: eight viewports, clipping bounds and research control hit coordinates passed");
    }
    private static void require(boolean condition,String message) {
        if(!condition) throw new AssertionError(message);
    }
}
