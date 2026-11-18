package com.sirin.hk3gtl.common.research;

import com.google.gson.JsonParser;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

 





public final class Hk3ResearchIcons {
    private Hk3ResearchIcons() {}
    private static final class Holder { private static final Map<String,String> ICONS=load(); }
    private static Map<String,String> load() {
        try(var in=Hk3ResearchIcons.class.getResourceAsStream("/data/hk3gtl/research/research_icons.json")) {
            if(in==null) throw new IllegalStateException("缺少研究图标目录");
            var root=JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject();
            Map<String,String> icons=new LinkedHashMap<>();
            for(var entry:root.getAsJsonObject("icons").entrySet()) icons.put(entry.getKey(),entry.getValue().getAsString());
            if(!icons.keySet().equals(Hk3ResearchCatalog.bundled().topics().keySet()))
                throw new IllegalStateException("研究成果图标未完整覆盖课题");
            return Collections.unmodifiableMap(icons);
        } catch(Exception e) { throw new IllegalStateException("无法加载研究成果图标",e); }
    }
    public static ItemStack stack(String topic) {
        String id=Holder.ICONS.get(topic);
        if(id==null) return new ItemStack(Items.KNOWLEDGE_BOOK);
        var item=BuiltInRegistries.ITEM.get(new ResourceLocation(id));
        return new ItemStack(item==Items.AIR?Items.KNOWLEDGE_BOOK:item);
    }
}

 
