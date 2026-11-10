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
/** 【变更记录 #1】2026-10-01 06:25:16（修订128）：删除无；新增真实阅读与操作记录；修改无；用途：服务器核对原始条件，失败或模拟不授予。 */
/** 【变更记录 #2】2026-10-01 13:27:41（修订128）：删除：无；新增/修改：原版地牢箱真实战利品展开前保留来源标记，避免开箱后丢失场景识别；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggNaturalChestMixin {
    @Shadow protected ResourceLocation lootTable;
    @Inject(method="unpackLootTable",at=@At("HEAD"))private void hk3gtl$loot(Player player,CallbackInfo ci){
        if((Object)this instanceof ChestBlockEntity chest&&chest.getLevel()!=null&&!chest.getLevel().isClientSide&&lootTable!=null&&lootTable.toString().equals("minecraft:chests/simple_dungeon")){chest.getPersistentData().putBoolean("hk3EggDungeonChest",true);chest.setChanged();}
        if(player instanceof ServerPlayer p&&(Object)this instanceof ChestBlockEntity chest&&lootTable!=null&&lootTable.getPath().startsWith("chests/")&&p.level().getBiome(chest.getBlockPos()).value().coldEnoughToSnow(chest.getBlockPos())){
            var s=com.sirin.hk3gtl.common.easter.Hk3EggRuntime.state(p);s.putLong("snowLootChest",chest.getBlockPos().asLong());s.putLong("snowLootTick",p.server.overworld().getGameTime());s.putString("snowLootDim",p.level().dimension().location().toString());
        }
    }
}
