package com.sirin.hk3gtl.client;

import com.sirin.hk3gtl.common.dimension.height.Hk3HeightConfig;
import com.sirin.hk3gtl.common.dimension.height.Hk3HeightPolicy;
import com.sirin.hk3gtl.common.dimension.height.Hk3HeightWorldUpgrade;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/**
 * 【文件职责】Forge配置界面仅编辑未来新世界模式和上界，不能给当前或旧档启用/缩高。
 * 【变更记录 #1】2026-10-17 21:26:10（第1次备注 · 修订166）
 * - 删除：无。新增：三种创建模式、合法上界输入与保存拒绝提示。
 * - 修改：不向服务器发送高度设置，不热改世界；用途：与服务端同一配置验证且明确旧档边界。
 */
/**
 * 【变更记录 #2】2026-10-29 23:06:53（第2次备注 · 本轮高度与预览修复）
 * - 删除：设置页不能为旧档选择升级的限制；不新增热修改世界入口。
 * - 新增：分号分隔的准确文件夹名单输入及非法路径、通配符、空条目校验。
 * - 修改：与Common配置同步保存，显示重开生效和不可直接缩高说明；小窗口保留底部按钮。
 * - 用途：新档和显式名单旧档均能选择既定高度方案，实际边界仍由服务端冻结合同决定。
 */
public final class Hk3HeightConfigScreen extends Screen {
    private final Screen parent;
    private Hk3HeightConfig.NewWorldMode mode;
    private EditBox top;
    private EditBox existing;
    private Component error = Component.empty();

    public Hk3HeightConfigScreen(Screen parent) {
        super(Component.translatable("hk3gtl.height.config.title"));
        this.parent = parent;
        this.mode = Hk3HeightConfig.MODE.get();
    }
    @Override protected void init() {
        int left = width / 2 - 150;
        addRenderableWidget(Button.builder(modeLabel(), button -> {
            var modes = Hk3HeightConfig.NewWorldMode.values();
            mode = modes[(mode.ordinal() + 1) % modes.length];
            button.setMessage(modeLabel());
        }).bounds(left, 68, 300, 24).build());
        top = new EditBox(font, left + 170, 100, 130, 22, Component.translatable("hk3gtl.height.config.top"));
        top.setValue(Integer.toString(Hk3HeightConfig.TOP_EXCLUSIVE.get()));
        top.setMaxLength(4);
        top.setFilter(value -> value.isEmpty() || value.chars().allMatch(Character::isDigit));
        addRenderableWidget(top);
        existing = new EditBox(font, left, 140, 300, 22, Component.translatable("hk3gtl.height.config.existing"));
        existing.setMaxLength(4096);
        existing.setValue(String.join(";", Hk3HeightConfig.EXISTING_WORLDS.get()));
        addRenderableWidget(existing);
        addRenderableWidget(Button.builder(Component.translatable("gui.done"), button -> save()).bounds(left, height - 28, 145, 24).build());
        addRenderableWidget(Button.builder(Component.translatable("gui.cancel"), button -> onClose()).bounds(left + 155, height - 28, 145, 24).build());
    }
    private Component modeLabel() {
        return Component.translatable("hk3gtl.height.config.mode_label", Component.translatable("hk3gtl.height.config.mode." + mode.name().toLowerCase(java.util.Locale.ROOT)));
    }
    private void save() {
        try {
            int target = Integer.parseInt(top.getValue());
            Hk3HeightPolicy.requireTopExclusive(target);
            var folders = existing.getValue().isBlank() ? java.util.List.<String>of()
                : java.util.Arrays.stream(existing.getValue().split(";", -1)).map(String::strip).distinct().toList();
            if (folders.stream().anyMatch(name -> !Hk3HeightWorldUpgrade.validFolderName(name))) {
                error = Component.translatable("hk3gtl.height.config.invalid_existing");
                return;
            }
            Hk3HeightConfig.MODE.set(mode);
            Hk3HeightConfig.TOP_EXCLUSIVE.set(target);
            Hk3HeightConfig.EXISTING_WORLDS.set(folders);
            Hk3HeightConfig.SPEC.save();
            onClose();
        } catch (IllegalArgumentException ex) {
            error = Component.translatable("hk3gtl.height.config.invalid");
        }
    }
    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        graphics.drawCenteredString(font, title, width / 2, 18, 0xFFFFFF);
        graphics.drawWordWrap(font, Component.translatable("hk3gtl.height.config.scope"), width / 2 - 150, 38, 300, 0xBECBE3);
        graphics.drawString(font, Component.translatable("hk3gtl.height.config.top"), width / 2 - 150, 106, 0xFFFFFF, false);
        graphics.drawString(font, Component.translatable("hk3gtl.height.config.existing"), width / 2 - 150, 128, 0xFFFFFF, false);
        graphics.drawWordWrap(font, error.getString().isEmpty() ? Component.translatable("hk3gtl.height.config.test_hint") : error,
            width / 2 - 150, 170, 300, error.getString().isEmpty() ? 0xBECBE3 : 0xFF7777);
        super.render(graphics, mouseX, mouseY, partialTick);
    }
    @Override public void onClose() { if (minecraft != null) minecraft.setScreen(parent); }
}
