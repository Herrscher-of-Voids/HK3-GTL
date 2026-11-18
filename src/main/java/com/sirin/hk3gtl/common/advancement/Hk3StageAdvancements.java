package com.sirin.hk3gtl.common.advancement;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.advancements.Advancement;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.PlayerAdvancements;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.Map;

 


























 
public final class Hk3StageAdvancements {

    private Hk3StageAdvancements() {}
    /** 旧事件仅请求真实数据投影，不再凭持物里程碑或旧世界毕业标记授予阶段。 */
    public static void onStageEvent(ServerPlayer player,String eventId){
        if(!eventId.startsWith("E-MS-")||!player.server.isSameThread())return;
        var scope=com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(player.server,player.getUUID());
        com.sirin.hk3gtl.common.integration.Hk3GuideAdvancements.sync(player,
                com.sirin.hk3gtl.common.integration.Hk3QuestProgressBridge.facts(player.server,scope));
    }
}
