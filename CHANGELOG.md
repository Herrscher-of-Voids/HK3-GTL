# 崩坏三-GTM 开发变动记录与进度追踪

> 本文档记录从初始状态到当前版本的所有代码变动，以及 P1 路线图的完成状态。
> 最后更新：2026-04-08

---

## 一、P1 路线图完成状态

### 1.1 电压系统扩展 — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.1.1 | Mixin 扩展 `GTValues.V[]` 到 31 个元素 (Tier 0~30) | ✅ |
| 1.1.2 | Mixin 扩展 `VN[]` / `VNF[]` (海渊/虚数/量子/终焉) | ✅ |
| 1.1.3 | Mixin 扩展 `VA[]` + `Hk3Values.VA_LONG[]` (long 版) | ✅ |
| 1.1.4 | JEI 电压显示适配 (`GTRecipeWidgetMixin` 扩展到 30 级) | ✅ |
| 1.1.5 | 验证：JEI 中可见海渊 I 电压 | ✅ |

### 1.2 魂钢工业链 — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.2.1 | 魂钢合成配方链 (shirabon + magmatter + neuro_processor → 前体 → 基质 → 初生质 → 锭) | ✅ |
| 1.2.2 | 移除魂钢 GT 自动配方 (NO_SMELTING + NO_SMASHING + removeRecipes) | ✅ |
| 1.2.3 | 崩坏能结晶获取配方 (吸收塔 → 颗粒 → 结晶 → 液态崩坏能) | ✅ |
| 1.2.4 | 魂钢前体处理配方 (前体混合物 → 活化纳米基质 → 初生质) | ✅ |
| 1.2.5 | 魂钢后加工 (板/框架/细丝/箔 通过 GT 标准机) | ✅ |

### 1.3 多方块机器 — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.3.1 | 崩坏能吸收塔 `honkai_absorption_tower` | ✅ |
| 1.3.2 | 崩坏能结晶凝结厂 `honkai_crystal_condenser` | ✅ |
| 1.3.3 | 魂钢冶铸中心 `soulium_smeltery` | ✅ |
| 1.3.4 | 3 种自定义 RecipeType 注册 | ✅ |
| 1.3.5 | 创造能源仓禁入成型 (`Hk3WorkableMultiblockMachine`) | ✅ |

### 1.4 海渊 I 八大件 — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.4.1 | 海渊 I 电动马达 | ✅ 物品+配方+贴图 |
| 1.4.2 | 海渊 I 电力活塞 | ✅ 物品+配方+贴图 |
| 1.4.3 | 海渊 I 电动泵 | ✅ 物品+配方+贴图 |
| 1.4.4 | 海渊 I 传送带 | ✅ 物品+配方+贴图 |
| 1.4.5 | 海渊 I 机械臂 | ✅ 物品+配方+贴图 |
| 1.4.6 | 海渊 I 力场发生器 | ✅ 物品+配方+贴图 |
| 1.4.7 | 海渊 I 发射器 | ✅ 物品+配方+贴图 |
| 1.4.8 | 海渊 I 传感器 | ✅ 物品+配方+贴图 |
| 1.4.9 | 贴图 | ✅ 仿 GT 风格像素画（深海蓝/紫/青配色） |

### 1.5 海渊 I~IV 电路 — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.5.1 | 4 级电路物品注册 (circuit_abyss_1~4) | ✅ |
| 1.5.2 | GT 电路标签绑定 (forge:circuits/ab-i~iv) | ✅ |
| 1.5.3 | 电路合成配方 (组装机, 海渊I EU/t) | ✅ |
| 1.5.4 | 电路贴图 (16x16 量子之海配色) | ✅ |

### 1.6 崩坏能系统基础 — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.6.1 | 崩坏能吸收塔可运行 | ✅ |
| 1.6.2 | 崩坏能结晶凝结厂可运行（编程电路 1=结晶 / 2=液态） | ✅ |
| 1.6.3 | 液态崩坏能流体注册 | ✅ |

### 1.7 语言文件与 JEI — 已完成

| 编号 | 任务 | 状态 |
|---:|---|:---:|
| 1.7.1 | zh_cn.json / en_us.json 双语 | ✅ |
| 1.7.2 | JEI 配方显示修复 (GTRecipeWidgetMixin 兜底) | ✅ |

### 待处理项

| 项目 | 状态 | 说明 |
|---|:---:|---|
| 八大件贴图 | ✅ | 8 张仿 GT 风格 16x16 PNG 已生成 |
| 5 种机壳合成配方 | ✅ | 已在 `addCasingRecipes()` 注册（组装机，海渊 I 级） |
| 凝结厂编程电路区分 | ✅ | circuitMeta(1)=结晶 / circuitMeta(2)=液态 |
| 事件系统（P1） | ✅ | `Hk3EventManager` 已实装 6 个事件（4 里程碑 + 2 多方块） |
| 流体客户端修复 | ✅ | `ResourceLocation.withDefaultNamespace` → `new ResourceLocation` |
| P1 闭环验证 | ❌ | 需实际游戏内完整走通 |

---

## 二、文件变动清单

### 新增文件（27 个 Java + 资源文件）

**核心入口**
- `src/main/java/.../Hk3Gtm.java` — @Mod 主类，注册物品/方块/流体/创造页签
- `src/main/java/.../Hk3GtAddon.java` — @GTAddon，配方增删入口

**数据层**
- `src/main/java/.../common/data/Hk3Constants.java` — mod_id 常量
- `src/main/java/.../common/data/Hk3Values.java` — 扩展电压查询工具（VA_LONG 等）
- `src/main/java/.../common/data/Hk3Tiers.java` — Tier 索引常量 (ABYSS_1~FINALITY_4)
- `src/main/java/.../common/data/Hk3RecipeTypes.java` — 3 种自定义 RecipeType
- `src/main/java/.../common/data/Hk3Machines.java` — 3 台多方块机器定义
- `src/main/java/.../common/data/Hk3RecipeAdder.java` — 全部 GT 配方（310行）
- `src/main/java/.../common/data/Hk3CreativeTabs.java` — 创造模式标签页

**物品**
- `src/main/java/.../common/item/Hk3Items.java` — DeferredRegister 总线
- `src/main/java/.../common/item/MaterialItems.java` — 崩坏能体系 + 魂钢中间件（13 件）
- `src/main/java/.../common/item/Hk3ComponentItems.java` — 海渊 I 八大件（8 件）
- `src/main/java/.../common/item/Hk3CircuitItems.java` — 海渊 I~IV 电路（4 件）

**方块**
- `src/main/java/.../common/block/Hk3Blocks.java` — DeferredRegister 总线
- `src/main/java/.../common/block/CasingBlocks.java` — 5 种机壳方块

**流体**
- `src/main/java/.../common/fluid/Hk3Fluids.java` — 液态崩坏能 + 浓缩崩坏能

**材料**
- `src/main/java/.../common/material/Hk3Materials.java` — 材料注册入口
- `src/main/java/.../common/material/SouliumMaterial.java` — 魂钢 GT 材料

**机器**
- `src/main/java/.../common/machine/Hk3WorkableMultiblockMachine.java` — 禁止创造仓

**Mixin（8 个）**
- `GTValuesMixin.java` — 扩展 V/VN/VNF/VA/VH/VHA/VOLTAGE_NAMES 到 31 元素
- `GTRecipeTypesMixin.java` — 注入 Hk3RecipeTypes.init()
- `GTMachinesMixin.java` — 注入 Hk3Machines.init()
- `GTRecipeWidgetMixin.java` — JEI 兜底 + 扩展电压上限到 30 级
- `ItemRecipeCapabilityMixin.java` — JEI 空内容防 AIOOB
- `SkyTearsAndGregHeartMixin.java` — GTLAdditions 兼容
- `AvaritiaShaderMixin.java` — Re-Avaritia 着色器兼容
- `CosmicBakeModelMixin.java` — Re-Avaritia 模型兼容

**资源文件**
- `src/main/resources/hk3gtm.mixins.json` — Mixin 配置
- `src/main/resources/META-INF/mods.toml` — 模组元数据
- `src/main/resources/assets/hk3gtm/lang/zh_cn.json` — 中文语言（64 条）
- `src/main/resources/assets/hk3gtm/lang/en_us.json` — 英文语言（64 条）
- `src/main/resources/data/forge/tags/items/circuits/ab-i~iv.json` — 电路标签（4 个）
- 7 个 blockstates JSON
- 8 个 block model JSON（5 机壳 + 3 控制器）
- 33 个 item model JSON
- 贴图：电路板 4 张 + 机壳 5 张 + 控制器正面 3 张（通过 `tools/GenerateTextures.java` 生成）

**构建/工具**
- `build.gradle` — 修改：增加 JEI Integration 依赖、processResources 扩展
- `gradle.properties` — 修改：增加 jei_integration_version/curse_file
- `tools/GenerateTextures.java` — 贴图程序化生成器
- `.cursor/rules/hk3gtm-project.mdc` — 项目规则

**KubeJS**
- `kubejs/server_scripts/recipes/removal.js` — 移除 EBF 配方 + 禁止创造物品
- `kubejs/server_scripts/events/milestone_test.js` — 事件原型
- `kubejs/server_scripts/recipes/soulium_chain.js.disabled` — 已禁用（冲突）
- `kubejs/server_scripts/recipes/honkai_energy_chain.js.disabled` — 已禁用（冲突）
- `kubejs/server_scripts/recipes/soulium_override.js.disabled` — 已禁用（冲突）

---

## 三、关键 Bug 修复记录

| 问题 | 根因 | 修复方式 |
|---|---|---|
| JEI 所有 GT 配方消失 | `ItemRecipeCapability.createXEIContainerContents` 遇空/畸形物品内容 → AIOOB → 整个 GTJEIPlugin 注册中断 | `GTRecipeWidgetMixin` 在 `collectStorage` 的 4 个 `createXEIContainerContents` 调用点做 try/catch 兜底 |
| 兜底后 JEI 仍崩溃 | `List.of()` 返回不可变列表，`collectStorage` 后续 `.add()` 抛 `UnsupportedOperationException` | 改为 `new ArrayList<>()` |
| 流体不在 JEI 显示 | 3 个 KubeJS 脚本与 Java 配方冲突，`soulium_chain.js` 语法错误导致配方异常 | 禁用 3 个 `.js` 文件 |
| 游戏启动崩溃 `Invalid modId: ${mod_id}` | `bin/main/META-INF/mods.toml` 缓存未经 processResources 处理 | 删除 `bin/` 目录 + `clean build` |
| 创造能源仓参与多方块成型 | `setError` 不能阻止成型 | 改用 `onStructureInvalid()` 拆结构 |
| setMaxIOSize 物品输入为 0 导致 JEI AIOOB | 吸收塔 RecipeType 无物品输入槽位 | 改为至少 1（编程电路占位） |

---

## 四、当前版本总结

**版本**: 0.1.0-alpha (P1 海渊基础版)

**已实现核心功能**:
- 16 级新电压体系 (海渊/虚数/量子/终焉 各 4 级)
- 魂钢工业链完整 8 步配方 (前体 → 锭 → 板/框架/细丝/箔)
- 3 台自定义多方块机器 (吸收塔/凝结厂/冶铸中心)
- 海渊 I 八大件 + 4 级电路
- 崩坏能体系 (颗粒 → 结晶 → 液态崩坏能)
- JEI 完整集成 (配方显示 + 电压扩展)
- 魂钢 GT 材料 (自动生成板/杆/齿轮等形态件)

---

## 五、未解决问题

### 高优先级（阻塞 P1 闭环）

| # | 问题 | 影响 | 备注 |
|---|---|---|---|
| 1 | ~~八大件缺少贴图 PNG~~ | ✅ 已解决 | `generateComponents()` 生成 8 张仿 GT 风格像素画 |
| 2 | ~~5 种机壳没有合成配方~~ | ✅ 已解决 | `addCasingRecipes()` 已实现 5 种机壳组装机配方 |
| 3 | ~~浓缩崩坏能流体没有合成配方~~ | ✅ 已移除 | 设计文档无此流体，代码中也不存在，属于 CHANGELOG 误记 |
| 4 | ~~JEI 流体显示待验证~~ | ✅ 已修复 | `ResourceLocation.withDefaultNamespace` 改为 `new ResourceLocation`（1.20.1 兼容） |
| 5 | P1 闭环未验证 | 不确定从 MAX 毕业到海渊 I 是否全流程可走通 | 需实际游戏内测试 |

### 中优先级（功能完善）

| # | 问题 | 影响 | 备注 |
|---|---|---|---|
| 6 | ~~事件系统未实装~~ | ✅ P1 事件已实装 | `Hk3EventManager` 实现 4 个里程碑 + 2 个多方块首建事件，状态存储在玩家 persistentData |
| 7 | Max 文明电路母机多方块未实装 | 设计文档标 P1，当前电路暂用 GT 组装机 | 后续可做专用多方块 |
| 8 | 魂钢 GT 自动加工配方移除待验证 | `Hk3GtAddon.removeRecipes()` 列举了多种 ID 模式，实际是否匹配未确认 | 需进游戏检查是否还有廉价魂钢加工路线 |
| 9 | 吸收塔/凝结厂/冶铸中心的配方实际运行未验证 | 配方在 JEI 显示了，但多方块结构能否正常匹配、启动、产出未确认 | 需搭建并测试 |

### 低优先级（优化/美化）

| # | 问题 | 影响 | 备注 |
|---|---|---|---|
| 10 | 贴图质量为程序化生成 | 视觉效果基础，后续可请美术精修 | 电路板/机壳/控制器正面均为 `tools/GenerateTextures.java` 生成 |
| 11 | `build/resources/main` 与 `bin/` 缓存问题 | 偶发 `${mod_id}` 未替换导致启动崩溃 | 已知规避方式：删 `bin/` + `clean build` |
| 12 | `SouliumMaterial` 使用已废弃的 `ResourceLocation(String)` | 编译警告 | 可改为 `ResourceLocation.tryParse()` 或双参数构造 |
| 13 | `Hk3Gtm` 使用已废弃的 `FMLJavaModLoadingContext.get()` | 编译警告 | 1.20.1 仍可用，后续版本需迁移 |

---

## 六、下一步计划

**P1 收尾（预计工作量）**:
1. ~~生成八大件贴图~~ — ✅ 已完成（仿 GT 风格像素画）
2. ~~添加 5 种机壳合成配方~~ — ✅ 已完成
3. ~~添加浓缩崩坏能流体配方~~ — ✅ 设计文档无此流体，已移除
4. ~~实装 Max 起始阶段事件系统~~ — ✅ 已实装 6 个 P1 事件
5. 游戏内 P1 闭环验证 — 中（唯一剩余项）

**P2 预备**:
- 海渊级电路铸造平台（专用多方块）
- 魂钢 P2 升级配方（稳定初生质 → 定向构件）
- 海渊 II~IV 八大件
- 海渊阶段事件系统
