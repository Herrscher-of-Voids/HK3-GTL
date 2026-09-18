package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IMachineLife;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableElectricMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.WorkableMultiblockMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.lowdragmc.lowdraglib.syncdata.annotation.Persisted;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.gregtechceu.gtceu.api.recipe.modifier.ParallelLogic;
import com.sirin.hk3gtl.common.machine.multiblock.part.HonkaiEnergyHatchPartMachine;
import com.sirin.hk3gtl.common.machine.trait.Hk3PlayerGridEnergyTrait;
import com.sirin.hk3gtl.common.block.energy.HonkaiHatchType;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.HonkaiWirelessNetwork;
import com.sirin.hk3gtl.common.capability.IDualEnergyConsumer;
import com.sirin.hk3gtl.common.capability.IHonkaiEnergyContainer;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.event.Hk3EventManager;
import com.sirin.hk3gtl.common.util.Hk3HonkaiEnergyFormatter;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.fml.common.Mod;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/**
 * 本模组所有可工作多方块控制器的通用基类。
 *
 * <h3>核心职责</h3>
 * <ul>
 *   <li>禁止创造模式能源仓 / 激光源仓参与结构成型（反外挂、反作弊）</li>
 *   <li>首次成型时触发 Hk3EventManager 里程碑事件（用于研究系统推进）</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>若新增黑名单仓类型：修改 {@link #hasCreativeHatch()} 中的 contains 关键字</li>
 *   <li>若需接入更多"成型事件"：在 {@link #notifyMultiblockEvent()} 中扩展分发</li>
 *   <li>建议所有本模组的 MultiblockMachine 继承此类，而不是直接继承 GT 原版</li>
 *   <li>{@link #notifyMultiblockEvent()} 使用 try/catch 兜底避免单个异常导致整个结构成型崩溃</li>
 *   <li>寻找最近玩家时使用 64 格距离阈值避免给离线 / 远处玩家误派事件</li>
 * </ul>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class Hk3WorkableMultiblockMachine extends WorkableElectricMultiblockMachine implements IMachineLife, IDualEnergyConsumer {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 本类新增持久化字段（ownerUUID）的字段管理器，链到 GT 父类 */
    protected static final ManagedFieldHolder HK3_MANAGED_FIELD_HOLDER =
            new ManagedFieldHolder(Hk3WorkableMultiblockMachine.class, WorkableMultiblockMachine.MANAGED_FIELD_HOLDER);
    /** 多方块扫描崩坏能仓的半径（立方盒半宽，以控制器为中心）。32 格覆盖 130 台机器中最大的文明验证矩阵 63×63×45 */
    private static final int HONKAI_HATCH_SCAN_RADIUS = 32;

    /**
     * 最近一次成型时扫描到的崩坏能仓 BE 列表。
     * <ul>
     *   <li>列表在 {@link #onStructureFormed} 中填充，{@link #onStructureInvalid} 中清空</li>
     *   <li>列表项都是 {@link HonkaiEnergyHatchPartMachine}，机器逻辑可按 {@link HonkaiHatchType} 分类使用</li>
     *   <li>不要持久化本列表 —— 方块可能在结构成型后被玩家摧毁，每次成型重新扫描才最安全</li>
     * </ul>
     */
    private List<HonkaiEnergyHatchPartMachine> honkaiHatches = Collections.emptyList();

    /**
     * 电网绑定的玩家 UUID。EU 全部从该玩家（或其 FTB 队伍）的 GTMThings 无线电网扣除。
     * <p>仅在玩家放置控制器时绑定；无法确认放置者时保持未绑定，避免错误归属。</p>
     */
    @Persisted
    @Nullable
    private UUID ownerUUID;

    /** 玩家电网 EU 特征：构造期挂载（MachineTrait 构造器自动 attachTraits），成型时被 GT 注入 EU IN 代理 */
    @SuppressWarnings("unused")
    private final Hk3PlayerGridEnergyTrait playerGridEnergy;

    /**
     * 构造函数：由 GT 机器注册系统反射调用，不要手动 new。
     */
    public Hk3WorkableMultiblockMachine(IMachineBlockEntity holder) {
        super(holder);
        this.playerGridEnergy = new Hk3PlayerGridEnergyTrait(this, this::getOwnerUUID);
    }

    @Override
    public ManagedFieldHolder getFieldHolder() {
        return HK3_MANAGED_FIELD_HOLDER;
    }

    /** 电网绑定的玩家 UUID；null = 未绑定（机器无法扣电，配方 WAITING） */
    @Nullable
    public UUID getOwnerUUID() {
        return ownerUUID;
    }

    /** 双能源结算归属：与 EU 电网共用同一个 ownerUUID，保证两条能源轨的账户一致 */
    @Override
    @Nullable
    public UUID getDualEnergyOwner() {
        return ownerUUID;
    }

    /**
     * 玩家放置控制器时自动绑定电网归属（GTMThings 无线能源仓同款交互模型）。
     */
    @Override
    public void onMachinePlaced(@Nullable LivingEntity player, ItemStack stack) {
        IMachineLife.super.onMachinePlaced(player, stack);
        if (player != null) {
            this.ownerUUID = player.getUUID();
        }
    }

    /** 外部只读访问：已缓存的崩坏能仓列表（供子类 serverTick 使用） */
    public List<HonkaiEnergyHatchPartMachine> getHonkaiHatches() {
        return honkaiHatches;
    }

    /**
     * 是否启用“多配方同时运行”配方逻辑（{@link Hk3MultiRecipeLogic}）。
     * <p>默认 true：制造类多方块统一获得跨配方便利。研究矩阵、崩坏能转换器等不跑标准配方的机器应重写为 false。</p>
     * <p>注意：本方法会在父类构造期被 {@link #createRecipeLogic} 调用，实现必须是不依赖实例字段的常量。</p>
     */
    protected boolean enableMultiRecipe() {
        return true;
    }

    /**
     * 重写配方逻辑工厂：按 {@link #enableMultiRecipe()} 决定挂载多配方逻辑还是原版单配方逻辑。
     */
    @Override
    protected RecipeLogic createRecipeLogic(Object... args) {
        if (enableMultiRecipe()) {
            return new Hk3MultiRecipeLogic(this);
        }
        return super.createRecipeLogic(args);
    }

    /**
     * 所有普通多方块默认无限并行。
     * <p>不跳过输入/输出校验，由 GTCEu 按库存与输出空间裁剪实际并行数，避免吞物品或复制。</p>
     *
     * <p>注意：当启用多配方逻辑（{@link Hk3MultiRecipeLogic}）时，并行倍乘已在
     * {@link Hk3RecipeCalculationHelper#calculateParallelsWithGreedyAllocation}
     * / {@link Hk3RecipeCalculationHelper#calculateParallelsWithFairAllocation}
     * 阶段完成，此处跳过并行避免双重倍乘。</p>
     */
    @Override
    protected GTRecipe getRealRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (getRecipeLogic() instanceof Hk3MultiRecipeLogic) {
            // 多配方逻辑已自行处理并行，此处只做超频
            return super.getRealRecipe(recipe, params, result);
        }
        GTRecipe modified = super.getRealRecipe(recipe, params, result);
        if (modified == null) {
            return null;
        }

        var parallel = ParallelLogic.applyParallel(self(), modified, Integer.MAX_VALUE, false);
        int amount = parallel.getSecond();
        if (amount <= 1) {
            return modified;
        }
        result.init(result.getEut(), modified.duration, amount, params.getOcAmount());
        return parallel.getFirst();
    }

    /**
     * 结构成型回调。
     * <p>流程：先调 super；若检测到创造仓则立即解散；否则派发里程碑事件。
     * 修改要点：不要在 super 之前做自定义检查，会破坏 GT 原版 part 列表初始化。
     */
    @Override
    public void onStructureFormed() {
        super.onStructureFormed();
        if (hasCreativeHatch()) {
            LOGGER.warn("[HK3GTL] 检测到创造模式能源仓/激光源仓，强制解散结构");
            onStructureInvalid();
            return;
        }
        // 需求 13 Phase A：扫描并缓存结构区域内的崩坏能仓，供子类机器 tick 使用
        scanHonkaiHatches();
        notifyMultiblockEvent();

        // Phase 5 诊断：成型时输出控制器 + appearance + parts 数量，便于定位贴图问题
        try {
            String machineId = getDefinition().getId().toString();
            String appearanceId = "?";
            try {
                var appearance = getDefinition().getAppearance();
                if (appearance != null) {
                    var st = appearance.get();
                    if (st != null && st.getBlock() != null) {
                        appearanceId = String.valueOf(net.minecraftforge.registries.ForgeRegistries.BLOCKS.getKey(st.getBlock()));
                    }
                }
            } catch (Throwable ignored) {}
            int partCount = 0;
            try { partCount = getParts().size(); } catch (Throwable ignored) {}
            LOGGER.info("[HK3GTL][texture-debug] formed machine={} appearanceBlock={} parts={} pos={}",
                    machineId, appearanceId, partCount,
                    (getHolder() instanceof BlockEntity be ? be.getBlockPos() : "?"));
        } catch (Throwable ignored) {
            // 诊断 LOG 失败不应影响成型流程
        }
    }

    @Override
    public void onStructureInvalid() {
        super.onStructureInvalid();
        honkaiHatches = Collections.emptyList();
    }

    /**
     * 扫描结构中的 {@link HonkaiEnergyHatchPartMachine}，缓存到 {@link #honkaiHatches}。
     *
     * <p>现在崩坏能仓已经升级为 GTCEu 原生 PartMachine，直接遍历 getParts() 即可拿到。</p>
     */
    private void scanHonkaiHatches() {
        try {
            List<HonkaiEnergyHatchPartMachine> hits = new ArrayList<>();
            for (IMultiPart part : getParts()) {
                if (part instanceof HonkaiEnergyHatchPartMachine hatch) {
                    hits.add(hatch);
                }
            }
            honkaiHatches = List.copyOf(hits);

            if (!hits.isEmpty()) {
                LOGGER.info("[HK3GTL] 多方块 {} 识别到 {} 个崩坏能仓",
                        getDefinition().getId().getPath(), hits.size());
            }
        } catch (Exception e) {
            LOGGER.warn("[HK3GTL] 崩坏能仓扫描失败", e);
            honkaiHatches = Collections.emptyList();
        }
    }

    /**
     * 向 {@link Hk3EventManager} 派发“多方块成型”事件。
     * 仅使用持久化 ownerUUID；未绑定、owner 离线或不在当前维度时不猜测归属。
     */
    private void notifyMultiblockEvent() {
        try {
            if (ownerUUID == null || !(getHolder() instanceof BlockEntity be)) return;
            Level level = be.getLevel();
            if (!(level instanceof ServerLevel serverLevel)) return;

            ServerPlayer owner = serverLevel.getServer().getPlayerList().getPlayer(ownerUUID);
            if (owner == null || owner.level() != serverLevel) return;

            Hk3EventManager.onMultiblockFormed(owner, getDefinition().getId().getPath());
        } catch (Exception e) {
            LOGGER.warn("[HK3GTL] 多方块事件通知失败", e);
        }
    }

    /**
     * GUI 显示追加电网绑定状态行：已绑定显示玩家/队伍名，未绑定给出操作提示。
     */
    @Override
    public void addDisplayText(List<Component> textList) {
        super.addDisplayText(textList);
        try {
            // 无限并行 + 无限跨配方能力标注：仅对启用多配方逻辑（enableMultiRecipe()==true）的制造类机器显示，
            // 研究矩阵 / 崩坏能转换器等重写为 false 的非配方机器不显示，避免错标。
            if (enableMultiRecipe()) {
                textList.add(Component.translatable("hk3gtl.machine.unlimited_parallel_cross_recipe")
                        .withStyle(net.minecraft.ChatFormatting.AQUA));
            }
            if (ownerUUID == null) {
                textList.add(Component.translatable("hk3gtl.machine.player_grid.unbound"));
            } else if (getLevel() != null) {
                textList.add(Component.translatable("hk3gtl.machine.player_grid.bound",
                        com.hepdd.gtmthings.utils.TeamUtil.GetName(getLevel(), ownerUUID)));
            }
            // 双能源机器：显示每 tick 崩坏能消耗 + 当前网络余额
            long honkaiCost = Hk3DualEnergyCosts.getMachineDefault(getDefinition().getId().getPath());
            if (honkaiCost > 0) {
                BigInteger balance = ownerUUID == null ? BigInteger.ZERO : HonkaiWirelessNetwork.getStoredAmount(ownerUUID);
                BigInteger defaultCost = BigInteger.valueOf(honkaiCost);
                textList.add(Component.translatable("hk3gtl.machine.dual_energy.cost",
                        Hk3HonkaiEnergyFormatter.formatEngineering(defaultCost, 4),
                        Hk3HonkaiEnergyFormatter.formatCompact(balance))
                        .withStyle(net.minecraft.ChatFormatting.LIGHT_PURPLE));
                if (ownerUUID != null && balance.compareTo(defaultCost) < 0) {
                    textList.add(Component.translatable("hk3gtl.machine.dual_energy.insufficient")
                            .withStyle(net.minecraft.ChatFormatting.RED));
                }
            }
        } catch (Throwable ignored) {
            // 显示行失败不影响 GUI 主体
        }
    }

    /**
     * 检查结构中是否存在创造能源仓 / 激光源仓。
     * 使用注册 ID 路径 contains 匹配，兼容 GT 各子模块的衍生命名（如 creative_energy_hatch 等）。
     */
    private boolean hasCreativeHatch() {
        for (IMultiPart part : getParts()) {
            MetaMachine machine = part.self();
            String defId = machine.getDefinition().getId().getPath();
            if (defId.contains("creative_energy") || defId.contains("creative_laser")) {
                return true;
            }
        }
        return false;
    }

    /** 聚合所有崩坏能仓的当前存量（不分输入/输出） */
    public long getTotalHonkai() {
        long sum = 0L;
        for (HonkaiEnergyHatchPartMachine h : honkaiHatches) {
            IHonkaiEnergyContainer c = h.getContainer();
            if (c == null) continue;
            sum += c.getAmount();
            if (sum < 0) return Long.MAX_VALUE;
        }
        return sum;
    }

    // ── 双向传输 ────────────────────────────────────────────────────────────

    /** 从所有崩坏能仓抽出能量 */
    public long consumeHonkai(long amount, boolean simulate) {
        if (amount <= 0) return 0;
        long remaining = amount;
        for (HonkaiEnergyHatchPartMachine h : honkaiHatches) {
            IHonkaiEnergyContainer c = h.getContainer();
            if (c == null || !c.canExtract()) continue;
            long got = c.extract(remaining, simulate);
            remaining -= got;
            if (remaining <= 0) break;
        }
        return amount - remaining;
    }

    /** 向崩坏能仓注入能量（发电机类机器用） */
    public long fillHonkai(long amount, boolean simulate) {
        if (amount <= 0) return 0;
        long remaining = amount;
        for (HonkaiEnergyHatchPartMachine h : honkaiHatches) {
            IHonkaiEnergyContainer c = h.getContainer();
            if (c == null || !c.canInsert()) continue;
            long put = c.insert(remaining, simulate);
            remaining -= put;
            if (remaining <= 0) break;
        }
        return amount - remaining;
    }

}
