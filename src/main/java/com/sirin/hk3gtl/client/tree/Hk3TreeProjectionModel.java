package com.sirin.hk3gtl.client.tree;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.GZIPInputStream;

/** 读取已确认树影的有限曲线与采样；不构造世界方块或浏览器运行环境。 */
public record Hk3TreeProjectionModel(float[] positions,float[] colors,float[] points,Flow[] flows){
    public record Flow(float offset,float speed,float size,float seed,float[] samples){}
    public static Hk3TreeProjectionModel read(InputStream raw)throws IOException{
        try(var in=new DataInputStream(new GZIPInputStream(raw))){
            if(in.readInt()!=0x49333454||in.readInt()!=1)throw new IOException("I34树影格式错误");
            int vertices=count(in,71948),pointCount;
            float[] positions=floats(in,vertices*3),colors=floats(in,vertices*3);
            pointCount=count(in,15567);float[] points=floats(in,pointCount*6);
            int flowCount=count(in,720);if(in.readInt()!=65)throw new IOException("I34树影采样数错误");
            Flow[] flows=new Flow[flowCount];for(int i=0;i<flowCount;i++){var p=floats(in,4);flows[i]=new Flow(p[0],p[1],p[2],p[3],floats(in,65*3));}
            if(in.read()!=-1)throw new IOException("I34树影有尾随数据");
            return new Hk3TreeProjectionModel(positions,colors,points,flows);
        }
    }
    private static int count(DataInputStream in,int expected)throws IOException{int n=in.readInt();if(n!=expected)throw new IOException("I34树影数量与确认版不符");return n;}
    private static float[] floats(DataInputStream in,int n)throws IOException{float[] a=new float[n];for(int i=0;i<n;i++){a[i]=in.readFloat();if(!Float.isFinite(a[i]))throw new IOException("I34树影出现非有限数");}return a;}
}
