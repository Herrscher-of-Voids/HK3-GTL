package com.sirin.hk3gtl.common.worldbubble;

import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** 资源身份包含完整栈数据，固定产量与NBT共同参与目录哈希。 */
public final class Hk3WorldResourceCatalog {
    public record Sampling(int itemKinds,int itemMax,int fluidKinds,int fluidMaxBuckets) {}
    public record Entry(String id,int tier,String survivalSource,int amount,CompoundTag stackData) {
        public Entry(String id,int tier,String survivalSource){this(id,tier,survivalSource,0);}
        public Entry(String id,int tier,String survivalSource,int amount){this(id,tier,survivalSource,amount,new CompoundTag());}
        public Entry {
            if(!validId(id)||tier<0||tier>14||survivalSource==null||survivalSource.isBlank()
                    ||survivalSource.length()>1024)throw new IllegalArgumentException("Invalid resource catalog entry");
            stackData=stackData.copy();
        }
        @Override public CompoundTag stackData(){return stackData.copy();}
    }
    private final String profile,version,hash;
    private final List<Entry> items,fluids;
    private final Sampling sampling;
    public Hk3WorldResourceCatalog(String profile,String version,List<Entry> items,List<Entry> fluids){
        this(profile,version,items,fluids,new Sampling(4,64,2,16));
    }
    public Hk3WorldResourceCatalog(String profile,String version,List<Entry> items,List<Entry> fluids,Sampling sampling){
        if(profile==null||profile.isBlank()||profile.length()>128||version==null||version.isBlank()||version.length()>128)
            throw new IllegalArgumentException("Invalid catalog identity");
        this.profile=profile;this.version=version;this.items=normalize(items);this.fluids=normalize(fluids);
        this.sampling=sampling;
        StringBuilder canonical=new StringBuilder(profile).append('\n').append(version).append('\n');
        canonical.append(sampling.itemKinds()).append('/').append(sampling.itemMax()).append('/')
                .append(sampling.fluidKinds()).append('/').append(sampling.fluidMaxBuckets()).append('\n');
        append(canonical,"item",this.items);append(canonical,"fluid",this.fluids);
        try{hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(canonical.toString().getBytes(StandardCharsets.UTF_8)));}
        catch(java.security.NoSuchAlgorithmException e){throw new IllegalStateException(e);}
    }
    private static List<Entry> normalize(List<Entry> entries){
        if(entries==null||entries.isEmpty()||entries.size()>100000)throw new IllegalArgumentException("Empty or excessive resource pool");
        Map<String,Entry> unique=new TreeMap<>();
        for(var entry:entries)if(unique.putIfAbsent(identity(entry.id(),entry.stackData()),entry)!=null)
            throw new IllegalArgumentException("Duplicate resource identity "+entry.id());
        return List.copyOf(unique.values());
    }
    private static void append(StringBuilder text,String kind,List<Entry> entries){
        for(var entry:entries)text.append(kind).append('\t').append(entry.id()).append('\t').append(entry.tier())
                .append('\t').append(entry.survivalSource().replace("\n"," ").replace("\r"," "))
                .append('\t').append(entry.amount()).append('\t').append(canonical(entry.stackData())).append('\n');
    }
    public static CompoundTag itemData(ItemStack stack){
        var data=stack.save(new CompoundTag());data.remove("id");data.remove("Count");return data;
    }
    public static CompoundTag fluidData(FluidStack stack){
        var data=stack.saveToTag(new CompoundTag());data.remove("FluidName");data.remove("Amount");return data;
    }
    public static String identity(String id,CompoundTag stackData){return id+'\t'+canonical(stackData);}
    public static String canonical(Tag tag){
        if(tag instanceof CompoundTag compound){
            var result=new StringJoiner(",","{","}");
            for(String key:new TreeSet<>(compound.getAllKeys()))result.add(StringTag.quoteAndEscape(key)+":"+canonical(compound.get(key)));
            return result.toString();
        }
        if(tag instanceof ListTag list){
            var result=new StringJoiner(",","[","]");for(var value:list)result.add(canonical(value));return result.toString();
        }
        return tag.toString();
    }
    public static boolean validId(String value){return value!=null&&value.length()<=256&&value.matches("[a-z0-9_.-]+:[a-z0-9/._-]+");}
    public String profile(){return profile;} public String version(){return version;} public String hash(){return hash;}
    public List<Entry> items(){return items;} public List<Entry> fluids(){return fluids;}
    public Sampling sampling(){return sampling;}
}
