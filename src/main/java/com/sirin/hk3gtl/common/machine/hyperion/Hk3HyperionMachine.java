package com.sirin.hk3gtl.common.machine.hyperion;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.fancy.IFancyUIProvider;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IDisplayUIMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextFieldWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderManagementPage;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.sirin.hk3gtl.common.multiblock.build.Hk3HyperionIntegrityTask;
import com.sirin.hk3gtl.common.multiblock.build.Hk3InterfaceChunks;
import com.sirin.hk3gtl.common.multiblock.build.Hk3BuildPlan;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public final class Hk3HyperionMachine extends com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine implements IDisplayUIMachine, com.sirin.hk3gtl.common.multiblock.build.Hk3IntegrityHost {
    private static final Set<Hk3HyperionMachine> LOADED=ConcurrentHashMap.newKeySet();
    private Hk3HyperionIntegrityTask integrity;
    private Hk3BuildPlan verifiedPlan;
    private Set<BlockPos> interfaces=Set.of();
    private Hk3InterfaceChunks interfaceChunks;
    private boolean verified;
    private Direction verifiedFacing;
    private String integrityText="尚未检查舰体";
    @Persisted private String navigationDimension="minecraft:overworld";
    @Persisted private int navigationX,navigationY=82,navigationZ;

    public Hk3HyperionMachine(IMachineBlockEntity holder) {
        super(holder,"H01");
    }
    @Override public MultiblockControllerMachine integrityController() {return this;}
    @Override public void acceptVerifiedPlan(Hk3BuildPlan plan){verifiedPlan=plan;}
    @Override public void acceptVerifiedInterfaces(Set<BlockPos> positions){interfaces=positions;}
    @Override public void acceptInterfaceChunks(Hk3InterfaceChunks chunks){interfaceChunks=chunks;}
    @Override public Set<BlockPos> verifiedInterfaces(){return interfaces;}

    @Override public void onLoad() {
        super.onLoad();
        if(getLevel() instanceof ServerLevel) {verified=false;onStructureInvalid();LOADED.add(this);subscribeServerTick(this::integrityTick);}
    }
    @Override public void onUnload() {
        LOADED.remove(this);onStructureInvalid();
        if(getLevel() instanceof ServerLevel level)MultiblockWorldSavedData.getOrCreate(level).removeMapping(getMultiblockState());
        super.onUnload();
    }
    @Override public void onStructureInvalid() {
        super.onStructureInvalid();verified=false;verifiedPlan=null;interfaces=Set.of();clearIntegrity();
        if(interfaceChunks!=null){interfaceChunks.close();interfaceChunks=null;}
        integrityText="舰体未成型，请检查";
    }
    @Override public void onPartUnload() {onStructureInvalid();super.onPartUnload();}
    @Override public void asyncCheckPattern(long periodID) { }
    @Override public boolean verified() {return hasVerifiedHull();}
    @Override protected boolean productionReady(GTRecipe recipe) {
        return !Hk3HyperionJumpData.moving(this)&&super.productionReady(recipe);
    }
    public boolean hasVerifiedHull() {return verified&&verifiedFacing==getFrontFacing();}
    public void requestIntegrityCheck() {
        if(!(getLevel() instanceof ServerLevel)||Hk3UniversalTerminalBuilder.isBuilding(this)||Hk3HyperionJumpData.moving(this))return;
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
        if(!checkPatternWithLock()) {integrityFailed("接口不符或未加载，请检查通用舱位");return;}
        onStructureFormed();
        if(!isFormed())return;
        com.sirin.hk3gtl.common.easter.Hk3EggProduction.receipt(this,17);
        var saved=MultiblockWorldSavedData.getOrCreate((ServerLevel)getLevel());saved.addMapping(getMultiblockState());saved.removeAsyncLogic(this);
        integrityText="舰体已成型 · 可执行正式舰载工程工艺";
    }
    public Hk3LargeStructurePattern.Bounds hullBounds() {
        return hullBounds(getPos(),getFrontFacing());
    }
    public static Hk3LargeStructurePattern.Bounds hullBounds(BlockPos anchor,Direction facing) {
        var r=Hk3UniversalTerminalBuilder.rotation(Direction.EAST,facing);
        var a=new BlockPos(-1061,-82,-274).rotate(r).offset(anchor);
        var b=new BlockPos(83,157,274).rotate(r).offset(anchor);
        return new Hk3LargeStructurePattern.Bounds(new BlockPos(Math.min(a.getX(),b.getX()),a.getY(),Math.min(a.getZ(),b.getZ())),
                new BlockPos(Math.max(a.getX(),b.getX()),b.getY(),Math.max(a.getZ(),b.getZ())));
    }
    public static boolean containsVerifiedInterior(ServerLevel level,BlockPos pos) {
        for(var ship:LOADED)if(ship.getLevel()==level&&ship.containsInterior(pos))return true;
        return false;
    }
    public boolean containsInterior(BlockPos pos) {
        if(!isFormed()||!hasVerifiedHull()||!hullBounds().contains(pos))return false;
        var rotation=Hk3UniversalTerminalBuilder.rotation(getFrontFacing(),Direction.EAST);
        var local=pos.subtract(getPos()).rotate(rotation);
        return Hk3HyperionInterior.contains(local.getX()+1061,local.getY()+82,local.getZ()+274);
    }
    public static void blockChanged(ServerLevel level,BlockPos pos) {
        for(var ship:LOADED)if(ship.getLevel()==level && (ship.verified||ship.integrity!=null)
                && !Hk3UniversalTerminalBuilder.isBuilding(ship) && ship.hullBounds().contains(pos)) {
            var rotation=Hk3UniversalTerminalBuilder.rotation(ship.getFrontFacing(),Direction.EAST);
            var local=pos.subtract(ship.getPos()).rotate(rotation);
            if(ship.verifiedPlan!=null&&!ship.verifiedPlan.contains(local.getX(),local.getY(),local.getZ()))continue;
            ship.integrityFailed("舰体发生变化，需重新检查："+pos.toShortString());
            MultiblockWorldSavedData.getOrCreate(level).removeMapping(ship.getMultiblockState());
        }
    }

    @Override public void addDisplayText(List<Component> textList) {
        super.addDisplayText(textList);textList.add(Component.literal(integrityText));
    }
    @Override public List<IFancyUIProvider> getSubTabs() {
        var tabs=new ArrayList<>(super.getSubTabs());
        tabs.add(new Hk3WonderManagementPage(this,this::createManagementWidget));return tabs;
    }
    private Widget createManagementWidget(Player player) {
        return new WidgetGroup(0,0,300,275)
                .addWidget(new LabelWidget(8, 8, "hk3gtl.hyperion.title"))
                .addWidget(new LabelWidget(8, 25, "hk3gtl.hyperion.size"))
                .addWidget(new LabelWidget(8, 40, "hk3gtl.hyperion.anchor"))
                .addWidget(new LabelWidget(8, 70, "hk3gtl.hyperion.creative"))
                .addWidget(new LabelWidget(8, 84, () -> Hk3UniversalTerminalBuilder.isBuilding(this)?"正在搭建，完成后自动检查":integrityText))
                .addWidget(new LabelWidget(8, 98, () -> Hk3UniversalTerminalBuilder.progress(this)))
                .addWidget(new ButtonWidget(8, 117, 138, 20,
                        new GuiTextureGroup(GuiTextures.BUTTON, new TextTexture("hk3gtl.hyperion.build")), click -> {
                    if (!click.isRemote&&!Hk3HyperionJumpData.moving(this)) Hk3UniversalTerminalBuilder.use(player, getMultiblockState(), null);
                }))
                .addWidget(new ButtonWidget(151, 117, 60, 20,
                        new GuiTextureGroup(GuiTextures.BUTTON, new TextTexture("hk3gtl.hyperion.cancel")), click -> {
                    if (!click.isRemote) Hk3UniversalTerminalBuilder.cancel(player, this);
                }))
                .addWidget(new ButtonWidget(216,117,76,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture("hk3gtl.hyperion.check")),click -> {
                    if(!click.isRemote)requestIntegrityCheck();
                }))
                .addWidget(new ButtonWidget(8,141,284,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture("启停舰载工程")),click->{
                    if(!click.isRemote&&!Hk3HyperionJumpData.moving(this))getRecipeLogic().setWorkingEnabled(!getRecipeLogic().isWorkingEnabled());
                }))
                .addWidget(new LabelWidget(8,165,()->"舰载工程："+(getRecipeLogic().isActive()?"运行中":"等待物料、供能或许可")))
                .addWidget(new LabelWidget(8,181,"hk3gtl.hyperion.navigation"))
                .addWidget(new TextFieldWidget(8,195,284,16,()->navigationDimension,value->{navigationDimension=value;markNavigationDirty();})
                        .setResourceLocationOnly().setMaxStringLength(128))
                .addWidget(new TextFieldWidget(8,215,90,16,()->Integer.toString(navigationX),value->{navigationX=Integer.parseInt(value);markNavigationDirty();})
                        .setNumbersOnly(-30_000_000,30_000_000))
                .addWidget(new TextFieldWidget(105,215,90,16,()->Integer.toString(navigationY),value->{navigationY=Integer.parseInt(value);markNavigationDirty();})
                        .setNumbersOnly(-20_000,20_000))
                .addWidget(new TextFieldWidget(202,215,90,16,()->Integer.toString(navigationZ),value->{navigationZ=Integer.parseInt(value);markNavigationDirty();})
                        .setNumbersOnly(-30_000_000,30_000_000))
                .addWidget(new ButtonWidget(8,235,284,20,new GuiTextureGroup(GuiTextures.BUTTON,new TextTexture("hk3gtl.hyperion.jump")),click->{
                    if(!click.isRemote)Hk3HyperionJumpData.get(getLevel().getServer()).start(this,(net.minecraft.server.level.ServerPlayer)player,
                            navigationDimension,new BlockPos(navigationX,navigationY,navigationZ));
                }))
                .addWidget(new LabelWidget(8,259,()->isRemote()?"":Hk3HyperionJumpData.get(getLevel().getServer()).status()));
    }
    private void markNavigationDirty() {if(!isRemote())((net.minecraft.world.level.block.entity.BlockEntity)getHolder()).setChanged();}
}
