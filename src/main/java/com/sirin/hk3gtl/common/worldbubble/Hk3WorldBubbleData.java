package com.sirin.hk3gtl.common.worldbubble;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

public final class Hk3WorldBubbleData extends SavedData {
    private static final String NAME = "hk3gtl_world_bubbles_v5";
    private Hk3WorldBubbleLedger ledger = new Hk3WorldBubbleLedger();
    private Hk3WorldResourceBatches resources = new Hk3WorldResourceBatches();
    private Hk3WorldResourceOutput output = new Hk3WorldResourceOutput();
    private CompoundTag routes = new CompoundTag();
    public Hk3WorldBubbleData() { ledger.onChange(this::setDirty); resources.onChange(this::setDirty); }

    public static Hk3WorldBubbleData get(MinecraftServer server) {
        return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(server, NAME,
                Hk3WorldBubbleData::load, Hk3WorldBubbleData::new);
    }
    /** 调用方须保持服务器线程，不把可写账本暴露给客户端消息直接结算。 */
    public Hk3WorldBubbleLedger ledger() { return ledger; }
    public java.util.List<java.util.UUID> routes(java.util.UUID team) {
        return routes.getList(team.toString(), Tag.TAG_COMPOUND).stream()
                .map(raw -> ((CompoundTag) raw).getUUID("Target")).toList();
    }
    public void discoverRoute(MinecraftServer server, java.util.UUID team, CompoundTag receipt) {
        var entries = routes.getList(team.toString(), Tag.TAG_COMPOUND);
        if (entries.stream().anyMatch(raw -> ((CompoundTag) raw).getUUID("Batch").equals(receipt.getUUID("Batch")))) return;
        // 同一宇宙的第n条解析航路对应同一目标，换队或复制载体不能重置公共采掘次数。
        var target = ledger.discover("catalog-v1/" + server.overworld().getSeed() + "/" + entries.size());
        var token = new CompoundTag();
        token.putString("id", "hk3gtl:located_real_world_bubble");
        token.putInt("Count", 1);
        token.putUUID("Source", target);
        var entry = receipt.copy(); entry.putUUID("Target", target); entry.put("Token", token); entries.add(entry);
        routes.put(team.toString(), entries); setDirty();
    }
    /** 工序完成时一并保存冻结收据与输出余量；实际仓储交付另行扣减。 */
    public CompoundTag completeWithResources(MinecraftServer server,java.util.UUID operation,java.util.UUID actor,
            java.util.UUID scope,CompoundTag completed,Hk3WorldResourceCatalog catalog){
        return completeWithResources(server,operation,actor,scope,completed,catalog,true);
    }
    CompoundTag completeWithResources(MinecraftServer server,java.util.UUID operation,java.util.UUID actor,
            java.util.UUID scope,CompoundTag completed,Hk3WorldResourceCatalog catalog,boolean project){
        if(!server.isSameThread())throw new IllegalStateException("World settlement requires server thread");
        var receipt=Hk3WorldResourceSettlement.prepare(ledger,resources,operation,actor,scope,completed,catalog,server.overworld().getSeed());
        settleCompleted(server,operation,actor,scope,receipt,project);return receipt.copy();
    }
    public void settleCompleted(MinecraftServer server,java.util.UUID operation,java.util.UUID actor,
            java.util.UUID scope,CompoundTag receipt) {
        settleCompleted(server,operation,actor,scope,receipt,true);
    }
    private void settleCompleted(MinecraftServer server,java.util.UUID operation,java.util.UUID actor,
            java.util.UUID scope,CompoundTag receipt,boolean project) {
        if(!server.isSameThread())throw new IllegalStateException("World settlement requires server thread");
        var tx=ledger.transaction(operation);
        if(tx==null)throw new IllegalArgumentException("Unknown world operation");
        Hk3WorldResourceSettlement.validate(ledger,resources,operation,actor,scope,receipt);
        ledger.settle(operation,actor,receipt);
        if(output.stage(ledger.transaction(operation)))setDirty();
        if(project)projectCompleted(server,scope);
    }
    public void deliverOutputs(MinecraftServer server,java.util.UUID scope,String role,String facility,
            Hk3WorldOutputPorts ports){
        if(!server.isSameThread())throw new IllegalStateException("World output requires server thread");
        if (role.equals("I25")) {
            for (var raw : routes.getList(scope.toString(), Tag.TAG_COMPOUND)) {
                var entry = (CompoundTag) raw;
                if (!entry.contains("Token") || !facility.equals(entry.getString("Facility"))) continue;
                var token = entry.getCompound("Token");
                Hk3WorldResourceOutput.deliverItem(token, ports, this::setDirty);
                if (token.getInt("Count") == 0) entry.remove("Token");
            }
            return;
        }
        for(var operation:output.operations(scope,role,facility)){
            var tx=ledger.transaction(operation);
            var receipt=tx.receipt();
            if(tx.delivered()||!Hk3WorldBubbleResearch.valid(receipt,scope,tx.id(),role)
                    ||!facility.equals(receipt.getString("Facility")))continue;
            if(output.deliver(ledger,tx,ports,this::setDirty))
                com.sirin.hk3gtl.common.easter.Hk3EggProduction.worldDelivered(server,tx);
        }
    }
    public CompoundTag remainingOutput(java.util.UUID operation,java.util.UUID actor){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||tx.phase()!=Hk3WorldBubbleLedger.Phase.SETTLED)
            throw new IllegalArgumentException("Unknown settled world output");
        if(tx.delivered())return new CompoundTag();
        if(output.stage(tx))setDirty();
        return output.remaining(operation);
    }
    public void createCompleted(MinecraftServer server,java.util.UUID batch,java.util.UUID actor,
            java.util.UUID scope,String origin,CompoundTag receipt) {
        createCompleted(server,batch,actor,scope,origin,receipt,true);
    }
    void createCompleted(MinecraftServer server,java.util.UUID batch,java.util.UUID actor,
            java.util.UUID scope,String origin,CompoundTag receipt,boolean project) {
        if(!server.isSameThread()||!Hk3WorldBubbleResearch.valid(receipt,scope,batch,"I29")
                &&!(Hk3WorldBubbleResearch.validSimulation(receipt,scope,batch,"CREATE")
                &&batch.equals(receipt.getUUID("WorldTarget"))))
            throw new IllegalArgumentException("Invalid completed simulation");
        ledger.createSimulation(batch,actor,origin,receipt);
        if(project)projectCompleted(server,scope);
    }
    void projectCompleted(MinecraftServer server,java.util.UUID scope) {
        Hk3WorldBubbleResearch.project(ledger,com.sirin.hk3gtl.common.research.Hk3ResearchData.get(server),scope);
    }
    public static Hk3WorldBubbleData load(CompoundTag tag) {
        if (!tag.contains("Ledger", Tag.TAG_COMPOUND)) throw new IllegalArgumentException("Missing world bubble ledger");
        if(tag.contains("ResourceVersion")&&(!tag.contains("ResourceVersion",Tag.TAG_INT)||tag.getInt("ResourceVersion")!=1
                ||!tag.contains("Resources",Tag.TAG_COMPOUND)))throw new IllegalArgumentException("Missing or unsupported resource ledger");
        if(tag.contains("Resources")&&!tag.contains("ResourceVersion",Tag.TAG_INT))throw new IllegalArgumentException("Missing resource schema");
        Hk3WorldBubbleData data = new Hk3WorldBubbleData();
        data.ledger = Hk3WorldBubbleLedger.load(tag.getCompound("Ledger"), data::setDirty);
        data.routes = tag.getCompound("Routes").copy();
        if(tag.contains("Resources")&&!tag.contains("Resources",Tag.TAG_COMPOUND))throw new IllegalArgumentException("Invalid resource ledger");
        data.resources=Hk3WorldResourceBatches.load(tag.contains("Resources")
                ?tag.getCompound("Resources"):data.resources.save(),data.ledger);
        data.resources.onChange(data::setDirty);
        if(tag.contains("OutputVersion")&&(!tag.contains("OutputVersion",Tag.TAG_INT)||tag.getInt("OutputVersion")!=1
                ||!tag.contains("OutputBuffer",Tag.TAG_COMPOUND)))throw new IllegalArgumentException("世界泡输出缓冲缺失或版本不受支持");
        if(tag.contains("OutputBuffer")){
            if(!tag.contains("OutputBuffer",Tag.TAG_COMPOUND))throw new IllegalArgumentException("Invalid world output buffer");
            data.output=Hk3WorldResourceOutput.load(tag.getCompound("OutputBuffer"),data.ledger);
        }else{
            for(var tx:data.ledger.settledTransactions())data.output.stage(tx);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        for(var tx:ledger.settledTransactions())output.stage(tx);
        tag.put("Ledger",ledger.save());tag.putInt("ResourceVersion",1);tag.put("Resources",resources.save());
        tag.putInt("OutputVersion",1);tag.put("OutputBuffer",output.save());tag.put("Routes",routes.copy());
        return tag;
    }
}

