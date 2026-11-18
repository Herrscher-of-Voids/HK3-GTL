from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_外置巨像操偶_F2_20261117'
LOG = ROOT/'logs/0005-theatre-f2-20261117'


def main():
    preview = json.loads((OUT/'预览记录.json').read_text('utf8'))
    manifest = json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['notes'][0] = '巨像位于剧场后方外侧，本体采用P3四倍整数格展开，身高1780格。'
    names = ['index.html', 'style.css', 'theatre.js', 'actors.js', 'viewer.bundle.js', '提线骨架.json',
             '演员色板.json', '演员整数格构件.npz', '整数格展开.json', '屋顶改造.json']
    manifest['files'] = {name: dict(bytes=(OUT/name).stat().st_size,
        sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest()) for name in names}
    manifest['preview'] = dict(captures=len(preview['captures']), browser_errors=preview['errors'],
        reviewed=['巨像与剧场', '正面操偶全景', '厅内仰视', '左侧平掌与长线', '两掌俯视', '厅顶敞口'])
    (OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', 'utf8')
    rules = ROOT/'AGENTS.md'
    backup = LOG/'before-memory.zip'
    with ZipFile(backup, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(rules, 'AGENTS.md')
    with ZipFile(backup) as archive:
        preserved = archive.read('AGENTS.md')
    memory = '''

## 2026-11-17 对话0005：支配剧场F2外置巨像操偶待审

- 负责人修正F1构图：乌合之众应在整个剧场外部放得巨大，两只手平放在剧场上方，提线垂吊两只人偶，强化压迫感与操纵感。当前入口为`deliveries/0005_支配剧场_外置巨像操偶_F2_20261117/index.html`；F1作为历史组合保留。
- 巨像根`(0,21,-1000)`，P3本体八构件按4倍整数展开，每个源格对应4×4×4单位格；本体宽1684、高1780，后方Z范围-1172..-733，与剧场后墙有244格净距。两个同源舒展平掌采用左右镜像和整数轴变换，掌心向下、指尖朝+Z，3倍单位格展开；掌位`(±235,800,20)`，腕枢轴在`(±235,800,-49)`。
- 两只D2人偶按0.4重新采样，脚根`(-235,70,230)`与`(235,70,230)`，高约154格。十条金色长丝连接指尖、头顶、双腕和双膝，手提拉、轻翻和倾转驱动人偶延迟0.18秒扭动。
- T2顶棚实体在X[-390,390]、Z[-100,430]范围开口，移除2379214格、净增11119格外侧奶白细金收边；建筑剩37723574格。剖面观察仅另隐藏前围护与左墙，开口外围顶棚实际保留。巨像、手和人偶沿原色板，建筑沿原GT/HK/原版材质。
- `theatre.js`保存开口建筑表面；巨像用原P3整数体素与展开规则压缩描述，平掌和人偶构件单独保存NPZ，避免生成3亿格展开数组。46张截图覆盖9组视角及0/2/5/9/13秒，浏览器错误0；已目视全景、厅内仰视、平掌、长线和顶棚开口。回执`logs/0005-theatre-f2-20261117/completion.json`，规则修改前直接压缩备份为同目录`before-memory.zip`。
- F2为W11组合动态待审稿，演员`pixel:*`仍为预览色板。正式W11结构、真实方块映射、游戏动画接入与JAR交付继续独立记录；本轮没有构建或安装JAR，W07停止决定及既有评分保持。
'''
    with rules.open('a', encoding='utf8') as handle:
        handle.write(memory)
    record = dict(completed_at=datetime.now(timezone.utc).isoformat(), candidate='F2',
        preview_url='http://127.0.0.1:9681/'+OUT.name+'/index.html', preview=manifest['preview'],
        theatre=manifest['theatre'], rig=manifest['rig'], giant_bounds=manifest['giant_bounds'],
        formal_machine_modified=False, jar_built=False, files=manifest['files'],
        memory_backup=dict(path=str(backup.relative_to(ROOT)), original_bytes=len(preserved),
            compressed_bytes=backup.stat().st_size, original_sha256=hashlib.sha256(preserved).hexdigest()))
    (LOG/'completion.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print(json.dumps(dict(captures=record['preview']['captures'], errors=record['preview']['browser_errors'])))


if __name__ == '__main__':
    main()
