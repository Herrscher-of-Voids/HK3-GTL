package com.sirin.hk3gtl.common.easter;

public final class Hk3EggFloorPattern {
    private Hk3EggFloorPattern(){}
    public static boolean contains(boolean[][] cells,int width,int height){
        if(width<=0||height<=0||cells.length<width)return false;int rows=cells.length,cols=cells[0].length;if(cols<height)return false;
        int[][] sum=new int[rows+1][cols+1];for(int x=0;x<rows;x++){if(cells[x].length!=cols)throw new IllegalArgumentException("非矩形布局");for(int z=0;z<cols;z++)sum[x+1][z+1]=(cells[x][z]?1:0)+sum[x][z+1]+sum[x+1][z]-sum[x][z];}
        for(int x=0;x+width<=rows;x++)for(int z=0;z+height<=cols;z++)if(sum[x+width][z+height]-sum[x][z+height]-sum[x+width][z]+sum[x][z]==width*height)return true;return false;
    }
}
