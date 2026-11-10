package com.sirin.hk3gtl.common.machine.research;

/**
 * 【文件职责／本轮边界】有电且区块加载时向绑定人的个人账户产点，不再要求本人在线。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：有电且区块加载时向绑定人的个人账户产点，不再要求本人在线。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 【变更记录 · 内测5修订100】2026-09-29：落实已批准研究费用、三公式及离线账户规则。 */

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.TieredEnergyMachine;
import com.gregtechceu.gtceu.api.machine.feature.IFancyUIMachine;
import com.gregtechceu.gtceu.api.machine.feature.IMachineLife;
import com.lowdragmc.lowdraglib.gui.widget.LabelWidget;
import com.lowdragmc.lowdraglib.gui.widget.SlotWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.BlockHitResult;
import java.util.UUID;

/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #2】2026-09-30 02:17:47（第2次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
public final class Hk3ResearchComputerMachine extends TieredEnergyMachine implements IFancyUIMachine, IMachineLife {
    private static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(Hk3ResearchComputerMachine.class,
            TieredEnergyMachine.MANAGED_FIELD_HOLDER);
    @Persisted private UUID owner;
    @Persisted private final ItemStackTransfer circuit;
    private static final String[] CIRCUITS = {"hbv", "hcv", "hrv", "hdv",
            "qsv", "qcv", "qev", "qav", "imv", "icv",
            "irv", "iwv", "wfv", "wsv", "civ", "cev"};
    private static final java.util.List<TagKey<Item>> EXTENDED = java.util.Arrays.stream(CIRCUITS)
            .map(id -> TagKey.create(Registries.ITEM, new ResourceLocation("forge", "circuits/" + id))).toList();
    private static final TagKey<Item> MAX_CIRCUIT = TagKey.create(Registries.ITEM, new ResourceLocation("gtceu", "circuits/max"));
    private static final TagKey<Item> FORGE_MAX = TagKey.create(Registries.ITEM, new ResourceLocation("forge", "circuits/max"));

    /** 中文说明：该处说明已按当前代码行为整理。*/
    public Hk3ResearchComputerMachine(IMachineBlockEntity holder) {
        super(holder, GTValues.MAX);
        circuit = new ItemStackTransfer(1) {
            @Override public int getSlotLimit(int slot) { return 1; }
        };
        circuit.setFilter(stack -> !stack.isEmpty() && circuitLevel(stack.copyWithCount(1)) >= 0);
        circuit.setOnContentsChanged(this::markDirty);
    }

    /** 继承GT能源存档并追加所有者与电路槽；不另写重复的BE存档钩子。 / Extend GT managed persistence for owner and inventory. */
    @Override public ManagedFieldHolder getFieldHolder() { return FIELDS; }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote()) subscribeServerTick(this::producePoints);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public void onMachinePlaced(LivingEntity player, ItemStack stack) {
        if (!isRemote() && owner == null && player instanceof ServerPlayer serverPlayer) {
            owner = serverPlayer.getUUID(); markDirty();
        }
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public boolean shouldOpenUI(Player player, InteractionHand hand, BlockHitResult hit) {
        return player.level().isClientSide || (owner != null && owner.equals(player.getUUID()));
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public Widget createUIWidget() {
        WidgetGroup group = new WidgetGroup(0, 0, 172, 70);
        group.addWidget(new LabelWidget(8, 7, "hk3gtl.research.computer.circuit"));
        group.addWidget(new SlotWidget(circuit, 0, 8, 25, true, true).setBackgroundTexture(GuiTextures.SLOT));
        group.addWidget(new LabelWidget(8, 51, () -> {
            ServerPlayer player = ownerPlayer();
            return player == null ? "" : net.minecraft.network.chat.Component.translatable("hk3gtl.research.computer.balance",
                    Hk3ResearchData.get(player).points(owner).toString()).getString();
        }));
        return group;
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private ServerPlayer ownerPlayer() {
        return owner == null || getLevel() == null || getLevel().getServer() == null ? null
                : getLevel().getServer().getPlayerList().getPlayer(owner);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private String facility() { return getLevel().dimension().location() + "@" + getPos().asLong(); }

    /** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
    private void producePoints() {
        if (isInValid()) return;
        if (owner == null || getLevel() == null || getLevel().getServer() == null) return;
        var server = getLevel().getServer();
        int level = circuitLevel(circuit.getStackInSlot(0));
        if (level < 0) return;
        long eut = Hk3Values.VA_LONG[GTValues.MAX];
        Hk3ResearchData.get(server).tickComputer(owner, facility(), server.overworld().getGameTime(), level, true, () -> {
            if (energyContainer.getEnergyStored() < eut) return false;
            long removed = energyContainer.removeEnergy(eut);
            if (removed != eut) {
                if (removed > 0) energyContainer.addEnergy(removed);
                return false;
            }
            return true;
        });
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override public void onMachineRemoved() {
        if (!isRemote() && getLevel() != null && getLevel().getServer() != null && owner != null) {
            Hk3ResearchData.get(getLevel().getServer()).removeComputer(owner, facility());
        }
        clearInventory(circuit);
    }

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static int circuitLevel(ItemStack stack) {
        if (stack.isEmpty() || stack.getCount() != 1) return -1;
        for (int n = EXTENDED.size() - 1; n >= 0; n--) if (stack.is(EXTENDED.get(n))) return n + 1;
        return stack.is(MAX_CIRCUIT) || stack.is(FORGE_MAX) ? 0 : -1;
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
