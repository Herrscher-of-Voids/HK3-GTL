package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceLocation;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(RandomizableContainerBlockEntity.class)
 
 
public abstract class Hk3EggNaturalChestMixin {
    @Shadow protected ResourceLocation lootTable;
    @Inject(method="unpackLootTable",at=@At("HEAD"))private void hk3gtl$loot(Player player,CallbackInfo ci){
        if((Object)this instanceof ChestBlockEntity chest&&chest.getLevel()!=null&&!chest.getLevel().isClientSide&&lootTable!=null&&lootTable.toString().equals("minecraft:chests/simple_dungeon")){chest.getPersistentData().putBoolean("hk3EggDungeonChest",true);chest.setChanged();}
        if(player instanceof ServerPlayer p&&(Object)this instanceof ChestBlockEntity chest&&lootTable!=null&&lootTable.getPath().startsWith("chests/")&&p.level().getBiome(chest.getBlockPos()).value().coldEnoughToSnow(chest.getBlockPos())){
            var s=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);s.putLong("snowLootChest",chest.getBlockPos().asLong());s.putLong("snowLootTick",p.server.overworld().getGameTime());s.putString("snowLootDim",p.level().dimension().location().toString());
        }
    }
}
