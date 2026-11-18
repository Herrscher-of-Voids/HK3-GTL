package com.sirin.hk3gtl.common.review;







public final class Hk3CocoonView {
    private Hk3CocoonView(){}
    private static double dx(double x){return Math.floor(x/512+.5)*512+.5-x;}
    private static double dz(double z){return Math.floor(z/512+.5)*512+300.5-z;}
    public static float yaw(double x,double z){return (float)-Math.toDegrees(Math.atan2(dx(x),dz(z)));}
    public static float pitch(double x,double eyeY,double z){return (float)-Math.toDegrees(Math.atan2(31-eyeY,Math.hypot(dx(x),dz(z))));}
}
