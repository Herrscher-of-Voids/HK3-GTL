package com.sirin.hk3gtl.client.compat;

import com.lowdragmc.lowdraglib.gui.widget.TextBoxWidget;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class Hk3JeiResearchWidget extends TextBoxWidget {
    private final Hk3ResearchRequirementPolicy.Requirements requirements;
    private final Map<String, String> topics;
    private Hk3ResearchRequirementPolicy.Evaluation previous;

    public Hk3JeiResearchWidget(int x, int y, int width,
                               Hk3ResearchRequirementPolicy.Requirements requirements, Map<String, String> topics) {
        super(x, y, width, List.of());
        this.requirements = requirements;
        this.topics = topics;
        setShadow(true);
        refresh();
    }

    @Override public void drawInBackground(GuiGraphics graphics, int mouseX, int mouseY, float partialTicks) {
        refresh();
        super.drawInBackground(graphics, mouseX, mouseY, partialTicks);
    }

    private void refresh() {
        var player = Minecraft.getInstance().player;
        var state = Hk3ResearchRequirementPolicy.evaluate(requirements,
                id -> player != null && Hk3ResearchManager.isCompleted(player, id));
        if (state.equals(previous)) return;
        previous = state;
        var names = new ArrayList<String>();
        var details = new ArrayList<Component>();
        topics.forEach((id, name) -> {
            boolean done = !state.missing().contains(id);
            String color = done ? "\u00a7a" : "\u00a7c";
            names.add(color + name);
            details.add(Component.literal(color + id + " · " + name + " [" + I18n.get(done
                    ? "hk3gtl.jei.research_status_done" : "hk3gtl.jei.research_status_locked") + "]"));
        });
        for (String invalid : requirements.invalid()) {
            if (requirements.requirements().contains(invalid)) continue;
            names.add("\u00a7c" + I18n.get("hk3gtl.jei.research_invalid"));
            details.add(Component.literal("\u00a7c" + I18n.get("hk3gtl.jei.research_status_locked") + ": " + invalid));
        }
        setContent(List.of("\u00a78" + I18n.get("hk3gtl.jei.research_summary",
                String.join("\u00a78" + I18n.get("hk3gtl.jei.research_separator"), names))));
        setHoverTooltips(details);
    }
}
