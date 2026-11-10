package com.sirin.hk3gtl.common.farview;

import java.util.ArrayList;
import java.util.List;

/** 按实际一格尺寸合并相邻同材表面；负材质代表不能遮挡不同材质的玻璃等立方体。 */
public final class Hk3FarMesh {
    public static final int CELL=1,SIDE=16,TILE=SIDE,COUNT=SIDE*SIDE*SIDE;
    public record Quad(int axis,int sign,int plane,int u,int v,int width,int height,int color) {}
    private Hk3FarMesh() {}
    public static int index(int x,int y,int z){return (x*SIDE+y)*SIDE+z;}
    public static List<Quad> bake(int[] colors) {
        return bake(colors,new int[6][SIDE*SIDE]);
    }
    public static List<Quad> bake(int[] colors,int[][] boundaries) {
        if(colors.length!=COUNT)throw new IllegalArgumentException("远景网格尺寸错误");
        if(boundaries.length!=6)throw new IllegalArgumentException("远景邻接面数量错误");
        for(int[] face:boundaries)if(face.length!=SIDE*SIDE)throw new IllegalArgumentException("远景邻接面尺寸错误");
        List<Quad> result=new ArrayList<>();int[] mask=new int[SIDE*SIDE];
        for(int axis=0;axis<3;axis++)for(int sign:new int[]{-1,1})for(int plane=0;plane<=SIDE;plane++) {
            for(int u=0;u<SIDE;u++)for(int v=0;v<SIDE;v++) {
                int here=plane-(sign>0?1:0),other=here+sign;
                int color=at(colors,axis,here,u,v);
                int neighbor=other<0?boundaries[axis*2][u*SIDE+v]:other>=SIDE?boundaries[axis*2+1][u*SIDE+v]:at(colors,axis,other,u,v);
                mask[u*SIDE+v]=color!=0&&(neighbor==0||neighbor<0&&neighbor!=color)?color:0;
            }
            for(int u=0;u<SIDE;u++)for(int v=0;v<SIDE;v++) {
                int color=mask[u*SIDE+v];if(color==0)continue;
                int w=1,h=1;
                while(u+w<SIDE&&mask[(u+w)*SIDE+v]==color)w++;
                outer:while(v+h<SIDE) {
                    for(int a=0;a<w;a++)if(mask[(u+a)*SIDE+v+h]!=color)break outer;
                    h++;
                }
                result.add(new Quad(axis,sign,plane,u,v,w,h,color));
                for(int a=0;a<w;a++)for(int b=0;b<h;b++)mask[(u+a)*SIDE+v+b]=0;
            }
        }
        return result;
    }
    private static int at(int[] cells,int axis,int p,int u,int v) {
        if(p<0||p>=SIDE)return 0;
        return cells[switch(axis){case 0->index(p,u,v);case 1->index(v,p,u);default->index(u,v,p);}];
    }
}
