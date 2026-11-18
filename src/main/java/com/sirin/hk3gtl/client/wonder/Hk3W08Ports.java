package com.sirin.hk3gtl.client.wonder;

import net.minecraft.client.renderer.texture.DynamicTexture;

public final class Hk3W08Ports implements AutoCloseable {
    private final DynamicTexture texture;
    private final int count;

    public Hk3W08Ports(int[] sortedLinearIds) {
        count=sortedLinearIds.length;
        texture=new DynamicTexture(1024,Math.max(1,(count+1023)/1024),false);
        var image=texture.getPixels();
        // NativeImage按ABGR整数存储，ID直接映射为RGBA四字节。
        for(int i=0;i<count;i++)image.setPixelRGBA(i%1024,i/1024,sortedLinearIds[i]);
        texture.upload();
        texture.setFilter(false,false);
    }

    public int textureId(){return texture.getId();}
    public int count(){return count;}
    @Override public void close(){texture.close();}
}
