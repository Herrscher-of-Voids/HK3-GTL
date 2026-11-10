package com.sirin.hk3gtl.client.wonder;

import com.google.gson.Gson;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.zip.GZIPInputStream;

/** C9只保存外露合并面，不展开441百万格空气；数据缺失时拒绝显示替代模型。 */
public record Hk3W03FxModel(Metadata metadata,byte[][] groups) {
    public record Rotation(float[] axis,float degrees_per_second) {}
    public record Part(String id,float[] pivot_export,float[] render_translation_xyz,Rotation[] rotations) {}
    public record Metadata(int version,int[] controller,int[] size,Part[] components,int quads,int blocks,int cycle_seconds) {}
    public static Hk3W03FxModel load() {
        var resources=Minecraft.getInstance().getResourceManager();
        try(var text=resources.open(new ResourceLocation("hk3gtl","models/scene/w03_c9.json"));
            var reader=new InputStreamReader(text,StandardCharsets.UTF_8);
            var input=new DataInputStream(new GZIPInputStream(resources.open(new ResourceLocation("hk3gtl","models/scene/w03_c9.bin.gz"))))) {
            var meta=new Gson().fromJson(reader,Metadata.class);
            if(meta.version!=1||meta.components.length!=33||meta.quads!=517262||meta.blocks!=6642464
                    ||meta.cycle_seconds!=360||meta.controller.length!=3)throw new IOException("C9身份或运动组不符");
            if(input.readInt()!=0x57303346||input.readInt()!=1||input.readInt()!=33)throw new IOException("C9网格头错误");
            var groups=new byte[33][];int total=0;
            for(int i=0;i<groups.length;i++) {
                int count=input.readInt();if(count<1||count>meta.quads-total)throw new IOException("C9面片数越界");
                groups[i]=input.readNBytes(Math.multiplyExact(count,10));
                if(groups[i].length!=count*10)throw new IOException("C9网格截断");
                var data=new DataInputStream(new ByteArrayInputStream(groups[i]));
                for(int n=0;n<count;n++) {
                    int x=data.readUnsignedShort(),y=data.readUnsignedShort(),z=data.readUnsignedShort(),length=data.readUnsignedShort();
                    int slot=data.readUnsignedByte(),face=data.readUnsignedByte();
                    if(x>=meta.size[0]||y>=meta.size[1]||z>=meta.size[2]||length<1||length>=2048||slot>=84||face>=6||slot%6!=face)
                        throw new IOException("C9面片坐标、纹理或朝向错误");
                }
                total+=count;
            }
            if(total!=meta.quads||input.read()!=-1)throw new IOException("C9网格数量或尾随数据错误");
            groups[0]=withoutPorts(groups[0]);
            return new Hk3W03FxModel(meta,groups);
        }catch(IOException|RuntimeException failure){throw new IllegalStateException("C9原生特效资源加载失败",failure);}
    }
    /** 主控和舱位由真实GT模型显示；合并面遇到这些格时切开，避免覆盖GUI入口。 */
    private static byte[] withoutPorts(byte[] source)throws IOException{
        var bytes=new ByteArrayOutputStream();var out=new DataOutputStream(bytes);
        var input=new DataInputStream(new ByteArrayInputStream(source));
        int[] holes={398,402,406,410,416,422,426,430,434};
        while(input.available()>0){
            int x=input.readUnsignedShort(),y=input.readUnsignedShort(),z=input.readUnsignedShort(),n=input.readUnsignedShort(),slot=input.readUnsignedByte(),face=input.readUnsignedByte();
            int start=face<2?z:x,end=start+n,segment=start;
            for(int at=start;at<end;at++){
                int px=face<2?x:at,pz=face<2?at:z;
                boolean hole=y==27&&pz==187&&java.util.Arrays.binarySearch(holes,px)>=0;
                if(hole){if(at>segment)face(out,face<2?x:segment,y,face<2?segment:z,at-segment,slot,face);segment=at+1;}
            }
            if(segment<end)face(out,face<2?x:segment,y,face<2?segment:z,end-segment,slot,face);
        }return bytes.toByteArray();
    }
    private static void face(DataOutputStream out,int x,int y,int z,int n,int slot,int face)throws IOException{
        out.writeShort(x);out.writeShort(y);out.writeShort(z);out.writeShort(n);out.writeByte(slot);out.writeByte(face);
    }
}
