package com.sirin.hk3gtl.client.compat;
import mezz.jei.api.gui.IRecipeLayoutDrawable;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.library.plugins.jei.tags.ITagInfoRecipe;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.BuiltInRegistries;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.easter.Hk3EggUiPacket;
import java.util.*;
/** 【变更记录 #1】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：JEI真实绘制后停留一秒记录配方；标签页只统计鼠标实际查看的同页物品，页面切换清空；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggJeiReading {
    private static net.minecraft.client.gui.screens.Screen screen;
    private static long lastTick=-1;
    private static String lastTag="";
    private static final Map<String,Long> SENT=new LinkedHashMap<>();
    private Hk3EggJeiReading(){}
    public static <R> void draw(IRecipeLayoutDrawable<R> layout,int mouseX,int mouseY){
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getConnection()==null||mc.screen==null||!mc.screen.getClass().getName().equals("mezz.jei.gui.recipes.RecipesGui"))return;
        long tick=mc.level.getGameTime();if(screen!=mc.screen||tick<lastTick){SENT.clear();screen=mc.screen;lastTag="";send("egg_tag_clear","");}lastTick=tick;
        var recipe=layout.getRecipe();var id=layout.getRecipeCategory().getRegistryName(recipe);
        if(id!=null)sendOnce("egg_recipe",id.toString(),tick);
        if(recipe instanceof ITagInfoRecipe tag){
            String key=tag.getTag().location().toString();if(!lastTag.equals(key)){lastTag=key;send("egg_tag_clear","");SENT.clear();}
            layout.getItemStackUnderMouse(mouseX,mouseY).ifPresent(stack->sendOnce("egg_tag",key+"|"+BuiltInRegistries.ITEM.getKey(stack.getItem()),tick));
        }else if(!lastTag.isEmpty()){lastTag="";SENT.clear();send("egg_tag_clear","");}
        boolean output=layout.getRecipeSlotsView().getSlotViews().stream().filter(v->v.getRole()==RecipeIngredientRole.OUTPUT).flatMap(v->v.getItemStacks()).anyMatch(v->BuiltInRegistries.ITEM.getKey(v.getItem()).toString().equals("gtceu:advanced_smd_transistor"));
        if(output)sendOnce("egg_transistor","gtceu:advanced_smd_transistor",tick);
    }
    private static void sendOnce(String action,String value,long tick){String key=action+value;Long previous=SENT.get(key);if(previous==null){if(SENT.size()>128)SENT.clear();SENT.put(key,tick);return;}if(previous>=0&&tick-previous>=20){send(action,value);SENT.put(key,-1L);}}
    /**
     * JEI can finish a render callback while the client is leaving a world. The
     * connection check in draw() is not sufficient because the connection may
     * disappear between two render callbacks. Treat the receipt as best-effort
     * telemetry and drop it when no server connection exists.
     */
    private static void send(String action,String value){
        var mc=Minecraft.getInstance();
        if(mc.getConnection()==null||mc.level==null||mc.player==null)return;
        Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket(action,value));
    }
}
