package com.sirin.hk3gtl.common.phone;

import com.sirin.hk3gtl.common.easter.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;

/** 【变更记录 #1】2026-11-05（修订207）：文明总览使用本队只读快照与既有全文令牌；不以打开目录、研究数量或客户端末页声明授奖。 */
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
            +"历史与当下\n历史最高称号："+snapshot.getString("CivilizationTitle")+"。当前核验等级：C"+snapshot.getInt("CivilizationVerified")+"。历史称号记录已经达到过的文明高度，当前核验反映此刻仍可确认的事实；两者不必相同。查看本页不会改变任何等级。\n\n"
            +"团队研究\n已完成 "+snapshot.getInt("ResearchDone")+" / "+snapshot.getInt("ResearchTotal")+" 项研究。这里读取本队已经保存的研究记录，不代替实验、材料提交或研究台操作。尚未完成研究时也可以阅读总览；阅读本身不解锁配方、设备或权限。\n\n"
            +"个人档案与收藏\n本人现有 "+snapshot.getInt("Archives")+" / "+snapshot.getInt("ArchiveTotal")+" 条档案与收藏记录。收藏数量不是正式资格；旧标记、可选彩蛋与本人正式经历应分别查看。需要核对正式回执或待补事项时，请返回总览，进入本人正式经历。\n\n"
            +"团队与工程\n当前研究记录中的成员数为 "+snapshot.getInt("Members")+"。团队机器目录只显示本队已有索引，目录条目不等于设备正在运行，也不能代替完整结构、供电与工艺验收。这里不提供远程开关、库存操作或他队位置。\n\n"
            +"文明成果\n文明等级与成果条件页面逐项列出当前满足情况。历史称号不会替代当前工程事实；缺少真实来源的成果仍须等待对应来源接入，不能凭一份总览或一条收藏补成已完成。\n\n"
            +"阅读到这里\n本页是打开总览时生成的只读快照。团队事实之后发生变化，请返回总览重新打开全文。完整阅读只记录本人这次阅读，不授予研究、物品、工程成果或终审资格。";
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
