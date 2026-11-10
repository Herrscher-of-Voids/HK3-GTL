package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.block.BlockProperties;
import com.gregtechceu.gtceu.api.block.MetaMachineBlock;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLPaths;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.network.chat.Component;
import com.mojang.logging.LogUtils;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.List;
import java.util.HashMap;
import java.util.Map;

/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-25 02:19:54（内测5修订70）
 * 删除：旧建筑退出四机正式入口，历史文件已归档。
 * 新增：已确认逐格建筑及一致的模板与验收入口。
 * 修改：同步主控坐标、材料或测试夹具，不改配方和研究扣费。
 * 用途：使预览、正式结构及游戏放置相互对应；未将静态验证写作实机通过。
 */
/**
 * 【变更记录 #2】2026-09-27 02:38:43（第 2 次备注 · 内测5修订87 · 正式六机接入）
 * 删除：相关正式入口对旧I04/I05结构的依赖；历史备注与旧布局数据保留。
 * 新增：显式游戏诊断夹具覆盖六台四向结构；仍只允许指定实例专用创造存档由玩家手动启动。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
/**
 * 【变更记录 #3】2026-10-15 01:19:00（第3次备注 · 内测5修订156）
 * 删除：仅允许旧GregTech-Leisure实例的路径，以及128格间距导致S05旋转夹具相交的布局。
 * 新增：当前指定GTL十一周目实例的专用创造超平坦测试入口，按最大批准水平尺寸计算夹具间距。
 * 修改：放置和卸载共用夹具坐标；测试仍需允许作弊及专用世界名，不写入普通玩家存档。
 * 用途：让21种结构的四向成型、破坏和恢复可在正确实例验证；入口不代表已经运行验收。
 */
/**
 * 【变更记录 #4】2026-10-15 01:49:15（第4次备注 · 内测5修订157）
 * 删除：正式结构验收对GTL十一周目实例的旧路径限制；历史备注保留。
 * 新增：负责人指定的GregTech Leisure-增强版 2.7实例、主世界与OP身份校验。
 * 修改：全部夹具与指定单建筑或单朝向共用相同的创造、作弊、超平坦专用存档边界。
 * 用途：将实机验收转移到内测5后续联机试玩所用整合包，不把入口开放写成验收通过。
 */
/**
 * 【变更记录 #5】2026-10-15 01:49:15（第5次备注 · 内测5修订157）
 * 删除：84个夹具完成前持续持有全部区块、重复扫描所有建筑计算间距及空气检查的逐格哈希集合。
 * 新增：单夹具空白场地复用、已放方块状态快照、仅释放本轮票据、失联与停服清理及单建筑/单朝向入口。
 * 修改：每座夹具七阶段通过后先清理再继续；失败仅清理放置前已验证为空的自有位置，保留外部替换方块。
 * 用途：让验收自身内存随最大单夹具增长，而非随84个夹具累积；保留全部批准尺寸、四向与破坏恢复检查。
 */
/**
 * 【变更记录 #6】2026-10-15 02:35:08（香港时间；第6次备注 · 内测5修订158）
 * 删除：无；保留失败时对外部替换方块的保护。
 * 新增：为放置时存在的GT方块实体记录对象身份；清理时允许其官方server_tick属性生命周期变化。
 * 修改：清理不再只比较静态状态ID；同方块、同一方块实体且仅server_tick变化仍认定为本轮夹具，朝向、方块、方块实体替换均保留并终止验收。
 * 用途：修复GT端口成型/失效更新造成的合法状态变化误报，不扩大清理授权，不捕获或覆盖stage7后的外部修改。
 */
/**
 * 【变更记录 #7】2026-10-20 00:55:29（香港时间；第7次备注 · 修订172）
 * 删除：验收路径中已失效的增强版2.7目录名；保留全部历史备注及其他验收条件。
 * 新增：无新的验收权限或入口。
 * 修改：指定实例路径改为已核实增强版2.9所在的绝对路径，与命令拒绝提示同步。
 * 用途：恢复当前唯一测试实例的结构验收入口；创造、OP、主世界、作弊、超平坦及专用存档限制不变。
 */
@Mod.EventBusSubscriber(modid="hk3gtl",bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ApprovedStructureRuntimeCheck {
    private static int fixture,stage;
    private static int[] selectedFixtures = new int[0], placedStateIds;
    private static final Map<Integer,BlockEntity> placedBlockEntities = new HashMap<>();
    private static long since;
    private static BlockPos origin,controller,changed;
    private static BlockState restore,mutation;
    private static int changedIndex=-1;
    private static BlockEntity mutationEntity;
    private static Hk3ApprovedArchitecture.Layout activeLayout;
    private static StructurePlaceSettings activeSettings;
    private static boolean ownsFixtureArea;
    private static final List<Long> FORCED = new ArrayList<>();
    private static boolean done;
    private static java.util.UUID operator;
    private Hk3ApprovedStructureRuntimeCheck() {}

    /** 世界保存前删除临时夹具并释放本轮票据，避免强制加载状态写入下一次启动。 */
    @SubscribeEvent public static void stopping(ServerStoppingEvent event) {
        if (operator != null || !FORCED.isEmpty()) finish(event.getServer(), null, "服务器停止，结束正式结构验收。");
    }

    /** 停服后只清除内存上下文；世界写入由停服前事件负责。 */
    @SubscribeEvent public static void stop(ServerStoppedEvent event) { reset(); }

    /** 默认验证全部21种获批建筑的四个朝向。 */
    public static boolean begin(ServerPlayer player) {
        return beginSelected(player, null, null);
    }

    /** 单建筑仍完整覆盖四向，便于低内存环境分批核验。 */
    public static boolean begin(ServerPlayer player, String id) {
        return id != null && beginSelected(player, id, null);
    }

    /** 指定朝向用于启动和内存排查，不将单朝向结果冒充四向全部通过。 */
    public static boolean begin(ServerPlayer player, String id, Rotation rotation) {
        return id != null && rotation != null && beginSelected(player, id, rotation);
    }

    /** 操作者或具有OP权限的玩家可主动取消，立即清理本轮临时夹具与票据。 */
    public static boolean cancel(ServerPlayer player) {
        if (operator==null || (!operator.equals(player.getUUID()) && !player.hasPermissions(2))) return false;
        finish(player.server,player,"已取消正式结构验收，临时夹具与本轮区块票据已清理。");
        return true;
    }

    private static boolean beginSelected(ServerPlayer player, String id, Rotation rotation) {
        String appdata=System.getenv("APPDATA");
        if (appdata==null || operator!=null || !player.isCreative() || !player.hasPermissions(2)
                || player.serverLevel() != player.server.overworld()) return false;
        var expected=java.nio.file.Path.of("C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft");
        if (!FMLPaths.GAMEDIR.get().toAbsolutePath().normalize().equals(expected.toAbsolutePath().normalize())
                || !player.server.getWorldData().getLevelName().startsWith("hk3gtl-structure70-")
                || !player.server.getWorldData().getAllowCommands() || !player.server.overworld().isFlat()) return false;
        int index=id==null?-1:Hk3ApprovedArchitecture.IDS.indexOf(id);
        if (id!=null && index<0) return false;
        reset();
        selectedFixtures = id==null
                ? java.util.stream.IntStream.range(0,Hk3ApprovedArchitecture.IDS.size()*4).toArray()
                : rotation==null ? new int[]{index*4,index*4+1,index*4+2,index*4+3}
                : new int[]{index*4+rotation.ordinal()};
        operator=player.getUUID();
        LogUtils.getLogger().info("[HK3-STRUCTURE70] 开始验收：{}个朝向；临时场地逐夹具清理",selectedFixtures.length);
        return true;
    }

    /** 单线程逐夹具验证；玩家失联或离开主世界时立即清理，防止票据无限持有。 */
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        MinecraftServer server=e.getServer();
        if (e.phase!=TickEvent.Phase.END || done || operator==null) return;
        ServerPlayer player=server.getPlayerList().getPlayer(operator);
        if (player==null || player.serverLevel()!=server.overworld()) {
            finish(server,player,"操作者失联或离开主世界，已结束正式结构验收。");
            return;
        }
        var level=server.overworld();long now=level.getGameTime();
        try {
            int selected=selectedFixtures[fixture];
            String id=Hk3ApprovedArchitecture.IDS.get(selected/4);
            Rotation rotation=Rotation.values()[selected%4];
            var settings=new StructurePlaceSettings().setRotation(rotation);
            if (stage==0) {
                origin=new BlockPos(256,100,256);
                activeLayout=Hk3ApprovedArchitecture.get(id);
                activeSettings=settings;
                forceFixtureChunks(level);
                requireEmptyFixture(level);
                // 只有全区域为空时才取得夹具清理权；预检失败不删除玩家方块。
                ownsFixtureArea=true;
                controller=Hk3ApprovedStructureCommands.place(player.createCommandSourceStack(),id,origin,rotation);
                capturePlacedStates(level);
                since=now;stage=1;
                LogUtils.getLogger().info("[HK3-STRUCTURE70] placed {} {} at {} forced={}",id,rotation,origin,FORCED.size());
                return;
            }
            if (now-since>400) throw new IllegalStateException("Timeout fixture="+fixture+" stage="+stage);
            if (!(MetaMachine.getMachine(level,controller) instanceof Hk3WorkableMultiblockMachine machine))
                throw new IllegalStateException("验收主控不存在："+controller);
            boolean expect=stage%2==1;
            if (machine.isFormed()!=expect || now-since<10) return;
            if (expect && !machine.checkPatternWithLock()) throw new IllegalStateException("Formed with invalid Pattern");
            if (!expect && machine.checkPatternWithLock()) throw new IllegalStateException("Malformed structure accepted");
            LogUtils.getLogger().info("[HK3-STRUCTURE70] PASS {} {} stage={} formed={} parts={}",id,rotation,stage,machine.isFormed(),machine.getParts().size());
            if (stage==1 || stage==3 || stage==5) {
                int[] port=activeLayout.ports().get(0).pos();
                BlockPos local=stage==1?solidCell(activeLayout):stage==3?airCell(activeLayout)
                        :new BlockPos(port[0],port[1],port[2]);
                changed=StructureTemplate.calculateRelativePosition(settings,local).offset(origin);
                changedIndex=-1;
                for (int i=0;i<placedStateIds.length;i++) {
                    if (worldPosition(activeLayout.blocks().get(i)).equals(changed)) { changedIndex=i;break; }
                }
                if (changedIndex>=0 ? !canClearOwnedCell(level,changedIndex,changed) : !level.isEmptyBlock(changed))
                    throw new IllegalStateException("验收位置被外部修改，保留当前方块："+changed);
                restore=level.getBlockState(changed);
                mutation=stage==1?Blocks.AIR.defaultBlockState():Blocks.STONE.defaultBlockState();
                level.setBlockAndUpdate(changed,mutation);
                mutationEntity=level.getBlockEntity(changed);
            } else if (stage==2 || stage==4 || stage==6) {
                restoreMutation(level);
            } else if (stage==7) {
                clearFixture(level);
                releaseChunks(level);
                fixture++;stage=0;
                if (fixture==selectedFixtures.length)
                    finish(server,player,"本轮正式结构："+fixture+"个朝向的成型、破坏与恢复检查通过，临时夹具已清理。");
                return;
            }
            since=now;stage++;
        } catch (Exception ex) {
            LogUtils.getLogger().error("[HK3-STRUCTURE70] FAILED",ex);
            finish(server,player,"正式结构验收失败："+ex.getMessage());
        }
    }

    /** 成功、失败、失联和停服共用收尾，清理失败仍尝试解除本轮区块票据。 */
    private static void finish(MinecraftServer server,ServerPlayer player,String message) {
        try {
            clearFixture(server.overworld());
        } catch (RuntimeException error) {
            LogUtils.getLogger().error("[HK3-STRUCTURE70] 临时夹具清理失败",error);
            message+=" 临时夹具清理失败，详见日志。";
        } finally {
            try { releaseChunks(server.overworld()); }
            finally { reset(); }
        }
        LogUtils.getLogger().info("[HK3-STRUCTURE70] {}",message);
        if (player!=null) player.sendSystemMessage(Component.literal(message));
    }

    private static void reset() {
        fixture=stage=0;since=0;done=false;operator=null;
        selectedFixtures=new int[0];placedStateIds=null;placedBlockEntities.clear();activeLayout=null;activeSettings=null;
        origin=controller=changed=null;restore=mutation=null;ownsFixtureArea=false;FORCED.clear();
        changedIndex=-1;mutationEntity=null;
    }

    private static BlockPos solidCell(Hk3ApprovedArchitecture.Layout layout) {
        var ports=layout.ports().stream().map(port -> new BlockPos(port.pos()[0],port.pos()[1],port.pos()[2]))
                .collect(java.util.stream.Collectors.toSet());
        var anchor=new BlockPos(layout.controller()[0],layout.controller()[1],layout.controller()[2]);
        return layout.blocks().stream().map(cell -> new BlockPos(cell.pos()[0],cell.pos()[1],cell.pos()[2]))
                .filter(pos -> !pos.equals(anchor) && !ports.contains(pos)).findFirst()
                .orElseThrow(() -> new IllegalStateException("缺少普通实体测试位置："+layout.key()));
    }

    /** 位图每格一位，S05约214KiB，避免为160406个实体格创建常驻哈希节点。 */
    private static BlockPos airCell(Hk3ApprovedArchitecture.Layout layout) {
        int[] size=layout.size();
        int volume=Math.multiplyExact(Math.multiplyExact(size[0],size[1]),size[2]);
        BitSet occupied=new BitSet(volume);
        for (var cell:layout.blocks()) {
            int[] p=cell.pos();
            occupied.set((p[1]*size[2]+p[2])*size[0]+p[0]);
        }
        int index=occupied.nextClearBit(0);
        if (index>=volume) throw new IllegalStateException("缺少空气测试位置："+layout.key());
        return new BlockPos(index%size[0],index/size[0]/size[2],index/size[0]%size[2]);
    }

    private static BlockPos fixtureEnd() {
        int[] size=activeLayout.size();
        return StructureTemplate.calculateRelativePosition(activeSettings,
                new BlockPos(size[0]-1,size[1]-1,size[2]-1)).offset(origin);
    }

    private static BlockPos worldPosition(Hk3ApprovedArchitecture.Cell cell) {
        int[] p=cell.pos();
        return StructureTemplate.calculateRelativePosition(activeSettings,new BlockPos(p[0],p[1],p[2])).offset(origin);
    }

    /** 预检失败不取得清理权；不向非空区域粘贴，也不删除已有建筑。 */
    private static void requireEmptyFixture(ServerLevel level) {
        BlockPos end=fixtureEnd();
        int minX=Math.min(origin.getX(),end.getX()), maxX=Math.max(origin.getX(),end.getX());
        int minY=Math.min(origin.getY(),end.getY()), maxY=Math.max(origin.getY(),end.getY());
        int minZ=Math.min(origin.getZ(),end.getZ()), maxZ=Math.max(origin.getZ(),end.getZ());
        BlockPos.MutableBlockPos pos=new BlockPos.MutableBlockPos();
        for (int x=minX;x<=maxX;x++) for (int y=minY;y<=maxY;y++) for (int z=minZ;z<=maxZ;z++) {
            pos.set(x,y,z);
            if (level.isOutsideBuildHeight(pos) || !level.getWorldBorder().isWithinBounds(pos))
                throw new IllegalStateException("验收场地越界："+pos);
            if (!level.isEmptyBlock(pos)) throw new IllegalStateException("验收场地非空，未放置："+pos);
        }
    }

    /** 快照使用每格4字节的状态索引，覆盖模板中实际仓室而非建筑预览的占位材料。 */
    private static void capturePlacedStates(ServerLevel level) {
        placedStateIds=new int[activeLayout.blocks().size()];
        placedBlockEntities.clear();
        for (int i=0;i<placedStateIds.length;i++) {
            BlockPos pos=worldPosition(activeLayout.blocks().get(i));
            placedStateIds[i]=Block.getId(level.getBlockState(pos));
            BlockEntity blockEntity=level.getBlockEntity(pos);
            if (blockEntity!=null) placedBlockEntities.put(i,blockEntity);
        }
    }

    /** 纯身份与属性检查，方便独立回归外部同方块替换；生命周期属性按官方对象身份白名单。 */
    static final class FixtureOwnership {
        private FixtureOwnership() {}
        static boolean permits(Object placedBlock,Object currentBlock,Object placedEntity,Object currentEntity,
                               Map<?,?> placedValues,Map<?,?> currentValues,Object lifecycleProperty) {
            if (placedBlock!=currentBlock || placedEntity!=currentEntity) return false;
            if (placedValues.equals(currentValues)) return true;
            if (placedEntity==null || !placedValues.keySet().equals(currentValues.keySet())) return false;
            for (var entry:placedValues.entrySet()) {
                Object current=currentValues.get(entry.getKey());
                if (!entry.getValue().equals(current)
                        && (entry.getKey()!=lifecycleProperty || !(entry.getValue() instanceof Boolean)
                        || !(current instanceof Boolean))) return false;
            }
            return true;
        }
    }

    private static boolean canClearOwnedCell(ServerLevel level,int index,BlockPos pos) {
        BlockState current=level.getBlockState(pos);
        if (current.isAir()) return true;
        BlockState placed=Block.stateById(placedStateIds[index]);
        return FixtureOwnership.permits(placed.getBlock(),current.getBlock(),
                placedBlockEntities.get(index),level.getBlockEntity(pos),placed.getValues(),current.getValues(),
                placed.getBlock() instanceof MetaMachineBlock?BlockProperties.SERVER_TICK:null);
    }

    /** 仅撤销验收自己执行的改动；外部替换时停止验收并保留外部方块。 */
    private static void restoreMutation(ServerLevel level) {
        if (changed==null || restore==null) return;
        if (!level.getBlockState(changed).equals(mutation) || level.getBlockEntity(changed)!=mutationEntity)
            throw new IllegalStateException("验收位置被外部修改，保留当前方块："+changed);
        level.setBlockAndUpdate(changed,restore);
        // 石头破坏测试会新建GT方块实体；仅在本方法确实撤销自有改动后更新这一格身份。
        if (changedIndex>=0) {
            BlockEntity restoredEntity=level.getBlockEntity(changed);
            if (restoredEntity==null) placedBlockEntities.remove(changedIndex);
            else placedBlockEntities.put(changedIndex,restoredEntity);
        }
        changed=null;restore=mutation=null;
        changedIndex=-1;mutationEntity=null;
    }

    /** 先移除主控以释放机器关联，再清理自有实体格；不遍历空气区域删除其他人的新方块。 */
    private static void clearFixture(ServerLevel level) {
        if (!ownsFixtureArea || activeLayout==null) return;
        if (changed!=null && restore!=null) {
            if (level.getBlockState(changed).equals(mutation) && level.getBlockEntity(changed)==mutationEntity)
                restoreMutation(level);
            else { changed=null;restore=mutation=null;changedIndex=-1;mutationEntity=null; }
        }
        // 粘贴中途异常仍处于同一服务器tick；预检确认的空白位置可安全记录为本轮夹具。
        if (placedStateIds==null) capturePlacedStates(level);
        if (controller!=null) {
            int[] anchor=activeLayout.controller();
            for (int i=0;i<placedStateIds.length;i++) {
                int[] p=activeLayout.blocks().get(i).pos();
                if (p[0]==anchor[0] && p[1]==anchor[1] && p[2]==anchor[2]) {
                    if (canClearOwnedCell(level,i,controller))
                        level.setBlockAndUpdate(controller,Blocks.AIR.defaultBlockState());
                    break;
                }
            }
        }
        int removed=0,preserved=0;
        for (int i=0;i<placedStateIds.length;i++) {
            BlockPos pos=worldPosition(activeLayout.blocks().get(i));
            BlockState current=level.getBlockState(pos);
            if (current.isAir()) continue;
            BlockState placed=Block.stateById(placedStateIds[i]);
            if (!placed.isAir() && canClearOwnedCell(level,i,pos)) {
                level.setBlock(pos,Blocks.AIR.defaultBlockState(),2);
                removed++;
            } else preserved++;
        }
        LogUtils.getLogger().info("[HK3-STRUCTURE70] 已清理夹具 {} 实体格={} 保留外部方块={}",activeLayout.key(),removed,preserved);
        ownsFixtureArea=false;placedStateIds=null;activeLayout=null;activeSettings=null;
        placedBlockEntities.clear();
        origin=controller=null;
        if (preserved>0) throw new IllegalStateException("验收场地存在外部替换方块，停止继续放置。");
    }

    /** 只记录并释放本轮新增加的票据；已有强制加载票据保持原状。 */
    private static void forceFixtureChunks(ServerLevel level) {
        BlockPos end=fixtureEnd();
        for (int x=Math.min(origin.getX(),end.getX())>>4;x<=Math.max(origin.getX(),end.getX())>>4;x++)
            for (int z=Math.min(origin.getZ(),end.getZ())>>4;z<=Math.max(origin.getZ(),end.getZ())>>4;z++) {
                long packed=ChunkPos.asLong(x,z);
                if (!level.getForcedChunks().contains(packed)) {
                    FORCED.add(packed);
                    level.setChunkForced(x,z,true);
                }
            }
    }

    private static void releaseChunks(ServerLevel level) {
        for (long packed:FORCED) {
            ChunkPos chunk=new ChunkPos(packed);
            level.setChunkForced(chunk.x,chunk.z,false);
        }
        FORCED.clear();
    }
}
