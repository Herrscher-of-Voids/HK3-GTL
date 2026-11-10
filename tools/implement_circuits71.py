"""修订71：同源生成跨级电路映射、资源与显示接线，备份所有被改文件。"""
if __name__ == "__main__":
    raise SystemExit("历史修订实施脚本已停用：禁止覆盖修订107的正式电压键。")

from pathlib import Path
from datetime import datetime
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl'
RES = ROOT / 'src/main/resources'
BACKUP = ROOT / 'archive/revision71-before'
STAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
SPEC = json.loads((ROOT/'logs/revision71/review-scope.json').read_text(encoding='utf-8'))
VOLT = json.loads((ROOT/'logs/revision71/voltage-map.json').read_text(encoding='utf-8'))
KEYS = [f'{g}_{i}' for g in ('abyss','imaginary','quantum','finality') for i in range(1,5)]
FORMS = ['processor','assembly','computer','processor_mainframe']
FORMS_EN = ['Processor','Processor Assembly','Supercomputer','Mainframe']
ENTRIES = []
for n, family in enumerate(SPEC['circuit_design']['series']):
    for form in range(4):
        tier = family['first_tier'] + form
        primary = n % 2 == 0
        item = KEYS[tier-15]+'_'+FORMS[form] if primary else family['id']+'_'+FORMS[form]
        ENTRIES.append(dict(id=item,tier=tier,family=family['id'],form=form,primary=primary,
            zh=family['zh']+SPEC['circuit_design']['forms'][form],en=family['en']+' '+FORMS_EN[form]))

def write(path, text):
    if path.exists():
        old=path.read_text(encoding='utf-8')
        if old == text:return
        backup=BACKUP/path.relative_to(ROOT)
        if not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')

def note(text, message):
    if '内测5修订71' in text:return text
    nums=[int(x) for x in re.findall(r'变更记录\s*#(\d+)',text)]
    num=max(nums,default=1)+1
    block=f'/**\n * 【变更记录 #{num}】{STAMP}（第 {num} 次备注 · 内测5修订71）\n * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。\n * 修改：{message}\n * 用途：保持同级电路可替换、资源与游戏行为一致。\n */\n'
    return re.sub(r'(?m)^(public (?:final |abstract )?class )',lambda m:block+m[0],text,count=1)

def patch(rel, fn, message):
    p=JAVA/rel;s=p.read_text(encoding='utf-8');new=fn(s)
    if new!=s:write(p,note(new,message))

def main():
    rows=',\n'.join('            new Entry("{id}", {tier}, "{family}", {form}, {primary})'.format(**{**e,'primary':str(e['primary']).lower()}) for e in ENTRIES)
    source='''package com.sirin.hk3gtl.common.item;

import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import java.util.List;

/**
 * 【变更记录 #1】STAMP（第 1 次备注 · 内测5修订71）
 * 删除：无。新增：七系列28种电路的唯一等级映射。
 * 修改：系列跨四级，相邻系列错开两级；旧16个正式物品保留注册键并赋予系列名。
 * 用途：注册、配方、创造栏和WMP共用映射；通用输入按等级标签，组装按系列前一形态。
 */
public final class Hk3CircuitCatalog {
    public record Entry(String id, int tier, String family, int form, boolean primary) {}
    public static final List<Entry> ENTRIES = List.of(
ROWS
    );
    private Hk3CircuitCatalog() {}
    public static TagKey<Item> tag(int tier) {
        return TagKey.create(Registries.ITEM, new ResourceLocation("forge", "circuits/" + Hk3Tiers.voltageKey(tier)));
    }
    public static int tier(ResourceLocation id) {
        if (id == null || !id.getNamespace().equals("hk3gtl")) return -1;
        return ENTRIES.stream().filter(e -> e.id().equals(id.getPath())).mapToInt(Entry::tier).findFirst().orElse(-1);
    }
    public static List<String> paths() { return ENTRIES.stream().map(Entry::id).toList(); }
}
'''.replace('STAMP',STAMP).replace('ROWS',rows)
    write(JAVA/'common/item/Hk3CircuitCatalog.java',source)
    patch('common/item/Hk3CircuitItems.java',lambda s:s.replace('        registerDetailedCircuits();','        registerDetailedCircuits();\n        for (var entry : Hk3CircuitCatalog.ENTRIES) {\n            if (!entry.primary()) MUTABLE_DETAILED_CIRCUITS.put(entry.id(), registerItem(entry.id()));\n        }'),'注册12种交叠系列电路，保留既有16种正式引用。')
    patch('common/registration/Hk3CreativeTabsImpl.java',lambda s:re.sub(r'private static final String\[\] CANONICAL_DETAILED_CIRCUIT_PATHS = \{.*?\n    \};','private static final String[] CANONICAL_DETAILED_CIRCUIT_PATHS =\n            com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.paths().toArray(String[]::new);',s,flags=re.S).replace('正式细分电路 16 档（与语言/标签 canonical 一致；创造栏只展示这些，其余 48 个注册物不列出）','正式跨级电路28种；历史占位形态不展示'),'创造栏按七个系列展示28种正式电路。')
    def wmp(s):
        s=re.sub(r'private static final Map<ResourceLocation, Integer> CIRCUIT_TIERS = Map.ofEntries\(.*?\n    \);','',s,flags=re.S)
        s=s.replace('CIRCUIT_TIERS.getOrDefault(id, -1)','com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tier(id)')
        s=s.replace('Hk3Tiers.VOLTAGE_KEYS[tier - Hk3Tiers.ABYSS_1].toUpperCase(java.util.Locale.ROOT)','Hk3Tiers.VOLTAGE_SYMBOLS[tier - Hk3Tiers.ABYSS_1]')
        return s
    patch('common/compat/wmp/Hk3WmpCircuitCompat.java',wmp,'WMP识别全部28种电路并显示已确认的电压标识。')
    def voltage(s):
        anchor='        TIER_COUNT = 15;'
        assert anchor in s
        extra='''
        // 注册短键保持稳定，玩家显示使用确认的16级标识和英文全称。
        for (int index = 0; index < 16; index++) {
            int tier = 15 + index;
            String color = new String[]{"§1§l", "§3§l", "§6§l", "§4§l"}[index / 4];
            VNF[tier] = color + com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_SYMBOLS[index];
            VOLTAGE_NAMES[tier] = com.sirin.hk3gtl.common.constants.Hk3Tiers.VOLTAGE_NAMES_EN[index];
        }'''
        return s.replace(anchor,anchor+extra)
    patch('mixin/GTValuesMixin.java',voltage,'VNF和英文全称接入HBV至CEV；VN注册键与电压数值保持稳定。')
    def values(s):
        s=s.replace('if (tier < GTValues.VN.length) return GTValues.VN[tier];','if (tier >= 15) return Hk3Tiers.VOLTAGE_SYMBOLS[tier - 15];\n        if (tier < GTValues.VN.length) return GTValues.VN[tier];')
        s=s.replace('if (tier < GTValues.VOLTAGE_NAMES.length) return GTValues.VOLTAGE_NAMES[tier];','if (tier >= 15) return Hk3Tiers.VOLTAGE_NAMES_EN[tier - 15];\n        if (tier < GTValues.VOLTAGE_NAMES.length) return GTValues.VOLTAGE_NAMES[tier];')
        s=s.replace('return FULL_VLVH[tier];','return tier >= 15 ? FULL_VCF[tier] + Hk3Tiers.VOLTAGE_SYMBOLS[tier - 15] : FULL_VLVH[tier];')
        s=s.replace('return FULL_VLVT[tier];','return tier >= 15 ? "§r" : FULL_VLVT[tier];')
        return s
    patch('common/constants/Hk3ValuesImpl.java',values,'安全显示查询统一采用16级标识，避免机器提示残留海渊序号。')
    for language in ['zh_cn','en_us']:
        p=RES/f'assets/hk3gtl/lang/{language}.json';data=json.loads(p.read_text(encoding='utf-8'))
        for i,key in enumerate(KEYS):
            data['hk3gtl.voltage.'+key]=VOLT['zh' if language=='zh_cn' else 'en'][i]+' ('+VOLT['symbols'][i]+')'
        for e in ENTRIES:
            data['item.hk3gtl.'+e['id']]=e['zh' if language=='zh_cn' else 'en']+' ('+VOLT['symbols'][e['tier']-15]+')'
        write(p,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    for tier in range(15,31):
        ids=['hk3gtl:'+e['id'] for e in ENTRIES if e['tier']==tier]
        key=KEYS[tier-15];symbol=VOLT['symbols'][tier-15].lower()
        aliases=[key,symbol,['ab','im','qt','fn'][(tier-15)//4]+'-'+['i','ii','iii','iv'][(tier-15)%4]]
        for namespace in ['forge','gtceu']:
            for alias in aliases:write(RES/f'data/{namespace}/tags/items/circuits/{alias}.json',json.dumps({'replace':False,'values':ids},indent=2)+'\n')
    for e in ENTRIES:
        if e['primary']:continue
        base=KEYS[(e['tier']-15)//4*4+e['form']]+'_'+FORMS[e['form']]
        model=json.loads((RES/f'assets/hk3gtl/models/item/{base}.json').read_text(encoding='utf-8'))
        write(RES/f'assets/hk3gtl/models/item/{e["id"]}.json',json.dumps(model,indent=2)+'\n')
    write(RES/'data/hk3gtl/catalog/circuit_series.json',json.dumps({'schema':1,'entries':ENTRIES},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'circuits':len(ENTRIES),'tiers':16,'backup':str(BACKUP)},ensure_ascii=False))

if __name__=='__main__':main()

# 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：删除旧电压输出键；修改为16档正式键；用途：防止工具重新生成过期引用。
