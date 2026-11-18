package com.sirin.hk3gtl.test.industry;

import com.google.gson.Gson;
import com.sirin.hk3gtl.client.wonder.Hk3W03FxModel;
import com.sirin.hk3gtl.client.wonder.Hk3W03FxMotion;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.nio.file.Files;
import java.nio.file.Path;
import java.io.DataInputStream;
import java.util.zip.GZIPInputStream;

/** 验证原生矩阵与已核验浏览器C9的法向、周期、固定中心及完整表面数量一致。 */
public final class NativeW03EffectsTest {
    public static void main(String[] args)throws Exception {
        var root=Path.of("src/main/resources/assets/hk3gtl/models/scene");
        var meta=new Gson().fromJson(Files.readString(root.resolve("w03_c9.json")),Hk3W03FxModel.Metadata.class);
        check(meta.components().length==33&&meta.quads()==517262,"C9网格或部件数改变");
        double[] expected={1,.3206682315279567,.31200329706948615,.7044680698021163,.38009807567614007};
        for(int i=1;i<=5;i++) {
            var part=meta.components()[i];
            var m=Hk3W03FxMotion.matrix(part,19,new Matrix4f());
            float[] tilt={0,-25,35,-45,20};
            var n=new Vector3f(0,0,1).rotateX((float)(tilt[i-1]*Math.PI/180));
            float dot=Math.abs(n.dot(new Vector3f(n).mulDirection(m)));
            check(Math.abs(dot-expected[i-1])<2e-6,"环面法向与C9查看器不同："+part.id());
        }
        for(var part:meta.components()) {
            var a=Hk3W03FxMotion.matrix(part,0,new Matrix4f());
            var b=Hk3W03FxMotion.matrix(part,360,new Matrix4f());
            var p=new Vector3f(400,370,420);check(new Vector3f(p).mulPosition(a).distance(new Vector3f(p).mulPosition(b))<.002,"360秒周期不闭合");
            if(part.id().startsWith("crystal:")) {
                var center=new Vector3f(part.pivot_export());
                check(new Vector3f(center).mulPosition(Hk3W03FxMotion.matrix(part,137,new Matrix4f())).distance(center)<.001,"晶体中心漂移");
            }
        }
        int count=0;
        try(var f=new DataInputStream(new GZIPInputStream(Files.newInputStream(root.resolve("w03_c9.bin.gz"))))) {
            check(f.readInt()==0x57303346&&f.readInt()==1&&f.readInt()==33,"C9资源头错误");
            for(int i=0;i<33;i++){int n=f.readInt();check(n>0,"丢失运动或静态组");count+=n;f.skipNBytes(n*10L);}
            check(f.read()==-1&&count==517262,"C9完整合并面丢失或增加");
        }
        System.out.println("W03 C9原生矩阵、五环法向、360秒周期、晶体枢轴及517262面核验通过");
    }
    private static void check(boolean value,String text){if(!value)throw new AssertionError(text);}
}
