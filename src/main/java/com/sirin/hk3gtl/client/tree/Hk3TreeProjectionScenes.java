package com.sirin.hk3gtl.client.tree;

import com.sirin.hk3gtl.common.machine.tree.Hk3TreeProjectionPacket;
import net.minecraft.client.Minecraft;
import java.util.ArrayList;
import java.util.List;

/** 树影依赖服务端成型心跳，跨维度、卸载及失效时自动撤销。 */
public final class Hk3TreeProjectionScenes {
    public record Scene(Hk3TreeProjectionPacket state,long received){}
    private static List<Scene> scenes=List.of();
    private static Object level;
    private Hk3TreeProjectionScenes(){}
    public static List<Scene> scenes(){return scenes;}
    public static void accept(Hk3TreeProjectionPacket state){
        var mc=Minecraft.getInstance();if(mc.level==null||!mc.level.dimension().location().equals(state.dimension())||state.mode()>3)return;
        if(level!=mc.level){clear();level=mc.level;}
        var next=new ArrayList<>(scenes);next.removeIf(s->s.state.pos().equals(state.pos()));
        if(state.mode()==1||state.mode()==2)next.add(new Scene(state,mc.level.getGameTime()));scenes=List.copyOf(next);
    }
    public static void maintain(){var mc=Minecraft.getInstance();if(level!=mc.level){clear();return;}if(mc.level!=null)scenes=scenes.stream().filter(s->mc.level.getGameTime()-s.received<100).toList();}
    public static void clear(){scenes=List.of();level=null;}
}
