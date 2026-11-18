package com.sirin.hk3gtl.mixin.client;

import com.sirin.hk3gtl.client.farview.Hk3WorldFarCapture;
import net.minecraft.client.multiplayer.ClientChunkCache;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.level.chunk.LevelChunk;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 整区数据实际到达后才登记；不触碰区块请求或服务器视距。 */
@Mixin(ClientChunkCache.class)
public abstract class Hk3WorldFarChunkMixin {
    @Shadow @Final private ClientLevel level;
    @Inject(method="replaceWithPacketData",at=@At("RETURN"))
    private void hk3gtl$worldSnapshot(CallbackInfoReturnable<LevelChunk> callback){
        Hk3WorldFarCapture.received(level,callback.getReturnValue());
    }
}
