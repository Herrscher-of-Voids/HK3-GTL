package com.sirin.hk3gtl.common.machine.wonder;

import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.gui.fancy.IFancyUIProvider;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.lowdragmc.lowdraglib.gui.texture.GuiTextureGroup;
import com.lowdragmc.lowdraglib.gui.texture.TextTexture;
import com.lowdragmc.lowdraglib.gui.widget.*;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.sirin.hk3gtl.common.capability.Hk3RefundJournal;
import com.sirin.hk3gtl.common.gaze.Hk3ResearchSuppression;
import com.sirin.hk3gtl.common.recipe.power.Hk3PortPayment;
import com.sirin.hk3gtl.common.recipe.power.Hk3PowerPorts;
import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.review.Hk3ReviewData;
import com.sirin.hk3gtl.common.review.Hk3ReviewLedger;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.BlockHitResult;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;

/** W13本体执行W14、W15正式研究；制造与专属研究分模式使用同一供能。 */
public final class Hk3W13ResearchMachine extends Hk3AnimatedWonderMachine {
    private static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(Hk3W13ResearchMachine.class, Hk3WonderMachine.FIELDS);
    private static final List<String> TOPICS = List.of("RN-WCE", "RN-TAA");
    @Persisted private boolean researchMode;
    private boolean researchWorking;
    private String researchStatus = "等待专属研究工单";

    public Hk3W13ResearchMachine(IMachineBlockEntity holder) { super(holder, "W13"); }
    @Override public ManagedFieldHolder getFieldHolder() { return FIELDS; }
    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote()) subscribeServerTick(this::researchTick);
    }
    @Override protected boolean productionReady(GTRecipe recipe) { return !researchMode && super.productionReady(recipe); }
    @Override protected boolean fieldRunning() { return super.fieldRunning() || researchWorking; }
    @Override public boolean researchServiceRunning() { return !researchMode && super.researchServiceRunning(); }
    private String facility() { return getLevel().dimension().location() + "@" + getPos().asLong(); }
    private double suppression() { return Hk3ResearchSuppression.at((ServerLevel) getLevel(), getPos(), getResearchTeamUUID()); }
    private boolean ready() {
        return !isInValid() && verified() && isFormed() && getRecipeLogic().isWorkingEnabled()
                && getOwnerUUID() != null && Hk3ResearchData.get(getLevel().getServer()).completed(getResearchTeamUUID(), "RN-ASR")
                && Hk3ReviewData.get(getLevel().getServer()).settled(getResearchTeamUUID(), Hk3ReviewLedger.Kind.SECOND);
    }
    private boolean authorized(Player player) {
        if (!(player instanceof ServerPlayer server)) return false;
        Hk3ResearchTeams.refresh(server.server);
        return !isInValid() && getOwnerUUID() != null && Hk3ResearchData.get(server).isMember(player.getUUID(), getResearchTeamUUID())
                && player.level() == getLevel() && player.distanceToSqr(getPos().getX() + .5, getPos().getY() + .5, getPos().getZ() + .5) <= 64
                && getLevel().getBlockEntity(getPos()) instanceof IMachineBlockEntity be && be.getMetaMachine() == this;
    }
    @Override public boolean shouldOpenUI(Player player, InteractionHand hand, BlockHitResult hit) {
        return player.level().isClientSide || authorized(player);
    }

    private void researchTick() {
        researchWorking = false;
        if (!com.sirin.hk3gtl.common.config.Hk3ResearchSettings.enabled()) return;
        if (!researchMode || !ready()) return;
        if (!Hk3W13ResearchService.settleRefund(this)) { researchStatus = "等待供能退款结清"; return; }
        var server = getLevel().getServer();
        var team = getResearchTeamUUID();
        var online = Hk3ResearchTeams.online(server, team);
        if (online.isEmpty()) { researchStatus = "团队离线，研究暂停"; return; }
        var data = Hk3ResearchData.get(server);
        var ports = Hk3PowerPorts.of(getRecipeLogic());
        var used = BigInteger.ZERO;
        long tick = server.overworld().getGameTime();
        double speed = Hk3ResearchMath.speed(5, Hk3ResearchTeams.gaze(server, team), suppression(), false, false);
        researchStatus = "等待专属研究工单";
        for (var job : data.activeResearch(team, facility())) {
            if (!Hk3ResearchStartService.dedicatedToW13(job.quote().topic())) continue;
            var cost = BigInteger.valueOf(job.quote().eut());
            if (Hk3PortPayment.power(ports).subtract(used).compareTo(cost) < 0) { researchStatus = "研究供能功率不足"; break; }
            var payment = Hk3RefundJournal.open(this);
            boolean[] paid = {false};
            Hk3ResearchWorkQueue.Outcome result;
            try {
                result = data.advanceResearch(team, job.quote().topic(), facility(), tick, true, true, speed,
                        () -> paid[0] = Hk3PortPayment.pay(ports, cost, payment));
            } finally {
                Hk3W13ResearchService.finishPayment(this, payment, paid[0]);
            }
            if (paid[0]) { used = used.add(cost); researchWorking = true; }
            researchStatus = result == Hk3ResearchWorkQueue.Outcome.COMPLETED ? "正式研究完成"
                    : paid[0] ? "正在推进正式研究" : "研究暂停：供能或前置不足";
            if (result == Hk3ResearchWorkQueue.Outcome.COMPLETED) {
                Hk3ResearchEvidenceAnalysis.researchCompleted(data, team, 5, job, tick);
                com.sirin.hk3gtl.common.narrative.story.Hk3StoryService.teamFact(server,team,"research_"+job.quote().topic());
                com.sirin.hk3gtl.common.phone.Hk3PhoneService.researchCompleted(server, team, job.quote().topic());
                com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(server)
                        .produced(Hk3ResearchData.payer(team, job.quote()), "receipt:165", 1);
                online.forEach(Hk3ResearchManager::syncClientResearchState);
            }
            if (!Hk3W13ResearchService.settleRefund(this)) break;
        }
    }

    @Override public List<IFancyUIProvider> getSubTabs() {
        var tabs = new ArrayList<>(super.getSubTabs());
        tabs.add(new Hk3WonderManagementPage(this, player -> new Session(player).widget(), "hk3gtl.w13.research.title"));
        return tabs;
    }
    private final class Session {
        private final Player player;
        private String selected = TOPICS.get(0);
        private Component feedback = Component.empty();
        private Session(Player player) { this.player = player; }
        private Widget widget() {
            var group = new WidgetGroup(0, 0, 330, 300);
            group.addWidget(button(8, 6, 154, "W14 · 轮回引擎", () -> selected = TOPICS.get(0)));
            group.addWidget(button(168, 6, 154, "W15 · 朝觐圣座", () -> selected = TOPICS.get(1)));
            var details = new DraggableScrollableWidgetGroup(8, 32, 314, 192).setDraggable(false).setYScrollBarWidth(4);
            details.addWidget(new ComponentPanelWidget(0, 0, this::describe).setMaxWidthLimit(302));
            group.addWidget(details);
            group.addWidget(button(8, 230, 154, "研究点开题", () -> start(true)));
            group.addWidget(button(168, 230, 154, "材料开题", () -> start(false)));
            group.addWidget(button(8, 252, 154, "切换制造／研究模式", this::toggleMode));
            group.addWidget(button(168, 252, 154, "取消所选研究", () -> {
                Hk3ResearchData.get((ServerPlayer) player).cancelResearch(getResearchTeamUUID(), player.getUUID(), selected);
            }));
            group.addWidget(button(8, 274, 314, "领取研究退款", () -> Hk3ResearchPayment.claimRefunds((ServerPlayer) player)));
            return group;
        }
        private ButtonWidget button(int x, int y, int width, String label, Runnable action) {
            return new ButtonWidget(x, y, width, 20, new GuiTextureGroup(GuiTextures.BUTTON, new TextTexture(label)), click -> {
                if (!click.isRemote && authorized(player)) action.run();
            });
        }
        private void toggleMode() {
            if (getRecipeLogic().isActive()) { feedback = Component.literal("请等待当前制造工序结束后切换"); return; }
            if (!Hk3W13ResearchService.settleRefund(Hk3W13ResearchMachine.this)) {
                feedback = Component.literal("请等待供能退款结清后切换"); return;
            }
            researchMode = !researchMode;
            markDirty();
            feedback = Component.literal(researchMode ? "已切换专属研究模式" : "已切换制造模式；未完成研究保留进度");
        }
        private void start(boolean points) {
            var server = (ServerPlayer) player;
            var result = Hk3ResearchStartService.start(server, getResearchTeamUUID(), facility(), 5,
                    researchMode && ready(), selected, points, Hk3ResearchTeams.gaze(server.server, getResearchTeamUUID()), suppression(), "W13");
            feedback = Component.translatable("hk3gtl.research.start." + result.name().toLowerCase(java.util.Locale.ROOT));
        }
        private void describe(List<Component> lines) {
            if (!authorized(player)) return;
            var server = (ServerPlayer) player;
            var data = Hk3ResearchData.get(server);
            var team = getResearchTeamUUID();
            var topic = Hk3ResearchCatalog.bundled().get(selected);
            var plan = Hk3ResearchPlans.get(selected);
            var job = data.researchJob(team, selected);
            lines.add(Component.translatable(plan.nameKey()).withStyle(ChatFormatting.AQUA));
            lines.add(Component.literal("模式：" + (researchMode ? "专属研究" : "工业制造")));
            lines.add(Component.literal(!ready() ? "须完整成型、启用、完成RN-ASR并通过二审"
                    : data.completed(team, selected) ? "该正式研究已完成" : researchMode ? researchStatus : "切换研究模式后推进；制造模式保留进度"));
            lines.add(Component.literal("进度：" + (data.completed(team, selected) ? "100%" : job == null ? "尚未开题"
                    : String.format(java.util.Locale.ROOT, "%.2f%%", 100 * job.progress() / job.quote().ticks()))));
            lines.add(Component.literal("基础时长：" + plan.ticks() / 20 + "秒；" + plan.eut() + " EU/t"));
            lines.add(Component.literal("研究点：" + plan.points() + "；个人余额：" + data.points(player.getUUID())));
            lines.add(Component.literal("材料支付与研究点支付二选一："));
            for (var material : Hk3ResearchStartService.materials(plan, 5, Hk3ResearchTeams.gaze(server.server, team), suppression())) {
                var tag = TagKey.create(Registries.ITEM, new ResourceLocation(material.tag()));
                Component name = BuiltInRegistries.ITEM.getTag(tag).flatMap(set -> set.stream().findFirst())
                        .map(item -> new ItemStack(item.value()).getHoverName()).orElse(Component.literal(material.tag()));
                long available = 0;
                for (int i = 0; i < 36; i++) if (player.getInventory().getItem(i).is(tag)) available += player.getInventory().getItem(i).getCount();
                lines.add(Component.literal("  ").append(name).append(" ×" + material.count() + "（背包" + available + "）"));
            }
            lines.add(Component.literal((data.hasExperiment(team, selected) ? "✓ " : "× ") + "I43真实实验凭据"));
            for (String parent : topic.prerequisites()) lines.add(Component.literal(data.completed(team, parent) ? "✓ " : "× ")
                    .append(Component.translatable(Hk3ResearchPlans.get(parent).nameKey())));
            lines.add(Component.literal("实验依据：" + plan.evidence()));
            lines.add(Component.literal("完成效果：" + plan.result()));
            lines.add(feedback);
        }
    }
}
