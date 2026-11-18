"""修订74配色生成器：直接读取GT/GTL原图，只替换RGB色相和饱和度。

变更记录 #1：按负责人纠正，取消自行重绘；原图像素位置、明度、透明度、
帧数和动画原样保留。RAM低饱和像素另行着色，避免旧导出全数等同原图。
输入为指定实例GTCEu JAR与KubeJS原资产，输出原有模型引用路径和校验清单。
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import colorsys
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw
from revision74_support import RES, LOG, save_json
from generate_electronic_art74 import backup

INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')
PLATFORMS = ['honkai_lattice', 'quantum_coherence', 'imaginary_topology', 'civilization_endurance']
COLORS = ['#A45BDA', '#22BCD2', '#EBA630', '#DC456F']
FAMILY_COLORS = ['#A45BDA', '#CC68F1', '#22BCD2', '#4784EA', '#EBA630', '#BFD57E', '#DC456F']
ORIGINALS = [('gtceu', 'nano'), ('gtceu', 'quantum'), ('gtceu', 'crystal'), ('gtceu', 'wetware'),
             ('kubejs', 'bioware'), ('kubejs', 'optical'), ('kubejs', 'supracausal')]
FORMS = ['processor', 'assembly', 'computer', 'mainframe']


def colorize(original, color, ram=False):
    rgb = tuple(int(color[n:n+2], 16) / 255 for n in (1, 3, 5))
    hue, saturation, _ = colorsys.rgb_to_hsv(*rgb)
    output = original.copy()
    changed = 0
    for y in range(original.height):
        for x in range(original.width):
            r, g, b, a = original.getpixel((x, y))
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # RAM原图近灰的硅片也需着色；其余资产保留无彩色金属针脚与高光。
            if (ram and v > .25) or s > .12:
                rgb2 = colorsys.hsv_to_rgb(hue, max(s, saturation * .85), v)
                pixel = tuple(round(c * 255) for c in rgb2) + (a,)
                output.putpixel((x, y), pixel)
                changed += pixel != (r, g, b, a)
    return output, changed


def _unconfirmed_full_catalog():
    stamp = datetime.now().astimezone().isoformat(timespec='seconds')
    jar_path = INSTANCE / 'mods/gtceu-1.20.1-1.4.4.jar'
    jar = zipfile.ZipFile(jar_path)
    entries = []

    def convert(item_id, namespace, source_name, color, ram=False):
        resource = f'assets/{namespace}/textures/item/{source_name}.png'
        if namespace == 'gtceu':
            source = jar.read(resource)
            meta = jar.read(resource + '.mcmeta') if resource + '.mcmeta' in jar.namelist() else None
            provenance = str(jar_path) + '!/' + resource
        else:
            source_path = INSTANCE / 'kubejs' / resource
            source = source_path.read_bytes()
            metadata = source_path.with_suffix('.png.mcmeta')
            meta = metadata.read_bytes() if metadata.exists() else None
            provenance = str(source_path)
        original = Image.open(BytesIO(source)).convert('RGBA')
        im, changed = colorize(original, color, ram)
        assert changed > 0, f'原图未发生配色变化：{item_id}'
        assert original.getchannel('A').tobytes() == im.getchannel('A').tobytes()
        assert [max(p[:3]) for p in original.getdata()] == [max(p[:3]) for p in im.getdata()]
        model_path = RES / f'assets/hk3gtl/models/item/{item_id}.json'
        model = json.loads(model_path.read_text('utf-8'))
        path = RES / ('assets/hk3gtl/textures/' + model['textures']['layer0'].split(':')[1] + '.png')
        backup(path)
        im.save(path)
        target_meta = path.with_suffix('.png.mcmeta')
        if meta is not None:
            backup(target_meta)
            target_meta.write_bytes(meta)
        elif target_meta.exists():
            # 不删除历史文件；无动画来源明确只播放第零帧。
            save_json(target_meta, {'animation': {'frametime': 20, 'frames': [0]},
                '_comment_revision74': f'变更记录 #2 {stamp}：来源原图无动画，保留元数据文件但仅使用零帧。'})
        history = model.setdefault('_history', [])
        if not any('原图换色' in h for h in history):
            history.append(f'变更记录 #4 {stamp} 内测5修订74：撤回自行重画，采用GT/GTL原图换色；像素布局、明度及透明度不变，按来源恢复动画。')
        save_json(model_path, model)
        entries.append({'id': item_id, 'source': provenance, 'source_sha256': hashlib.sha256(source).hexdigest(),
                        'destination': path.relative_to(RES).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'color': color, 'size': list(im.size), 'changed_pixels': changed, 'alpha_preserved': True,
                        'value_preserved': True, 'animation_preserved': meta is not None})
        return im.crop((0, 0, im.width, im.width))

    circuits = json.loads((RES/'data/hk3gtl/catalog/circuit_series.json').read_text('utf-8'))['entries']
    families = list(dict.fromkeys(e['family'] for e in circuits))
    sheet = Image.new('RGB', (512, 896), (24, 27, 34))
    for entry in circuits:
        index = families.index(entry['family'])
        namespace, family = ORIGINALS[index]
        form = FORMS[entry['form']]
        name = family + ('_processor_' + form if namespace == 'gtceu' and form != 'processor' else '_' + form)
        # GT的主机后缀为processor_mainframe，其余名称同样以原文件为准。
        im = convert(entry['id'], namespace, name, FAMILY_COLORS[index])
        preview = im.resize((112, 112), Image.Resampling.NEAREST)
        sheet.paste(preview, (entry['form'] * 128 + 8, index * 128 + 8), preview)
    sheet.save(LOG/'circuits-original-recolored.png')
    sheet = Image.new('RGB', (512, 256), (24, 27, 34))
    for index, platform in enumerate(PLATFORMS):
        for j, part in enumerate(['ram_wafer', 'ram_chip']):
            # 采用同一对GT原始晶圆/切片，四平台只换配色，保留其原生切割关系。
            im = convert(platform + '_' + part, 'gtceu', part, COLORS[index], ram=True)
            preview = im.resize((112, 112), Image.Resampling.NEAREST)
            sheet.paste(preview, (index * 128 + 8, j * 128 + 8), preview)
    sheet.save(LOG/'ram-original-recolored.png')
    platform_families = ['wetware', 'optical', 'exotic', 'supracausal']
    new_sources = {'dielectric_film': 'carbon_fiber_plate', 'interconnect_mesh': 'carbon_fiber_mesh',
                   'epitaxial_wafer': 'neutronium_wafer', 'logic_wafer': 'nano_cpu_wafer',
                   'logic_die': 'nano_cpu_chip', 'smd_array': 'highly_advanced_soc'}
    parts_zh = {'dielectric_film': '介电隔离膜', 'interconnect_mesh': '定向互连网',
                'epitaxial_wafer': '外延晶圆', 'logic_wafer': '逻辑晶圆', 'logic_die': '逻辑裸片', 'smd_array': '贴片功能阵列'}
    parts_en = {'dielectric_film': 'Dielectric Film', 'interconnect_mesh': 'Oriented Interconnect Mesh',
                'epitaxial_wafer': 'Epitaxial Wafer', 'logic_wafer': 'Logic Wafer', 'logic_die': 'Logic Die', 'smd_array': 'SMD Functional Array'}
    platform_zh = ['崩坏晶格', '量子相干', '虚数拓扑', '文明存续']
    platform_en = ['Honkai Lattice', 'Quantum Coherence', 'Imaginary Topology', 'Civilization Endurance']
    languages = {language: json.loads((RES/f'assets/hk3gtl/lang/{language}.json').read_text('utf-8'))
                 for language in ['zh_cn', 'en_us']}
    for index, platform in enumerate(PLATFORMS):
        for part, source in new_sources.items():
            item_id = platform + '_' + part
            model_path = RES/f'assets/hk3gtl/models/item/{item_id}.json'
            if not model_path.exists():
                save_json(model_path, {'_comment': f'变更记录 #1 {stamp} 修订74：高阶电子工序半成品，直接复用GT原图配色。',
                    'parent': 'minecraft:item/generated', 'textures': {'layer0': 'hk3gtl:item/electronics/' + item_id}})
            convert(item_id, 'gtceu', source, COLORS[index], ram=True)
            languages['zh_cn']['item.hk3gtl.' + item_id] = platform_zh[index] + parts_zh[part]
            languages['en_us']['item.hk3gtl.' + item_id] = platform_en[index] + ' ' + parts_en[part]
        for part in ['circuit_substrate', 'printed_circuit_board']:
            suffix = 'circuit_board' if part == 'circuit_substrate' else part
            source = platform_families[index] + '_' + suffix
            convert(platform + '_' + part, 'gtceu' if index == 0 else 'kubejs', source, COLORS[index], ram=True)
        for part in ['smd_capacitor','smd_diode','smd_resistor','smd_transistor','smd_inductor']:
            convert(platform + '_' + part, 'gtceu', 'advanced_' + part, COLORS[index], ram=True)
        cpu_source = ['nano_cpu_chip','qbit_cpu_chip','crystal_cpu','highly_advanced_soc'][index]
        convert(platform + '_cpu', 'gtceu', cpu_source, COLORS[index], ram=True)
    for language, data in languages.items():
        data['_comment_revision74_parts'] = f'变更记录 #1 {stamp}：新增24种确有工艺用途的中间体名称；保留原40件物品。'
        save_json(RES/f'assets/hk3gtl/lang/{language}.json', data)
    jar.close()
    save_json(RES/'data/hk3gtl/catalog/electronic_art74.json', {
        'revision': 74, 'generated_at': stamp,
        'changes': '变更记录 #2：按负责人纠正，取消重绘；直接使用GT/GTL原图换色。七个电路系列选择不同原版技术底图，RAM保留GT原始晶圆和切片对应关系。',
        'entries': entries})
    catalog_path = RES/'data/hk3gtl/catalog/gt_circuit_assets.json'
    catalog = json.loads(catalog_path.read_text('utf-8'))
    if catalog['revision'] != 74:
        catalog.setdefault('history', []).append({k: v for k, v in catalog.items() if k != 'history'})
    catalog.update({'revision': 74, 'generated_at': stamp, 'entries': entries,
                    'changes': '变更记录 #2：采用GT/GTL不同原版系列图形换色；保留像素布局、明度和透明度，恢复来源动画。新增24个工序中间体原图资源。'})
    save_json(catalog_path, catalog)
    print(json.dumps({'written': len(entries), 'original_alpha_and_value_checks': len(entries),
                      'distinct_ram_files': len(set(e['sha256'] for e in entries if '_ram_' in e['id']))}))


def main():
    # 变更记录 #2：负责人确认基板/RAM轮用和B整体染色；电路板待定，默认入口仅处理已确认的12张图。
    from apply_confirmed_parts74 import main as apply_confirmed
    apply_confirmed()


if __name__ == '__main__':
    main()
