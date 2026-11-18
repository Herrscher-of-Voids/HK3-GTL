package com.sirin.hk3gtl.common.worldbubble;

import net.minecraft.nbt.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** 按目标与包序号冻结资源及计量规则，目录变更保留已分配结果。 */
public final class Hk3WorldResourceBatches {
    private record Key(Hk3WorldBubbleLedger.Domain domain,UUID target,int ordinal) {}
    private final Map<Key,CompoundTag> allocated=new LinkedHashMap<>();
    private Runnable changed=()->{};
    public void onChange(Runnable callback){changed=Objects.requireNonNull(callback);}

    /** 必须在实际工序完成后的服务端结算流程调用；预览只能读取已有结果，不提前生成奖励。 */
    public ListTag prepare(Hk3WorldBubbleLedger ledger,UUID operation,UUID actor,Hk3WorldResourceCatalog catalog,long worldSalt){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||tx.phase()!=Hk3WorldBubbleLedger.Phase.RESERVED)
            throw new IllegalArgumentException("Unknown, foreign or non-pending resource operation");
        int first=1,last=0;
        switch(tx.action()){
            case MINE->{first=ledger.real(tx.target()).miningCount()+1;last=first;}
            case TERMINATE_REAL->{first=ledger.real(tx.target()).miningCount()+1;last=Hk3WorldBubbleLedger.MAX_MINING;}
            case TERMINATE_SIMULATION->{first=1;last=1;}
            default->{return new ListTag();}
        }
        var result=new ListTag();var additions=new LinkedHashMap<Key,CompoundTag>();
        for(int n=first;n<=last;n++){
            var key=new Key(tx.domain(),tx.target(),n);var existing=allocated.get(key);
            if(existing==null){existing=sample(key,Objects.requireNonNull(catalog),worldSalt);additions.put(key,existing);}
            result.add(existing.copy());
        }
        if(!additions.isEmpty()){allocated.putAll(additions);changed.run();}return result;
    }
    /** 原始抽样结果与已结算回执逐包一致；调用者不能追加物品、改数量或伪造新目录。 */
    public boolean matchesPrepared(Hk3WorldBubbleLedger ledger,UUID operation,UUID actor,ListTag supplied){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||tx.phase()!=Hk3WorldBubbleLedger.Phase.RESERVED)return false;
        int first=1,last=0;
        switch(tx.action()){
            case MINE->{first=ledger.real(tx.target()).miningCount()+1;last=first;}
            case TERMINATE_REAL->{first=ledger.real(tx.target()).miningCount()+1;last=Hk3WorldBubbleLedger.MAX_MINING;}
            case TERMINATE_SIMULATION->{last=1;}
            default->{return supplied.isEmpty();}
        }
        if(supplied.size()!=Math.max(0,last-first+1))return false;
        for(int n=first;n<=last;n++){
            var expected=allocated.get(new Key(tx.domain(),tx.target(),n));
            if(expected==null||!expected.equals(supplied.get(n-first)))return false;
        }return true;
    }
    private static CompoundTag sample(Key key,Hk3WorldResourceCatalog catalog,long salt){
        String identity=salt+"/"+key.domain()+"/"+key.target()+"/"+key.ordinal()+"/"+catalog.hash();
        long seed;
        try{byte[] bytes=MessageDigest.getInstance("SHA-256").digest(identity.getBytes(StandardCharsets.UTF_8));
            seed=java.nio.ByteBuffer.wrap(bytes).getLong();}
        catch(java.security.NoSuchAlgorithmException e){throw new IllegalStateException(e);}
        var rng=new SplittableRandom(seed);var out=new CompoundTag();
        out.putString("Domain",key.domain().name());out.putUUID("Target",key.target());out.putInt("Ordinal",key.ordinal());
        out.putString("Profile",catalog.profile());out.putString("CatalogVersion",catalog.version());out.putString("CatalogHash",catalog.hash());
        var sampling=catalog.sampling();
        var policy=new CompoundTag();
        policy.putInt("ItemKinds",sampling.itemKinds());policy.putInt("ItemMaximum",sampling.itemMax());
        policy.putInt("FluidKinds",sampling.fluidKinds());policy.putInt("FluidMaximum",sampling.fluidMaxBuckets()*1000);
        out.put("Sampling",policy);
        out.put("Items",draw(catalog.items(),sampling.itemKinds(),sampling.itemMax(),false,rng));
        out.put("Fluids",draw(catalog.fluids(),sampling.fluidKinds(),sampling.fluidMaxBuckets(),true,rng));return out;
    }
    /** 稀疏Fisher-Yates：大目录不在每次抽样时复制整份列表，各资源等概率、无放回。 */
    private static ListTag draw(List<Hk3WorldResourceCatalog.Entry> entries,int count,int maximum,boolean fluid,SplittableRandom rng){
        Map<Integer,Integer> swaps=new HashMap<>();var out=new ListTag();
        for(int i=0;i<Math.min(count,entries.size());i++){
            int j=i+rng.nextInt(entries.size()-i);int selected=swaps.getOrDefault(j,j);
            swaps.put(j,swaps.getOrDefault(i,i));
            var entry=entries.get(selected);var value=new CompoundTag();value.putString("id",entry.id());
            var stackData=entry.stackData();if(!stackData.isEmpty())value.put("StackData",stackData);
            value.putInt(fluid?"Amount":"Count",entry.amount()>0?entry.amount():(1+rng.nextInt(maximum))*(fluid?1000:1));out.add(value);
        }return out;
    }
    public CompoundTag save(){
        var root=new CompoundTag();root.putInt("Version",1);var list=new ListTag();
        allocated.values().forEach(p->list.add(p.copy()));root.put("Packages",list);return root;
    }
    public static Hk3WorldResourceBatches load(CompoundTag root,Hk3WorldBubbleLedger ledger){
        if(!root.contains("Version",Tag.TAG_INT)||root.getInt("Version")!=1||!root.contains("Packages",Tag.TAG_LIST))
            throw new IllegalArgumentException("Invalid resource batch schema");
        var result=new Hk3WorldResourceBatches();var list=root.getList("Packages",Tag.TAG_COMPOUND);
        if(list.size()!=((ListTag)root.get("Packages")).size())throw new IllegalArgumentException("Invalid resource package list");
        for(var raw:list){
            var tag=(CompoundTag)raw;
            if(!tag.hasUUID("Target")||!tag.contains("Ordinal",Tag.TAG_INT))throw new IllegalArgumentException("Missing resource identity");
            var domain=Hk3WorldBubbleLedger.Domain.valueOf(tag.getString("Domain"));var target=tag.getUUID("Target");int n=tag.getInt("Ordinal");
            if(n<1||n>(domain==Hk3WorldBubbleLedger.Domain.REAL?Hk3WorldBubbleLedger.LEGACY_MINING_LIMIT:1)
                    ||(domain==Hk3WorldBubbleLedger.Domain.REAL?ledger.real(target)==null:ledger.simulation(target)==null))
                throw new IllegalArgumentException("Invalid resource target or ordinal");
            if(!tag.getString("CatalogHash").matches("[0-9a-f]{64}")||tag.getString("CatalogVersion").isBlank()||tag.getString("Profile").isBlank())
                throw new IllegalArgumentException("Missing catalog provenance");
            if(tag.contains("Sampling",Tag.TAG_COMPOUND)){
                var policy=tag.getCompound("Sampling");
                validateDraw(tag,"Items","Count",policy.getInt("ItemKinds"),1,policy.getInt("ItemMaximum"),1);
                validateDraw(tag,"Fluids","Amount",policy.getInt("FluidKinds"),1,policy.getInt("FluidMaximum"),1);
            }else{
                validateDraw(tag,"Items","Count",4,1,64,1);validateDraw(tag,"Fluids","Amount",2,1000,16000,1000);
            }
            if(result.allocated.putIfAbsent(new Key(domain,target,n),tag.copy())!=null)throw new IllegalArgumentException("Duplicate resource package");
        }
        for(var tx:ledger.settledTransactions()){
            var outputs=tx.receipt().getCompound("Outputs");
            if(!outputs.contains("ResourcePackages"))continue;
            if(!outputs.contains("ResourcePackages",Tag.TAG_LIST))throw new IllegalArgumentException("Invalid settled resource packages");
            var packages=outputs.getList("ResourcePackages",Tag.TAG_COMPOUND);
            if(packages.size()!=((ListTag)outputs.get("ResourcePackages")).size())throw new IllegalArgumentException("Invalid settled resource entry");
            Set<Key> seen=new HashSet<>();
            for(var raw:packages){
                var pkg=(CompoundTag)raw;
                if(!pkg.hasUUID("Target")||!pkg.getUUID("Target").equals(tx.target())||!pkg.getString("Domain").equals(tx.domain().name()))
                    throw new IllegalArgumentException("Foreign settled resource package");
                var key=new Key(tx.domain(),tx.target(),pkg.getInt("Ordinal"));
                if(!seen.add(key)||!pkg.equals(result.allocated.get(key)))throw new IllegalArgumentException("Missing or changed frozen settlement");
            }
        }
        return result;
    }
    private static void validateDraw(CompoundTag root,String key,String amount,int max,int minValue,int maxValue,int step){
        if(!root.contains(key,Tag.TAG_LIST))throw new IllegalArgumentException("Missing resource pool result");
        var list=root.getList(key,Tag.TAG_COMPOUND);Set<String> ids=new HashSet<>();
        if(list.isEmpty()||list.size()>max||list.size()!=((ListTag)root.get(key)).size())throw new IllegalArgumentException("Invalid draw size");
        for(var raw:list){var value=(CompoundTag)raw;int n=value.getInt(amount);
            if(!Hk3WorldResourceCatalog.validId(value.getString("id"))
                    ||value.contains("StackData")&&!value.contains("StackData",Tag.TAG_COMPOUND)
                    ||!ids.add(Hk3WorldResourceCatalog.identity(value.getString("id"),value.getCompound("StackData")))
                    ||!value.contains(amount,Tag.TAG_INT)||n<minValue||n>maxValue||n%step!=0)
                throw new IllegalArgumentException("Invalid resource draw");}
    }
}
