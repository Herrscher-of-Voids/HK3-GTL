from datetime import datetime
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-ae-nexus-integration-a1-20261114'
OUT = ROOT / 'deliveries/0005_万象天枢_A1接入_20261114'
VERSION = '0.5.0-AENexusA1-r1'
JAR = '0005多方块设计-' + VERSION + '.jar'
RESOURCE = 'data/hk3gtl/structures/ae_nexus_a1.nbt'
SOURCES = ['src/main/java/com/sirin/hk3gtl/common/machine/ae/Hk3NexusStructure.java',
           'src/main/java/com/sirin/hk3gtl/common/machine/ae/Hk3NexusMachines.java',
           'src/main/java/com/sirin/hk3gtl/common/multiblock/build/Hk3BuildPlans.java',
           'src/main/java/com/sirin/hk3gtl/common/integration/FtbQuestsIntegration.java',
           'src/main/resources/' + RESOURCE,
           'src/main/resources/assets/hk3gtl/lang/zh_cn.json',
           'src/main/resources/assets/hk3gtl/lang/en_us.json',
           'src/main/resources/assets/hk3gtl/ftbquests/chapters/hk3_story_01.snbt',
           'tools/quest_tutorial.py', 'tools/generate_quest_catalog.py']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'build/libs' / JAR, OUT / JAR)
    shutil.copy2(ROOT / 'deliveries/0005_万象天枢_三位一体取形_A1_20261114/前右预览.png', OUT / '外观.png')
    with zipfile.ZipFile(OUT / JAR) as jar:
        resource_hash = hashlib.sha256(jar.read(RESOURCE)).hexdigest()
        classes = [jar.getinfo('com/sirin/hk3gtl/common/machine/ae/' + name + '.class').filename
                   for name in ('Hk3NexusStructure', 'Hk3NexusMachines')]
    record = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
        conversation='0005', conversation_id='01a1d6b8-bd81-79d3-a6f4-4f590806cc8e',
        version=VERSION, jar=str((OUT / JAR).relative_to(ROOT)), jar_sha256=hashlib.sha256((OUT / JAR).read_bytes()).hexdigest(),
        size_wdh=[35, 35, 33], total_blocks=6733, shell_blocks=6732, controller_xyz=[17, 3, 2], controller_facing='north',
        appearance_approved=True, pattern_implemented=True, jei_shape_implemented=True, builder_implemented=True,
        structure_resource=RESOURCE, packaged_resource_sha256=resource_hash, packaged_classes=classes,
        build=dict(command="gradlew.bat build -x check -x test -x renameToChinese --offline --console=plain -Parchives_base_name=0005多方块设计 -Pmod_version=" + VERSION,
            succeeded=True, log='logs/0005-ae-nexus-integration-a1-20261114/build.log'),
        source_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES},
        quest='开创者赠送主控1及全部6732外壳；保留主控奖励ID；外壳奖励按物品ID使用新身份，旧铁／玻璃领取状态不拦新材料',
        integration='Pattern、JEI、统一建造器同用完整A1蓝图；空域允许空气、AE线缆及自然雪层；原AE能力和准入生命周期保持',
        compatibility='旧3×3×3占位外壳不再满足新Pattern，需要按A1完整重建；现有主控ID保持',
        installed=False, game_started=False, game_verified=False, automated_tests_run=False,
        parallel_build_scope='本包来自本轮构建时的共享工作区，不宣称包括其他并行对话尚未完成或尚未写入的更新')
    text = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    (LOG / 'completion.json').write_text(text, 'utf8')
    (OUT / 'completion.json').write_text(text, 'utf8')
    (OUT / 'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>万象天枢A1 · 0005结构接入</title>
<style>body{{background:#121523;color:#e3e7f3;font:16px/1.8 "Microsoft YaHei";max-width:1200px;margin:30px auto;padding:20px}}a{{color:#a7caff}}img{{width:100%}}</style>
<h1>万象天枢A1 · 0005结构接入</h1>
<p>外观已批准，正式结构为宽35×深35×高33、6733方块。主控沿用 hk3gtl:ae_nexus，位于(17,3,2)，源朝北。</p>
<img src="外观.png" alt="已批准的万象天枢A1方块预览">
<p>原生GT成型Pattern、JEI完整预览、统一建造蓝图共用同一份A1资源。任务赠送主控及6732外壳；旧占位3×3×3结构需按完整蓝图重建。</p>
<p><a href="{JAR}">{JAR}</a> · <a href="completion.json">构建与来源回执</a> · <a href="../0005_万象天枢_三位一体取形_A1_20261114/三维评审.html">A1交互外观原件</a></p>
<p>构建通过。未安装到实例、未启动游戏、未进行实机成型或运行验收；保留原验收分数。交互原件中的未批准状态是生成时的历史标注，本页及外观批准归档记录本次决定。</p>
<p>SHA256：{record['jar_sha256']}</p></html>''', 'utf8')
    print(json.dumps(dict(jar=str(OUT / JAR), sha256=record['jar_sha256'], completion=str(LOG / 'completion.json')), ensure_ascii=True))


if __name__ == '__main__':
    main()
