package com.sirin.hk3gtl.client.wonder;

import net.minecraft.client.renderer.texture.DynamicTexture;
import java.util.Arrays;

final class Hk3W11Ports implements AutoCloseable{
    private final DynamicTexture texture;
    private final int count;
    Hk3W11Ports(int[] xyz){
        count=xyz.length/3;
        long[] sorted=new long[count];
        for(int i=0;i<count;i++)sorted[i]=((long)xyz[i*3]<<24)|((long)xyz[i*3+1]<<12)|xyz[i*3+2];
        Arrays.sort(sorted);
        texture=new DynamicTexture(1024,Math.max(1,(count*2+1023)/1024),false);
        var pixels=texture.getPixels();
        for(int i=0;i<count;i++){
            int x=(int)(sorted[i]>>>24),y=(int)(sorted[i]>>>12)&4095,z=(int)sorted[i]&4095,at=i*2;
            pixels.setPixelRGBA(at%1024,at/1024,x|(y<<16));
            pixels.setPixelRGBA((at+1)%1024,(at+1)/1024,z);
        }
        texture.upload();texture.setFilter(false,false);
    }
    int textureId(){return texture.getId();}
    int count(){return count;}
    @Override public void close(){texture.close();}
}
