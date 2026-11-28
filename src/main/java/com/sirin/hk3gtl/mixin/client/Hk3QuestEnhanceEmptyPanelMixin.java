package com.sirin.hk3gtl.mixin.client;

import dev.ftb.mods.ftblibrary.ui.ModalPanel;
import dev.ftb.mods.ftblibrary.ui.Panel;
import dev.ftb.mods.ftbquests.client.gui.quests.ViewQuestPanel;
import dev.ftb.mods.ftbquests.quest.Quest;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = ViewQuestPanel.class, remap = false, priority = 1100)
public abstract class Hk3QuestEnhanceEmptyPanelMixin extends ModalPanel {
    @Shadow private Quest quest;

    protected Hk3QuestEnhanceEmptyPanelMixin(Panel parent) {
        super(parent);
    }

    @Inject(method = "addWidgets", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$closeEmptyPanel(CallbackInfo ci) {
        if (quest != null) return;
        setPosAndSize(-1, -1, 1, 1);
        ci.cancel();
    }
}
