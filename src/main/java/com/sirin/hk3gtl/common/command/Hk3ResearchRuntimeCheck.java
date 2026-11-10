package com.sirin.hk3gtl.common.command;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.common.machine.multiblock.part.ItemBusPartMachine;
import com.gregtechceu.gtceu.common.machine.multiblock.part.FluidHatchPartMachine;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.item.IntCircuitBehaviour;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchComputerMachine;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLLoader;
import com.mojang.logging.LogUtils;
import java.util.UUID;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/**
 * 【变更记录 #1】2026-09-25 02:23:27（内测5修订70）
 * 删除：旧三格研究所夹具的执行入口。新增：指向新验收的提示。
 * 修改：历史实现留在私有归档方法，不再放置。用途：避免新大结构覆盖旧夹具场地。
 */
@Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ResearchRuntimeCheck {
    private static UUID playerId;
    private static int stage;
    private static long start, pausedAt;
    private static double pausedProgress;
    private static final BlockPos TOWER=new BlockPos(96,-58,64), LAB=new BlockPos(104,-58,64);
    private Hk3ResearchRuntimeCheck() {}

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public static int begin(ServerPlayer p) {
        // 修订70：旧夹具仅按3格研究所预留空间，不得再放置放大后的正式研究所。
        // 当前正式包只允许通过指定实例的新版结构／光谱验收入口启动，历史实现保留便于追溯。
        p.sendSystemMessage(Component.literal("旧研究夹具已归档，请在指定GTL实例的新作弊超平坦创造存档中使用新版结构验收。"));
        return 0;
    }

    /** 历史三格研究所夹具仅供追溯，不再由命令或正式测试入口调用。 */
    private static int beginLegacyArchived(ServerPlayer p) {
        if (FMLLoader.isProduction() || !p.isCreative() || playerId!=null
                || !p.server.getWorldData().getLevelName().contains("Registry-Smoke")) return 0;
        for (BlockPos pos:BlockPos.betweenClosed(92,-60,60,108,-54,68)) if (!p.level().isEmptyBlock(pos)) {
            p.sendSystemMessage(Component.literal("测试区域已有方块，未作改动。"));return 0;
        }
        if (p.getInventory().getFreeSlot()<0) return 0;
        place(p,TOWER,"honkai_absorption_tower"); place(p,LAB,"abyss_research_analysis_matrix");
        // 中文备注：该处说明已按当前代码行为整理。
        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        int port=0;
        for (BlockPos pos:BlockPos.betweenClosed(TOWER.offset(-2,-1,-3),TOWER.offset(2,1,3))) {
            if (!p.level().getBlockState(pos).is(com.sirin.hk3gtl.common.block.CasingBlocks.CASING_ABYSS_ENERGY.get())) continue;
            var block=(port==0 ? com.gregtechceu.gtceu.common.data.GTMachines.ITEM_IMPORT_BUS[1]
                    : com.gregtechceu.gtceu.common.data.GTMachines.FLUID_EXPORT_HATCH[1]).getBlock();
            p.serverLevel().setBlockAndUpdate(pos,block.defaultBlockState());
            if (++port==2) break;
        }
        check(port==2,"两个真实外壳仓室已安装");
        p.teleportTo(p.serverLevel(),104.5,-58,61.5,0,0);
        playerId=p.getUUID();stage=0;start=p.server.overworld().getGameTime();
        p.sendSystemMessage(Component.literal("研究运行测试已启动；使用真实游戏刻，不授予实验凭据或知识。")); return 1;
    }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static void place(ServerPlayer p,BlockPos pos,String id) {
        var block=BuiltInRegistries.BLOCK.get(new ResourceLocation("hk3gtl",id));
        p.serverLevel().setBlockAndUpdate(pos,block.defaultBlockState());
        var m=(MultiblockControllerMachine)MetaMachine.getMachine(p.level(),pos);
        ((com.gregtechceu.gtceu.api.machine.feature.IMachineLife)m).onMachinePlaced(p,new ItemStack(block));
        m.getPattern().autoBuild(p,m.getMultiblockState());
    }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @SubscribeEvent public static void stopped(ServerStoppedEvent event) { playerId=null; }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase!=TickEvent.Phase.END || playerId==null || FMLLoader.isProduction()) return;
        var server=event.getServer();var p=server.getPlayerList().getPlayer(playerId); if (p==null) return;
        try {
            long tick=server.overworld().getGameTime();
            if (tick-start>4000) throw new IllegalStateException("阶段超时："+stage);
            var tower=(com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine)MetaMachine.getMachine(p.level(),TOWER);
            var lab=(Hk3ResearchInstituteMachine)MetaMachine.getMachine(p.level(),LAB);
            var data=Hk3ResearchData.get(p);
            if (stage==0) {
                if (!tower.isFormed() || !lab.isFormed()) return;
                check(!data.hasExperiment(playerId,"RN-HED"),"新账号状态");
                check(lab.requestResearch(p,"RN-HED",false)==Hk3ResearchStartService.Result.LOCKED,"缺少实验凭据时应拒绝开题");
                // 中文维护备注：历史说明已整理；当前实现以代码为准。
                // 中文备注：该处说明已按当前代码行为整理。
                var maxTag=net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM,new ResourceLocation("gtceu","circuits/max"));
                var maxCircuit=BuiltInRegistries.ITEM.getTag(maxTag).orElseThrow().iterator().next().value();
                check(p.getInventory().add(new ItemStack(maxCircuit)),"MAX入口电路可以放入背包");
                com.sirin.hk3gtl.common.communication.Hk3FirstContactService.checkInventory(p);
                check(Hk3CommunicationData.get(p).state(playerId).hasObservationData(),"已获得MAX阶段首信情报");
                var bus=tower.getParts().stream().filter(part -> part instanceof ItemBusPartMachine b && b.getInventory().getHandlerIO()==IO.IN)
                        .map(part -> (ItemBusPartMachine)part).findFirst().orElseThrow();
                bus.getInventory().setStackInSlot(0,IntCircuitBehaviour.stack(3));
                WirelessEnergyManager.addEUToGlobalEnergyMap(playerId,5_000_000_000_000L,lab);
                mark(p,"真实输入输出仓室已成型，缺少凭据时拒绝开题的检查通过"); pausedAt=tick;stage=10;
            } else if (stage==10) {
                var loaded=com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.COLLECTION.getRecipe(
                        p.server.getRecipeManager(), com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine.SAMPLING);
                check(loaded!=null,"sampling recipe is loaded under exact ID");
                mark(p,"sampling recipe loaded: "+loaded.id);
                if (tick-pausedAt<240) return;
                check(!data.hasExperiment(playerId,"RN-HED"),"no detector cannot grant evidence");
                var bus=tower.getParts().stream().filter(part -> part instanceof ItemBusPartMachine b && b.getInventory().getHandlerIO()==IO.IN)
                        .map(part -> (ItemBusPartMachine)part).findFirst().orElseThrow();
                check(bus.getInventory().getSlots()>=2,"two catalyst slots available");
                bus.getInventory().setStackInSlot(1,new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation("hk3gtl","prototype_honkai_detector"))));
                mark(p,"missing detector rejected; begin actual sampling");stage=11;
            } else if (stage==11) {
                if (tower.getRecipeLogic().getProgress()<80) return;
                check(com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine.SAMPLING.equals(tower.getRecipeLogic().getLastRecipe().id),"exact sampling recipe ID");
                tower.getRecipeLogic().interruptRecipe();
                check(!data.hasExperiment(playerId,"RN-HED"),"interrupted sample must not grant evidence");
                mark(p,"exact recipe and interruption without evidence passed");stage=1;
            } else if (stage==1) {
                if (!data.hasExperiment(playerId,"RN-HED")) return;
                check(!data.completed(playerId,"RN-HED"),"experiment not knowledge");
                var bus=tower.getParts().stream().filter(part -> part instanceof ItemBusPartMachine b && b.getInventory().getHandlerIO()==IO.IN)
                        .map(part -> (ItemBusPartMachine)part).findFirst().orElseThrow();
                check(bus.getInventory().getStackInSlot(0).getCount()==1 && bus.getInventory().getStackInSlot(1).getCount()==1,"both catalysts retained");
                tower.getRecipeLogic().setWorkingEnabled(false);
                check(tower.getParts().stream().anyMatch(part -> part instanceof FluidHatchPartMachine h && !h.tank.getFluidInTank(0).isEmpty()),"liquid produced");
                check(lab.requestResearch(p,"RN-HED",true)==Hk3ResearchStartService.Result.INSUFFICIENT,"empty points rejection");
                var tag=net.minecraft.tags.TagKey.create(net.minecraft.core.registries.Registries.ITEM,new ResourceLocation("gtceu","circuits/max"));
                var circuit=BuiltInRegistries.ITEM.getTag(tag).orElseThrow().iterator().next().value();
                p.getInventory().add(new ItemStack(circuit,2));
                p.getInventory().add(ChemicalHelper.get(TagPrefix.plate,GTMaterials.Steel,16));
                var result=lab.requestResearch(p,"RN-HED",false);
                check(result==Hk3ResearchStartService.Result.STARTED,"actual material start: "+result);
                var paid=data.researchJob(playerId,"RN-HED").quote().paid().getList("Items",10);
                int paidCount=0;for (int i=0;i<paid.size();i++) paidCount+=ItemStack.of(paid.getCompound(i)).getCount();
                check(paidCount==18,"receipt contains two circuits and sixteen plates");
                var inventory=p.getInventory().save(new net.minecraft.nbt.ListTag());
                check(lab.requestResearch(p,"RN-HED",false)==Hk3ResearchStartService.Result.RUNNING,"duplicate rejected");
                check(inventory.equals(p.getInventory().save(new net.minecraft.nbt.ListTag())),"duplicate did not debit inventory");
                mark(p,"actual liquid evidence and material payment passed"); stage=2;
            } else if (stage==2) {
                var job=data.researchJob(playerId,"RN-HED"); if (job==null || job.progress()<100) return;
                lab.getRecipeLogic().setWorkingEnabled(false);pausedProgress=job.progress();pausedAt=tick;stage=3;
            } else if (stage==3) {
                if (tick-pausedAt<60) return;
                check(data.researchJob(playerId,"RN-HED").progress()==pausedProgress,"pause retains progress");
                lab.getRecipeLogic().setWorkingEnabled(true); mark(p,"pause/resume passed");stage=4;
            } else if (stage==4 && data.completed(playerId,"RN-HED")) {
                check(data.researchJob(playerId,"RN-HED")==null,"settled once");
                check(lab.requestResearch(p,"RN-HED",false)==Hk3ResearchStartService.Result.COMPLETED,"completed cannot repay");
                mark(p,"PASS: actual sampling -> evidence -> materials -> powered research -> pause/resume -> completion");
                server.saveEverything(false,true,true);playerId=null;
            }
        } catch (Exception failure) {
            LogUtils.getLogger().error("[HK3-RESEARCH-RUNTIME] FAIL stage="+stage,failure);
            p.sendSystemMessage(Component.literal("RESEARCH RUNTIME FAIL: "+failure));playerId=null;
        }
    }
    private static void check(boolean ok,String message) { if (!ok) throw new IllegalStateException(message); }
    private static void mark(ServerPlayer p,String text) {
        LogUtils.getLogger().info("[HK3-RESEARCH-RUNTIME] {}",text);p.sendSystemMessage(Component.literal(text));
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
