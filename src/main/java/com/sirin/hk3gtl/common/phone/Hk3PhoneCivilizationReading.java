package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;

public final class Hk3PhoneCivilizationReading {
    public static final String ID="civilization_overview_read";
    private Hk3PhoneCivilizationReading(){}
    public static boolean managed(String id){return ID.equals(id);}
    public static boolean authorize(ServerPlayer p){
        var state=Hk3EggRuntime.state(p);
        return Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p)
            &&state.getBoolean("phoneOpen")&&state.getString("phoneMode").equals("civilization_read");
    }
    public static String body(CompoundTag snapshot){
        return "文明总览\n\n"
            +"历史与当下\n历史最高称号："+snapshot.getString("CivilizationTitle")+"。当前核验等级：C"+snapshot.getInt("CivilizationVerified")+"。历史称号记录曾经达到的文明高度，当前等级根据现有研究与工程成果核对。\n\n"
            +"团队研究\n已完成 "+snapshot.getInt("ResearchDone")+" / "+snapshot.getInt("ResearchTotal")+" 项研究。可在研究所查看各课题的实验、材料和前置要求。\n\n"
            +"个人档案与收藏\n本人现有 "+snapshot.getInt("Archives")+" / "+snapshot.getInt("ArchiveTotal")+" 条档案与收藏记录。正式经历与可选收藏分别记录。要查看尚未完成的经历，请返回总览，进入本人正式经历。\n\n"
            +"团队与工程\n当前研究记录中的成员数为 "+snapshot.getInt("Members")+"。团队机器目录可查看设备的位置与状态。请在设备处检查结构、供电与生产情况。\n\n"
            +"文明成果\n文明等级与成果条件页面列出各项目标。奇观需要完成生产，并保持原机结构完整。\n\n"
            +"阅读到这里\n本页显示打开时的资料。研究或工程进度变化后，请返回总览重新打开全文。阅读进度会单独保存。";
    }
    static int open(ServerPlayer p,CompoundTag snapshot){
        if(!Hk3PhoneData.get(p).installed(p.getUUID())||!Hk3PhoneRuntime.requirePower(p))return 0;
        Hk3EggPhone.opened(p,"civilization_read");
        var view=new CompoundTag();view.putString("Mode","archive_detail");view.putString("Id",ID);
        view.putBoolean("CivilizationRead",true);view.putString("Title","文明总览 · 全文");view.putString("Body",body(snapshot));
        Hk3PhoneService.send(p,view);return 1;
    }
    public static void completed(ServerPlayer p,Hk3ReadingSessions.Session session){
        if(managed(session.id())&&session.cursor().done()&&authorize(p))
            Hk3EggRuntime.observe(p,"civilization_overview_read",Hk3EggRuntime.fields("complete","true"));
    }
}
