package com.sirin.hk3gtl.client.wonder;

import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderFxPacket;
import net.minecraft.client.Minecraft;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public final class Hk3W07FieldScenes {
    public record Scene(Hk3WonderFxPacket state,long received,Hk3W11Ports ports){}
    private static List<Scene> scenes=List.of();
    private static Object level;
    private Hk3W07FieldScenes(){}
    public static List<Scene> scenes(){return scenes;}
    public static void accept(Hk3WonderFxPacket packet){
        var mc=Minecraft.getInstance();
        if(mc.level==null||!mc.level.dimension().location().equals(packet.dimension()))return;
        if(level!=mc.level){clear();level=mc.level;}
        var previous=scenes.stream().filter(scene->scene.state().pos().equals(packet.pos())).findFirst().orElse(null);
        var next=new ArrayList<>(scenes);next.removeIf(scene->scene.state().pos().equals(packet.pos()));
        if(packet.formed()){
            var ports=previous!=null&&Arrays.equals(previous.state().ports(),packet.ports())?previous.ports():new Hk3W11Ports(packet.ports());
            if(previous!=null&&ports!=previous.ports())previous.ports().close();
            next.add(new Scene(packet,mc.level.getGameTime(),ports));
        }else if(previous!=null)previous.ports().close();
        scenes=List.copyOf(next);
    }
    public static void maintain(){
        var mc=Minecraft.getInstance();
        if(level!=mc.level){clear();return;}
        scenes.stream().filter(scene->mc.level.getGameTime()-scene.received()>120).forEach(scene->scene.ports().close());
        scenes=scenes.stream().filter(scene->mc.level.getGameTime()-scene.received()<=120).toList();
    }
    public static void clear(){scenes.forEach(scene->scene.ports().close());scenes=List.of();level=null;}
}
