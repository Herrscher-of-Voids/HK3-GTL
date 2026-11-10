package com.sirin.hk3gtl.common.research;

/** 【变更记录 #3】2026-10-01 00:17:25（修订122）：删除无；新增/修改：用long补存并行物品实际数量，避免NBT字节Count溢出造成公开数量失真；用途：五方首信与团队限定交流保持一致。 */



import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import net.minecraft.nbt.*;
import java.util.UUID;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：最终执行配方的完整物品/流体收支快照，含废物与回流。
 * 修改：只在实际输出成功后进入研究账本；用途：OPR复核已结算生产，不再次扣料。
 * 输入记录是最终配方消耗规范，标签保留候选集合；不冒称逐槽实际NBT提取记录。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：保留最终配方收支规格、批次身份与来源；不声称其记录了每个实际抽取槽的NBT。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3ProcessReceipts {
    private Hk3ProcessReceipts() {}
    public static final String RECEIPTS = "hk3gtlProcessReceipts";
    public static String category(GTRecipe recipe) {
        String id = recipe.id.getPath();
        if (!id.startsWith("industrial_medium_regeneration/")) return "";
        if (id.endsWith("/industrial_stabilization_medium_recovery")) return "medium";
        if (id.endsWith("/industrial_heat_exchange")) return "heat";
        if (id.endsWith("/industrial_spent_rod_reprocessing")) return "spent_rods";
        return "";
    }
    public static CompoundTag snapshot(GTRecipe recipe) {
        var result = new CompoundTag();
        result.putString("Category", category(recipe)); result.putString("Recipe", recipe.id.toString());
        result.put("Inputs", contents(recipe, true)); result.put("Outputs", contents(recipe, false));
        return result;
    }
    public static CompoundTag settle(CompoundTag source, String facility, long tick) {
        var result = source.copy(); result.putString("Facility", facility); result.putLong("Tick", tick);
        result.putUUID("Batch", UUID.nameUUIDFromBytes((facility + "/" + tick + "/" + source.getString("Recipe"))
                .getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        return result;
    }
    private static CompoundTag contents(GTRecipe recipe, boolean input) {
        var result = new CompoundTag(); var items = new ListTag(); var fluids = new ListTag();
        var ic = ItemRecipeCapability.CAP; var fc = FluidRecipeCapability.CAP;
        for (var entry : input ? recipe.getInputContents(ic) : recipe.getOutputContents(ic)) {
            if (entry.chance <= 0) continue;
            var alternatives = new ListTag();
            for (var stack : ic.of(entry.content).getItems()) {var item=stack.save(new CompoundTag());item.putLong("ActualCount",stack.getCount());alternatives.add(item);}
            var line = new CompoundTag(); line.put("Alternatives", alternatives); line.putFloat("Chance", entry.chance);
            items.add(line);
        }
        for (var entry : input ? recipe.getInputContents(fc) : recipe.getOutputContents(fc)) {
            if (entry.chance <= 0) continue;
            var stack = fc.of(entry.content); var line = new CompoundTag();
            var alternatives=new ListTag();
            for(var fluid:stack.getStacks())alternatives.add(StringTag.valueOf(net.minecraft.core.registries.BuiltInRegistries.FLUID.getKey(fluid.getFluid()).toString()));
            line.put("Alternatives",alternatives);
            line.putLong("Amount", stack.getAmount()); line.putFloat("Chance", entry.chance); fluids.add(line);
        }
        if (!items.isEmpty()) result.put("Items", items);
        if (!fluids.isEmpty()) result.put("Fluids", fluids);
        return result;
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
