package com.sirin.hk3gtl.common.dimension.melon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.LecternBlock;
import net.minecraft.world.level.block.entity.LecternBlockEntity;
import net.minecraft.world.level.saveddata.SavedData;

public final class Hk3MelonWorld {
    public static final ResourceKey<Level> KEY = ResourceKey.create(Registries.DIMENSION,
            new ResourceLocation("hk3gtl", "melon_reality"));
    public static final int WORLD_MIN_Y = -64;
    public static final BlockPos LECTERN = new BlockPos(0, 96, -1);
    private static final int LAYOUT_VERSION = 2;

    private Hk3MelonWorld() {}

    public static void ensure(ServerLevel level) {
        var landmarks = level.getDataStorage().computeIfAbsent(Landmarks::load, Landmarks::new,
                "hk3gtl_melon_landmarks");
        if (landmarks.layoutVersion >= LAYOUT_VERSION) return;
        if (landmarks.built) removeEntrance(level);
        shore(level);
        placeLetter(level);
        landmarks.built = true;
        landmarks.layoutVersion = LAYOUT_VERSION;
        landmarks.setDirty();
    }

    private static void shore(ServerLevel level) {
        var rind = Hk3MelonBlocks.MELON_RIND.get().defaultBlockState();
        var at = new BlockPos.MutableBlockPos();
        for (int x = -8; x <= 8; x++) for (int z = -9; z <= 16; z++) {
            double radius = Math.sqrt(x * x + (z - 3.5) * (z - 3.5) * 0.36);
            if (radius > 8) continue;
            int top = 95 - Math.max(0, (int) Math.ceil(radius - 5.5));
            for (int y = top; y > WORLD_MIN_Y; y--) {
                at.set(x, y, z);
                if (!level.isEmptyBlock(at) && level.getFluidState(at).isEmpty()) break;
                level.setBlock(at, rind, 2);
            }
        }
        for (int x = -5; x <= 5; x++) for (int z = -2; z <= 10; z++)
            for (int y = 96; y <= 105; y++) {
                at.set(x, y, z);
                var state = level.getBlockState(at);
                if (state.is(Hk3MelonBlocks.MELON_RIND.get()) || state.is(Hk3MelonBlocks.SEED_SAND.get())
                        || !state.getFluidState().isEmpty())
                    level.setBlock(at, Blocks.AIR.defaultBlockState(), 2);
            }
    }

    private static void removeEntrance(ServerLevel level) {
        var rind = Hk3MelonBlocks.MELON_RIND.get();
        for (int x = -10; x <= 10; x++) for (int z = -5; z <= 19; z++)
            remove(level, new BlockPos(x, 95, z),
                    Math.abs(x) == 10 || z == -5 || z == 19 ? rind : Hk3MelonBlocks.SEED_SAND.get());
        remove(level, new BlockPos(0, 95, 0), Blocks.MOSS_BLOCK);
        for (int step = 1; step <= 3; step++) remove(level, new BlockPos(step, 95, 0), Blocks.WHITE_CONCRETE);
        for (int step = 1; step <= 4; step++) remove(level, new BlockPos(0, 95, -step), Blocks.BLACK_CONCRETE);
        for (int side : new int[]{-1, 1}) {
            remove(level, new BlockPos(2, 95, side), Blocks.WHITE_CONCRETE);
            remove(level, new BlockPos(side, 95, -3), Blocks.BLACK_CONCRETE);
        }
        remove(level, new BlockPos(-3, 96, -2), Blocks.LODESTONE);
        for (int x : new int[]{-9, 9}) for (int z : new int[]{-4, 18}) {
            for (int y = 96; y <= 100; y++) remove(level, new BlockPos(x, y, z), rind);
            remove(level, new BlockPos(x, 101, z), Blocks.SEA_LANTERN);
        }
        var oldLectern = new BlockPos(6, 96, -3);
        if (level.getBlockEntity(oldLectern) instanceof LecternBlockEntity lectern
                && (lectern.getBook().isEmpty() || lectern.getBook().getOrCreateTag().getString("title").equals("入口记录"))) {
            lectern.setBook(ItemStack.EMPTY);
            level.setBlock(oldLectern, Blocks.AIR.defaultBlockState(), 2);
        }
        removeAccess(level, new BlockPos(0, 96, -5), Direction.NORTH);
        removeAccess(level, new BlockPos(10, 96, 0), Direction.EAST);
    }

    private static void removeAccess(ServerLevel level, BlockPos threshold, Direction outward) {
        var rind = Hk3MelonBlocks.MELON_RIND.get();
        var side = outward.getClockWise();
        for (int step = 0; step <= 3; step++) for (int width = -1; width <= 1; width++)
            remove(level, threshold.relative(outward, step).relative(side, width).below(), rind);
        for (int direction : new int[]{1, -1}) {
            for (int y = direction == 1 ? 96 : 95; y > WORLD_MIN_Y && y < level.getMaxBuildHeight(); y += direction) {
                var pos = threshold.relative(outward, 3).atY(y);
                var state = level.getBlockState(pos);
                if (!state.is(Blocks.LADDER) || state.getValue(LadderBlock.FACING) != outward) break;
                remove(level, pos, Blocks.LADDER);
                remove(level, threshold.relative(outward, 2).atY(y), rind);
            }
        }
    }

    private static void remove(ServerLevel level, BlockPos pos, Block expected) {
        if (level.getBlockState(pos).is(expected)) level.setBlock(pos, Blocks.AIR.defaultBlockState(), 2);
    }

    static void placeLetter(ServerLevel level) {
        level.setBlock(LECTERN, Blocks.LECTERN.defaultBlockState().setValue(LecternBlock.FACING, Direction.SOUTH)
                .setValue(LecternBlock.HAS_BOOK, true), 3);
        var book = new ItemStack(Items.WRITTEN_BOOK);
        var tag = book.getOrCreateTag();
        tag.putString("title", "给自己这种西瓜");
        tag.putString("author", "■■■与另一个我");
        var pages = new ListTag();
        for (String page : Hk3MelonAdventure.LETTER.split("\n\n"))
            pages.add(StringTag.valueOf(Component.Serializer.toJson(Component.literal(page))));
        tag.put("pages", pages);
        var lectern = (LecternBlockEntity) level.getBlockEntity(LECTERN);
        lectern.setBook(book);
        lectern.setChanged();
    }

    private static final class Landmarks extends SavedData {
        private boolean built;
        private int layoutVersion;

        private static Landmarks load(CompoundTag tag) {
            var data = new Landmarks();
            data.built = tag.getBoolean("Built");
            data.layoutVersion = tag.getInt("LayoutVersion");
            return data;
        }

        @Override
        public CompoundTag save(CompoundTag tag) {
            tag.putBoolean("Built", built);
            tag.putInt("LayoutVersion", layoutVersion);
            return tag;
        }
    }
}
