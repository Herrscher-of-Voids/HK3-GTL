package com.sirin.hk3gtl.common.review;

import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.server.MinecraftServer;
import java.util.UUID;

/** 【变更记录 #1】2026-10-01 01:28:10（修订125）：删除无；新增服务端真实资格采集及一次性来源快照；修改准入不以预览、微讯息或管理员标记通过；用途：达标后资格保留，停机不抹除；召入和二审降临仍须正式场景接入。 */
public final class Hk3ReviewQualification {
    private Hk3ReviewQualification() {}
    public static Hk3ReviewRequirements.Evaluation inspect(MinecraftServer server,UUID team,Hk3ReviewLedger.Kind kind){
        var research=Hk3ResearchData.get(server);var review=Hk3ReviewData.get(server);
        return Hk3ReviewRequirements.evaluate(team,kind,id->research.completed(team,id),
                id->research.processFactReceipt(team,id),review.settlement(team,Hk3ReviewLedger.Kind.FIRST));
    }
    /** 按在线团队五秒一批调用；不向客户端开放写资格入口，不改已有许可。 */
    public static void refresh(MinecraftServer server,UUID team){
        var data=Hk3ReviewData.get(server);var snapshot=data.snapshot();
        for(var kind:Hk3ReviewLedger.Kind.values()){
            if(snapshot.qualified(team,kind))continue;
            var result=inspect(server,team,kind);
            if(result.ready())data.change(ledger->ledger.qualify(team,kind,result.sources()));
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
