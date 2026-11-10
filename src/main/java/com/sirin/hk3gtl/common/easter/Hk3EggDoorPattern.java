package com.sirin.hk3gtl.common.easter;
import java.util.*;
/** 【变更记录 #1】2026-10-01 05:44:13（修订128）：删除无；新增固定33格邻域的四向门三维范围检查；修改无；用途：验证存在同一16格跨度内四种方向，避免以最后一扇门为中心误缩到半径8。 */
public final class Hk3EggDoorPattern {
    public record Door(int x,int y,int z,int direction){}
    private static final int N=34;
    private Hk3EggDoorPattern(){}
    private static int at(int x,int y,int z){return (x*N+y)*N+z;}
    public static boolean matches(List<Door> doors){
        int mask=0;for(var d:doors)if(Math.abs(d.x)<=16&&Math.abs(d.y)<=16&&Math.abs(d.z)<=16&&d.direction>=0&&d.direction<4)mask|=1<<d.direction;if(mask!=15)return false;
        int[][] sums=new int[4][N*N*N];
        for(var d:doors)if(Math.abs(d.x)<=16&&Math.abs(d.y)<=16&&Math.abs(d.z)<=16&&d.direction>=0&&d.direction<4)sums[d.direction][at(d.x+17,d.y+17,d.z+17)]=1;
        for(var sum:sums)for(int x=1;x<N;x++)for(int y=1;y<N;y++)for(int z=1;z<N;z++)sum[at(x,y,z)]+=sum[at(x-1,y,z)]+sum[at(x,y-1,z)]+sum[at(x,y,z-1)]-sum[at(x-1,y-1,z)]-sum[at(x-1,y,z-1)]-sum[at(x,y-1,z-1)]+sum[at(x-1,y-1,z-1)];
        for(int x=0;x<=16;x++)for(int y=0;y<=16;y++)for(int z=0;z<=16;z++){
            boolean all=true;for(var s:sums){int a=x+17,b=y+17,c=z+17;int count=s[at(a,b,c)]-s[at(x,b,c)]-s[at(a,y,c)]-s[at(a,b,z)]+s[at(x,y,c)]+s[at(x,b,z)]+s[at(a,y,z)]-s[at(x,y,z)];if(count==0){all=false;break;}}
            if(all)return true;
        }return false;
    }
}
