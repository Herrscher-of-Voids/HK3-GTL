package com.sirin.hk3gtl.common.communication;

/** 【变更记录 #2】2026-10-01 00:17:25（修订122）：删除无；新增/修改：公开格式严格白名单校验，大数量不受字节Count截断；未可靠留存的旧数量不补造；用途：五方首信与团队限定交流保持一致。 */
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import com.sirin.hk3gtl.common.research.Hk3ResearchBatchProofs;
import java.util.*;

/** 【变更记录 #1】2026-10-01 00:14:30（修订122）：删除无；新增/修改：真实采样、光谱、稳定化首批快照；公开字段白名单及中文收支预览；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */
/** 【变更记录 #3】2026-10-01 00:59:10（修订124）：删除无；新增/修改：正式交流/批次原始存档损坏拒绝空白回退，兼容有Teams的既有版本；用途：按五方交流系统整链收口，真实权限和本人经历不混用。 */
/** 【变更记录 #4】2026-10-01 01:01:52（修订124）：删除无；新增团队批次容器格式检查；修改损坏批次不被新输出静默覆盖；用途：保留原始生产证据。 */
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
        b.append("批次：").append(r.getUUID("Batch")).append("\n工艺：").append(r.getString("Recipe")).append("\n结算刻：").append(r.getLong("Tick"));
        for(String side:List.of("Inputs","Outputs")){
            b.append(side.equals("Inputs")?"\n投入（已执行配方规格）：":"\n产出（已结算配方规格）：");var c=r.getCompound(side);
            for(Tag t:c.getList("Items",Tag.TAG_COMPOUND)){var line=(CompoundTag)t;b.append("\n · ");var options=new ArrayList<String>();for(Tag o:line.getList("Alternatives",Tag.TAG_COMPOUND)){var item=(CompoundTag)o;options.add(item.getString("id")+" × "+item.getLong("Count"));}b.append(String.join(" 或 ",options));if(line.getFloat("Chance")<1)b.append("（配方概率项，非逐槽实测）");}
            for(Tag t:c.getList("Fluids",Tag.TAG_COMPOUND)){var line=(CompoundTag)t;b.append("\n · ").append(line.getList("Alternatives",Tag.TAG_STRING)).append(" × ").append(line.getLong("Amount")).append(" mB");}
        }
        return b.append("\n设备实际输出成功后留存；标签候选不是逐槽提取记录。后续储存、运输及回收状态未追踪，不推定已回收。").toString();
    }
}
