package com.sirin.hk3gtl.common.util;

import net.minecraft.nbt.*;
import java.util.UUID;

/**
 * 【变更记录 #1】2026-10-01 17:04:49（修订136）
 * 删除：无；新增：账本类型、列表元素、规范UUID及布尔字段校验。
 * 修改：NBT默认空值不能再掩盖已有字段的错误类型；用途：读取失败交回防覆盖保护，不吞条目或记录私人正文。
 */
public final class Hk3LedgerValidation {
    private Hk3LedgerValidation(){}
    public static void require(boolean valid,String field){if(!valid)throw new IllegalStateException("账本字段损坏，拒绝重置："+field);}
    public static void type(CompoundTag n,String key,int type){require(n.contains(key,type),key);}
    public static void optionalType(CompoundTag n,String key,int type){if(n.contains(key))type(n,key,type);}
    public static ListTag list(CompoundTag n,String key,int type){
        type(n,key,Tag.TAG_LIST);var list=n.getList(key,type);
        require(list.size()==((ListTag)n.get(key)).size(),key);return list;
    }
    public static UUID uuid(String key){
        try{var id=UUID.fromString(key);require(id.toString().equals(key),"UUID");return id;}
        catch(IllegalArgumentException e){throw new IllegalStateException("账本UUID损坏，拒绝重置",e);}
    }
    public static void flag(CompoundTag n,String key,boolean required){
        if(!required&&!n.contains(key))return;type(n,key,Tag.TAG_BYTE);
        require(n.getByte(key)==0||n.getByte(key)==1,key);
    }
}
