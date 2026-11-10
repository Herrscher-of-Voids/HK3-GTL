package com.sirin.hk3gtl.common.easter;
/** 【变更记录 #1】2026-10-01 05:41:36（修订128）：删除无；新增普通地板前缀和校验，检查完整矩形而非仅数方块；修改无；用途：只读当前已加载建筑，不生成结构或授予工程验收。 */
public final class Hk3EggFloorPattern {
    private Hk3EggFloorPattern(){}
    public static boolean contains(boolean[][] cells,int width,int height){
        if(width<=0||height<=0||cells.length<width)return false;int rows=cells.length,cols=cells[0].length;if(cols<height)return false;
        int[][] sum=new int[rows+1][cols+1];for(int x=0;x<rows;x++){if(cells[x].length!=cols)throw new IllegalArgumentException("非矩形布局");for(int z=0;z<cols;z++)sum[x+1][z+1]=(cells[x][z]?1:0)+sum[x][z+1]+sum[x+1][z]-sum[x][z];}
        for(int x=0;x+width<=rows;x++)for(int z=0;z+height<=cols;z++)if(sum[x+width][z+height]-sum[x][z+height]-sum[x+width][z]+sum[x][z]==width*height)return true;return false;
    }
}
