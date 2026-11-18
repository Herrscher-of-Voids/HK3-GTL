package com.sirin.hk3gtl.common.machine.research;

/**
 * 【文件职责／本轮边界】有电且区块加载时向绑定人的个人账户产点，不再要求本人在线。
 */


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
import com.sirin.hk3gtl.common.capability.Hk3EnergyTick;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
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
import java.math.BigInteger;
import java.util.List;
import java.util.UUID;

public final class Hk3ResearchComputerMachine extends TieredEnergyMachine implements IFancyUIMachine, IMachineLife {
    private static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(Hk3ResearchComputerMachine.class,
            TieredEnergyMachine.MANAGED_FIELD_HOLDER);
    @Persisted private UUID owner;
    @Persisted private final ItemStackTransfer circuit;
    private Hk3EnergyTick computerRefund;
    private static final String[] CIRCUITS = {"hbv", "hcv", "hrv", "hdv",
            "qsv", "qcv", "qev", "qav", "imv", "icv",
            "irv", "iwv", "wfv", "wsv", "civ", "cev"};
    private static final java.util.List<TagKey<Item>> EXTENDED = java.util.Arrays.stream(CIRCUITS)
            .map(id -> TagKey.create(Registries.ITEM, new ResourceLocation("forge", "circuits/" + id))).toList();
    private static final TagKey<Item> MAX_CIRCUIT = TagKey.create(Registries.ITEM, new ResourceLocation("gtceu", "circuits/max"));
    private static final TagKey<Item> FORGE_MAX = TagKey.create(Registries.ITEM, new ResourceLocation("forge", "circuits/max"));

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

    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote()) subscribeServerTick(this::producePoints);
    }

    @Override public void onMachinePlaced(LivingEntity player, ItemStack stack) {
        if (!isRemote() && owner == null && player instanceof ServerPlayer serverPlayer) {
            owner = serverPlayer.getUUID(); markDirty();
        }
    }

    @Override public boolean shouldOpenUI(Player player, InteractionHand hand, BlockHitResult hit) {
        return player.level().isClientSide || (owner != null && owner.equals(player.getUUID()));
    }

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

    private ServerPlayer ownerPlayer() {
        return owner == null || getLevel() == null || getLevel().getServer() == null ? null
                : getLevel().getServer().getPlayerList().getPlayer(owner);
    }

    private String facility() { return getLevel().dimension().location() + "@" + getPos().asLong(); }

    private void producePoints() {
        if (isInValid()) return;
        if (owner == null || getLevel() == null || getLevel().getServer() == null) return;
        if (computerRefund == null) computerRefund = Hk3RefundJournal.resume(this);
        if (computerRefund != null) {
            if (!computerRefund.finish(false)) return;
            computerRefund = null;
        }
        var server = getLevel().getServer();
        int level = circuitLevel(circuit.getStackInSlot(0));
        if (level < 0) return;
        var cost = BigInteger.valueOf(Hk3Values.VA_LONG[GTValues.MAX]);
        var payment = Hk3RefundJournal.open(this);
        boolean advanced = false;
        try {
            advanced = Hk3ResearchData.get(server).tickComputer(owner, facility(),
                    server.overworld().getGameTime(), level, true,
                    () -> Hk3PortPayment.pay(List.of(Hk3PowerPorts.of(energyContainer)), cost, payment));
        } finally {
            if (!payment.finish(advanced)) computerRefund = payment;
        }
    }

    @Override public void onMachineRemoved() {
        if (!isRemote() && getLevel() != null && getLevel().getServer() != null && owner != null) {
            Hk3ResearchData.get(getLevel().getServer()).removeComputer(owner, facility());
        }
        clearInventory(circuit);
    }

    private static int circuitLevel(ItemStack stack) {
        if (stack.isEmpty() || stack.getCount() != 1) return -1;
        for (int n = EXTENDED.size() - 1; n >= 0; n--) if (stack.is(EXTENDED.get(n))) return n + 1;
        return stack.is(MAX_CIRCUIT) || stack.is(FORGE_MAX) ? 0 : -1;
    }
}

