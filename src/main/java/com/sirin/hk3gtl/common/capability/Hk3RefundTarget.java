package com.sirin.hk3gtl.common.capability;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.trait.MachineTrait;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.server.ServerLifecycleHooks;
import com.sirin.hk3gtl.common.util.Hk3LedgerValidation;

/** 退款固定到原维度、方块实例和标准仓室；不加载区块、不向同坐标的新机器退款。 */
public record Hk3RefundTarget(MinecraftServer server, CompoundTag address) {
    private static final String ID = "Hk3RefundIdentity";

    public static String key(MetaMachine machine) {
        return machine.getLevel().dimension().location() + "/" + machine.getPos().asLong();
    }

    public static Hk3RefundTarget capture(MetaMachine machine) {
        if (!(machine.getLevel() instanceof ServerLevel level)
                || level.getServer() != ServerLifecycleHooks.getCurrentServer() || !level.getServer().isSameThread()
                || !level.hasChunkAt(machine.getPos()) || MetaMachine.getMachine(level, machine.getPos()) != machine
                || !(machine.getHolder() instanceof BlockEntity block))
            throw new IllegalStateException("退款目标不是当前服务器已加载的机器");
        var persistent = block.getPersistentData();
        if (!persistent.contains(ID)) {
            persistent.putUUID(ID, java.util.UUID.randomUUID());
            block.setChanged();
        }
        if (!persistent.hasUUID(ID)) throw new IllegalStateException("机器退款实例身份损坏");
        return new Hk3RefundTarget(level.getServer(), identity(machine, persistent.getUUID(ID)));
    }

    private static CompoundTag identity(MetaMachine machine, java.util.UUID instance) {
        var tag = new CompoundTag();
        tag.putString("Dimension", machine.getLevel().dimension().location().toString());
        tag.putLong("Position", machine.getPos().asLong());
        tag.putString("Definition", machine.getDefinition().getId().toString());
        tag.putUUID("Instance", instance);
        return tag;
    }

    public static Hk3RefundTarget capture(MachineTrait trait) {
        var target = capture(trait.getMachine());
        int index = -1;
        var traits = trait.getMachine().getTraits();
        for (int i = 0; i < traits.size(); i++) if (traits.get(i) == trait) { index = i; break; }
        if (index < 0) throw new IllegalStateException("退款仓室不在机器特性列表");
        target.address.putInt("Trait", index);
        target.address.putString("TraitClass", trait.getClass().getName());
        return target;
    }

    public static void validate(CompoundTag tag, boolean trait) {
        Hk3LedgerValidation.type(tag, "Dimension", Tag.TAG_STRING);
        Hk3LedgerValidation.type(tag, "Position", Tag.TAG_LONG);
        Hk3LedgerValidation.type(tag, "Definition", Tag.TAG_STRING);
        Hk3LedgerValidation.require(ResourceLocation.tryParse(tag.getString("Dimension")) != null, "退款维度");
        Hk3LedgerValidation.require(ResourceLocation.tryParse(tag.getString("Definition")) != null, "退款机器类型");
        Hk3LedgerValidation.require(tag.hasUUID("Instance"), "退款机器实例");
        if (trait) {
            Hk3LedgerValidation.type(tag, "Trait", Tag.TAG_INT);
            Hk3LedgerValidation.type(tag, "TraitClass", Tag.TAG_STRING);
            Hk3LedgerValidation.require(tag.getInt("Trait") >= 0 && !tag.getString("TraitClass").isEmpty(), "退款仓室");
        }
    }

    public MetaMachine machine() {
        validate(address, false);
        if (server != ServerLifecycleHooks.getCurrentServer() || !server.isSameThread())
            throw new IllegalStateException("退款服务器已变化");
        var dimension = ResourceKey.create(Registries.DIMENSION, ResourceLocation.tryParse(address.getString("Dimension")));
        var level = server.getLevel(dimension);
        var pos = BlockPos.of(address.getLong("Position"));
        if (level == null || !level.hasChunkAt(pos)) throw new IllegalStateException("退款区块未加载，等待原区块");
        var machine = MetaMachine.getMachine(level, pos);
        if (machine == null || !(machine.getHolder() instanceof BlockEntity block)
                || !block.getPersistentData().hasUUID(ID)
                || !sameIdentity(address, identity(machine, block.getPersistentData().getUUID(ID))))
            throw new IllegalStateException("退款机器已被替换或身份变化，禁止改写");
        return machine;
    }

    static boolean sameIdentity(CompoundTag expected, CompoundTag actual) {
        validate(expected, false);
        validate(actual, false);
        return expected.getString("Dimension").equals(actual.getString("Dimension"))
                && expected.getLong("Position") == actual.getLong("Position")
                && expected.getString("Definition").equals(actual.getString("Definition"))
                && expected.getUUID("Instance").equals(actual.getUUID("Instance"));
    }

    public MachineTrait trait() {
        validate(address, true);
        var traits = machine().getTraits();
        int index = address.getInt("Trait");
        if (index >= traits.size() || !traits.get(index).getClass().getName().equals(address.getString("TraitClass")))
            throw new IllegalStateException("退款仓室布局变化，禁止猜测新仓室");
        return traits.get(index);
    }
}
