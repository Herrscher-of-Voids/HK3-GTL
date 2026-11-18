# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W09_识律武器细节复刻_S2_20261116'
REF = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116'
LOG = ROOT / 'logs/0005-w09-weapons-details-s2-20261116'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    LOG.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
    refs = json.loads((REF / '参考清单.json').read_text('utf8'))
    captures = json.loads((OUT / '预览记录.json').read_text('utf8'))
    item = dict(candidate='W09识律武器细节复刻S2', updated_at=now, approved=False,
        preview=OUT.relative_to(ROOT).as_posix() + '/index.html',
        gallery=REF.relative_to(ROOT).as_posix() + '/index.html',
        reference_counts=refs['counts'],
        models=[dict(id=m['id'], size_xyz=m['sizeXYZ'], blocks=m['blocks'],
            nbt=m['nbt'], sha256=m['sha256']) for m in manifest['models']],
        total_blocks=sum(m['blocks'] for m in manifest['models']),
        method=manifest['modeling_method'], integer_voxels=True,
        changes=['匣体正背云火纹与太极、红色侧脊', '无金纹红黑宝剑与卷环三瓣护手',
            '长叶枪头、红X、卷叉和收腰颈', '九段收束链剑、八处红V及单柄'],
        status='四件独立外观候选待评审，W09整机改造后续设计。',
        evidence=LOG.relative_to(ROOT).as_posix() + '/completion.json')
    history = LOG / ('report-before-' + datetime.now().strftime('%H%M%S'))
    history.mkdir()
    for name in ['index.html', 'current-summary.json']:
        shutil.copy2(REPORT / name, history / name)
    summary = json.loads((REPORT / 'current-summary.json').read_text('utf-8-sig'))
    summary['current_work']['w09_weapons_details_s2_0005'] = item
    system = next(s for s in summary['systems'] if s['id'] == 'multiblocks')
    system['w09_weapons_details_s2_0005'] = item
    system['updated_at'] = now
    summary['report_updated_at'] = now
    html = (REPORT / 'index.html').read_text('utf8')
    notice = f'''<section class="notice" id="w09-weapons-details-s2-0005"><h2>0005 · 识律武器补充参考R2与细节方块稿S2</h2><p>新增16幅外网原图或视频帧、48幅官方公开MMD离线观察图，分别计数，旧39幅保留。按正背侧图重建匣体饰纹与侧脊、宝剑卷环护手、长枪分段枪头及九段收束链剑。4件共{item['total_blocks']:,}实体格，21幅三维预览已记录，外观待审。</p><p><a href="../../{item['preview']}">打开S2方块模型</a> · <a href="../../{item['gallery']}">打开补充参考图册</a> · <a href="../0005-w09-weapons-details-s2-20261116/completion.json">交付回执</a></p><p>默认静态相对比例约25.2格/MMD单位；游戏展开形态另有参考记录。W09整机、批准数量与系统评分保持。</p></section>'''
    html = re.sub(r'<section class="notice" id="w09-weapons-details-s2-0005">.*?</section>', '', html, flags=re.S)
    html = html.replace('<body>', '<body>' + notice, 1)
    html = re.sub(r'(?<=id="audit-data">).*?(?=</script>)',
        lambda _: json.dumps(summary, ensure_ascii=False).replace('<', '\\u003c'), html, flags=re.S)
    save(REPORT / 'current-summary.json', summary)
    (REPORT / 'index.html').write_text(html, 'utf8')
    record = dict(updated_at=now, delivery=item,
        preview=dict(captures=len(captures['captures']), errors=captures['errors'], failed=captures['failed']),
        status='独立参考与外观候选，未构建或安装JAR，未操作游戏或实例。',
        scores_changed=False, approval_count_changed=False, overall_percent=summary['overall_percent'],
        report_history=history.relative_to(ROOT).as_posix(),
        geometry_note='由截图轮廓与侧视投影重建体素截面，未直接导入官方网格；各部件保留默认静态形态。',
        official_assets='官方模型与原始贴图仅保留本地观察缓存，交付包含观察截图、原生方块模型与NBT。')
    save(LOG / 'completion.json', record)
    block = '''\n\n## 2026-11-16 对话0005：W09武器补充参考R2与细节复刻S2\n\n- 负责人要求继续找几十幅不同角度的清晰图补武器细节。R2入口 `deliveries/0005_W09_识律武器补充参考_R2_20261116/index.html`，新增16幅外网原图／视频帧及48幅官方公开MMD离线观察图，后者分30幅全形与18幅局部；来源与计数分别记录。旧39幅、局部裁图与联系图不重复计数。\n- S2入口 `deliveries/0005_W09_识律武器细节复刻_S2_20261116/index.html`。依据正背侧截图重建双面太极云火纹与红脊，撤除宝剑刃面金色菱纹，校准三瓣卷环护手、长叶枪头／红X／卷叉；链剑改为九段扁平斜片、八处红V与单柄的默认收束态。立绘的红片展开状态单列参考。\n- 四件统一尖端+Y，默认静态相对比例约25.2格/MMD单位。实际XYZ尺寸：匣体138×627×57、宝剑45×324×15、长枪59×552×23、链剑48×360×18，共1595921实体方块；均用真实整数格与原生像素方块贴图，官方网格和原始贴图只用于缓存观察。21幅三维预览与页面资源记录已保存。\n- S2为独立外观待审候选，S1保留历史，W09整机布局后续处理；W07继续停止。回执 `logs/0005-w09-weapons-details-s2-20261116/completion.json`。本次无JAR、安装或游戏操作，系统评分与批准数量保持。\n'''
    for name in ['AGENTS.md', 'rule/当前多方块设计规则.md']:
        with (ROOT / name).open('a', encoding='utf8') as handle:
            handle.write(block)
    for name in [Path(__file__).name, 'preview_senti_s2_20261116.mjs']:
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
    print(json.dumps(dict(models=4, blocks=item['total_blocks'], references=refs['counts'],
        overall_percent=summary['overall_percent']), ensure_ascii=False))


if __name__ == '__main__':
    main()
