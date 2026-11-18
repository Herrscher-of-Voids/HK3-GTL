from datetime import datetime
from html import escape
import json
from pathlib import Path
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from package_0005_w11_author_blueprint_20261117 import ROOT, OUT, LOG, digest, save


geometry = json.loads((OUT / 'geometry.json').read_text('utf8'))
preview = json.loads((OUT / '预览记录.json').read_text('utf8'))
readback = json.loads((OUT / 'NBT回读.json').read_text('utf8'))
now = datetime.now().astimezone()
images = [('整体预览.png', '完整机械剧场'), ('剧场剖面.png', '前半回廊剖开展示，方块文件保留完整结构'),
    ('木偶近景.png', '中央六臂机械木偶'), ('机舱近景.png', '三圈五层与内向面具'), ('像素近景.png', '原生像素方块'),
    ('冷却井近景.png', '深渊冷却井与八向基座'), ('主控近景.png', '舞台中心唯一红石主控定位'), ('运行预览.png', '红金提线信号与天幕全息粒子')]
gallery = ''.join(f'<figure><img loading="lazy" src="{file}" alt="{escape(label)}"><figcaption>{escape(label)}</figcaption></figure>' for file, label in images)
html = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>W11 A1 方块图集</title><style>
body{{margin:0;background:#15151a;color:#e7e3dc;font:15px/1.8 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1500px;margin:32px auto;padding:0 24px}}a{{color:#e8be65}}h1{{font-size:27px;margin-bottom:5px}}p{{color:#c4bcb0}}figure{{margin:24px 0;border:1px solid #494035;background:#202126}}img{{display:block;width:100%}}figcaption{{padding:8px 14px;color:#d6c59d}}.note{{padding:14px 18px;border-left:3px solid #a87c42;background:#292128}}small{{color:#a9a49d}}</style><main>
<small>0005 多方块设计 / 作者蓝图 A1 / 外观待审</small><h1>W11 支配之律者·千律·分布式工业统御阵</h1>
<p>1000×1000×311 · {geometry['blocks']:,} 个实体方块 · 1000座机舱 · 188构件 · 12种已有方块</p>
<p><a href="index.html">打开交互三维预览</a> · <a href="sources.json">官方依据与作者设计</a> · <a href="conflicts.json">坐标取样与规则冲突</a> · <a href="manifest.json">完整文件记录</a></p>
<p>三圈回廊按每层40／64／96舱排成5层。750条深红提线、250条金色提线连接舱顶与天幕。六臂木偶胸部保留红金球心和三层分半径机械框。</p>
<p>唯一主控源坐标(-1,190,-1)，归一化坐标(499,190,499)，位于舞台中心。红石块用于预览定位。其余全部实体格可自由替换合法通用接口。</p>
<div class="note">作者指定尺寸与黑白金红配色保留。占地高于既有CEV比较值；包围盒、高度、实体数量与材料种类存在递增规则冲突，专项例外与外观均待审。网页粒子、呼吸光与全息环属于运行演示。</div>
{gallery}<p>完整NBT与归一化逐格模型已生成。正式W11仍沿用待完成结构Pattern；本轮交付为作者蓝图候选。</p></main></html>'''
(OUT / '评审图集.html').write_text(html, 'utf8')
backup = LOG / 'prior-rules.zip'
rules = [ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']
before = {str(path.relative_to(ROOT)): dict(bytes=path.stat().st_size, sha256=digest(path)) for path in rules}
with ZipFile(backup, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
    for path in rules:
        archive.write(path, str(path.relative_to(ROOT)))
with ZipFile(backup) as archive:
    archive_ok = archive.testzip() is None and all(archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes() for path in rules)
if not archive_ok:
    raise RuntimeError('规则压缩备份回读不一致')
entry = f'''

## 2026-11-17 对话0005：W11千律机械剧场作者蓝图A1待审

- 负责人提供W11作者蓝图。本轮入口为`deliveries/{OUT.name}/index.html`，静态图集`评审图集.html`；实际宽深高1000×1000×311，X/Z=-500..499、Y=0..310，{geometry['blocks']}个去重实体方块、188分件、12种已有GT/HK/原版方块，全部使用真实整数格与原生像素贴图。
- 三圈机舱中心R212/320/440，竖向5层，各层40/64/96座，恰好1000舱；Y底46/69/92/115/138，每舱15×15×20。R200解释为内回廊边缘；750条深红与250条金色提线采用分层外半径避让，保留1000个独立舱端连接。八座150×150×45梯形基座按22.5度错位八向布置。
- 中央倒八角舞台、六臂五指机械木偶、R15红金胸核与R20/24/28分层框、顶层50格厚十字控制架及外接环完整生成。主控红石定位源坐标`(-1,190,-1)`、归一化`(499,190,499)`、朝南；仅该主控位置固定，其余全部实体格可自由替换合法通用接口。
- 网页包含天幕显隐、前半回廊剖开、XYZ剖切、分组、待机/运行/暂停与1000条信号粒子；NBT保留完整固定实体。12张网页截图错误与请求失败均0，已目视整体、剧场剖面、木偶、机舱、像素与主控；NBT回读{readback['nbt_blocks']}格与NPZ坐标全部对应。
- 官方聚合人偶、机械关节、细指、提线与剧场来源见`sources.json`。半身六臂、黑白甲、红金丝线、十字天幕与工业机构为负责人作者设计，不冒充官方原型。
- 沿用正式身份`w11_distributed_industrial_command`、CEV/Tier30与RN-DIO。作者指定尺寸及配色保留；相对既有CEV比较baseline，占地通过，包围盒311000000<441313404、高311<636、实体{geometry['blocks']}<23541415、种类12<58，电压机壳主导亦待专项决定；W09的34种例外不套用W11。
- A1外观与专项规则冲突均待审，未新增批准或计分；正式W11待完成Pattern、生产源码与配方保持。本轮没有构建或安装JAR、启动游戏或进行游戏验收。独立回执`logs/{LOG.name}/completion.json`。W07停止决定保持。
'''
for path in rules:
    with path.open('a', encoding='utf8') as handle:
        handle.write(entry)
for name in ['prepare_0005_w11_viewer_20261117.py', Path(__file__).name]:
    shutil.copy2(ROOT / 'tools/structure_delivery' / name, OUT / '生成脚本' / name)
files = [path for path in OUT.rglob('*') if path.is_file() and path.name != 'manifest.json']
manifest = dict(machine='W11', candidate='A1', conversation='0005', conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
    status='作者蓝图完整方块预览待审', updated_at=now.isoformat(), actual_size_wdh=geometry['actual_size_wdh'],
    blocks=geometry['blocks'], cabin_count=1000, unique_block_types=12, controller=geometry['controller'],
    scale_comparison=geometry['scale_comparison'], files={str(path.relative_to(OUT)): dict(bytes=path.stat().st_size, sha256=digest(path)) for path in files})
save(OUT / 'manifest.json', manifest)
save(LOG / 'completion.json', dict(recorded_at=now.isoformat(), machine='W11', candidate='A1', status='外观与专项规则冲突待审',
    entry=str(OUT / 'index.html'), gallery=str(OUT / '评审图集.html'), actual_size_wdh=geometry['actual_size_wdh'], blocks=geometry['blocks'],
    materials=12, cabins=1000, parts=188, surface_quads=geometry['surface_quads'], nbt_readback=readback, screenshots=len(preview['captures']),
    page_errors=preview['errors'], failed_requests=preview['failed'], scale_comparison=geometry['scale_comparison'],
    manifest_sha256=digest(OUT / 'manifest.json'), backup=dict(path=str(backup), bytes=backup.stat().st_size, sha256=digest(backup),
        verified=archive_ok, original_files=before, original_total_bytes=sum(item['bytes'] for item in before.values())),
    appearance_approved=False, scores_changed=False, game_code_modified=False, jar_built=False, installed=False, game_verified=False))
print(json.dumps(dict(status='W11 A1待审预览已完成', blocks=geometry['blocks'], files=len(files), backup_verified=archive_ok), ensure_ascii=False))
