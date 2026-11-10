package com.sirin.hk3gtl.common.machine.hyperion;


/**
 * 【文件职责】
 * - 定义 Hk3HyperionMachine 机器行为与结构逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.UITemplate;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IDisplayUIMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.sirin.hk3gtl.common.multiblock.build.Hk3HyperionIntegrityTask;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/** 中文说明：该处说明已按当前代码行为整理。*/
public final class Hk3HyperionMachine extends MultiblockControllerMachine implements IDisplayUIMachine, com.sirin.hk3gtl.common.multiblock.build.Hk3IntegrityHost {
    private static final Set<Hk3HyperionMachine> LOADED=ConcurrentHashMap.newKeySet();
    private Hk3HyperionIntegrityTask integrity;
    private boolean verified;
    private Direction verifiedFacing;
    private String integrityText="尚未检查舰体";

    public Hk3HyperionMachine(IMachineBlockEntity holder) {
        super(holder);
    }
    @Override public MultiblockControllerMachine integrityController() {return this;}

    @Override public void onLoad() {
        super.onLoad();
        if(getLevel() instanceof ServerLevel) {verified=false;onStructureInvalid();LOADED.add(this);subscribeServerTick(this::integrityTick);}
    }
    @Override public void onUnload() {
        LOADED.remove(this);onStructureInvalid();
        if(getLevel() instanceof ServerLevel level)MultiblockWorldSavedData.getOrCreate(level).removeMapping(getMultiblockState());
        super.onUnload();
    }
    @Override public void onStructureInvalid() {super.onStructureInvalid();verified=false;clearIntegrity();integrityText="舰体未成型，请检查";}
    @Override public void onPartUnload() {onStructureInvalid();super.onPartUnload();}
    @Override public void asyncCheckPattern(long periodID) { }
    public boolean hasVerifiedHull() {return verified&&verifiedFacing==getFrontFacing();}
    public void requestIntegrityCheck() {
        if(!(getLevel() instanceof ServerLevel)||Hk3UniversalTerminalBuilder.isBuilding(this))return;
        onStructureInvalid();
        var saved=MultiblockWorldSavedData.getOrCreate((ServerLevel)getLevel());saved.removeMapping(getMultiblockState());
        integrity=new Hk3HyperionIntegrityTask(this);integrityText="准备舰体检查…";
    }
    private void integrityTick() {
        if(integrity==null)return;
        try {integrityText=integrity.progress();integrity.tick();}
        catch(RuntimeException failure) {com.mojang.logging.LogUtils.getLogger().error("休伯利安分批舰体检查失败",failure);integrityFailed("舰体检查失败，详见日志");}
    }
    private void clearIntegrity() {var old=integrity;integrity=null;if(old!=null)old.close();}
    public void integrityFailed(String text) {onStructureInvalid();integrityText=text;}
    public void integrityPassed(Direction facing) {
        clearIntegrity();verified=true;verifiedFacing=facing;
        if(!checkPatternWithLock()) {verified=false;integrityText="接口不符或未加载，请检查通用舱位";return;}
        onStructureFormed();
        var saved=MultiblockWorldSavedData.getOrCreate((ServerLevel)getLevel());saved.addMapping(getMultiblockState());saved.removeAsyncLogic(this);
        integrityText="舰体已成型 · 工程运行尚未开放";
    }
    public Hk3LargeStructurePattern.Bounds hullBounds() {
        var r=Hk3UniversalTerminalBuilder.rotation(Direction.EAST,getFrontFacing());
        var a=new BlockPos(-1061,-82,-274).rotate(r).offset(getPos());
        var b=new BlockPos(83,157,274).rotate(r).offset(getPos());
        return new Hk3LargeStructurePattern.Bounds(new BlockPos(Math.min(a.getX(),b.getX()),a.getY(),Math.min(a.getZ(),b.getZ())),
                new BlockPos(Math.max(a.getX(),b.getX()),b.getY(),Math.max(a.getZ(),b.getZ())));
    }
    public static void blockChanged(ServerLevel level,BlockPos pos) {
        for(var ship:LOADED)if(ship.getLevel()==level && (ship.verified||ship.integrity!=null)
                && !Hk3UniversalTerminalBuilder.isBuilding(ship) && ship.hullBounds().contains(pos)) {
            ship.integrityFailed("舰体发生变化，需重新检查："+pos.toShortString());
            MultiblockWorldSavedData.getOrCreate(level).removeMapping(ship.getMultiblockState());
        }
    }

    /** 2026-11-08：原稿舰体创造搭建入口，不授予工程运行、研究或毕业资格。 */
    @Override public ModularUI createUI(Player player) {
        return new ModularUI(300, 238, this, player).background(GuiTextures.BACKGROUND)
                .widget(new LabelWidget(8, 8, "hk3gtl.hyperion.title"))
                .widget(new LabelWidget(8, 25, "hk3gtl.hyperion.size"))
                .widget(new LabelWidget(8, 40, "hk3gtl.hyperion.anchor"))
                .widget(new LabelWidget(8, 55, "hk3gtl.hyperion.height"))
                .widget(new LabelWidget(8, 70, "hk3gtl.hyperion.creative"))
                .widget(new LabelWidget(8, 84, () -> Hk3UniversalTerminalBuilder.isBuilding(this)?"正在搭建，完成后自动检查":integrityText))
                .widget(new LabelWidget(8, 98, () -> Hk3UniversalTerminalBuilder.progress(this)))
                .widget(new ButtonWidget(8, 117, 138, 20,
                        new GuiTextureGroup(GuiTextures.BUTTON, new TextTexture("hk3gtl.hyperion.build")), click -> {
                    if (!click.isRemote) Hk3UniversalTerminalBuilder.use(player, getMultiblockState(), null);
                }))
                .widget(new ButtonWidget(151, 117, 60, 20,
                        new GuiTextureGroup(GuiTextures.BUTTON, new TextTexture("hk3gtl.hyperion.cancel")), click -> {
                    if (!click.isRemote) Hk3UniversalTerminalBuilder.cancel(player, this);
                }))
                .widget(new ButtonWidget(216,117,76,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture("hk3gtl.hyperion.check")),click -> {
                    if(!click.isRemote)requestIntegrityCheck();
                }))
                .widget(UITemplate.bindPlayerInventory(player.getInventory(), GuiTextures.SLOT, 62, 153, true));
    }
}
