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

 






 






 






 






@Mod.EventBusSubscriber(modid="hk3gtl", bus=Mod.EventBusSubscriber.Bus.FORGE)
 




public final class Hk3ApprovedStructureCommands {
    private Hk3ApprovedStructureCommands() {}

    public static BlockPos controller(String id) {
        int[] p=com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.get(id).controller();
        return new BlockPos(p[0],p[1],p[2]);
    }

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
            source.sendFailure(Component.literal("此指令需要单独配置的验收环境，以及开启作弊的超平坦测试存档。"));
            return 0;
        }
        int count = com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture.IDS.size();
        String scope=id==null ? "全部"+count+"种正式结构的"+(count*4)+"个朝向"
                : rotation==null ? id+"的四个朝向" : id+"的"+direction+"朝向";
        source.sendSuccess(() -> Component.literal("开始验收"+scope+"；临时夹具每座完成后清理，可用/hk3structure verify-cancel取消。"),false);
        return 1;
    }

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
