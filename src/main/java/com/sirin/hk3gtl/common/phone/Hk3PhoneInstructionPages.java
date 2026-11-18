package com.sirin.hk3gtl.common.phone;

import com.google.gson.JsonParser;
import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import com.sirin.hk3gtl.common.easter.Hk3ReadingSessions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Difficulty;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;


public final class Hk3PhoneInstructionPages {
    public static final String COST="instruction_research_cost", DIFFICULTY="instruction_game_difficulty", REACTOR="instruction_reactor_safety";
    private static final String PREFIX="hk3gtl.phone.instructions.";
    private static final Map<String,String> ZH=load("zh_cn"), EN=load("en_us");
    private Hk3PhoneInstructionPages(){}

    private static Map<String,String> load(String language){
        try(var in=Hk3PhoneInstructionPages.class.getResourceAsStream("/assets/hk3gtl/lang/"+language+".json")){
            var values=new LinkedHashMap<String,String>();
            for(var entry:JsonParser.parseReader(new InputStreamReader(in,StandardCharsets.UTF_8)).getAsJsonObject().entrySet())
                if(entry.getKey().startsWith(PREFIX))values.put(entry.getKey(),entry.getValue().getAsString());
            return Map.copyOf(values);
        }catch(java.io.IOException failure){throw new IllegalStateException("无法读取手机说明正文："+language,failure);}
    }
    static String text(ServerPlayer p,String key,Object... args){
        return String.format(Locale.ROOT,(p.getLanguage().startsWith("zh")?ZH:EN).get(PREFIX+key),args);
    }
    public static boolean managed(String id){return COST.equals(id)||DIFFICULTY.equals(id)||REACTOR.equals(id);}
    public static boolean authorize(ServerPlayer p,String id){
        var state=Hk3EggRuntime.state(p);
        return managed(id)&&Hk3PhoneData.get(p).installed(p.getUUID())&&Hk3PhoneRuntime.powered(p)
                &&state.getBoolean("phoneOpen")&&state.getString("phoneMode").equals("instructions_read")
                &&state.getString("instructionId").equals(id);
    }
    public static int index(ServerPlayer p){
        if(!Hk3PhoneData.get(p).installed(p.getUUID())||!Hk3PhoneRuntime.requirePower(p))return 0;
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(p,"instructions");
        var view=new CompoundTag();view.putString("Mode","instructions");Hk3PhoneService.send(p,view);return 1;
    }
    public static int open(ServerPlayer p,String id){
        if(!managed(id)||!Hk3PhoneData.get(p).installed(p.getUUID())||!Hk3PhoneRuntime.requirePower(p))return 0;
        com.sirin.hk3gtl.common.easter.Hk3EggPhone.opened(p,"instructions_read");
        Hk3EggRuntime.state(p).putString("instructionId",id);
        String key=switch(id){case COST->"cost";case DIFFICULTY->"difficulty";default->"reactor";};
        var view=new CompoundTag();view.putString("Mode","instruction_read");view.putString("Id",id);
        view.putString("Title",text(p,key+".title"));view.putString("Body",DIFFICULTY.equals(id)?difficultyBody(p):text(p,key+".body"));
        view.putBoolean("InstructionPage",true);Hk3PhoneService.send(p,view);
        if(COST.equals(id)&&holdsGoldCredit(p))Hk3EggVanilla.caseEvent(p,239);
        return 1;
    }
    public static void completed(ServerPlayer p,Hk3ReadingSessions.Session session){
        if(session.cursor().done()&&authorize(p,session.id())&&REACTOR.equals(session.id()))Hk3EggVanilla.caseEvent(p,461);
    }
    public static void closed(ServerPlayer p,String id){
        if(DIFFICULTY.equals(id))Hk3EggVanilla.caseEvent(p,457);
    }
    private static boolean holdsGoldCredit(ServerPlayer p){
        var item=net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation("gtceu","gold_credit"));
        return p.getInventory().items.stream().anyMatch(stack->stack.is(item))||p.getOffhandItem().is(item);
    }
    private static String difficultyBody(ServerPlayer p){
        var world=p.serverLevel().getLevelData();var difficulty=world.getDifficulty();
        var body=new StringBuilder(text(p,"difficulty.snapshot",text(p,"difficulty."+difficulty.getKey()),text(p,world.isDifficultyLocked()?"difficulty.locked":"difficulty.unlocked")));
        for(var value:Difficulty.values())body.append("\n\n").append(text(p,"difficulty."+value.getKey())).append("\n").append(text(p,"difficulty."+value.getKey()+".info"));
        return body.append("\n\n").append(text(p,"difficulty.read_only")).toString();
    }
}
