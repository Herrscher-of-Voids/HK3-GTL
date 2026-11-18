package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.dispatch.Hk3EnergyDispatch;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.UUID;

/** 本人明确建立工单后，记录两台已授权机器的真实生产与物料交接。 */
public final class Hk3CrossMachineOrders extends SavedData {
    private static final String ORDER="hk3gtlCrossMachineWorkOrder";
    private static final String INPUT_TICK="hk3gtlCrossMachineInputTick";
    private final CompoundTag orders;

    public Hk3CrossMachineOrders() { this(new CompoundTag()); }
    private Hk3CrossMachineOrders(CompoundTag orders) { this.orders=orders; }
    private static Hk3CrossMachineOrders get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(
                tag->new Hk3CrossMachineOrders(tag.getCompound("Orders")),
                Hk3CrossMachineOrders::new,"hk3gtl_cross_machine_orders");
    }
    @Override public CompoundTag save(CompoundTag tag) { tag.put("Orders",orders.copy());return tag; }

    public static void started(Hk3WorkableMultiblockMachine machine,GTRecipe recipe) {
        var registration=Hk3EnergyDispatch.registration(machine);
        recipe.data.remove(ORDER);
        recipe.data.remove(INPUT_TICK);
        if(registration.hasUUID("Order")) {
            recipe.data.putUUID(ORDER,registration.getUUID("Order"));
            recipe.data.putLong(INPUT_TICK,machine.getLevel().getServer().overworld().getGameTime());
        }
    }

    public static void settled(Hk3WorkableMultiblockMachine machine,GTRecipe recipe) {
        var registration=Hk3EnergyDispatch.registration(machine);
        if(!registration.hasUUID("Order")||!recipe.data.hasUUID(ORDER)
                ||!registration.getUUID("Order").equals(recipe.data.getUUID(ORDER)))return;
        var server=machine.getLevel().getServer();var store=get(server);
        var owner=registration.getUUID("Owner");var team=registration.getUUID("Team");
        var order=registration.getUUID("Order");String key=owner.toString();
        var state=store.orders.getCompound(key);
        if(!state.hasUUID("Order")||!state.getUUID("Order").equals(order)) {
            state=registration.copy();store.orders.put(key,state);
        }
        if(state.getBoolean("Complete"))return;
        var receipt=Hk3ProcessReceipts.settle(Hk3ProcessReceipts.snapshot(recipe),
                machine.getLevel().dimension().location()+"@"+machine.getPos(),server.overworld().getGameTime());
        receipt.putLong("InputTick",recipe.data.getLong(INPUT_TICK));
        receipt.putUUID("Team",team);receipt.putUUID("Owner",owner);receipt.putUUID("Order",order);
        receipt.putString("Controller",machine.getDefinition().getId().toString());
        if(!state.contains("First",Tag.TAG_COMPOUND)) {
            state.put("First",receipt);store.setDirty();return;
        }
        var first=state.getCompound("First");
        if(first.getString("Facility").equals(receipt.getString("Facility"))
                ||receipt.getLong("InputTick")<=first.getLong("Tick"))return;
        var material=handoff(first.getCompound("Outputs"),receipt.getCompound("Inputs"));
        if(material.isEmpty())return;
        state.put("Second",receipt);state.put("Material",material);state.putBoolean("Complete",true);store.setDirty();
        var proof=receipt.copy();proof.put("WorkOrder",state.copy());
        Hk3ResearchData.get(server).recordProcessFact(team,"cross_machine_handoff",proof);
    }

    private static CompoundTag handoff(CompoundTag output,CompoundTag input) {
        for(var outRaw:output.getList("Items",Tag.TAG_COMPOUND)) {
            var out=(CompoundTag)outRaw;var produced=out.getList("Alternatives",Tag.TAG_COMPOUND);
            if(out.getFloat("Chance")!=10000||produced.size()!=1)continue;
            var source=produced.getCompound(0);
            for(var inRaw:input.getList("Items",Tag.TAG_COMPOUND)) {
                var in=(CompoundTag)inRaw;var consumed=in.getList("Alternatives",Tag.TAG_COMPOUND);
                if(in.getFloat("Chance")!=10000||consumed.size()!=1)continue;
                var target=consumed.getCompound(0);
                if(source.getLong("ActualCount")>=target.getLong("ActualCount")
                        &&source.getString("id").equals(target.getString("id"))
                        &&source.getCompound("tag").equals(target.getCompound("tag"))) {
                    var result=new CompoundTag();result.putString("Kind","item");
                    result.putString("Id",source.getString("id"));result.putLong("Count",target.getLong("ActualCount"));
                    result.put("Item",target.copy());return result;
                }
            }
        }
        for(var outRaw:output.getList("Fluids",Tag.TAG_COMPOUND)) {
            var out=(CompoundTag)outRaw;var produced=out.getList("Alternatives",Tag.TAG_STRING);
            if(out.getFloat("Chance")!=10000||produced.size()!=1)continue;
            for(var inRaw:input.getList("Fluids",Tag.TAG_COMPOUND)) {
                var in=(CompoundTag)inRaw;var consumed=in.getList("Alternatives",Tag.TAG_STRING);
                if(in.getFloat("Chance")==10000&&consumed.size()==1
                        &&produced.getString(0).equals(consumed.getString(0))&&out.getLong("Amount")>=in.getLong("Amount")) {
                    var result=new CompoundTag();result.putString("Kind","fluid");
                    result.putString("Id",produced.getString(0));result.putLong("Amount",in.getLong("Amount"));return result;
                }
            }
        }
        return new CompoundTag();
    }

    public static void verified(Hk3ResearchData data,UUID team,CompoundTag receipt) {
        receipt.put("Handoff",data.processFactReceipt(team,"cross_machine_handoff"));
        receipt.put("Authorization",data.processFactReceipt(team,"manual_dispatch"));
        data.recordProcessFact(team,"cross_machine_order",receipt);
    }
}
