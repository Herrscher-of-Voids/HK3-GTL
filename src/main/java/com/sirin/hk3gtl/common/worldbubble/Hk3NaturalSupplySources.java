package com.sirin.hk3gtl.common.worldbubble;

import com.google.gson.JsonParser;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public final class Hk3NaturalSupplySources {
    private Hk3NaturalSupplySources() {}

    public static Hk3WorldResourceCatalog load() {
        try (var reader = new InputStreamReader(Hk3NaturalSupplySources.class.getResourceAsStream(
                "/data/hk3gtl/catalog/world_bubble_resources.json"), StandardCharsets.UTF_8)) {
            var data = JsonParser.parseReader(reader).getAsJsonObject();
            var items = new ArrayList<Hk3WorldResourceCatalog.Entry>();
            var fluids = new ArrayList<Hk3WorldResourceCatalog.Entry>();
            for (String group : new String[]{"roots", "processed"}) {
                for (var raw : data.getAsJsonArray(group)) {
                    var row = raw.getAsJsonObject();
                    var entry = new Hk3WorldResourceCatalog.Entry(row.get("id").getAsString(),
                            row.get("tier").getAsInt(), row.get("source").getAsString(), row.get("amount").getAsInt(),
                            row.has("stack_data") ? TagParser.parseTag(row.get("stack_data").getAsString()) : new CompoundTag());
                    (row.get("kind").getAsString().equals("item") ? items : fluids).add(entry);
                }
            }
            var sampling=data.getAsJsonObject("sampling");
            return new Hk3WorldResourceCatalog(data.get("profile").getAsString(),
                    data.get("version").getAsString(), items, fluids,
                    new Hk3WorldResourceCatalog.Sampling(sampling.get("itemKinds").getAsInt(),
                            sampling.get("itemMax").getAsInt(),sampling.get("fluidKinds").getAsInt(),
                            sampling.get("fluidMaxBuckets").getAsInt()));
        } catch (IOException | CommandSyntaxException e) {
            throw new IllegalStateException("读取世界泡资源目录失败", e);
        }
    }
}
