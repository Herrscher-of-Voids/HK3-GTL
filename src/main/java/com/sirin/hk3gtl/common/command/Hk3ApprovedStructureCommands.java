package com.sirin.hk3gtl.common.command;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 中文说明：该处说明已按当前代码行为整理。*/
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
 * 新增：放置子命令自动包含i04/i05，核验提示改为六台；不自动放置或执行验收。
 * 修改：沿获批逐格资源接入23×27×23稳定塔与27×19×23再生中心，数量与方向由正式资源确定。
 * 用途：统一成型、放置模板和诊断坐标；不改变研究费用，不启动游戏，不视为成型验收。
 */
/**
 * 【变更记录 #3】2026-10-15 01:51:56（第3次备注 · 内测5修订157）
 * 删除：验收入口只能一次运行全部建筑的限制；全部四向入口及历史备注保留。
 * 新增：verify后按批准建筑键选择四向或north/east/south/west单朝向，以及verify-cancel主动清理入口。
 * 修改：命令统一调用Hk3ApprovedStructureRuntimeCheck的受限入口，中文提示明确增强版2.7实例与测试存档条件。
 * 用途：让实际整合包可分批验收与测量内存；单朝向结果只计本轮，不代表21种建筑全部通过。
 */
/**
 * 【变更记录 #4】2026-10-20 00:55:29（香港时间；第4次备注 · 修订172）
 * 删除：结构验收拒绝提示中失效的增强版2.7目录名；全部历史备注保留。
 * 新增：提示当前增强版2.9唯一测试实例的完整绝对路径。
 * 修改：提示与Hk3ApprovedStructureRuntimeCheck的路径门禁一致，其余命令及权限判断不变。
 * 用途：明确被拒绝时应使用的实际实例，保留主世界、创造OP、作弊、超平坦及专用存档要求。
 */
@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.FORGE)
/**
 * 【变更记录 #5】2026-10-26 20:41:55（第5次备注 · 修订177）
 * - 删除：验收提示中固定21形态和增强版2.9的旧口径；新增：按批准清单动态统计。
 * - 修改：当前提示指向唯一增强版2.9.2实例；用途：真实控制器与新增十份模板共用入口。
 */
public final class Hk3ApprovedStructureCommands {
    private Hk3ApprovedStructureCommands() {}

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static BlockPos controller(String id) {
        int[] p=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(id).controller();
        return new BlockPos(p[0],p[1],p[2]);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @SubscribeEvent
    public static void register(RegisterCommandsEvent event) {
        var root=Commands.literal("hk3structure").requires(s -> s.hasPermission(2));
        root.then(Commands.literal("clear-snow").then(Commands.argument("controller",BlockPosArgument.blockPos()).executes(c -> {
            if (!(c.getSource().getEntity() instanceof net.minecraft.server.level.ServerPlayer player)) {
                c.getSource().sendFailure(Component.literal("请由创造模式OP玩家指定控制器坐标除雪。")); return 0;
            }
            return Hk3StructureSnowCleanup.start(player,BlockPosArgument.getLoadedBlockPos(c,"controller"));
        })));
        var place=Commands.literal("place");
        for (String id : com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.IDS) {
            place.then(Commands.literal(id).then(Commands.argument("origin",BlockPosArgument.blockPos()).executes(c -> {
                var source=c.getSource();
                if (source.getEntity() instanceof net.minecraft.server.level.ServerPlayer p && !p.isCreative()) {
                    source.sendFailure(Component.translatable("hk3gtl.structure.creative_required")); return 0;
                }
                try {
                    BlockPos pos=place(source,id,BlockPosArgument.getBlockPos(c,"origin"),Rotation.NONE);
                    source.sendSuccess(() -> Component.translatable("hk3gtl.structure.placed",id,pos.toShortString()),false);
                    return 1;
                } catch (IllegalArgumentException | IllegalStateException e) {
                    source.sendFailure(Component.literal(e.getMessage())); return 0;
                }
            })));
        }
        // 验收只能在指定实例专用存档由创造模式OP显式启动，不允许开发环境替代。
        // 中文备注：该处说明已按当前代码行为整理。
        var verify=Commands.literal("verify").executes(c -> startVerification(c.getSource(),null,null,null));
        String[] directions={"north","east","south","west"};
        Rotation[] rotations={Rotation.NONE,Rotation.CLOCKWISE_90,Rotation.CLOCKWISE_180,Rotation.COUNTERCLOCKWISE_90};
        for (String id:com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.IDS) {
            var building=Commands.literal(id).executes(c -> startVerification(c.getSource(),id,null,null));
            for (int i=0;i<directions.length;i++) {
                String direction=directions[i];
                Rotation rotation=rotations[i];
                building.then(Commands.literal(direction)
                        .executes(c -> startVerification(c.getSource(),id,rotation,direction)));
            }
            verify.then(building);
        }
        root.then(verify).then(Commands.literal("verify-cancel").executes(c -> {
            boolean cancelled=c.getSource().getEntity() instanceof net.minecraft.server.level.ServerPlayer player
                    && Hk3ApprovedStructureRuntimeCheck.cancel(player);
            if (!cancelled) c.getSource().sendFailure(Component.literal("没有正在运行的正式结构验收，或当前来源不是有权限的玩家。"));
            return cancelled?1:0;
        }));
        root.then(Commands.literal("verify-spectrum").executes(c -> {
            boolean started=c.getSource().getEntity() instanceof net.minecraft.server.level.ServerPlayer player
                    && Hk3SpectrumRuntimeCheck.begin(player);
            c.getSource().sendSuccess(() -> Component.literal(started ? "开始光谱研究专用验收。"
                    : "需要光谱验收指定实例、新建hk3gtl-research64专用创造存档及空白测试区。"),false);
            return started?1:0;
        }));
        root.then(place).then(Commands.literal("check").then(Commands.argument("controller",BlockPosArgument.blockPos()).executes(c -> {
            var source=c.getSource();var pos=BlockPosArgument.getLoadedBlockPos(c,"controller");
            if (!(MetaMachine.getMachine(source.getLevel(),pos) instanceof Hk3WorkableMultiblockMachine machine)) {
                source.sendFailure(Component.translatable("hk3gtl.structure.no_controller"));return 0;
            }
            // 只读已成型标志；手动checkPattern会改变匹配上下文，因此不在诊断中调用。
            // 中文备注：该处说明已按当前代码行为整理。
            source.sendSuccess(() -> Component.translatable("hk3gtl.structure.status",machine.isFormed(),machine.getParts().size()),false);
            return machine.isFormed()?1:0;
        })));
        event.getDispatcher().register(root);
    }

    /** 三种验收范围共用身份校验与提示，拒绝时返回失败，不向控制台开放玩家夹具入口。 */
    private static int startVerification(CommandSourceStack source,String id,Rotation rotation,String direction) {
        boolean started=false;
        if (source.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)
            started=id==null ? Hk3ApprovedStructureRuntimeCheck.begin(player)
                    : rotation==null ? Hk3ApprovedStructureRuntimeCheck.begin(player,id)
                    : Hk3ApprovedStructureRuntimeCheck.begin(player,id,rotation);
        if (!started) {
            source.sendFailure(Component.literal("需要增强版2.9.2指定实例 C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft 的主世界、创造模式OP、允许作弊的超平坦存档；存档名须以hk3gtl-structure70-开头，且不能重复启动验收。"));
            return 0;
        }
        int count = com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.IDS.size();
        String scope=id==null ? "全部"+count+"种正式结构的"+(count*4)+"个朝向"
                : rotation==null ? id+"的四个朝向" : id+"的"+direction+"朝向";
        source.sendSuccess(() -> Component.literal("开始验收"+scope+"；临时夹具每座完成后清理，可用/hk3structure verify-cancel取消。"),false);
        return 1;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public static BlockPos place(CommandSourceStack source,String id,BlockPos origin,Rotation rotation) {
        BlockPos controller=controller(id);
        ServerLevel level=source.getLevel();
        StructureTemplate template=level.getStructureManager().get(new ResourceLocation("hk3gtl","approved/"+id))
                .orElseThrow(() -> new IllegalStateException("Missing approved template: "+id));
        Vec3i size=template.getSize();
        int[] approvedSize=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(id).size();
        if (!size.equals(new Vec3i(approvedSize[0],approvedSize[1],approvedSize[2])))
            throw new IllegalStateException("Unexpected approved template dimensions: "+size);
        var settings=new StructurePlaceSettings().setRotation(rotation).setIgnoreEntities(true);
        BlockPos end=StructureTemplate.calculateRelativePosition(settings,new BlockPos(size.getX()-1,size.getY()-1,size.getZ()-1)).offset(origin);
        for (BlockPos pos:BlockPos.betweenClosed(origin,end)) {
            if (level.isOutsideBuildHeight(pos) || !level.getWorldBorder().isWithinBounds(pos))
                throw new IllegalArgumentException("Outside build limits: "+pos.toShortString());
            if (!level.isEmptyBlock(pos)) throw new IllegalArgumentException("Area occupied at "+pos.toShortString()+"; nothing placed.");
        }
        if (!template.placeInWorld(level,origin,origin,settings,level.random,3))
            throw new IllegalStateException("Template placement failed: "+id);
        BlockPos pos=StructureTemplate.calculateRelativePosition(settings,controller).offset(origin);
        if (!(MetaMachine.getMachine(level,pos) instanceof Hk3WorkableMultiblockMachine machine))
            throw new IllegalStateException("Controller missing after template placement: "+pos);
        // 正式四机均朝模板-Z；旋转放置时同步主控朝向，避免结构正确而成型坐标反转。
        machine.setFrontFacing(rotation.rotate(net.minecraft.core.Direction.NORTH));
        if (source.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)
            machine.onMachinePlaced(player,new ItemStack(machine.getBlockState().getBlock()));
        return pos;
    }
}
