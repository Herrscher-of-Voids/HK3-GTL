package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.core.registries.BuiltInRegistries;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:24:23（修订128）：删除无；新增GT成功输出/手工制造归属适配；修改无；用途：仅必定产出且禁止虚空的真实完成，不承认输入、预览、库存或附近玩家；无归属机器不猜。 */
/** 【变更记录 #2】2026-10-01 04:25:20（修订128）：删除：旧固定上限或被替代的分支；新增/修改：魂钢统计通过当前ChemicalHelper物品实例匹配，避免猜测GT自动生成命名空间；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 04:41:04（修订128）：删除：旧固定上限或被替代的分支；新增/修改：随机数量及未知自定义输出Ingredient不作固定产量凭据；有界解包SizedIngredient，禁止重新抽样；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #4】2026-10-01 04:43:52（修订128）：删除：旧固定上限或被替代的分支；新增/修改：NBT固定物品使用Forge实际StrictNBTIngredient类型；GT的NBTIngredient只是工厂工具；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #5】2026-10-01 04:45:29（修订128）：删除：旧固定上限或被替代的分支；新增/修改：AE压印机真实放置绑定归属；离线已确认压印事务旁注随产量账本延后投递；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #6】2026-10-01 04:58:34（修订128）：删除：旧固定上限或被替代的分支；新增/修改：魂钢框架从正式材料解析；正式工业数量拒绝手工增量；配方消耗证明与本人历史产物关联，离线回执延后投递；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 05:36:00（修订128）：删除：旧固定上限或被替代的分支；新增/修改：本人从容器取出树脂印刷板后，由实际成功配方输入证明用于新配方；电容保留真实制造计数；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 05:47:22（修订128）：删除：无；新增/修改：只有真实制造的MV及以上电路留下高阶记录，再制造基础电路才触发；16档新电压使用当前tag定义；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #9】2026-10-01 05:56:06（修订128）：删除：无；新增/修改：高阶后再造基础电路读取批次开始前历史，不能把同一批次两种输出的遍历先后当新一轮制造；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #10】2026-10-01 06:04:42（修订128）：删除：无；新增/修改：控制器上线回执纳入实际产量旁注白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #11】2026-10-01 06:11:31（修订128）：删除：无；新增/修改：双能源实际扣款配对回执加入本人旁注白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #12】2026-10-01 06:15:25（修订128）：删除：无；新增/修改：无线覆盖板实际交付旁注纳入当前账本白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #13】2026-10-01 06:19:47（修订128）：删除：无；新增/修改：LV无线能源覆盖板仅以实际接收结果留下旁注，不把扣款或模拟当接收；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #14】2026-10-01 06:23:20（修订128）：删除：无；新增/修改：本人丢弃结晶确因虚空销毁后记录，离线回执纳入白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #15】2026-10-01 06:27:59（修订128）：删除：无；新增/修改：AE转化参与者、CPU正常交付与1221数量操作进入真实生产旁注白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #16】2026-10-01 06:31:11（修订128）：删除：无；新增/修改：AE已安装升级卡实际作用及单元真实流体插入旁注加入白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #17】2026-10-01 06:45:17（修订128）：删除：无；新增/修改：仅真实配方EU输出累计到本人账本，34/68回执支持归属者离线后领取；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #18】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：记录本人实际先进贴片晶体管产出，用于之后对应配方阅读前置；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #19】2026-10-01 12:16:23（修订128）：删除：无；新增/修改：电池真实充电回执可持久化并在本人上线后投递；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #20】2026-10-01 12:33:29（修订128）：删除：无；新增/修改：覆盖板满载暂停恢复回执进入离线生产旁注白名单；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #21】2026-10-01 13:24:37（修订128）：删除：无；新增/修改：本人实际改过的配置与成功完成配方的IntCircuitIngredient匹配，不靠电路库存授予235；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #22】2026-10-01 13:31:18（修订128）：删除：无；新增/修改：碎界采集器已由GTL正常输出事务调用，仅有实际固定物品输出才记270；模拟卡真实转换旁注共用归属；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #23】2026-10-01 13:36:23（修订128）：删除：无；新增/修改：新分支已实际送入的固定配方物料被消耗且机器成功产出后授483，单建管线或未产出不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggProduction {
    public static final String OWNER="hk3gtl_egg_machine_owner";
    private static final Set<String> WATCHED=Hk3EggRules.forEvent("produced").stream().flatMap(r->r.checks().stream()).filter(c->c.field().equals("item")&&c.op()==Hk3EggRules.Operation.EQ).map(Hk3EggRules.Check::value).collect(java.util.stream.Collectors.toUnmodifiableSet());
    private Hk3EggProduction(){}
    private static String itemId(ItemStack stack){
        var soulium=com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper.get(com.gregtechceu.gtceu.api.data.tag.TagPrefix.ingot,com.sirin.hk3gtl.common.material.SouliumMaterial.SOULIUM);
        var frame=com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper.get(com.gregtechceu.gtceu.api.data.tag.TagPrefix.frameGt,com.sirin.hk3gtl.common.material.SouliumMaterial.SOULIUM);
        if(!frame.isEmpty()&&stack.is(frame.getItem()))return "material:soulium_frame";
        return !soulium.isEmpty()&&stack.is(soulium.getItem())?"material:soulium_ingot":BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
    }
    public static boolean watches(String item){return item.matches("context:circuit_(?:[0-9]|[12][0-9]|3[0-2])")||WATCHED.contains(item)||Set.of("receipt:483","receipt:245","receipt:270","receipt:235","receipt:279","receipt:278","receipt:249","gtceu:advanced_smd_transistor","context:generated_eu","receipt:34","receipt:68","receipt:204","receipt:205","receipt:206","receipt:207","receipt:248","receipt:182","receipt:209","receipt:210","receipt:335","receipt:84","receipt:276","receipt:271","receipt:272","receipt:273","receipt:274","receipt:7","receipt:38","receipt:195","receipt:47","context:higher_circuit","receipt:233","context:240","receipt:240","gtceu:advanced_smd_capacitor","receipt:163","receipt:165","receipt:187","receipt:188","receipt:189","receipt:190","receipt:216","receipt:220","receipt:250","receipt:258","receipt:265","receipt:266","receipt:267","receipt:268","gtceu:smd_resistor","gtlcore:max_electric_motor","gtladditions:harmonizing_core").contains(item);}
    public static void handmade(ServerPlayer p,ItemStack stack){
        if(!stack.isEmpty()&&!itemId(stack).startsWith("material:")&&!itemId(stack).equals("hk3gtl:honkai_energy_crystal")){
            var data=Hk3EggProductionData.get(p.server);circuitHistory(data,p.getUUID(),stack,data.counts(p.getUUID()).getOrDefault("context:higher_circuit",0L)>0);data.produced(p.getUUID(),itemId(stack),stack.getCount());
        }
    }
    private static void circuitHistory(Hk3EggProductionData data,UUID owner,ItemStack stack,boolean higherBefore){
        if(stack.isEmpty())return;
        if(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals("gtceu:basic_electronic_circuit")&&higherBefore)data.produced(owner,"receipt:233",1);
        for(int tier=2;tier<=30;tier++){
            String key=tier<15?com.gregtechceu.gtceu.api.GTValues.VN[tier].toLowerCase(java.util.Locale.ROOT):com.sirin.hk3gtl.common.constants.Hk3Tiers.voltageKey(tier);
            if(stack.is(net.minecraft.tags.ItemTags.create(new net.minecraft.resources.ResourceLocation("forge","circuits/"+key)))){data.produced(owner,"context:higher_circuit",1);break;}
        }
    }
    public static void receipt(MetaMachine machine,int id){
        if(!(machine.getLevel() instanceof net.minecraft.server.level.ServerLevel level)||!(machine.getHolder() instanceof BlockEntity be)||!level.getServer().isSameThread())return;
        UUID owner=machine instanceof Hk3WorkableMultiblockMachine own?own.getOwnerUUID():be.getPersistentData().hasUUID(OWNER)?be.getPersistentData().getUUID(OWNER):null;
        if(owner!=null)Hk3EggProductionData.get(level.getServer()).produced(owner,"receipt:"+id,1);
    }
    public static void placed(ServerPlayer p,net.minecraft.core.BlockPos pos){
        if(p.level().getBlockEntity(pos) instanceof appeng.blockentity.networking.ControllerBlockEntity controller){controller.getPersistentData().putUUID(OWNER,p.getUUID());controller.setChanged();if(controller.getMainNode().isActive())Hk3EggProductionData.get(p.server).produced(p.getUUID(),"receipt:195",1);}
        if(p.level().getBlockEntity(pos) instanceof appeng.blockentity.misc.InscriberBlockEntity inscriber){inscriber.getPersistentData().putUUID(OWNER,p.getUUID());inscriber.setChanged();}
        var machine=MetaMachine.getMachine(p.level(),pos);if(machine==null||!(machine.getHolder() instanceof BlockEntity be))return;
        be.getPersistentData().putUUID(OWNER,p.getUUID());be.setChanged();
    }
    public static void settled(IRecipeLogicMachine logic,GTRecipe recipe){
        var machine=logic.self();var level=machine.getLevel();
        if(level==null||level.isClientSide||level.getServer()==null||logic.canVoidRecipeOutputs(ItemRecipeCapability.CAP)||!(machine.getHolder() instanceof BlockEntity be))return;
        UUID owner=machine instanceof Hk3WorkableMultiblockMachine own?own.getOwnerUUID():be.getPersistentData().hasUUID(OWNER)?be.getPersistentData().getUUID(OWNER):null;
        if(owner==null)return;
        var data=Hk3EggProductionData.get(level.getServer());
        var before=data.counts(owner);
        for(var content:recipe.getInputContents(ItemRecipeCapability.CAP)){
            var ingredient=ItemRecipeCapability.CAP.of(content.content);
            for(int depth=0;depth<16&&ingredient instanceof com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient sized;depth++)ingredient=sized.getInner();
            if(ingredient instanceof com.gregtechceu.gtceu.api.recipe.ingredient.IntCircuitIngredient){var stacks=ingredient.getItems();if(stacks.length==1){int cfg=com.gregtechceu.gtceu.common.item.IntCircuitBehaviour.getCircuitConfiguration(stacks[0]);if(before.getOrDefault("context:circuit_"+cfg,0L)>0)data.produced(owner,"receipt:235",1);}}
        }
        for(var content:recipe.getOutputContents(ItemRecipeCapability.CAP)){
            if(content.maxChance<=0||content.chance<content.maxChance)continue;
            var ingredient=ItemRecipeCapability.CAP.of(content.content);
            if(!fixedOutput(ingredient))continue;
            var choices=ingredient.getItems();if(choices.length!=1||choices[0].isEmpty())continue;
            be.getPersistentData().putBoolean("hk3EggActualProduction",true);be.setChanged();
            var branch=be.getPersistentData();if(branch.hasUUID("hk3EggBranchBy")&&branch.getUUID("hk3EggBranchBy").equals(owner)&&!branch.getString("hk3EggBranchItem").isEmpty()&&consumes(recipe,branch.getString("hk3EggBranchItem"))){
                var player=level.getServer().getPlayerList().getPlayer(owner);var at=net.minecraft.core.BlockPos.of(branch.getLong("hk3EggBranchPipe"));if(player!=null&&player.level()==level&&Hk3EggBuildMemory.get(player.serverLevel()).owns(player,at)){data.produced(owner,"receipt:483",1);branch.remove("hk3EggBranchBy");branch.remove("hk3EggBranchItem");be.setChanged();}
            }
            var stack=choices[0];if(machine.getDefinition().getId().toString().equals("gtlsupb:fragment_world_collector"))data.produced(owner,"receipt:270",1);String id=itemId(stack);circuitHistory(data,owner,stack,before.getOrDefault("context:higher_circuit",0L)>0);data.produced(owner,id,stack.getCount());
            if(id.equals("gtceu:advanced_smd_resistor")&&before.getOrDefault("gtceu:smd_resistor",0L)>0)data.produced(owner,"receipt:216",1);
            if(id.equals("gtceu:resin_printed_circuit_board")&&consumes(recipe,"gtceu:resin_circuit_board"))data.produced(owner,"receipt:220",1);
        }
        if(before.getOrDefault("context:240",0L)>0&&consumes(recipe,"gtceu:resin_printed_circuit_board"))data.produced(owner,"receipt:240",1);
        if(before.getOrDefault("gtlcore:max_electric_motor",0L)>0&&consumes(recipe,"gtlcore:max_electric_motor"))data.produced(owner,"receipt:250",1);
        if(before.getOrDefault("gtladditions:harmonizing_core",0L)>0&&consumes(recipe,"gtladditions:harmonizing_core"))data.produced(owner,"receipt:258",1);
        String machineId=machine.getDefinition().getId().toString();
        Integer caseId=Map.of("gtlsupb:primitive_stone_furnace",265,"gtlsupb:quantum_weaver",266,"gtlsupb:electric_assembly_line",267).get(machineId);
        if(caseId!=null)data.produced(owner,"receipt:"+caseId,1);
        if(machineId.equals("gtlsupb:universal_factory")){
            String last=be.getPersistentData().getString("hk3gtl_egg_last_recipe");
            if(!last.isEmpty()&&!last.equals(recipe.id.toString()))data.produced(owner,"receipt:268",1);
            be.getPersistentData().putString("hk3gtl_egg_last_recipe",recipe.id.toString());be.setChanged();
        }
    }
    private static boolean consumes(GTRecipe recipe,String id){
        for(var c:recipe.getInputContents(ItemRecipeCapability.CAP)){
            if(c.maxChance<=0||c.chance<c.maxChance)continue;var ingredient=ItemRecipeCapability.CAP.of(c.content);if(!fixedOutput(ingredient))continue;
            var choices=ingredient.getItems();if(choices.length==1&&!choices[0].isEmpty()&&BuiltInRegistries.ITEM.getKey(choices[0].getItem()).toString().equals(id))return true;
        }return false;
    }
    private static boolean fixedOutput(net.minecraft.world.item.crafting.Ingredient ingredient){
        for(int depth=0;depth<16;depth++){
            if(ingredient.getClass()==com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient.class){
                ingredient=((com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient)ingredient).getInner();
            }else return ingredient.getClass()==net.minecraft.world.item.crafting.Ingredient.class
                    ||ingredient.getClass()==net.minecraftforge.common.crafting.StrictNBTIngredient.class;
        }
        return false;
    }
    public static void poll(ServerPlayer p){
        for(var e:Hk3EggProductionData.get(p.server).counts(p.getUUID()).entrySet()){
            if(e.getKey().startsWith("receipt:")&&e.getValue()>0)Hk3EggRuntime.observe(p,"industrial_receipt",Map.of("case",e.getKey().substring(8)));
            else Hk3EggRuntime.observe(p,"produced",Hk3EggRuntime.fields("item",e.getKey(),"count",Long.toString(e.getValue())));
        }
    }
}
