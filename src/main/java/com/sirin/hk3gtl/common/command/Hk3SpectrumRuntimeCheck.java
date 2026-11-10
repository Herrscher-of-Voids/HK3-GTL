package com.sirin.hk3gtl.common.command;

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.SimpleTieredMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.common.data.GTMachines;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.item.IntCircuitBehaviour;
import com.gregtechceu.gtceu.common.machine.multiblock.part.ItemBusPartMachine;
import com.gregtechceu.gtceu.common.machine.multiblock.part.FluidHatchPartMachine;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.communication.Hk3FirstContactService;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3ResearchInstituteMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3SpectrumAnalysisMachine;
import com.sirin.hk3gtl.common.recipe.machine.Hk3SpectrumBootstrapRecipes;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchStartService;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Rotation;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/**
 * 【变更记录 #1】2026-09-25 02:19:54（内测5修订70）
 * 删除：旧建筑退出四机正式入口，历史文件已归档。
 * 新增：已确认逐格建筑及一致的模板与验收入口。
 * 修改：同步主控坐标、材料或测试夹具，不改配方和研究扣费。
 * 用途：使预览、正式结构及游戏放置相互对应；未将静态验证写作实机通过。
 */
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3SpectrumRuntimeCheck {
    private static UUID owner;
    private static int stage;
    private static long since, started;
    private static BlockPos towerPos, analyzerPos;
    private static final BlockPos LAB = new BlockPos(190, 100, 160), CANNER = new BlockPos(212, 100, 164);
    private Hk3SpectrumRuntimeCheck() {}

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public static boolean begin(ServerPlayer player) {
        String appdata=System.getenv("APPDATA");
        if (appdata==null || owner!=null || !player.isCreative()
                || !player.server.getWorldData().getLevelName().equals("hk3gtl-research64")
                || !FMLPaths.GAMEDIR.get().toAbsolutePath().normalize().equals(Path.of(appdata,
                    "PrismLauncher", "instances", "GregTech-Leisure-1.4.5.2", "minecraft").toAbsolutePath().normalize())) return false;
        var data=Hk3ResearchData.get(player);
        if (data.hasExperiment(player.getUUID(), "RN-HED") || data.hasExperiment(player.getUUID(), "RN-HSA")) return false;
        for (BlockPos pos : BlockPos.betweenClosed(120,95,120,230,140,185))
            if (!player.level().isEmptyBlock(pos)) return false;
        owner=player.getUUID();stage=0;since=started=player.server.overworld().getGameTime();return true;
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @SubscribeEvent public static void stop(ServerStoppedEvent event) { owner=null; }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static void chunks(ServerPlayer player, boolean forced) {
        for (int x=7;x<=14;x++) for(int z=7;z<=11;z++) player.serverLevel().setChunkForced(x,z,forced);
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static List<ItemBusPartMachine> buses(Hk3WorkableMultiblockMachine machine, IO io) {
        return machine.getParts().stream().filter(p -> p instanceof ItemBusPartMachine b && b.getInventory().getHandlerIO()==io)
                .map(p -> (ItemBusPartMachine)p).toList();
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static int outputCount(Hk3WorkableMultiblockMachine machine, Item item) {
        int count=0; for(var bus:buses(machine,IO.OUT)) for(int i=0;i<bus.getInventory().getSlots();i++) {
            var stack=bus.getInventory().getStackInSlot(i); if(stack.is(item)) count+=stack.getCount();
        } return count;
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static void fundMaterials(ServerPlayer player) {
        var tag=TagKey.create(Registries.ITEM,new ResourceLocation("gtceu","circuits/max"));
        var circuit=BuiltInRegistries.ITEM.getTag(tag).orElseThrow().iterator().next().value();
        require(player.getInventory().add(new ItemStack(circuit,2)),"MAX circuits fit inventory");
        require(player.getInventory().add(ChemicalHelper.get(TagPrefix.plate,GTMaterials.Steel,16)),"plates fit inventory");
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase!=TickEvent.Phase.END || owner==null) return;
        var player=event.getServer().getPlayerList().getPlayer(owner); if(player==null) return;
        long now=player.server.overworld().getGameTime();
        try {
            require(now-started<6000 && now-since<1200,"stage timeout: "+stage);
            if(stage==0) {
                chunks(player,true);
                towerPos=Hk3ApprovedStructureCommands.place(player.createCommandSourceStack(),"i01",new BlockPos(128,100,128),Rotation.NONE);
                analyzerPos=Hk3ApprovedStructureCommands.place(player.createCommandSourceStack(),"i02",new BlockPos(208,100,128),Rotation.NONE);
                Hk3ApprovedStructureCommands.place(player.createCommandSourceStack(),"s01",LAB.offset(-8,-2,-2),Rotation.NONE);
                player.serverLevel().setBlockAndUpdate(CANNER,GTMachines.CANNER[GTValues.LV].getBlock().defaultBlockState());
                // 中文维护备注：历史说明已整理；当前实现以代码为准。
                player.teleportTo(player.serverLevel(),190.5,102,160.5,180,0);
                next(now); return;
            }
            var tower=(Hk3WorkableMultiblockMachine)MetaMachine.getMachine(player.level(),towerPos);
            var analyzer=(Hk3SpectrumAnalysisMachine)MetaMachine.getMachine(player.level(),analyzerPos);
            var lab=(Hk3ResearchInstituteMachine)MetaMachine.getMachine(player.level(),LAB);
            var canner=(SimpleTieredMachine)MetaMachine.getMachine(player.level(),CANNER);
            var data=Hk3ResearchData.get(player);
            // 中文维护备注：历史说明已整理；当前实现以代码为准。
            if ((now-since)%200==0) {
                var active=stage<=2?tower:analyzer;
                var type=stage<=2?com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.COLLECTION
                        :com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS;
                var id=stage<=2?com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine.SAMPLING:Hk3SpectrumAnalysisMachine.INITIAL;
                var recipe=type.getRecipe(player.server.getRecipeManager(),id);
                var modified=recipe==null?null:active.fullModifyRecipe(recipe.copy(),
                        new com.gregtechceu.gtceu.api.recipe.logic.OCParams(),new com.gregtechceu.gtceu.api.recipe.logic.OCResult());
                LogUtils.getLogger().info("[HK3-SPECTRUM64] diagnostic stage={} status={} progress={} coreMatch={} powerMatch={} modified={} modifiedMatch={} enabled={}",
                        stage,active.getRecipeLogic().getStatus(),active.getRecipeLogic().getProgress(),
                        recipe!=null && org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper.matchRecipe(active,recipe),
                        recipe!=null && recipe.matchTickRecipe(active).isSuccess(),modified!=null,
                        modified!=null && org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper.matchRecipe(active,modified),
                        active.getRecipeLogic().isWorkingEnabled());
            }
            // 中文维护备注：历史说明已整理；当前实现以代码为准。
            canner.energyContainer.changeEnergy(32000);
            if(stage==1) {
                if(!tower.isFormed() || !analyzer.isFormed() || !lab.isFormed()) return;
                require(lab.requestResearch(player,"RN-HSA",false)==Hk3ResearchStartService.Result.LOCKED,"missing experiment locked");
                player.getInventory().add(Hk3SpectrumBootstrapRecipes.item("analyzed_honkai_sample"));
                require(!data.hasExperiment(owner,"RN-HSA"),"possessing analyzed sample grants no evidence");
                fundMaterials(player); Hk3FirstContactService.checkInventory(player);
                require(com.sirin.hk3gtl.common.communication.Hk3CommunicationData.get(player).state(owner).hasObservationData(),"MAX entry delivered observation data");
                WirelessEnergyManager.addEUToGlobalEnergyMap(owner,10_000_000_000_000L,lab);
                var input=buses(tower,IO.IN).get(0).getInventory();
                buses(tower,IO.IN).get(0).getCircuitInventory().setStackInSlot(0,IntCircuitBehaviour.stack(3));
                input.setStackInSlot(1,Hk3SpectrumBootstrapRecipes.item("prototype_honkai_detector"));
                for(String id:new String[]{"i01_collection_controller","i02_spectrum_controller"})
                    require(GTRecipeTypes.ASSEMBLER_RECIPES.getRecipe(player.server.getRecipeManager(),new ResourceLocation("hk3gtl","assembler/"+id))!=null,"controller recipe loaded: "+id);
                require(org.gtlcore.gtlcore.common.data.GTLRecipeTypes.SUPRACHRONAL_ASSEMBLY_LINE_RECIPES
                        .getRecipe(player.server.getRecipeManager(),new ResourceLocation("hk3gtl",
                                "suprachronal_assembly_line/industrial_prototype_honkai_detector"))!=null,"prototype detector manufacturing recipe loaded");
                next(now);
            } else if(stage==2) {
                var hatch=tower.getParts().stream().filter(p -> p instanceof FluidHatchPartMachine).map(p -> (FluidHatchPartMachine)p).findFirst().orElseThrow();
                if(hatch.tank.getFluidInTank(0).getAmount()<200) return;
                require(data.hasExperiment(owner,"RN-HED"),"actual I01 sampling evidence");
                tower.getRecipeLogic().setWorkingEnabled(false);
                var sampled=hatch.tank.drain(200,false);
                require(sampled.getAmount()==200 && canner.importFluids.fill(sampled,false)==200,"transfer 200mB actual sample");
                canner.importItems.setStackInSlot(0,new ItemStack(Items.GLASS_BOTTLE,2));
                require(lab.requestResearch(player,"RN-HED",false)==Hk3ResearchStartService.Result.STARTED,"HED material startup");
                next(now);
            } else if(stage==3) {
                var samples=canner.exportItems.getStackInSlot(0);
                if(samples.getCount()<2) return;
                require(samples.is(Hk3SpectrumBootstrapRecipes.item("honkai_analysis_sample").getItem()),"actual canning product");
                require(canner.importFluids.getFluidInTank(0).isEmpty() && canner.importItems.isEmpty(),"canning consumes exactly 200mB and two bottles");
                buses(analyzer,IO.IN).get(0).getCircuitInventory().setStackInSlot(0,IntCircuitBehaviour.stack(1));
                buses(analyzer,IO.IN).get(0).getInventory().setStackInSlot(1,canner.exportItems.extractItem(0,2,false));
                next(now);
            } else if(stage==4) {
                if(now-since<60) return;
                require(!data.hasExperiment(owner,"RN-HSA") && analyzer.getRecipeLogic().getProgress()==0,"missing paper cannot run");
                buses(analyzer,IO.IN).get(0).getInventory().setStackInSlot(2,new ItemStack(Items.PAPER,2));
                for(var bus:buses(analyzer,IO.OUT)) for(int i=0;i<bus.getInventory().getSlots();i++)
                    bus.getInventory().setStackInSlot(i,new ItemStack(Items.COBBLESTONE,64));
                next(now);
            } else if(stage==5) {
                if(now-since<60) return;
                require(!data.hasExperiment(owner,"RN-HSA") && analyzer.getRecipeLogic().getProgress()==0,"full output cannot run or grant evidence");
                for(var bus:buses(analyzer,IO.OUT)) for(int i=0;i<bus.getInventory().getSlots();i++) bus.getInventory().setStackInSlot(i,ItemStack.EMPTY);
                next(now);
            } else if(stage==6) {
                if(analyzer.getRecipeLogic().getProgress()<60) return;
                require(Hk3SpectrumAnalysisMachine.INITIAL.equals(analyzer.getRecipeLogic().getLastRecipe().id),"exact standalone experiment ID");
                analyzer.getRecipeLogic().interruptRecipe();
                require(!data.hasExperiment(owner,"RN-HSA"),"interrupted analysis grants no evidence");
                next(now);
            } else if(stage==7) {
                if(!data.hasExperiment(owner,"RN-HSA")) return;
                analyzer.getRecipeLogic().setWorkingEnabled(false);
                require(outputCount(analyzer,Hk3SpectrumBootstrapRecipes.item("analyzed_honkai_sample").getItem())==1,"one actual output after one interrupted and one completed recipe");
                require(!data.completed(owner,"RN-HSA"),"experiment does not grant knowledge");
                require(buses(analyzer,IO.IN).get(0).getCircuitInventory().getStackInSlot(0).getCount()==1,"programmed circuit not consumed");
                next(now);
            } else if(stage==8) {
                if(!data.completed(owner,"RN-HED")) return;
                fundMaterials(player);
                require(lab.requestResearch(player,"RN-HSA",false)==Hk3ResearchStartService.Result.STARTED,"HSA actual research startup");
                var inventory=player.getInventory().save(new net.minecraft.nbt.ListTag());
                require(lab.requestResearch(player,"RN-HSA",false)==Hk3ResearchStartService.Result.RUNNING,"duplicate startup rejected");
                require(inventory.equals(player.getInventory().save(new net.minecraft.nbt.ListTag())),"duplicate did not debit");
                next(now);
            } else if(stage==9) {
                if(!data.completed(owner,"RN-HSA")) return;
                require(data.researchJob(owner,"RN-HSA")==null,"HSA job settled once");
                var restored=Hk3ResearchData.load(data.save(new CompoundTag()));
                require(restored.hasExperiment(owner,"RN-HSA") && restored.completed(owner,"RN-HSA"),"evidence and knowledge survive NBT roundtrip");
                LogUtils.getLogger().info("[HK3-SPECTRUM64] ALL PASS: I01 -> canner -> I02 -> RN-HED/RN-HSA paid research; negative cases and persistence verified");
                player.sendSystemMessage(Component.literal("I01/I02 experiment and research verification passed."));
                chunks(player,false);player.server.saveEverything(false,true,true);owner=null;
            }
        } catch(Exception error) {
            LogUtils.getLogger().error("[HK3-SPECTRUM64] FAIL stage="+stage,error);
            player.sendSystemMessage(Component.literal("Spectrum verification failed: "+error.getMessage()));chunks(player,false);owner=null;
        }
    }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    private static void next(long now) { LogUtils.getLogger().info("[HK3-SPECTRUM64] PASS stage={}",stage++);since=now; }
    private static void require(boolean valid,String message) { if(!valid) throw new IllegalStateException(message); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
