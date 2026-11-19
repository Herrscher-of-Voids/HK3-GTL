package com.sirin.hk3gtl.client.wonder;

import com.sirin.hk3gtl.common.util.Hk3PackedResources;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.UncheckedIOException;

final class Hk3W15FxGeometry {
    record Lines(float[] positions,int[] colors) {}
    record Dots(float[] values) {}
    record Path(boolean inward,float[] positions) {}
    record Flow(int path,float phase,float speed,float size,float seed) {}
    record World(float x,float y,float z,float phase,Lines lines) {}
    record Glyph(float phase,float angle,float radius,float speed,float size,float seed) {}
    final Lines branches,diamonds,spirals,waves;
    final Dots dust,nodes,leaves;
    final Path[] paths;
    final Flow[] flows;
    final World[] worlds;
    final Glyph[] glyphs;

    private Hk3W15FxGeometry(DataInputStream input) throws IOException {
        if(input.readInt()!=0x57313546)throw new IOException("W15树海特效格式错误");
        branches=lines(input);diamonds=lines(input);spirals=lines(input);waves=lines(input);
        dust=dots(input);nodes=dots(input);leaves=dots(input);
        paths=new Path[input.readInt()];
        for(int i=0;i<paths.length;i++)paths[i]=new Path(input.readInt()==1,floats(input,195));
        flows=new Flow[input.readInt()];
        for(int i=0;i<flows.length;i++)flows[i]=new Flow(input.readInt(),input.readFloat(),input.readFloat(),input.readFloat(),input.readFloat());
        worlds=new World[input.readInt()];
        for(int i=0;i<worlds.length;i++)worlds[i]=new World(input.readFloat(),input.readFloat(),input.readFloat(),input.readFloat(),lines(input));
        glyphs=new Glyph[input.readInt()];
        for(int i=0;i<glyphs.length;i++)glyphs[i]=new Glyph(input.readFloat(),input.readFloat(),input.readFloat(),input.readFloat(),input.readFloat(),input.readFloat());
    }
    static Hk3W15FxGeometry load() {
        try(var raw=Hk3PackedResources.resource(Hk3W15FxGeometry.class,"/assets/hk3gtl/wonder/w15_book_fx.bin.gz");
            var input=new DataInputStream(Hk3PackedResources.decompress(raw))) {
            return new Hk3W15FxGeometry(input);
        } catch(IOException failure) {
            throw new UncheckedIOException("W15树海特效加载失败",failure);
        }
    }
    private static Lines lines(DataInputStream input) throws IOException {
        int count=input.readInt();float[] positions=new float[count*3];int[] colors=new int[count];
        for(int i=0;i<count;i++) {
            positions[i*3]=input.readFloat();positions[i*3+1]=input.readFloat();positions[i*3+2]=input.readFloat();colors[i]=input.readInt();
        }
        return new Lines(positions,colors);
    }
    private static Dots dots(DataInputStream input) throws IOException {return new Dots(floats(input,input.readInt()*5));}
    private static float[] floats(DataInputStream input,int count) throws IOException {
        float[] values=new float[count];for(int i=0;i<count;i++)values[i]=input.readFloat();return values;
    }
}
