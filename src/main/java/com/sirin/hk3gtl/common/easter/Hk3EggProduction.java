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























public final class Hk3EggProduction {
    public static final String OWNER="hk3gtl_egg_machine_owner";
    public static final String REACTOR_FUEL_SETTLED="hk3gtlEggReactorFuelSettled";
    private static final Set<String> WATCHED=java.util.stream.Stream.concat(
            Hk3EggRules.forEvent("produced").stream().flatMap(r->r.checks().stream()).filter(c->c.field().equals("item")&&c.op()==Hk3EggRules.Operation.EQ).map(Hk3EggRules.Check::value),
            java.util.stream.Stream.of("receipt:12","receipt:167","receipt:168")).collect(java.util.stream.Collectors.toUnmodifiableSet());
    private Hk3EggProduction(){}
    private static String itemId(ItemStack stack){
        var soulium=com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper.get(com.gregtechceu.gtceu.api.data.tag.TagPrefix.ingot,com.sirin.hk3gtl.common.material.SouliumMaterial.SOULIUM);
        var frame=com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper.get(com.gregtechceu.gtceu.api.data.tag.TagPrefix.frameGt,com.sirin.hk3gtl.common.material.SouliumMaterial.SOULIUM);
        if(!frame.isEmpty()&&stack.is(frame.getItem()))return "material:soulium_frame";
        return !soulium.isEmpty()&&stack.is(soulium.getItem())?"material:soulium_ingot":BuiltInRegistries.ITEM.getKey(stack.getItem()).toString();
    }
    public static boolean watches(String item){return item.startsWith(Hk3EggVoltageProgress.PREFIX)||item.startsWith(Hk3EggEngineering.PREFIX)||item.startsWith("context:hw_node:")||item.startsWith("context:interface:")||item.equals("context:world_mining_deliveries")||item.startsWith("context:voltage_changed:")||item.equals("context:manual_voltage_ready")||item.matches("context:circuit_(?:[0-9]|[12][0-9]|3[0-2])")||WATCHED.contains(item)||Set.of("receipt:14","receipt:15","receipt:17","receipt:18","receipt:39","receipt:48","receipt:49","receipt:269","receipt:277","receipt:166","receipt:483","receipt:245","receipt:270","receipt:235","receipt:279","receipt:278","receipt:249","gtceu:advanced_smd_transistor","context:generated_eu","receipt:34","receipt:68","receipt:204","receipt:205","receipt:206","receipt:207","receipt:248","receipt:182","receipt:209","receipt:210","receipt:335","receipt:84","receipt:276","receipt:271","receipt:272","receipt:273","receipt:274","receipt:7","receipt:38","receipt:195","receipt:47","context:higher_circuit","receipt:233","context:240","receipt:240","gtceu:advanced_smd_capacitor","receipt:163","receipt:165","receipt:187","receipt:188","receipt:189","receipt:190","receipt:216","receipt:220","receipt:250","receipt:258","receipt:265","receipt:266","receipt:267","receipt:268","gtceu:smd_resistor","gtlcore:max_electric_motor","gtladditions:harmonizing_core").contains(item);}
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
        reactorFuel(machine,recipe,data,owner);
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
            var stack=choices[0];Hk3EggVoltageProgress.produced(level.getServer(),owner,recipe,stack);if(machine.getDefinition().getId().toString().equals("gtlsupb:fragment_world_collector"))data.produced(owner,"receipt:270",1);String id=itemId(stack);circuitHistory(data,owner,stack,before.getOrDefault("context:higher_circuit",0L)>0);data.produced(owner,id,stack.getCount());
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
    private static void reactorFuel(MetaMachine machine,GTRecipe recipe,Hk3EggProductionData data,UUID owner){
        if(recipe.data.getBoolean(REACTOR_FUEL_SETTLED)
                ||!(machine instanceof com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine process)
                ||!Set.of("I19","I20","I21","I22").contains(process.researchRole())
                ||!com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime.allowed(process,recipe))return;
        long consumed=0;
        for(var content:recipe.getInputContents(ItemRecipeCapability.CAP)){
            if(content.maxChance<=0||content.chance<content.maxChance)continue;
            var ingredient=ItemRecipeCapability.CAP.of(content.content);
            if(!fixedOutput(ingredient))continue;
            var choices=ingredient.getItems();
            if(choices.length==1&&com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels.FUEL_IDS
                    .contains(BuiltInRegistries.ITEM.getKey(choices[0].getItem()).toString()))
                consumed+=(long)choices[0].getCount()*com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuels
                        .bundleSize(BuiltInRegistries.ITEM.getKey(choices[0].getItem()).toString());
        }
        data.produced(owner,"context:reactor_fuel_consumed",consumed);
        recipe.data.putBoolean(REACTOR_FUEL_SETTLED,true);
    }
    public static void worldDelivered(net.minecraft.server.MinecraftServer server,
            com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger.Transaction tx){
        boolean resources=tx.receipt().getCompound("Outputs").getList("ResourcePackages",10).stream().anyMatch(raw->{
            var pack=(net.minecraft.nbt.CompoundTag)raw;
            return pack.getList("Items",10).stream().anyMatch(row->((net.minecraft.nbt.CompoundTag)row).getInt("Count")>0)
                    ||pack.getList("Fluids",10).stream().anyMatch(row->((net.minecraft.nbt.CompoundTag)row).getInt("Amount")>0);
        });
        var data=Hk3EggProductionData.get(server);
        if(resources&&data.count(tx.actor(),"receipt:168")==0)data.produced(tx.actor(),"receipt:168",1);
        if(resources&&tx.action()==com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger.Action.MINE){
            if(data.count(tx.actor(),"context:world_mining_deliveries")<10)data.produced(tx.actor(),"context:world_mining_deliveries",1);
            if(data.count(tx.actor(),"receipt:15")==0)data.produced(tx.actor(),"receipt:15",1);
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
        Hk3EggVoltageProgress.poll(p);
        Hk3EggEngineering.poll(p);
        for(var e:Hk3EggProductionData.get(p.server).counts(p.getUUID()).entrySet()){
            if(e.getKey().startsWith("receipt:")&&e.getValue()>0)Hk3EggRuntime.observe(p,"industrial_receipt",Map.of("case",e.getKey().substring(8)));
            else Hk3EggRuntime.observe(p,"produced",Hk3EggRuntime.fields("item",e.getKey(),"count",Long.toString(e.getValue())));
        }
    }
}
