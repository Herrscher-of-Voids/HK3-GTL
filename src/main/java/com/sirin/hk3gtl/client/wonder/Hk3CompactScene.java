package com.sirin.hk3gtl.client.wonder;

import com.google.gson.GsonBuilder;
import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;
import com.sirin.hk3gtl.common.util.Hk3PackedResources;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import java.io.DataInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

final class Hk3CompactScene {
    private final DataInputStream input;

    private Hk3CompactScene(DataInputStream input){this.input=input;}

    static synchronized <T> T load(String resource,Class<T> type){
        var resources=Minecraft.getInstance().getResourceManager();
        String path="models/scene/"+resource+".scene.bin.gz";
        var gzip=resources.getResource(new ResourceLocation("hk3gtl",path));
        try(var raw=gzip.isPresent()?gzip.get().open():resources.open(new ResourceLocation("hk3gtl",Hk3PackedResources.xzPath(path)));
            var input=new DataInputStream(Hk3PackedResources.decompress(raw))){
            if(input.readInt()!=0x484B5343||input.readInt()!=1)throw new IOException("场景数据格式错误");
            String header=new String(input.readNBytes(input.readInt()),StandardCharsets.UTF_8);
            var scene=new Hk3CompactScene(input);
            var gson=new GsonBuilder()
                    .registerTypeAdapter(int[][][].class,new TypeAdapter<int[][][]>(){
                        @Override public int[][][] read(JsonReader reader)throws IOException{
                            reader.skipValue();return scene.cube();
                        }
                        @Override public void write(JsonWriter writer,int[][][] value){throw new UnsupportedOperationException();}
                    })
                    .registerTypeAdapter(int[][].class,new TypeAdapter<int[][]>(){
                        @Override public int[][] read(JsonReader reader)throws IOException{
                            reader.skipValue();return scene.rectangles();
                        }
                        @Override public void write(JsonWriter writer,int[][] value){throw new UnsupportedOperationException();}
                    }).create();
            return gson.fromJson(header,type);
        }catch(IOException failure){throw new IllegalStateException(resource+"场景资源读取失败",failure);}
    }

    private int unsigned()throws IOException{
        int value=0,shift=0,next;
        do{next=input.readUnsignedByte();value|=(next&127)<<shift;shift+=7;}while((next&128)!=0);
        return value;
    }

    private int delta()throws IOException{
        int value=unsigned();return (value>>>1)^-(value&1);
    }

    private int[][][] cube()throws IOException{
        int[][][] result=new int[unsigned()][][];
        for(int material=0;material<result.length;material++){
            int[][] faces=new int[unsigned()][];result[material]=faces;
            for(int face=0;face<faces.length;face++){
                int[] values=new int[unsigned()];faces[face]=values;int previous=0;
                for(int at=0;at<values.length;at++){previous+=delta();values[at]=previous;}
            }
        }
        return result;
    }

    private int[][] rectangles()throws IOException{
        int rows=unsigned(),columns=unsigned();int[][] result=new int[rows][columns];
        int[] previous=new int[columns];
        for(int[] row:result)for(int column=0;column<columns;column++){
            previous[column]+=delta();row[column]=previous[column];
        }
        return result;
    }
}
