package com.sirin.hk3gtl.common.review;

import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.server.MinecraftServer;
import java.util.UUID;

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

