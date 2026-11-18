package com.sirin.hk3gtl.mixin.enhanced.client;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.MultiblockShapeInfo;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3ApprovedArchitecture;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeArchitectureShapes;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3SparsePreviewData;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

@Pseudo
@Mixin(targets = "com.gtl.enhancedcore.client.preview.LazyMultiblockPreviewWidget", remap = false)
abstract class Hk3JeiMaterialIndexMixin {
    @Redirect(method = "addIndexedMaterials", at = @At(value = "INVOKE", target =
            "Lcom/gregtechceu/gtceu/api/machine/MultiblockMachineDefinition;getMatchingShapes()Ljava/util/List;"), require = 0)
    private static List<MultiblockShapeInfo> hk3gtl$materialPalette(MultiblockMachineDefinition definition) {
        var source = Hk3SparsePreviewData.source(definition.getId().toString());
        if (source == null || !Hk3ApprovedArchitecture.IDS.contains(source.key())) return definition.getMatchingShapes();
        // 材料索引只需要方块种类，完整形状在打开预览时加载。
        String path = "/data/hk3gtl/structures/jei_materials/" + source.key() + ".txt";
        try (var input = new BufferedReader(new InputStreamReader(
                Hk3LargeArchitectureShapes.class.getResourceAsStream(path), StandardCharsets.US_ASCII))) {
            BlockInfo[] palette = input.lines().map(Hk3LargeArchitectureShapes::state)
                    .map(BlockInfo::fromBlockState).toArray(BlockInfo[]::new);
            return List.of(new MultiblockShapeInfo(new BlockInfo[][][]{{palette}}));
        } catch (IOException failure) {
            throw new UncheckedIOException(failure);
        }
    }
}
