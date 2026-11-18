package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.research.Hk3ResearchWorkQueue;
import com.sirin.hk3gtl.common.util.Hk3SavedDataGuard;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.Map;
import java.util.UUID;

public final class Hk3EggResearchScenes extends SavedData {
    private final CompoundTag users;
    private Hk3EggResearchScenes(){this(new CompoundTag());}
    private Hk3EggResearchScenes(CompoundTag users){this.users=users;}
    private static Hk3EggResearchScenes get(MinecraftServer server){
        return Hk3SavedDataGuard.get(server,"hk3gtl_egg_experiment_scenes",
                tag->new Hk3EggResearchScenes(tag.getCompound("Users")),Hk3EggResearchScenes::new);
    }
    private CompoundTag user(UUID player){
        String id=player.toString();
        if(!users.contains(id))users.put(id,new CompoundTag());
        return users.getCompound(id);
    }
    public static void login(ServerPlayer p){
        var data=get(p.server);var user=data.user(p.getUUID());user.putLong("Session",user.getLong("Session")+1);data.setDirty();
    }
    public static void paused(MinecraftServer server,UUID payer,Hk3ResearchWorkQueue.Snapshot job,String research){
        var data=get(server);var user=data.user(payer);var old=user.getCompound("Pause");
        if(old.hasUUID("Job")&&old.getUUID("Job").equals(job.id()))return;
        var pause=new CompoundTag();pause.putUUID("Job",job.id());pause.putUUID("Payer",payer);
        pause.putString("Research",research);pause.putString("Experiment",job.quote().topic());
        pause.putString("Facility",job.quote().facility());pause.putDouble("Progress",job.progress());
        pause.putLong("Session",user.getLong("Session"));pause.putLong("Tick",server.overworld().getGameTime());
        user.put("Pause",pause);data.setDirty();
    }
    public static boolean hasPause(ServerPlayer p){return !get(p.server).user(p.getUUID()).getCompound("Pause").isEmpty();}
    public static void discussed(ServerPlayer p,int egg){
        var pause=get(p.server).user(p.getUUID()).getCompound("Pause");
        if(pause.isEmpty())return;
        Hk3EggRuntime.observe(p,"experiment_pause_discussed",Map.of("case",Integer.toString(egg),
                "research",pause.getString("Research"),"own_pause","true"));
    }
    public static void opened(ServerPlayer p,String research){
        var user=get(p.server).user(p.getUUID());var pause=user.getCompound("Pause");
        if(!pause.isEmpty()&&pause.getString("Research").equals(research)&&user.getLong("Session")>pause.getLong("Session"))
            Hk3EggRuntime.observe(p,"experiment_reopened_after_login",Map.of("same_research","true","new_login","true","own_pause","true"));
    }
    @Override public CompoundTag save(CompoundTag tag){tag.put("Users",users);return tag;}
}
