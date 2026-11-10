package com.sirin.hk3gtl.common.worldbubble;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * 【文件职责】资源池采用独立、等概率、去重的ULV—MAX生存目录，不自动导入整个注册表。
 * 【变更记录 #1】2026-09-29 23:51:00（内测5修订102）
 * 删除：无。新增：分物品/源流体目录、等级/来源检查及规范化SHA256。
 * 修改：目录排序不改变身份；用途：真实和模拟共用同一版资源池，后续改版不重抽已分配包。
 * 边界：目录条目的实际注册和生存配方仍须由实例侧核验，字符串声明不替代该核验。
 */
public final class Hk3WorldResourceCatalog {
    public record Entry(String id,int tier,String survivalSource) {
        public Entry {
            if(!validId(id)||tier<0||tier>14||survivalSource==null||survivalSource.isBlank()
                    ||survivalSource.length()>1024)throw new IllegalArgumentException("Invalid resource catalog entry");
        }
    }
    private final String profile,version,hash;
    private final List<Entry> items,fluids;
    public Hk3WorldResourceCatalog(String profile,String version,List<Entry> items,List<Entry> fluids){
        if(profile==null||profile.isBlank()||profile.length()>128||version==null||version.isBlank()||version.length()>128)
            throw new IllegalArgumentException("Invalid catalog identity");
        this.profile=profile;this.version=version;this.items=normalize(items);this.fluids=normalize(fluids);
        StringBuilder canonical=new StringBuilder(profile).append('\n').append(version).append('\n');
        append(canonical,"item",this.items);append(canonical,"fluid",this.fluids);
        try{hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(canonical.toString().getBytes(StandardCharsets.UTF_8)));}
        catch(java.security.NoSuchAlgorithmException e){throw new IllegalStateException(e);}
    }
    private static List<Entry> normalize(List<Entry> entries){
        if(entries==null||entries.isEmpty()||entries.size()>100000)throw new IllegalArgumentException("Empty or excessive resource pool");
        Map<String,Entry> unique=new TreeMap<>();
        for(var entry:entries)if(unique.putIfAbsent(entry.id(),entry)!=null)throw new IllegalArgumentException("Duplicate resource identity "+entry.id());
        return List.copyOf(unique.values());
    }
    private static void append(StringBuilder text,String kind,List<Entry> entries){
        for(var entry:entries)text.append(kind).append('\t').append(entry.id()).append('\t').append(entry.tier())
                .append('\t').append(entry.survivalSource().replace("\n"," ").replace("\r"," ")).append('\n');
    }
    public static boolean validId(String value){return value!=null&&value.length()<=256&&value.matches("[a-z0-9_.-]+:[a-z0-9/._-]+");}
    public String profile(){return profile;} public String version(){return version;} public String hash(){return hash;}
    public List<Entry> items(){return items;} public List<Entry> fluids(){return fluids;}
}
