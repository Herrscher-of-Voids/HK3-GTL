from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_俯身撑墙操偶_F3_20261117'
LOG = ROOT/'logs/0005-theatre-f3-20261117'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', 'utf8')


def main():
    preview = json.loads((OUT/'预览记录.json').read_text('utf8'))
    manifest = json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest['giant_pose'] = preview['captures'][0]['giantPose']
    manifest['preview'] = dict(captures=len(preview['captures']), browser_errors=preview['errors'],
        reviewed=['俯身撑墙全貌', '正面敞开大厅', '侧面弯腰', '左右主手撑墙', '双人偶动作', '厅内仰视'])
    names = ['index.html', 'style.css', 'theatre.js', 'actors.js', 'viewer.bundle.js', '提线骨架.json',
             '演员色板.json', '演员整数格构件.npz', '整数格展开.json', '建筑改造.json', '剧情动作依据.json']
    manifest['files'] = {name: dict(bytes=(OUT/name).stat().st_size,
        sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest()) for name in names}
    save(OUT/'manifest.json', manifest)
    rules, backup = ROOT/'AGENTS.md', LOG/'before-memory.zip'
    original = rules.read_bytes()
    with ZipFile(backup, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(rules, 'AGENTS.md')
    with ZipFile(backup) as archive:
        restored = archive.read('AGENTS.md')
    if restored != original:
        raise OSError('规则压缩备份回读不一致')
    memory = '''

## 2026-11-17 对话0005：支配剧场F3俯身撑墙与正面敞开待审

- 负责人要求乌合之众弯腰俯视剧场、主臂双手搭左右墙、人偶采用剧情动作，并删除红笔标出的整面前墙。当前入口为`deliveries/0005_支配剧场_俯身撑墙操偶_F3_20261117/index.html`，F2及此前模型保留。
- 巨像根改为`(0,21,-850)`，腰轴原Y230×4，上身前倾65°，头追加8.4°；腿保留原姿。主臂按源Y289与150拆为上臂、含完整金球肘的前臂及手掌，两段长度274.197、496.161格；腕位`(±480,731,80)`，掌绕X90°，最低实体表面Y619接触左右墙沿顶面。浮空提线掌保留F2世界位置。
- 左人偶采用歪头曲肘垂腕，右人偶采用单臂高举与翻掌外展，依据24章剧情原帧B002/C003/C004/C025；参考图册为`deliveries/0005_千人人偶_剧情动作参考_F3_20261117/index.html`。悬吊与腿部动作属于本项目编排，十条线继续连接头顶、双腕、双膝，动作延迟0.18秒。
- 建筑数据实体删除`front_wall`与`front_gallery`两件，共3903946格；余33819628格、116构件。完整模式默认正面敞开，内部柱、红毯、双楼梯与F2屋顶开口保留；侧墙剖面仍可单独切换。
- 13张预览截图覆盖完整正面、侧面弯腰、左右撑墙、厅内仰视与两套人偶动作，浏览器错误0；上述画面已目视。回执`logs/0005-theatre-f3-20261117/completion.json`，规则修改前直接压缩备份为同目录`before-memory.zip`并完整回读。
- 当前为W11组合外观与动画待审候选。演员仍用原预览色板，正式结构、真实方块映射与游戏动画接入分别记录；本轮没有构建或安装JAR，W07停止决定及既有评分保持。
'''
    with rules.open('a', encoding='utf8') as handle:
        handle.write(memory)
    record = dict(completed_at=datetime.now(timezone.utc).isoformat(), candidate='F3',
        preview_url='http://127.0.0.1:9681/'+OUT.name+'/index.html',
        theatre=manifest['theatre'], giant_pose=manifest['giant_pose'], preview=manifest['preview'],
        files=manifest['files'], formal_machine_modified=False, jar_built=False,
        memory_backup=dict(path=str(backup.relative_to(ROOT)), original_bytes=len(original),
            compressed_bytes=backup.stat().st_size, original_sha256=hashlib.sha256(original).hexdigest()))
    save(LOG/'completion.json', record)
    print(json.dumps(dict(out=str(OUT), captures=len(preview['captures']), errors=preview['errors'])))


if __name__ == '__main__':
    main()
