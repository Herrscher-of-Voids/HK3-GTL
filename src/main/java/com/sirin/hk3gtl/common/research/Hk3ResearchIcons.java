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

/**
 * 【变更记录 #1】2026-09-26 21:56:00（第 1 次备注 · 内测5修订75）
 * 删除：无。新增：100课题到研究成果物品的只读目录。
 * 修改：研究所从此目录读取图标，不再从费用列表推断课题成果。
 * 用途：物品在注册完成后解析；缺失图标回退知识书，目录缺失或重复立即报错。
 */
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
