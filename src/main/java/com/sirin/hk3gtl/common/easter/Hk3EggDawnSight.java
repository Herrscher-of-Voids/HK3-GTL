package com.sirin.hk3gtl.common.easter;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;






public final class Hk3EggDawnSight {
    private Hk3EggDawnSight() {}
    public interface World {
        boolean loaded(int chunkX, int chunkZ);
        BlockPos firstHit(Vec3 from, Vec3 to);
        boolean orange(BlockPos pos);
        boolean sky(BlockPos pos);
    }
    public static boolean visible(ServerPlayer player) {
        var level = player.level();
        return visible(player.getEyePosition(), player.getLookAngle(), new World() {
            public boolean loaded(int x, int z) { return level.hasChunk(x, z); }
            public BlockPos firstHit(Vec3 from, Vec3 to) {
                var hit = level.clip(new ClipContext(from, to, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, player));
                return hit.getType() == HitResult.Type.BLOCK ? hit.getBlockPos() : null;
            }
            public boolean orange(BlockPos pos) { return level.getBlockState(pos).is(Blocks.ORANGE_STAINED_GLASS); }
            public boolean sky(BlockPos pos) { return level.canSeeSky(pos); }
        });
    }
    public static boolean visible(Vec3 eye, Vec3 look, World world) {
        if (!Double.isFinite(look.lengthSqr()) || look.y < 0 || look.lengthSqr() < .99 || look.lengthSqr() > 1.01) return false;
        Vec3 end = eye.add(look.scale(64));
        BlockPos startBlock = BlockPos.containing(eye), endBlock = BlockPos.containing(end);
        for (int x = Math.min(startBlock.getX(), endBlock.getX()) >> 4; x <= (Math.max(startBlock.getX(), endBlock.getX()) >> 4); x++)
            for (int z = Math.min(startBlock.getZ(), endBlock.getZ()) >> 4; z <= (Math.max(startBlock.getZ(), endBlock.getZ()) >> 4); z++)
                if (!world.loaded(x, z)) return false;
        Vec3 from = eye; boolean crossed = false; double previous = 0;
        for (int i = 0; i < 64; i++) {
            BlockPos hit = world.firstHit(from, end);
            if (hit == null) return crossed && world.sky(endBlock);
            if (!world.orange(hit)) return false;
            double exit = Hk3EggScpFacts.exitDistance(eye, look, hit) + 1e-5;
            if (!Double.isFinite(exit) || exit <= previous || exit >= 64) return false;
            crossed = true; previous = exit; from = eye.add(look.scale(exit));
        }
        return false;
    }
}
