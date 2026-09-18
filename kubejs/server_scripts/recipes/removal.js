ServerEvents.recipes(event => {
    event.remove({
        type: 'gtceu:electric_blast_furnace',
        output: 'gtceu:soulium_ingot'
    });

    event.remove({
        type: 'gtceu:electric_blast_furnace',
        output: 'gtceu:soulium_hot_ingot'
    });

    // 创造箱/创造储罐：保留获取方式，不移除配方；生存模式禁开 GUI 由 Java Hk3CreativeItemGuard 处理。
});
