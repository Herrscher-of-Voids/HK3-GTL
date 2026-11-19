package com.sirin.hk3gtl.client.compat;
import mezz.jei.api.gui.IRecipeLayoutDrawable;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.library.plugins.jei.tags.ITagInfoRecipe;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.registries.BuiltInRegistries;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.easter.Hk3EggUiPacket;
import java.lang.ref.WeakReference;
import java.util.*;
public final class Hk3EggJeiReading {
    private static WeakReference<Screen> screen=new WeakReference<>(null);
    private static long lastTick=-1;
    private static String lastTag="";
    private static final Map<String,Long> SENT=new LinkedHashMap<>();
    private Hk3EggJeiReading(){}
    public static <R> void draw(IRecipeLayoutDrawable<R> layout,int mouseX,int mouseY){
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getConnection()==null||mc.screen==null||!mc.screen.getClass().getName().equals("mezz.jei.gui.recipes.RecipesGui"))return;
        long tick=mc.level.getGameTime();if(screen.get()!=mc.screen||tick<lastTick){SENT.clear();screen=new WeakReference<>(mc.screen);lastTag="";send("egg_tag_clear","");}lastTick=tick;
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
    private static void send(String action,String value){
        var mc=Minecraft.getInstance();
        if(mc.getConnection()==null||mc.level==null||mc.player==null)return;
        Hk3Network.CHANNEL.sendToServer(new Hk3EggUiPacket(action,value));
    }
}
