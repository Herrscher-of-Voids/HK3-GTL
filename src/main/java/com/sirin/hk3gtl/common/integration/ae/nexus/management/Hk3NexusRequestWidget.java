package com.sirin.hk3gtl.common.integration.ae.nexus.management;

import appeng.api.behaviors.ContainerItemStrategies;
import appeng.api.client.AEKeyRendering;
import appeng.api.stacks.AEFluidKey;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import com.lowdragmc.lowdraglib.gui.ingredient.IGhostIngredientTarget;
import com.lowdragmc.lowdraglib.gui.ingredient.IIngredientSlot;
import com.lowdragmc.lowdraglib.gui.ingredient.Target;
import com.lowdragmc.lowdraglib.gui.widget.ButtonWidget;
import com.lowdragmc.lowdraglib.gui.widget.PhantomFluidWidget;
import com.lowdragmc.lowdraglib.gui.widget.SwitchWidget;
import com.lowdragmc.lowdraglib.gui.widget.TextFieldWidget;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import com.lowdragmc.lowdraglib.gui.widget.WidgetGroup;
import com.sirin.hk3gtl.common.integration.ae.nexus.ui.Hk3NexusTheme;
import mezz.jei.api.ingredients.ITypedIngredient;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.Rect2i;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public final class Hk3NexusRequestWidget extends WidgetGroup {
    private static final int ROWS = 8;
    private final Hk3NexusManagement management;
    private final Player player;
    private final List<RequestRow> rows = new ArrayList<>();
    private final List<AEKey> targetSlots = new ArrayList<>();
    private final Set<AEKey> missing = new HashSet<>();
    private int page;
    private int pages = 1;
    private boolean loaded;

    public Hk3NexusRequestWidget(Hk3NexusManagement management, Player player) {
        super(0, 0, 300, 191);
        this.management = management;
        this.player = player;
        addWidget(Hk3NexusTheme.label(5, 2, "开"));
        addWidget(Hk3NexusTheme.label(25, 2, "目标"));
        addWidget(Hk3NexusTheme.label(49, 2, "库存目标"));
        addWidget(Hk3NexusTheme.label(141, 2, "单批数量"));
        addWidget(Hk3NexusTheme.label(275, 2, "状态"));
        for (int index = 0; index < ROWS; index++) {
            var row = new RequestRow(15 + index * 19);
            rows.add(row);
            addWidget(row);
        }
        addWidget(new ButtonWidget(6, 172, 56, 18, Hk3NexusTheme.button("上一页"), click -> {
            if (!click.isRemote) { page = Math.max(0, page - 1); loadPage(); }
        }));
        addWidget(Hk3NexusTheme.label(70, 177, () -> (page + 1) + " / " + pages));
        addWidget(new ButtonWidget(128, 172, 56, 18, Hk3NexusTheme.button("下一页"), click -> {
            if (!click.isRemote) { page = Math.min(page + 1, pages - 1); loadPage(); }
        }));
        addWidget(Hk3NexusTheme.label(194, 177, "流体单位：mB"));
    }

    private void loadPage() {
        var targets = management.stockTargets();
        if (!loaded) targets.forEach(view -> targetSlots.add(view.target().key()));
        pages = (targetSlots.size() + ROWS - 1) / ROWS + 1;
        page = Math.min(page, pages - 1);
        var byKey = new HashMap<AEKey, Hk3NexusManagement.StockView>();
        for (var view : targets) byKey.put(view.target().key(), view);
        for (int index = 0; index < ROWS; index++) {
            int target = page * ROWS + index;
            var row = rows.get(index);
            row.targetSlot = target;
            row.bind(target < targetSlots.size() ? byKey.get(targetSlots.get(target)) : null);
        }
        loaded = true;
    }

    @Override public void writeInitialData(FriendlyByteBuf buffer) {
        loadPage();
        super.writeInitialData(buffer);
    }

    @Override public void detectAndSendChanges() {
        if (!loaded) loadPage();
        var targets = management.stockTargets();
        pages = (targetSlots.size() + ROWS - 1) / ROWS + 1;
        page = Math.min(page, pages - 1);
        var byKey = new HashMap<AEKey, Hk3NexusManagement.StockView>();
        for (var view : targets) byKey.put(view.target().key(), view);
        missing.clear();
        for (var order : management.crafting().orders()) if (!order.missing().isEmpty()) missing.add(order.target());
        for (var row : rows) row.refresh(byKey.get(row.original));
        super.detectAndSendChanges();
    }

    private final class RequestRow extends WidgetGroup {
        private final SwitchWidget toggle;
        private final GhostSlot ghost;
        private final TextFieldWidget amountField;
        private final TextFieldWidget batchField;
        private final ButtonWidget saveButton;
        private final ButtonWidget deleteButton;
        private int targetSlot;
        private AEKey original;
        private AEKey key;
        private Hk3NexusManagement.StockTarget saved;
        private String amount = "1000";
        private String batch = "1";
        private boolean enabled = true;
        private boolean locked;
        private String status = "";
        private String error = "";
        private String info = "拖入物品或流体；右键读取容器或清空";
        private CompoundTag lastState;

        RequestRow(int y) {
            super(0, y, 300, 18);
            toggle = new SwitchWidget(4, 1, 16, 16, (click, value) -> {
                if (click.isRemote) return;
                enabled = value;
                if (saved != null) management.setTarget(original, saved.amount(), saved.batch(), enabled, saved.owner());
            }).setTexture(Hk3NexusTheme.button("×"), Hk3NexusTheme.button("✓"))
                    .setSupplier(() -> enabled);
            toggle.setHoverTooltips("启用补货");
            addWidget(toggle);
            ghost = new GhostSlot(this, 24, 0);
            addWidget(ghost);
            amountField = numberField(47, true);
            batchField = numberField(139, false);
            addWidget(amountField);
            addWidget(batchField);
            saveButton = new ButtonWidget(231, 0, 20, 18, Hk3NexusTheme.button("存"), click -> {
                if (!click.isRemote) save();
            });
            saveButton.setHoverTooltips("保存；输入后也可按回车");
            addWidget(saveButton);
            deleteButton = new ButtonWidget(254, 0, 20, 18, Hk3NexusTheme.button("删"), click -> {
                if (!click.isRemote) clear();
            });
            addWidget(deleteButton);
            addWidget(Hk3NexusTheme.label(276, 5, () -> status));
        }

        private TextFieldWidget numberField(int x, boolean target) {
            var field = new TextFieldWidget(x, 0, 89, 18,
                    () -> target ? amount : batch,
                    value -> { if (target) amount = value; else batch = value; error = ""; }) {
                @Override public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
                    if ((keyCode == 257 || keyCode == 335) && isFocus()) {
                        writeClientAction(2, buffer -> {});
                        return true;
                    }
                    return super.keyPressed(keyCode, scanCode, modifiers);
                }

                @Override public void handleClientAction(int id, FriendlyByteBuf buffer) {
                    if (id == 2) save();
                    else super.handleClientAction(id, buffer);
                }
            };
            return Hk3NexusTheme.field(field).setMaxStringLength(32767)
                    .setValidator(value -> value.matches("[0-9]*") ? value : field.getCurrentString());
        }

        private void bind(Hk3NexusManagement.StockView view) {
            original = key = view == null ? null : view.target().key();
            amount = view == null ? "1000" : view.target().amount().toString();
            batch = view == null ? "1" : view.target().batch().toString();
            enabled = view == null || view.target().enabled();
            error = "";
            refresh(view);
        }

        private void select(AEKey selected) {
            key = selected;
            batch = selected == null ? "1" : Integer.toString(selected.getAmountPerUnit());
            error = "";
            status = "未存";
        }

        private void save() {
            if (locked) return;
            if (amount.isEmpty() || batch.isEmpty()) { error = "数量"; return; }
            if (key == null || new BigInteger(amount).signum() == 0) {
                clear();
            } else {
                BigInteger size = new BigInteger(batch);
                if (size.signum() == 0) { error = "批量"; return; }
                if (original != null && !original.equals(key)) management.removeTarget(original);
                management.setTarget(key, new BigInteger(amount), size, enabled, player.getUUID());
                int previous = targetSlots.indexOf(key);
                if (previous >= 0) {
                    targetSlots.set(previous, null);
                    if (previous != targetSlot && previous / ROWS == page) rows.get(previous % ROWS).bind(null);
                }
                while (targetSlots.size() <= targetSlot) targetSlots.add(null);
                targetSlots.set(targetSlot, key);
                original = key;
            }
        }

        private void clear() {
            if (original != null) {
                management.removeTarget(original);
                targetSlots.set(targetSlot, null);
            }
            bind(null);
        }

        private void refresh(Hk3NexusManagement.StockView view) {
            saved = view == null ? null : view.target();
            locked = view != null && view.inFlight().signum() > 0;
            if (!error.isEmpty()) status = error;
            else if (key == null) status = "";
            else if (!Objects.equals(key, original) || view == null) status = "未存";
            else if (!enabled) status = "停用";
            else if (view.infinite()) status = "无限";
            else if (locked) status = missing.contains(key) ? "缺料" : "合成";
            else status = view.stored().compareTo(view.target().amount()) >= 0 ? "充足" : "待补";
            String unit = key instanceof AEFluidKey ? " mB" : "";
            info = key == null ? "拖入物品或流体；右键读取容器或清空" : key.getDisplayName().getString();
            if (view != null && Objects.equals(key, original)) info += "\n库存："
                    + (view.infinite() ? "∞" : view.stored() + unit) + "\n在途：" + view.inFlight() + unit;
            applyState();
        }

        private void applyState() {
            ghost.setActive(!locked).setHoverTooltips(info);
            amountField.setActive(!locked);
            batchField.setActive(!locked);
            saveButton.setActive(!locked);
            deleteButton.setActive(!locked);
        }

        private CompoundTag state() {
            var tag = new CompoundTag();
            if (key != null) tag.put("Key", key.toTagGeneric());
            tag.putBoolean("Enabled", enabled);
            tag.putBoolean("Locked", locked);
            tag.putString("Status", status);
            tag.putString("Info", info);
            return tag;
        }

        private void readState(CompoundTag tag) {
            key = tag.contains("Key") ? AEKey.fromTagGeneric(tag.getCompound("Key")) : null;
            enabled = tag.getBoolean("Enabled");
            locked = tag.getBoolean("Locked");
            status = tag.getString("Status");
            info = tag.getString("Info");
            applyState();
        }

        @Override public void writeInitialData(FriendlyByteBuf buffer) {
            amountField.setCurrentString(amount);
            batchField.setCurrentString(batch);
            super.writeInitialData(buffer);
            lastState = state();
            buffer.writeNbt(lastState);
        }

        @Override public void readInitialData(FriendlyByteBuf buffer) {
            super.readInitialData(buffer);
            readState(buffer.readNbt());
        }

        @Override public void detectAndSendChanges() {
            var current = state();
            if (!current.equals(lastState)) {
                lastState = current;
                writeUpdateInfo(10, buffer -> buffer.writeNbt(current));
            }
            super.detectAndSendChanges();
        }

        @Override public void readUpdateInfo(int id, FriendlyByteBuf buffer) {
            if (id == 10) readState(buffer.readNbt());
            else super.readUpdateInfo(id, buffer);
        }
    }

    private static final class GhostSlot extends Widget implements IGhostIngredientTarget, IIngredientSlot {
        private final RequestRow row;

        GhostSlot(RequestRow row, int x, int y) {
            super(x, y, 18, 18);
            this.row = row;
            setBackground(Hk3NexusTheme.SLOT);
        }

        @OnlyIn(Dist.CLIENT)
        @Override public void drawInBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
            super.drawInBackground(graphics, mouseX, mouseY, partialTicks);
            if (row.key != null) AEKeyRendering.drawInGui(Minecraft.getInstance(), graphics,
                    getPositionX() + 1, getPositionY() + 1, row.key);
        }

        @OnlyIn(Dist.CLIENT)
        @Override public boolean mouseClicked(double mouseX, double mouseY, int button) {
            if (!isMouseOverElement(mouseX, mouseY)) return false;
            ItemStack held = gui.getModularUIContainer().getCarried();
            GenericStack contained = button == 1 ? ContainerItemStrategies.getContainedStack(held) : null;
            AEKey selected = contained == null ? ingredientKey(held) : contained.what();
            writeClientAction(1, buffer -> AEKey.writeOptionalKey(buffer, selected));
            return true;
        }

        @Override public void handleClientAction(int id, FriendlyByteBuf buffer) {
            if (id == 1 && !row.locked) row.select(AEKey.readOptionalKey(buffer));
        }

        @OnlyIn(Dist.CLIENT)
        @Override public List<Target> getPhantomTargets(Object ingredient) {
            if (ingredientKey(ingredient) == null) return List.of();
            return List.of(new Target() {
                @Override public Rect2i getArea() { return toRectangleBox(); }
                @Override public void accept(Object value) {
                    AEKey selected = ingredientKey(value);
                    writeClientAction(1, buffer -> AEKey.writeOptionalKey(buffer, selected));
                }
            });
        }

        @OnlyIn(Dist.CLIENT)
        @Override public Object getXEIIngredientOverMouse(double mouseX, double mouseY) {
            if (!isMouseOverElement(mouseX, mouseY)) return null;
            if (row.key instanceof AEItemKey item) return item.toStack();
            if (row.key instanceof AEFluidKey fluid) return fluid.toStack(1000);
            return null;
        }

        @OnlyIn(Dist.CLIENT)
        private static AEKey ingredientKey(Object ingredient) {
            if (ingredient instanceof ITypedIngredient<?> typed) ingredient = typed.getIngredient();
            ingredient = PhantomFluidWidget.checkJEIIngredient(ingredient);
            if (ingredient instanceof com.lowdragmc.lowdraglib.side.fluid.FluidStack fluid)
                return AEFluidKey.of(fluid.getFluid(), fluid.getTag());
            if (ingredient instanceof ItemStack stack) {
                GenericStack generic = GenericStack.fromItemStack(stack);
                return generic == null ? null : generic.what();
            }
            return null;
        }
    }
}
