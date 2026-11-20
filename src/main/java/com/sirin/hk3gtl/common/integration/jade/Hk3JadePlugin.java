package com.sirin.hk3gtl.common.integration.jade;

import com.gregtechceu.gtceu.api.block.MetaMachineBlock;
import com.gregtechceu.gtceu.api.blockentity.MetaMachineBlockEntity;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.machine.Hk3MultiRecipeLogic;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine;
import com.sirin.hk3gtl.common.machine.energy.Hk3ReactorMachine;
import com.sirin.hk3gtl.common.machine.multiblock.part.HonkaiEnergyHatchPartMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import com.sirin.hk3gtl.common.util.Hk3HonkaiEnergyFormatter;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import snownee.jade.api.BlockAccessor;
import snownee.jade.api.IBlockComponentProvider;
import snownee.jade.api.IServerDataProvider;
import snownee.jade.api.ITooltip;
import snownee.jade.api.IWailaClientRegistration;
import snownee.jade.api.IWailaCommonRegistration;
import snownee.jade.api.IWailaPlugin;
import snownee.jade.api.WailaPlugin;
import snownee.jade.api.config.IPluginConfig;
import snownee.jade.api.ui.BoxStyle;

import java.math.BigInteger;
import java.util.HashSet;
import java.util.UUID;

@WailaPlugin
public final class Hk3JadePlugin implements IWailaPlugin {
    @Override
    public void register(IWailaCommonRegistration registration) {
        registration.registerBlockDataProvider(MachineProvider.INSTANCE, MetaMachineBlockEntity.class);
    }

    @Override
    public void registerClient(IWailaClientRegistration registration) {
        registration.registerBlockComponent(MachineProvider.INSTANCE, MetaMachineBlock.class);
    }

    private enum MachineProvider implements IBlockComponentProvider, IServerDataProvider<BlockAccessor> {
        INSTANCE;

        private static final ResourceLocation ID = new ResourceLocation("hk3gtl", "machine_status");
        private static final String KEY = "Hk3HonkaiEnergy";
        private static final String UNLIMITED = HonkaiWirelessNetwork.UNLIMITED_CAPACITY_TEXT;

        @Override
        public ResourceLocation getUid() {
            return ID;
        }

        @Override
        public void appendServerData(CompoundTag data, BlockAccessor accessor) {
            var machine = ((MetaMachineBlockEntity) accessor.getBlockEntity()).getMetaMachine();
            if (machine instanceof HonkaiEnergyHatchPartMachine hatch) {
                if (hatch.getHatchType().wireless) {
                    var owner = hatch.getOwnerId();
                    if (owner != null) data.putString(KEY + "Wireless", compact(HonkaiWirelessNetwork.getStoredAmount(owner)));
                    else data.putBoolean(KEY + "Unbound", true);
                } else {
                    var storage = hatch.getContainer();
                    writeStorage(data, storage.getAmount(), storage.getCapacity());
                }
            } else if (machine instanceof Hk3WorkableMultiblockMachine controller) {
                if (controller.getRecipeLogic() instanceof Hk3MultiRecipeLogic logic && logic.hasUnlimitedParallelism())
                    data.putBoolean("Hk3UnlimitedParallel", true);
                long amount = 0;
                long capacity = 0;
                var owners = new HashSet<UUID>();
                boolean direct = usesWirelessHonkai(controller);
                boolean wireless = direct;
                if (direct && controller.getDualEnergyOwner() != null) owners.add(controller.getDualEnergyOwner());
                for (var hatch : controller.getHonkaiHatches()) {
                    if (hatch.getHatchType().wireless) {
                        wireless = true;
                        if (!direct && hatch.getOwnerId() != null) owners.add(hatch.getOwnerId());
                    } else if (hatch.getHatchType().creative) {
                        amount = capacity = Long.MAX_VALUE;
                    } else if (capacity != Long.MAX_VALUE) {
                        var storage = hatch.getContainer();
                        amount += storage.getAmount();
                        capacity += storage.getCapacity();
                    }
                }
                if (capacity > 0) writeStorage(data, amount, capacity);
                if (!owners.isEmpty()) {
                    BigInteger balance = BigInteger.ZERO;
                    for (var owner : owners) balance = balance.add(HonkaiWirelessNetwork.getStoredAmount(owner));
                    data.putString(KEY + "Wireless", compact(balance));
                } else if (wireless) {
                    data.putBoolean(KEY + "Unbound", true);
                }
            }
        }

        @Override
        public void appendTooltip(ITooltip tooltip, BlockAccessor accessor, IPluginConfig config) {
            var data = accessor.getServerData();
            if (data.getBoolean("Hk3UnlimitedParallel"))
                tooltip.add(Component.translatable("hk3gtl.machine.unlimited_parallel_cross_recipe").withStyle(ChatFormatting.AQUA));
            if (data.contains(KEY)) {
                var storage = data.getCompound(KEY);
                long amount = storage.getLong("Amount");
                long capacity = storage.getLong("Capacity");
                if (capacity == Long.MAX_VALUE) addBar(tooltip, 1, "hk3gtl.jade.honkai_energy", UNLIMITED, UNLIMITED);
                else addBar(tooltip, (float) amount / capacity, "hk3gtl.jade.honkai_energy",
                        compact(BigInteger.valueOf(amount)), compact(BigInteger.valueOf(capacity)));
            }
            if (data.contains(KEY + "Wireless"))
                addBar(tooltip, 0, "hk3gtl.jade.wireless_honkai_energy", data.getString(KEY + "Wireless"), UNLIMITED);
            else if (data.getBoolean(KEY + "Unbound"))
                addBar(tooltip, 0, "hk3gtl.jade.wireless_honkai_energy", Component.translatable("hk3gtl.jade.unbound"), UNLIMITED);
        }

        private static boolean usesWirelessHonkai(Hk3WorkableMultiblockMachine machine) {
            String path = machine.getDefinition().getId().getPath();
            if (machine instanceof Hk3HonkaiNetworkInjectorMachine || machine instanceof Hk3ReactorMachine
                    || machine instanceof Hk3LateIndustrialMachine process && process.researchRole().equals("I38")
                    || Hk3DualEnergyCosts.getMachineDefault(path) > 0)
                return true;
            var recipe = machine.getRecipeLogic().getLastRecipe();
            if (recipe == null) return false;
            var cost = Hk3DualEnergyCosts.getMergedCost(recipe);
            return cost == null ? Hk3DualEnergyCosts.resolve(recipe.id, path) > 0 : cost.signum() > 0;
        }

        private static void writeStorage(CompoundTag data, long amount, long capacity) {
            var storage = new CompoundTag();
            storage.putLong("Amount", amount);
            storage.putLong("Capacity", capacity);
            data.put(KEY, storage);
        }

        private static String compact(BigInteger value) {
            return Hk3HonkaiEnergyFormatter.formatCompact(value);
        }

        private static void addBar(ITooltip tooltip, float ratio, String key, Object amount, String capacity) {
            var text = Component.translatable(key, amount, capacity).withStyle(ChatFormatting.GRAY);
            var helper = tooltip.getElementHelper();
            var style = helper.progressStyle().color(0xFFAA0000, 0xFF660000);
            tooltip.add(helper.progress(ratio, text, style, BoxStyle.DEFAULT, true));
        }
    }
}
