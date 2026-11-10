package com.sirin.hk3gtl.common.easter;
import com.sirin.hk3gtl.common.phone.Hk3PhoneGames;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
/** 【变更记录 #1】2026-10-01 04:48:51（修订128）：删除无；新增个人小游戏操作重放；用途：仅接种子和方向，不接分数/任意彩蛋编号；每tick限32次操作，断线释放，离线App游戏本身仍可运行。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggGames {
    private static final class Session {Hk3PhoneGames.Tiles tiles;Hk3PhoneGames.Snake snake;long tick=-1;int requests;}
    private static final Map<UUID,Session> SESSIONS=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggGames(){}
    public static void input(ServerPlayer p,String action,String value){
        var s=SESSIONS.computeIfAbsent(p.getUUID(),k->new Session());long now=p.server.overworld().getGameTime();
        if(s.tick!=now){s.tick=now;s.requests=0;}if(++s.requests>32)return;
        try{
            switch(action){
                case "tiles_start"->s.tiles=new Hk3PhoneGames.Tiles(Long.parseLong(value));
                case "snake_start"->s.snake=new Hk3PhoneGames.Snake(Long.parseLong(value));
                case "tiles_move"->{if(s.tiles==null)return;int direction=Integer.parseInt(value);if(direction<0||direction>3)return;
                    s.tiles.move(direction);int max=Arrays.stream(s.tiles.cells()).max().orElse(0);
                    Hk3EggRuntime.observe(p,"tiles_replay",Map.of("highest",Integer.toString(max)));
                }
                case "snake_turn"->{if(s.snake!=null)s.snake.turn(Integer.parseInt(value));}
                case "snake_step"->{if(s.snake!=null){s.snake.step();if(!s.snake.over()&&s.snake.cells().size()>=16)Hk3EggVanilla.caseEvent(p,476);}}
                default->{}
            }
        }catch(NumberFormatException invalid){}
    }
    public static void home(ServerPlayer p){var s=SESSIONS.get(p.getUUID());if(s!=null&&s.tiles!=null&&s.tiles.over()&&Hk3EggRuntime.state(p).getString("phoneMode").equals("tiles2048"))Hk3EggVanilla.caseEvent(p,475);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SESSIONS.remove(e.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent e){SESSIONS.clear();}
}
