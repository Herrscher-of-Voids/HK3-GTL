# -*- coding: utf-8 -*-
"""修订91，2026-09-28：只读核对双底包类链接、兼容入口和增强版执行器调用点；不替代游戏加载。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def pool(data):
    """读取常量池，区分真实类引用与普通文本，避免把可选Mixin字符串误报为硬依赖。"""
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('不是Java类')
    count = struct.unpack_from('>H', data, 8)[0]
    entries = [None] * count
    offset, index = 10, 1
    while index < count:
        tag = data[offset]
        offset += 1
        if tag == 1:
            size = struct.unpack_from('>H', data, offset)[0]
            offset += 2
            entries[index] = (tag, data[offset:offset+size].decode('utf-8', errors='replace'))
            offset += size
        elif tag in (7, 8, 16, 19, 20):
            entries[index] = (tag, struct.unpack_from('>H', data, offset)[0])
            offset += 2
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            offset += 4
        elif tag in (5, 6):
            offset += 8
            index += 1
        elif tag == 15:
            offset += 3
        else:
            raise ValueError('未知常量池标签 '+str(tag))
        index += 1
    return entries


def referenced_classes(data):
    entries = pool(data)
    names = set()
    for entry in entries:
        if entry and entry[0] == 7:
            name = entries[entry[1]][1]
            names.add(name)
        elif entry and entry[0] == 1 and entry[1].startswith(('(', 'L', '[')):
            names.update(re.findall(r'L([\w/$]+);', entry[1]))
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, type=Path)
    parser.add_argument('--enhanced', required=True, type=Path)
    parser.add_argument('--output', default='logs/revision91/compatibility.json', type=Path)
    args = parser.parse_args()
    prefixes = ('org/gtlcore/', 'com/gtladd/', 'com/hepdd/gtmthings/')
    refs = {}
    for path in (ROOT/'build/classes/java/main/com/sirin/hk3gtl').rglob('*.class'):
        for ref in referenced_classes(path.read_bytes()):
            if ref.startswith(prefixes):
                refs.setdefault(ref, []).append(str(path.relative_to(ROOT/'build/classes/java/main')))
    profiles = {}
    for label, folder in [('original', args.original), ('enhanced', args.enhanced)]:
        classes, mods, hashes = set(), {}, {}
        for jar in (folder/'mods').glob('*.jar'):
            with zipfile.ZipFile(jar) as archive:
                names = archive.namelist()
                classes.update(name[:-6] for name in names if name.endswith('.class'))
                if 'META-INF/mods.toml' in names:
                    # 只取模组声明段，不把dependencies中的modId算作已安装。
                    toml = archive.read('META-INF/mods.toml').decode('utf-8-sig')
                    for section in re.findall(r'\[\[mods\]\]([^\[]*)', toml):
                        match = re.search(r'modId\s*=\s*"([^"]+)"', section)
                        if match:
                            mods.setdefault(match[1], []).append(jar.name)
                if jar.name.startswith(('gtceu-', 'gtlcore-', 'ldlib-', 'gtladditions-', 'gtmthings-', 'GTL-Enhancedcore')):
                    hashes[jar.name] = hashlib.sha256(jar.read_bytes()).hexdigest()
        profiles[label] = {'missing_direct_classes':sorted(set(refs)-classes), 'duplicate_top_level_modids':{k:v for k,v in mods.items() if len(v)>1}, 'dependency_hashes':hashes}
    core = next((args.enhanced/'mods').glob('GTL-Enhancedcore-*.jar'))
    javap = subprocess.run(['javap', '-classpath', str(core), '-p', '-c', 'com.gtl.enhancedcore.common.recipe.iv.IvNativeEngine'], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True).stdout
    sections = {}
    for method, next_method in [('allowed', 'start'), ('start', 'multiplier'), ('advance', 'flush')]:
        match = re.search(r'  private [^\n]*\b'+method+r'\(', javap)
        end = re.search(r'  private [^\n]*\b'+next_method+r'\(', javap[match.end():])
        sections[method] = javap[match.start():match.end()+end.start()]
    hooks = {'allowed_calls_gt_conditions':'GTRecipe.checkConditions:' in sections['allowed'],
             'start_calls_allowed':'Method allowed:' in sections['start'],
             'advance_calls_allowed':'Method allowed:' in sections['advance'],
             'advance_calls_tick_guard':'RecipeLogic.handleTickRecipe:' in sections['advance']}
    source = (ROOT/'src/main/java/com/sirin/hk3gtl/mixin/Hk3MixinConfigPlugin.java').read_text(encoding='utf-8')
    hooks['enhanced_initializer_patch_disabled'] = 'SkyTearsAndGregHeartMixin") && enhanced) return false' in source
    config = json.loads((ROOT/'src/main/resources/hk3gtl.mixins.json').read_text(encoding='utf-8'))
    hooks['conditions_mixin_registered'] = 'EnhancedRecipeConditionsMixin' in config['mixins']
    hooks['tick_mixin_registered'] = 'EnhancedRecipeTickMixin' in config['mixins']
    result = {'scope':'编译后HK3的GTLCore、GTLAdditions及GTMThings直接类引用；增强版2.8.2调用点；不等于完整方法链接、Mixin实际应用、配方或游戏验证。',
              'direct_class_count':len(refs), 'references':refs, 'profiles':profiles, 'hooks':hooks,
              'game_launched':False, 'deployed':False}
    output = ROOT/args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'direct_class_count':len(refs), 'profiles':{k:{a:b for a,b in v.items() if a!='dependency_hashes'} for k,v in profiles.items()}, 'hooks':hooks}, ensure_ascii=False, indent=2))
    return int(any(p['missing_direct_classes'] for p in profiles.values()) or not all(hooks.values()))


if __name__ == '__main__':
    raise SystemExit(main())
