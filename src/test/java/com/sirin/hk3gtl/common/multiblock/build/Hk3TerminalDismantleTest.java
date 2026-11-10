package com.sirin.hk3gtl.common.multiblock.build;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/** 生产拆除顺序与安全入口合同回归；真实Forge保护和仓室掉落仍须实例验收。 */
public final class Hk3TerminalDismantleTest {
    private static final String ROOT = "src/main/java/com/sirin/hk3gtl/";

    public static void main(String[] args) throws Exception {
        int[] heights={0,2,1,0,2,1}, phases={0,0,1,2,2,1};
        var order = new Hk3BuildOrder(heights.length,3,0,i -> heights[i],i -> phases[i]);
        while (!order.step()) { }
        int[] actual = new int[heights.length];
        for (int i=0;i<actual.length;i++) actual[i]=order.dismantleIndex(i);
        check(Arrays.equals(actual,new int[]{4,3,5,2,1,0}),"先附着、后重力、最后高至低承重主体，且每格恰好一次");
        reject(() -> order.dismantleIndex(-1)); reject(() -> order.dismantleIndex(actual.length));
        var unready = new Hk3BuildOrder(1,1,0,i -> 0,i -> 0);
        reject(() -> unready.dismantleIndex(0));

        String entry=read("mixin/gtlcore/Hk3TerminalDismantleMixin.java");
        contains(entry,"UltimateTerminalBehavior.class","method = \"dismantleMultiblock\"","@At(\"HEAD\")",
                "getNamespace()","Hk3UniversalTerminalBuilder.use","callback.cancel()");
        String operation=read("common/multiblock/build/Hk3DismantleOperation.java");
        contains(operation,"pos.equals(controller.getPos())","actual.isAir()","shouldPreserveDuringDismantle",
                "machine instanceof IMultiController","plan.dismantlePort(index) == null","setting.isNoHatchMode()",
                "part.getControllers().stream().anyMatch(other -> other != controller)","rotation.rotate(face)",
                "actual == expected","predicate.test(probe)","ForgeHooks.onBlockBreakEvent",
                "!player.isSpectator()","player.getAbilities().mayBuild","mayInteract(player,pos)",
                "getWorldBorder().isWithinBounds(pos)","getDestroySpeed","Block.getDrops",
                "level.getBlockEntity(pos) != entity","!active.getAsBoolean()","mutationFailure",
                "if (!level.getBlockState(pos).isAir())");
        check(operation.indexOf("Block.getDrops") < operation.indexOf("level.setBlock"),"移除前读取真实仓室NBT与掉落");
        check(operation.indexOf("level.setBlock") < operation.indexOf("materials.deliver"),"世界成功移除后才结算掉落");
        String jobs=read("common/multiblock/build/Hk3UniversalTerminalBuilder.java");
        contains(jobs,"order.dismantleIndex(at)","plan::prepareStep","System.nanoTime() < deadline",
                "Hk3W01BuildBudget.nanos","Hk3W01BuildBudget.BUILD_STEPS","job.removeTickets()","job.plan.close()",
                "job.controller.getMultiblockState()).hk3gtl$clean()","previous.dismantle != setting.isDismantleMode()",
                "PlayerLoggedOutEvent","ChunkEvent.Unload","ServerStoppingEvent","controllerUnloaded",
                "JOBS.get(level.getServer()) == this && valid()","job.preparation.close()");
        String plans=read("common/multiblock/build/Hk3BuildPlans.java");
        contains(plans,"large.dismantlePort","matches[port.z][port.y][port.x]","predicate.isAny()",
                "portPredicates.put(at,predicate)","portFaces.put(at,port.face)");
        String config=Files.readString(Path.of("src/main/resources/hk3gtl.mixins.json"),StandardCharsets.UTF_8);
        contains(config,"gtlcore.Hk3TerminalDismantleMixin","gtceu.Hk3BuildPatternAccess");
        System.out.println("终端拆除：生产逆序算法、主控/仓室/权限守卫及预算/清理入口合同通过；未运行游戏。");
    }

    private static String read(String path) throws Exception { return Files.readString(Path.of(ROOT+path),StandardCharsets.UTF_8); }
    private static void contains(String source,String... tokens) {
        for (String token:tokens) check(source.contains(token),"缺少必要安全入口："+token);
    }
    private static void check(boolean ok,String message) { if (!ok) throw new AssertionError(message); }
    private static void reject(Runnable action) {
        try { action.run(); throw new AssertionError("无效拆除索引未拦截"); }
        catch (IndexOutOfBoundsException | IllegalStateException expected) { }
    }
}
