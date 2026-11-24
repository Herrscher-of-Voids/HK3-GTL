package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.crafting.CalculationStrategy;
import appeng.api.storage.ISubMenuHost;
import appeng.menu.AEBaseMenu;
import appeng.menu.me.crafting.CraftAmountMenu;
import appeng.menu.me.crafting.CraftConfirmMenu;
import appeng.menu.MenuOpener;
import appeng.menu.ISubMenu;
import appeng.menu.guisync.GuiSync;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactAmountMenu;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ExactOrderService;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityTerminalService;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusStock;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.MenuType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;

import java.math.BigInteger;

@Mixin(value = CraftAmountMenu.class, remap = false)
public abstract class Hk3ExactAmountMenuMixin extends AEBaseMenu implements Hk3ExactAmountMenu, Hk3NexusNativeMenus.Amount {
    @Unique @GuiSync(41) public String hk3gtl$initialExactAmount = "";
    protected Hk3ExactAmountMenuMixin(MenuType<?> type, int id, Inventory inventory, Object host) {
        super(type, id, inventory, host);
    }

    @Inject(method = "<init>", at = @At("TAIL"))
    private void hk3gtl$registerExactAction(int id, Inventory inventory, ISubMenuHost host, CallbackInfo ci) {
        registerClientAction("hk3gtlNexusAmount", String.class, action -> {
            String[] parts = action.split("\\|", 3);
            if (parts.length == 3 && parts[0].matches("[0-9]{1,512}"))
                hk3gtl$confirmAmount(new BigInteger(parts[0]), parts[1].equals("1"), parts[2].equals("1"));
        });
        registerClientAction("hk3gtlExactOrder", String.class, action -> {
            if (action != null && action.length() <= 576 && !getPlayer().level().isClientSide) {
                if (action.startsWith("probability|")) {
                    if (Hk3ProbabilitySupport.AVAILABLE)
                        Hk3ProbabilityTerminalService.action((CraftAmountMenu) (Object) this, action.substring(12));
                } else Hk3ExactOrderService.action((CraftAmountMenu) (Object) this, action);
            }
        });
    }

    @Override public String hk3gtl$initialAmount() { return hk3gtl$initialExactAmount; }
    @Override public void hk3gtl$initialAmount(String amount) { hk3gtl$initialExactAmount = amount; }

    @Override public void hk3gtl$confirmAmount(BigInteger amount, boolean missing, boolean immediate) {
        if (isClientSide()) {
            sendClientAction("hk3gtlNexusAmount", amount + "|" + (missing ? "1" : "0") + "|" + (immediate ? "1" : "0"));
            return;
        }
        var menu = (CraftAmountMenu) (Object) this;
        var node = getActionHost().getActionableNode();
        if (node == null || !node.isActive()) return;
        if (amount.signum() <= 0) return;
        var target = menu.getWhatToCraft().what();
        BigInteger requested = amount;
        if (missing) {
            var nexus = Hk3NexusCrafting.firstOn(node.getGrid());
            requested = nexus == null ? amount.subtract(Hk3NexusStock.snapshot(node.getGrid()).getOrDefault(target, BigInteger.ZERO)).max(BigInteger.ZERO)
                    : nexus.missingAmount(target, amount);
        }
        if (requested.signum() == 0) {
            menu.getHost().returnToMainMenu(getPlayer(), (ISubMenu) menu);
            return;
        }
        MenuOpener.open(CraftConfirmMenu.TYPE, getPlayer(), getLocator());
        if (getPlayer().containerMenu instanceof CraftConfirmMenu confirm) {
            confirm.setAutoStart(immediate);
            var exact = (Hk3NexusNativeMenus.Confirm) confirm;
            exact.hk3gtl$planAmount(target, requested, CalculationStrategy.REPORT_MISSING_ITEMS);
        }
    }

    @Override
    public void hk3gtl$exactAction(String action) {
        if (action != null && action.length() <= 576 && getPlayer().level().isClientSide) {
            sendClientAction("hk3gtlExactOrder", action);
        }
    }
}
