package com.sirin.hk3gtl.common.review;

/**
 * 【文件职责】一审固定观礼朝向；服务端位置约束与客户端镜头采用相同计算。
 * 【变更记录 #1】2026-10-01 20:19:52（内测5修订147）
 * - 删除：无；新增：512格房间内指向茧正面的偏航、俯仰计算。
 * - 修改：抽取修订146入场角度；用途：会面期间持续锁定朝向，返回不依赖此类。
 */
public final class Hk3CocoonView {
    private Hk3CocoonView(){}
    private static double dx(double x){return Math.floor(x/512+.5)*512+.5-x;}
    private static double dz(double z){return Math.floor(z/512+.5)*512+260.5-z;}
    public static float yaw(double x,double z){return (float)-Math.toDegrees(Math.atan2(dx(x),dz(z)));}
    public static float pitch(double x,double eyeY,double z){return (float)-Math.toDegrees(Math.atan2(120-eyeY,Math.hypot(dx(x),dz(z))));}
}
