package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.recipe.ingredient.IntCircuitIngredient;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialDependencyAudit;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialAuditReport;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.fml.loading.FMLPaths;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import com.mojang.logging.LogUtils;
import java.util.*;

 






 






@Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3LiquidLineAudit {
    private Hk3LiquidLineAudit() {}
    public static final Map<String,String> DEVICES=Map.ofEntries(
        Map.entry("industrial_honkai_collection","i01_honkai_collection_tower"),
        Map.entry("industrial_honkai_spectrum_analysis","i02_spectrum_analysis_array"),
        Map.entry("industrial_liquid_honkai_refining","liquid_honkai_fractionation_center"),
        Map.entry("industrial_honkai_stabilization","liquid_honkai_stabilization_tower"),
        Map.entry("industrial_medium_regeneration","stabilization_medium_regeneration_tower"),
        Map.entry("industrial_fuel_blending","honkai_fuel_blending_plant"),
        Map.entry("industrial_detector_calibration","honkai_detector_calibration_bench"),
        Map.entry("industrial_fuel_concentration","honkai_fuel_concentration_plant"),
        Map.entry("industrial_honkai_network_injection","honkai_network_injector"));

    /** 服务端配方及标签均加载后检查，任何问题明确记为失败而非继续打印通过。 */
    @SubscribeEvent public static void started(ServerStartedEvent event) {
        try { export(event.getServer()); }
        catch(Exception error) { LogUtils.getLogger().error("[HK3-LIQUID66-AUDIT] FAIL",error); }
    }

    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("hk3industrialaudit").requires(s -> s.hasPermission(2))
                .executes(context -> {
                    try {
                        var snapshot = export(context.getSource().getServer());
                        long reachable = snapshot.productionRecipes().stream().filter(snapshot.result().finishedRecipes()::contains).count();
                        context.getSource().sendSuccess(() -> Component.literal("工业材料支付路径核验：生产配方拓扑可达 "
                                + reachable + "/" + snapshot.productionRecipes().size() + "；报告：logs/hk3gtl-industrial-audit/工业依赖核验_最新.html；不代表实机验收"), false);
                        return 1;
                    } catch (Exception error) {
                        LogUtils.getLogger().error("[HK3-INDUSTRIAL-AUDIT] 导出失败", error);
                        context.getSource().sendFailure(Component.literal("工业依赖核验未完成，请查看日志"));
                        return 0;
                    }
                }));
    }

    /** 原液态实机夹具的前置核验只检查相关子集，仍不授予研究或物品。 */
    public static void audit(MinecraftServer server) {
        var snapshot = export(server);
        var blocked = snapshot.result().blockedRecipes().keySet().stream().filter(Hk3LiquidLineAudit::liquidFixtureRecipe).toList();
        require(blocked.isEmpty(), "液态验收子集仍有" + blocked.size() + "项拓扑阻断，详见工业依赖HTML；未自动授予研究");
        require(snapshot.result().state().research().containsAll(List.of("RN-HED","RN-HSA","RN-LSE","RN-LES","RN-BCE","RN-DMT","RN-SMR","RN-HFB")),"液态研究入口不完整，详见工业依赖HTML");
    }

    /** 全系统导出保留失败细节；未适配事件或阻断也生成报告，不把它们写成启动崩溃。 */
    public static Hk3IndustrialDependencyAudit.Snapshot export(MinecraftServer server) {
        for(String material:Hk3LiquidLineLayout.MATERIALS.values())Hk3StructureBlocks.require(material);
        for(String material:Hk3LiquidLineLayout.create(Hk3LiquidLineLayout.Kind.INJECTION).materials().values())Hk3StructureBlocks.require(material);
        for(String device:DEVICES.values())Hk3StructureBlocks.require("hk3gtl:"+device);
        var snapshot = Hk3IndustrialDependencyAudit.inspect(server);
        try {
            var path = Hk3IndustrialAuditReport.write(snapshot, FMLPaths.GAMEDIR.get().resolve("logs/hk3gtl-industrial-audit"));
            long reachable = snapshot.productionRecipes().stream().filter(snapshot.result().finishedRecipes()::contains).count();
            LogUtils.getLogger().info("[HK3-INDUSTRIAL-AUDIT] 材料路径拓扑可达 {}/{}，研究 {}，未核验视图/格式问题 {}，报告 {}；未执行生存实机验收",
                    reachable, snapshot.productionRecipes().size(), snapshot.result().state().research().size(), snapshot.unresolvedViews().size(), path);
            return snapshot;
        } catch (java.io.IOException error) { throw new IllegalStateException("工业依赖HTML报告未能写入", error); }
    }

    private static boolean liquidFixtureRecipe(String id) {
        return DEVICES.keySet().stream().anyMatch(type -> id.contains(":" + type + "/"))
                || id.endsWith("/i01_collection_controller") || id.endsWith("/i02_spectrum_controller")
                || id.endsWith("/hk3gtl_honkai_network_injector") || id.endsWith("/stabilized_crystal") || id.endsWith("/compressed_honkai_core");
    }
    /** 空标签、无效数量与超出配方类型接口上限均属于错误；由依赖适配器在建图前统一校验。 */
    private static void require(boolean valid,String message) { if(!valid)throw new IllegalStateException(message); }
}

 

 
