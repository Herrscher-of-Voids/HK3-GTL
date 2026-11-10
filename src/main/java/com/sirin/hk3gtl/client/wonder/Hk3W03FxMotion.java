package com.sirin.hk3gtl.client.wonder;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** 与C9查看器相同的右乘四元数顺序；保留每个部件独立枢轴与初始位移。 */
public final class Hk3W03FxMotion {
    private Hk3W03FxMotion() {}
    public static Matrix4f matrix(Hk3W03FxModel.Part part,double seconds,Matrix4f origin) {
        var rotation=new Quaternionf();var axis=new Vector3f();
        for(var r:part.rotations()) {
            axis.set(r.axis()[0],r.axis()[1],r.axis()[2]).normalize();
            rotation.mul(new Quaternionf().fromAxisAngleRad(axis,(float)(seconds*r.degrees_per_second()*Math.PI/180)));
        }
        var p=part.pivot_export();var t=part.render_translation_xyz();
        return new Matrix4f(origin).translate(p[0],p[1],p[2]).rotate(rotation).translate(-p[0]+t[0],-p[1]+t[1],-p[2]+t[2]);
    }
}
