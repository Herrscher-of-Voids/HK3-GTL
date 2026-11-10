"""修订74：把电压从显示名称移至物品提示，保留内部注册键、等级与标签。"""
import json
import re
from revision74_support import JAVA, RES, patch_java, new_java, save_json


def main():
    new_java('common/item/Hk3CircuitItem.java', '''package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.constants.Hk3Values;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import java.util.List;
import javax.annotation.Nullable;

public final class Hk3CircuitItem extends Item {
    private final int tier;

    public Hk3CircuitItem(int tier) {
        super(new Item.Properties());
        this.tier = tier;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        super.appendHoverText(stack, level, tooltip, flag);
        // 未列入正式目录的历史占位物不推断等级；正式电路按稳定目录显示。
        if (tier >= 0) {
            tooltip.add(Component.translatable("hk3gtl.tooltip.circuit_voltage", Hk3Values.getVNF(tier)));
        }
    }
}
''', '删除：无。新增：正式电路的独立电压提示类。\n * 修改：参照整包GTL高阶电路的独立等级提示，使用安全long电压体系的显示接口。\n * 用途：注册ID与标签负责配方兼容，名称表达技术形态；客户端提示只读，不改变服务端等级。')
    def registration(s):
        return s.replace('return Hk3Items.ITEMS.register(id, () -> new Item(new Item.Properties()));', '''int tier = Hk3CircuitCatalog.tier(new net.minecraft.resources.ResourceLocation("hk3gtl", id));
        for (int i = 0; i < HONKAI_CIRCUIT_TIERS.length; i++) {
            if (id.equals("honkai_circuit_" + HONKAI_CIRCUIT_TIERS[i])) tier = i;
        }
        final int displayTier = tier;
        return Hk3Items.ITEMS.register(id, () -> new Hk3CircuitItem(displayTier));''')
    patch_java('common/item/Hk3CircuitItems.java', registration,
        '删除：普通Item缺失电压提示的注册方式。新增：正式电路等级的只读传参。\n * 修改：28个目录电路与15个崩坏能电路改用Hk3CircuitItem，其他占位物不猜测等级。\n * 用途：把电压显示移到tooltip，保留注册键、系列映射及同级标签。')
    circuits = json.loads((RES/'data/hk3gtl/catalog/circuit_series.json').read_text('utf-8'))['entries']
    old_tiers = ['ulv','lv','mv','hv','ev','iv','luv','zpm','uv','uhv','uev','uiv','uxv','opv','max']
    zh = ['崩坏感应电路','崩坏整流电路','崩坏逻辑电路','崩坏集成电路','崩坏微型处理器','崩坏纳米处理器','崩坏光子处理器','崩坏神经处理器','崩坏并行阵列','崩坏相位阵列','崩坏空间阵列','崩坏因果阵列','崩坏时序计算机','崩坏全域计算机','崩坏统一场主机']
    en = ['Honkai Sensing Circuit','Honkai Rectifier Circuit','Honkai Logic Circuit','Honkai Integrated Circuit','Honkai Microprocessor','Honkai Nanoprocessor','Honkai Photonic Processor','Honkai Neural Processor','Honkai Parallel Array','Honkai Phase Array','Honkai Spatial Array','Honkai Causal Array','Honkai Temporal Computer','Honkai Omnidomain Computer','Honkai Unified Field Mainframe']
    for lang in ['zh_cn','en_us']:
        p = RES/f'assets/hk3gtl/lang/{lang}.json'
        data = json.loads(p.read_text('utf-8'))
        for entry in circuits:
            key = 'item.hk3gtl.' + entry['id']
            data[key] = re.sub(r'\s*\([A-Za-z0-9]+\)$', '', data[key])
        for i, tier in enumerate(old_tiers):
            data['item.hk3gtl.honkai_circuit_' + tier] = (zh if lang == 'zh_cn' else en)[i]
        data['hk3gtl.tooltip.circuit_voltage'] = '%s级电路' if lang == 'zh_cn' else '%s-Tier Circuit'
        data['_comment_revision74_names'] = '变更记录 #1：修订74移除43个正式电路名称的电压后缀；电压只在tooltip显示，15个传统电路使用技术形态名称。'
        save_json(p, data)
    print('已修改43个电路名称及电压提示注册；等级与标签未改。')


if __name__ == '__main__':
    main()
