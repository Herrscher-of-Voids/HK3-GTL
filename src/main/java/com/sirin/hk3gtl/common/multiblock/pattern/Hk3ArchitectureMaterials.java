package com.sirin.hk3gtl.common.multiblock.pattern;

import com.google.gson.stream.JsonReader;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;




public final class Hk3ArchitectureMaterials {
    private Hk3ArchitectureMaterials() {}

    public static Set<String> states(String layout) {
        var stream=Hk3ArchitectureMaterials.class.getResourceAsStream(
                "/data/hk3gtl/compact_architecture/"+layout+".json");
        if(stream==null)throw new IllegalStateException("缺少轻量建筑材料元数据："+layout);
        try(var reader=new JsonReader(new InputStreamReader(stream,StandardCharsets.UTF_8))) {
            Set<String> states=new HashSet<>();
            boolean found=false;
            reader.beginObject();
            while(reader.hasNext()) {
                if(!reader.nextName().equals("material_counts")) { reader.skipValue(); continue; }
                found=true;
                reader.beginObject();
                while(reader.hasNext()) {
                    String state=reader.nextName();
                    if(reader.nextLong()>0)states.add(state);
                }
                reader.endObject();
            }
            reader.endObject();
            if(!found)throw new IllegalStateException("缺少轻量建筑材料清单："+layout);
            return Set.copyOf(states);
        }catch(IOException failure) {
            throw new IllegalStateException("读取轻量建筑材料失败："+layout,failure);
        }
    }
}
