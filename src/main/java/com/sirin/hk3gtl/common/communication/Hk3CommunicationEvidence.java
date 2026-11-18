package com.sirin.hk3gtl.common.communication;

 
import net.minecraft.nbt.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.fluids.FluidStack;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import com.sirin.hk3gtl.common.research.Hk3ResearchBatchProofs;
import java.util.*;

 
 
 
public final class Hk3CommunicationEvidence extends SavedData {
    private CompoundTag teams=new CompoundTag();
    public static Hk3CommunicationEvidence get(MinecraftServer s){return com.sirin.hk3gtl.common.util.Hk3SavedDataGuard.get(s,"hk3gtl_communication_evidence_v5",Hk3CommunicationEvidence::load,Hk3CommunicationEvidence::new);}
    public static Hk3CommunicationEvidence load(CompoundTag n){if(!n.contains("Teams",Tag.TAG_COMPOUND)||(n.contains("Version")&&n.getInt("Version")!=1))throw new IllegalArgumentException("正式交流账本异常，拒绝重置");var d=new Hk3CommunicationEvidence();d.teams=n.getCompound("Teams").copy();return d;}
    @Override public CompoundTag save(CompoundTag n){n.putInt("Version",1);n.put("Teams",teams.copy());return n;}
    /** 首批真实输出后保存，不读物品持有、研究完成或旧标记；每队每类仅首份，存量有界。 */
    public boolean record(UUID team,String kind,CompoundTag receipt){
        if(team==null||!Set.of("sampling","spectrum","stabilization").contains(kind)||!Hk3ResearchBatchProofs.valid(receipt))return false;
        if(teams.contains(team.toString())&&!teams.contains(team.toString(),Tag.TAG_COMPOUND))return false;
        var r=teams.getCompound(team.toString()).copy();if(r.contains(kind))return false;r.put(kind,receipt.copy());teams.put(team.toString(),r);setDirty();return true;
    }
    public CompoundTag source(UUID team,String kind){return teams.getCompound(team.toString()).getCompound(kind).copy();}
    /** 公开白名单不含设备坐标、玩家UUID、物品私有NBT、其他通信或工厂布局。 */
    public static CompoundTag publicCopy(CompoundTag raw){
        if(!Hk3ResearchBatchProofs.valid(raw))return new CompoundTag();var out=new CompoundTag();
        out.putUUID("Batch",raw.getUUID("Batch"));out.putString("Recipe",raw.getString("Recipe"));out.putLong("Tick",raw.getLong("Tick"));
        for(String side:List.of("Inputs","Outputs")){
            var clean=new CompoundTag();var source=raw.getCompound(side);
            for(String type:List.of("Items","Fluids")){
                var lines=source.getList(type,Tag.TAG_COMPOUND);if(lines.size()>64)return new CompoundTag();var copy=new ListTag();
                for(Tag t:lines){var r=(CompoundTag)t;var n=new CompoundTag();var alternatives=new ListTag();n.putFloat("Chance",r.getFloat("Chance"));
                    if(type.equals("Items")){
                        var options=r.getList("Alternatives",Tag.TAG_COMPOUND);if(options.size()>64)return new CompoundTag();
                        for(Tag o:options){var item=(CompoundTag)o;var v=new CompoundTag();v.putString("id",item.getString("id"));long count=item.contains("ActualCount",Tag.TAG_LONG)?item.getLong("ActualCount"):item.getByte("Count");if(count<=0)return new CompoundTag();v.putLong("Count",count);alternatives.add(v);}
                    }else{var options=r.getList("Alternatives",Tag.TAG_STRING);if(options.size()>64)return new CompoundTag();for(Tag o:options)alternatives.add(StringTag.valueOf(o.getAsString()));n.putLong("Amount",r.getLong("Amount"));}
                    n.put("Alternatives",alternatives);copy.add(n);
                }
                if(!copy.isEmpty())clean.put(type,copy);
            }
            if(clean.isEmpty())return new CompoundTag();out.put(side,clean);
        }
        return out;
    }
    /** 已去隐私的公开格式与工业原始回执分别验证，防止把坐标或任意复合标签塞进公开附件。 */
    public static boolean validPublic(CompoundTag r){
        if(!r.getAllKeys().equals(Set.of("Batch","Recipe","Tick","Inputs","Outputs"))||!r.hasUUID("Batch")||r.getString("Recipe").isBlank()||!r.contains("Tick",Tag.TAG_LONG)||r.getLong("Tick")<0)return false;
        for(String side:List.of("Inputs","Outputs")){
            var c=r.getCompound(side);if(c.isEmpty()||!Set.of("Items","Fluids").containsAll(c.getAllKeys()))return false;
            for(String type:c.getAllKeys()){
                if(!c.contains(type,Tag.TAG_LIST))return false;var raw=(ListTag)c.get(type);var lines=c.getList(type,Tag.TAG_COMPOUND);if(lines.isEmpty()||lines.size()!=raw.size()||lines.size()>64)return false;
                for(Tag t:lines){var line=(CompoundTag)t;boolean items=type.equals("Items");if(!line.getAllKeys().equals(items?Set.of("Alternatives","Chance"):Set.of("Alternatives","Chance","Amount")))return false;
                    if(!line.contains("Chance",Tag.TAG_FLOAT)||!Float.isFinite(line.getFloat("Chance"))||line.getFloat("Chance")<=0||line.getFloat("Chance")>1)return false;
                    var options=line.getList("Alternatives",items?Tag.TAG_COMPOUND:Tag.TAG_STRING);if(options.isEmpty()||options.size()>64)return false;
                    for(Tag option:options)if(items){var v=(CompoundTag)option;if(!v.getAllKeys().equals(Set.of("id","Count"))||v.getString("id").isBlank()||!v.contains("Count",Tag.TAG_LONG)||v.getLong("Count")<=0)return false;}else if(option.getAsString().isBlank())return false;
                    if(!items&&(!line.contains("Amount",Tag.TAG_LONG)||line.getLong("Amount")<=0))return false;
                }
            }
        }return true;
    }
    public static boolean validEnvelope(String topic,CompoundTag e){
        var keys=switch(topic){case "public","anti_entropy"->Set.of("稳定化");case "schicksal"->Set.of("首次采样","光谱分析");case "world_serpent"->Set.of("魂钢成型","重构退火");default->Set.<String>of();};
        return !keys.isEmpty()&&e.getAllKeys().equals(keys)&&keys.stream().allMatch(k->validPublic(e.getCompound(k)));
    }
    public static String describe(CompoundTag r){
        if(r.isEmpty())return "暂无可核验的真实批次";var b=new StringBuilder();
        b.append("生产批次记录");
        for(String side:List.of("Inputs","Outputs")){
            b.append(side.equals("Inputs")?"\n投入：":"\n产出：");var c=r.getCompound(side);
            for(Tag t:c.getList("Items",Tag.TAG_COMPOUND)){var line=(CompoundTag)t;b.append("\n · ");var options=new ArrayList<String>();for(Tag o:line.getList("Alternatives",Tag.TAG_COMPOUND)){var item=(CompoundTag)o;options.add(new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(item.getString("id")))).getHoverName().getString()+" × "+item.getLong("Count"));}b.append(String.join(" 或 ",options));if(line.getFloat("Chance")<1)b.append("（按配方概率计算）");}
            for(Tag t:c.getList("Fluids",Tag.TAG_COMPOUND)){var line=(CompoundTag)t;var options=new ArrayList<String>();for(Tag fluid:line.getList("Alternatives",Tag.TAG_STRING))options.add(new FluidStack(BuiltInRegistries.FLUID.get(new ResourceLocation(fluid.getAsString())),1).getDisplayName().getString());b.append("\n · ").append(String.join(" 或 ",options)).append(" × ").append(line.getLong("Amount")).append(" mB");}
        }
        return b.append("\n本记录保存该批配方的投入产出规格。后续运输与回收请另查对应记录。").toString();
    }
}
