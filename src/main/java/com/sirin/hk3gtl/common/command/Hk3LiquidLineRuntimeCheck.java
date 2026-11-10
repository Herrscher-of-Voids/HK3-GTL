package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.capability.recipe.*;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.IntCircuitIngredient;
import com.gregtechceu.gtceu.common.data.GTMachines;
import com.gregtechceu.gtceu.common.machine.multiblock.part.ItemBusPartMachine;
import com.gregtechceu.gtceu.common.machine.multiblock.part.FluidHatchPartMachine;
import com.hepdd.gtmthings.api.misc.WirelessEnergyManager;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LiquidLineLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3StructureBlocks;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchCatalog;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;
import java.math.BigInteger;
import java.nio.file.Path;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-24 17:02:00（内测5修订66）
 * 删除：无。新增：指定Prism专用新存档的七机四向成型、破坏恢复及生产验收。
 * 修改：只从正式逐格定义和已加载配方建立夹具，不创建预览文件。
 * 用途：逐机验证真实接口及输出；夹具明确预置原料和前置研究，不冒充生存全流程验证。
 * 仅创造模式管理员显式启动；拒绝非空场地、错误实例或其他存档，不覆盖玩家建筑。
 *
 * 【变更记录 #2】2026-09-24 17:22:00（内测5修订66）
 * 删除：固定起点导致失败后无法再次验收的限制。
 * 新增：可指定空地起点，仍逐格检查空地；启用创造飞行以免测试者坠落。
 * 修改：只有本轮创建的区块加载标记会释放；用途：重跑不覆盖旧夹具或玩家建筑。
 *
 * 【变更记录 #3】2026-09-24 18:56:36（内测5修订67）
 * 修改：验收夹具的物品/流体仓由 HV 改为 MAX，结构服务口改用 MAX 海渊能源机壳。
 * 用途：验收材料等级必须与第一条工业线的 MAX 配方和 Pattern 契约一致，避免测试夹具掩盖低阶结构问题。
 *
 * 【变更记录 #4】2026-09-24 19:40:00（内测5修订68）
 * 新增：交替夹具将同类输入仓与输出仓对调，验证 Pattern 允许端口互换且机器仍能按能力分类取放资源。
 * 修改：夹具日志记录端口方向；物品与流体端口仍严格保持类型隔离。
 * 用途：把端口互换从静态代码约定提升为指定实例中的实际成型与生产验收。
 */
/**
 * 【变更记录 #5】2026-09-25 02:19:54（内测5修订70）
 * 删除：旧建筑退出四机正式入口，历史文件已归档。
 * 新增：已确认逐格建筑及一致的模板与验收入口。
 * 修改：同步主控坐标、材料或测试夹具，不改配方和研究扣费。
 * 用途：使预览、正式结构及游戏放置相互对应；未将静态验证写作实机通过。
 */
/**
 * 【变更记录 #6】2026-09-27 02:38:43（第 6 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：I03/I04/I05使用批准模板与真实尺寸；同类端口轮换保持数量，破坏恢复夹具使用实际通道与端口。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
@Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3LiquidLineRuntimeCheck {
    private static final String[] IDS={"liquid_honkai_fractionation_center","liquid_honkai_stabilization_tower",
            "stabilization_medium_regeneration_tower","honkai_fuel_blending_plant","honkai_detector_calibration_bench",
            "honkai_fuel_concentration_plant","honkai_network_injector"};
    private static final String[] RECIPES={"industrial_liquid_fractionation","industrial_liquid_stabilization",
            "industrial_stabilization_medium_recovery","industrial_liquid_fuel_blending","industrial_prototype_detector_calibration",
            "industrial_liquid_fuel_concentration","industrial_inject_liquid_honkai_fuel"};
    private static UUID owner;
    private static int fixture,stage,originX;
    private static long since;
    private static BlockPos controller,changed;
    private static BlockState restore;
    private static GTRecipe recipe;
    private static BigInteger networkBefore;
    private static final Set<Long> FORCED=new HashSet<>();
    private Hk3LiquidLineRuntimeCheck() {}
    @SubscribeEvent public static void register(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("hk3liquidverify").requires(s -> s.hasPermission(2))
                .executes(c -> {
                    var p=c.getSource().getPlayerOrException();
                    boolean accepted=begin(p,256);
                    p.sendSystemMessage(Component.literal(accepted?"开始液态工业逐机验收；夹具预置材料及研究，不是生存全流程验收。"
                            :"需要指定Prism实例、创造模式和新建的hk3gtl-liquid66专用测试存档，且不能重复运行。"));
                    return accepted?1:0;
                }).then(Commands.argument("起点X",com.mojang.brigadier.arguments.IntegerArgumentType.integer(256,100000))
                    .executes(c -> begin(c.getSource().getPlayerOrException(),
                            com.mojang.brigadier.arguments.IntegerArgumentType.getInteger(c,"起点X"))?1:0)));
    }
    private static boolean begin(ServerPlayer p,int x) {
        String app=System.getenv("APPDATA");
        if(app==null||owner!=null||!p.isCreative()||!p.server.getWorldData().getLevelName().equals("hk3gtl-liquid66"))return false;
        if(!FMLPaths.GAMEDIR.get().toAbsolutePath().normalize().equals(Path.of(app,"PrismLauncher","instances",
                "GregTech-Leisure-1.4.5.2","minecraft").toAbsolutePath().normalize()))return false;
        Hk3LiquidLineAudit.audit(p.server);
        owner=p.getUUID();originX=x;fixture=stage=0;since=p.server.overworld().getGameTime();return true;
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent e) { owner=null;FORCED.clear(); }
    private static void release(ServerPlayer p) {
        for(long packed:FORCED){var chunk=new net.minecraft.world.level.ChunkPos(packed);p.server.overworld().setChunkForced(chunk.x,chunk.z,false);}
        FORCED.clear();
    }
    private static String approvedId(Hk3LiquidLineLayout.Kind kind) {
        return switch(kind){case SEPARATION -> "i03";case STABILIZATION -> "i04";case REGENERATION -> "i05";default -> null;};
    }
    /** 本地坐标与控制器朝向换算，独立于GT成型实现，验证四向旋转是否一致。 */
    private static BlockPos position(Hk3LiquidLineLayout.Kind kind,Direction facing,int x,int y,int z) {
        if(approvedId(kind)!=null)
            return controller.relative(facing.getClockWise(),x-8).above(y-2).relative(facing.getOpposite(),z-2);
        return controller.relative(facing.getClockWise(),x-kind.width/2).above(y-2).relative(facing.getOpposite(),z);
    }
    /**
     * 放置一座验收夹具。
     *
     * @param swapPorts 本轮是否把同类输入/输出仓位对调；只对物品与流体各自的同类端口生效
     */
    private static void place(ServerPlayer p,Hk3LiquidLineLayout.Kind kind,Direction facing,boolean swapPorts) {
        var level=p.server.overworld();controller=new BlockPos(originX+fixture*96,162,256);
        String approved=approvedId(kind);
        int[] size=approved==null?new int[]{kind.width,kind.height,kind.depth}:
                com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(approved).size();
        var first=position(kind,facing,0,0,0);var last=position(kind,facing,size[0]-1,size[1]-1,size[2]-1);
        for(int x=(Math.min(first.getX(),last.getX())>>4)-1;x<=(Math.max(first.getX(),last.getX())>>4)+1;x++)
            for(int z=(Math.min(first.getZ(),last.getZ())>>4)-1;z<=(Math.max(first.getZ(),last.getZ())>>4)+1;z++) {
                var chunk=new net.minecraft.world.level.ChunkPos(x,z);require(!level.getForcedChunks().contains(chunk.toLong()),"场地已被其他系统强制加载");
                level.setChunkForced(x,z,true);FORCED.add(chunk.toLong());
            }
        for(var pos:BlockPos.betweenClosed(first,last))require(level.isEmptyBlock(pos)&&!level.isOutsideBuildHeight(pos),"验收场地非空或越界："+pos);
        if(approved!=null) {
            var rotation=switch(facing){case EAST -> net.minecraft.world.level.block.Rotation.CLOCKWISE_90;
                case SOUTH -> net.minecraft.world.level.block.Rotation.CLOCKWISE_180;
                case WEST -> net.minecraft.world.level.block.Rotation.COUNTERCLOCKWISE_90;
                default -> net.minecraft.world.level.block.Rotation.NONE;};
            controller=Hk3ApprovedStructureCommands.place(p.createCommandSourceStack(),approved,first,rotation);
            // 在同类槽之间轮换既有方块，保留输入输出数量，I03的2进4出不可反转成4进2出。
            if(swapPorts)for(String prefix:new String[]{"M","F"}) {
                var ports=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(approved).ports().stream()
                        .filter(port->port.id().startsWith(prefix)).toList();
                var states=new ArrayList<BlockState>();
                for(var port:ports){int[] q=port.pos();states.add(level.getBlockState(position(kind,facing,q[0],q[1],q[2])));}
                for(int i=0;i<ports.size();i++) {
                    int[] q=ports.get(i).pos();var pos=position(kind,facing,q[0],q[1],q[2]);
                    level.setBlockAndUpdate(pos,states.get((i+1)%states.size()));
                    var part=MetaMachine.getMachine(level,pos);
                    if(part!=null)part.setFrontFacing(rotation.rotate(Direction.byName(ports.get(i).face())));
                }
            }
            machine(p).getRecipeLogic().setWorkingEnabled(false);return;
        }
        var layout=Hk3LiquidLineLayout.create(kind);
        for(int z=0;z<kind.depth;z++)for(int y=0;y<kind.height;y++)for(int x=0;x<kind.width;x++) {
            char symbol=layout.at(x,y,z);if(symbol=='#')continue;
            var block=switch(symbol) {
                case 'S' -> Hk3StructureBlocks.require("hk3gtl:"+IDS[fixture/4]);
                case 'i' -> kind==Hk3LiquidLineLayout.Kind.INJECTION
                        ? ((x+y+(swapPorts?1:0))%2==0 ? GTMachines.ITEM_IMPORT_BUS[GTValues.MAX].getBlock()
                            : GTMachines.FLUID_IMPORT_HATCH[GTValues.MAX].getBlock())
                        : swapPorts ? GTMachines.ITEM_EXPORT_BUS[GTValues.MAX].getBlock()
                            : GTMachines.ITEM_IMPORT_BUS[GTValues.MAX].getBlock();
                case 'o' -> swapPorts
                        ? GTMachines.ITEM_IMPORT_BUS[GTValues.MAX].getBlock()
                        : GTMachines.ITEM_EXPORT_BUS[GTValues.MAX].getBlock();
                case 'u' -> swapPorts
                        ? GTMachines.FLUID_EXPORT_HATCH[GTValues.MAX].getBlock()
                        : GTMachines.FLUID_IMPORT_HATCH[GTValues.MAX].getBlock();
                case 'v' -> swapPorts
                        ? GTMachines.FLUID_IMPORT_HATCH[GTValues.MAX].getBlock()
                        : GTMachines.FLUID_EXPORT_HATCH[GTValues.MAX].getBlock();
                case 'h' -> Hk3StructureBlocks.require(layout.materials().get('C'));
                default -> Hk3StructureBlocks.require(layout.materials().get(symbol));
            };
            level.setBlockAndUpdate(position(kind,facing,x,y,z),block.defaultBlockState());
        }
        var machine=machine(p);machine.setFrontFacing(facing);machine.onMachinePlaced(p,machine.getDefinition().asStack());
        machine.getRecipeLogic().setWorkingEnabled(false);
        p.getAbilities().flying=true;p.onUpdateAbilities();
        LogUtils.getLogger().info("[HK3-LIQUID68-RUNTIME] 放置 {}，朝向={}，同类端口互换={}",
                IDS[fixture/4], facing, swapPorts);
        p.teleportTo(level,controller.getX()+.5,166,controller.getZ()+.5,0,0);
    }
    private static Hk3WorkableMultiblockMachine machine(ServerPlayer p) {
        return (Hk3WorkableMultiblockMachine)MetaMachine.getMachine(p.server.overworld(),controller);
    }
    private static List<ItemBusPartMachine> buses(Hk3WorkableMultiblockMachine m,IO io) {
        return m.getParts().stream().filter(v -> v instanceof ItemBusPartMachine b&&b.getInventory().getHandlerIO()==io)
                .map(v -> (ItemBusPartMachine)v).toList();
    }
    private static List<FluidHatchPartMachine> tanks(Hk3WorkableMultiblockMachine m,IO io) {
        return m.getParts().stream().filter(v -> v instanceof FluidHatchPartMachine b&&b.tank.getHandlerIO()==io)
                .map(v -> (FluidHatchPartMachine)v).toList();
    }
    private static void grantParents(ServerPlayer p,String id) {
        if(id==null)return;
        var node=Hk3ResearchCatalog.bundled().get(id);require(node!=null,"夹具不接受旧研究节点："+id);
        for(String parent:node.prerequisites())grantParents(p,parent);
        var data=Hk3ResearchData.get(p);
        if(!data.completed(owner,id))require(data.recordCompletion(owner,id,5),"无法设置夹具前置："+id);
    }
    /** 投料来自当前配方，按槽上限分拆，不写超堆叠物品；注入器用两批验证真实并行。 */
    private static void supply(ServerPlayer p,Hk3WorkableMultiblockMachine m) {
        recipe=p.server.getRecipeManager().getAllRecipesFor(m.getRecipeType()).stream()
                .filter(r -> r.id.getPath().endsWith("/"+RECIPES[fixture/4])).findFirst().orElseThrow();
        // 修订163 · 2026-10-17 15:07:22：创造测试夹具授予全部前置，不再只准备首个研究。
        Hk3CommunicationData.get(p).discover(owner);
        for(String research:Hk3RecipeResearchGate.getAllRequiredResearch(recipe.id))grantParents(p,research);
        WirelessEnergyManager.addEUToGlobalEnergyMap(owner,4_000_000_000_000_000_000L,m);
        networkBefore=HonkaiWirelessNetwork.getStoredAmount(owner);int multiplier=fixture/4==6?2:1;
        var inputs=buses(m,IO.IN);
        for(var c:recipe.getInputContents(ItemRecipeCapability.CAP)) {
            var ingredient=ItemRecipeCapability.CAP.of(c.content);var stack=ingredient.getItems()[0].copy();
            if(ingredient instanceof IntCircuitIngredient){inputs.get(0).getCircuitInventory().setStackInSlot(0,stack);continue;}
            int remaining=stack.getCount()*(c.chance==0?1:multiplier);
            for(var bus:inputs)for(int slot=0;slot<bus.getInventory().getSlots()&&remaining>0;slot++) {
                var portion=stack.copy();portion.setCount(Math.min(remaining,stack.getMaxStackSize()));
                int inserted=portion.getCount()-bus.getInventory().insertItem(slot,portion,false).getCount();remaining-=inserted;
            }
            require(remaining==0,"物品输入仓容纳不了单批配方："+recipe.id);
        }
        for(var c:recipe.getInputContents(FluidRecipeCapability.CAP)) {
            var ingredient=FluidRecipeCapability.CAP.of(c.content);var stack=ingredient.getStacks()[0].copy();
            stack.setAmount(ingredient.getAmount()*multiplier);long remaining=stack.getAmount();
            for(var tank:tanks(m,IO.IN)){stack.setAmount(remaining);remaining-=tank.tank.fill(stack,false);if(remaining==0)break;}
            require(remaining==0,"流体输入仓容纳不了配方："+recipe.id);
        }
    }
    private static boolean outputsReady(ServerPlayer p,Hk3WorkableMultiblockMachine m) {
        if(fixture/4==6)return HonkaiWirelessNetwork.getStoredAmount(owner).subtract(networkBefore).equals(BigInteger.valueOf(32000));
        for(var c:recipe.getOutputContents(ItemRecipeCapability.CAP)) {
            var expected=ItemRecipeCapability.CAP.of(c.content).getItems()[0];int count=0;
            for(var b:buses(m,IO.OUT))for(int i=0;i<b.getInventory().getSlots();i++) {
                var actual=b.getInventory().getStackInSlot(i);if(ItemStack.isSameItemSameTags(expected,actual))count+=actual.getCount();
            }
            if(count!=expected.getCount())return false;
        }
        for(var c:recipe.getOutputContents(FluidRecipeCapability.CAP)) {
            var expected=FluidRecipeCapability.CAP.of(c.content).getStacks()[0];long count=0;
            for(var h:tanks(m,IO.OUT))for(int i=0;i<h.tank.getTanks();i++) {
                var actual=h.tank.getFluidInTank(i);if(actual.getFluid()==expected.getFluid())count+=actual.getAmount();
            }
            if(count!=expected.getAmount())return false;
        }
        return true;
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END||owner==null)return;
        var p=e.getServer().getPlayerList().getPlayer(owner);if(p==null)return;
        long now=p.server.overworld().getGameTime();var kind=Hk3LiquidLineLayout.Kind.values()[fixture/4];
        var facing=new Direction[]{Direction.NORTH,Direction.EAST,Direction.SOUTH,Direction.WEST}[fixture%4];
        try {
            require(now-since<4000,"验收超时 fixture="+fixture+" stage="+stage);
            if(stage==0){place(p,kind,facing,(fixture&1)==1);since=now;stage=1;return;}
            var m=machine(p);
            if(stage<=7) {
                boolean formed=stage%2==1;if(m.isFormed()!=formed||now-since<10)return;
                require(m.checkPatternWithLock()==formed,"成型标志与Pattern检查不一致");
                LogUtils.getLogger().info("[HK3-LIQUID68-RUNTIME] PASS {} {} 成型检查{}（端口互换={}）",
                        IDS[fixture/4],facing,stage,(fixture&1)==1);
                if(stage==1||stage==3||stage==5) {
                    String approved=approvedId(kind);
                    if(approved!=null) {
                        var data=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(approved);
                        int[] q=stage==1?new int[]{8,0,8}:stage==3?
                                new int[]{data.size()[0]/2,2,5}:data.ports().get(0).pos();
                        // I03的纵向通道位于X=16，其余两台位于正中。
                        if(stage==3&&approved.equals("i03"))q=new int[]{16,2,5};
                        changed=position(kind,facing,q[0],q[1],q[2]);
                    }else changed=kind==Hk3LiquidLineLayout.Kind.SEPARATION
                            ?stage==1?position(kind,facing,8,0,8):stage==3?position(kind,facing,16,2,5):position(kind,facing,4,2,2)
                            :stage==1?position(kind,facing,0,0,0):stage==3?position(kind,facing,kind.width/2,2,5):position(kind,facing,2,2,kind.depth-1);
                    restore=p.server.overworld().getBlockState(changed);
                    p.server.overworld().setBlockAndUpdate(changed,stage==1?Blocks.AIR.defaultBlockState():Blocks.STONE.defaultBlockState());
                } else if(stage==2||stage==4||stage==6)p.server.overworld().setBlockAndUpdate(changed,restore);
                else if(fixture%4!=0 && fixture%4!=1){advance(p,now);return;}
                // 朝向 0 使用正常端口，朝向 1 使用同类端口互换并再次跑一批真实配方；
                // 另外两种朝向只做成型、破坏和恢复检查，避免把验收时间用于重复产出。
                else supply(p,m);
                stage++;since=now;return;
            }
            if(stage==8) {m.getRecipeLogic().setWorkingEnabled(true);stage=9;since=now;return;}
            if(!outputsReady(p,m))return;
            m.getRecipeLogic().setWorkingEnabled(false);
            String evidence=recipe.data.getString(com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine.EXPERIMENT);
            require(evidence.isBlank()||Hk3ResearchData.get(p).hasExperiment(owner,evidence),"真实输出没有生成实验记录");
            require(!buses(m,IO.IN).get(0).getCircuitInventory().getStackInSlot(0).isEmpty(),"编程电路被消耗");
            for(var c:recipe.getInputContents(ItemRecipeCapability.CAP)) {
                var input=ItemRecipeCapability.CAP.of(c.content);if(c.chance==0||input instanceof IntCircuitIngredient)continue;
                for(var bus:buses(m,IO.IN))for(int i=0;i<bus.getInventory().getSlots();i++)
                    require(!input.test(bus.getInventory().getStackInSlot(i)),"产出后仍有应消耗物品");
            }
            for(var tank:tanks(m,IO.IN))for(int i=0;i<tank.tank.getTanks();i++)require(tank.tank.getFluidInTank(i).isEmpty(),"产出后仍有应消耗流体");
            LogUtils.getLogger().info("[HK3-LIQUID68-RUNTIME] PASS {} 实际扣料、完整输出、实验与编程电路；端口互换={}；配方={}",
                    IDS[fixture/4],(fixture&1)==1,recipe.id);
            advance(p,now);
        } catch(Exception error) {
            LogUtils.getLogger().error("[HK3-LIQUID68-RUNTIME] FAIL fixture="+fixture+" stage="+stage,error);
            p.sendSystemMessage(Component.literal("液态工业验收失败："+error.getMessage()));release(p);owner=null;
        }
    }
    private static void advance(ServerPlayer p,long now) {
        release(p);fixture++;stage=0;since=now;
        if(fixture==28) {
            LogUtils.getLogger().info("[HK3-LIQUID68-RUNTIME] ALL PASS：28座四向夹具、196项成型破坏恢复检查、端口互换与7台实际生产；前置为夹具预置，非完整生存实测");
            p.sendSystemMessage(Component.literal("七台四向成型与逐机生产验收通过。"));owner=null;p.server.saveEverything(false,true,true);
        }
    }
    private static void require(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
