from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_支配剧场_提线共演_F1_20261117'
LOG = ROOT/'logs/0005-theatre-f1-20261117'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    preview = json.loads((OUT/'预览记录.json').read_text('utf8'))
    manifest = json.loads((OUT/'manifest.json').read_text('utf8'))
    files = ['index.html', 'style.css', 'actors.js', 'viewer.bundle.js', '提线骨架.json', '演员色板.json', '演员整数格构件.npz']
    record = dict(completed_at=datetime.now(timezone.utc).isoformat(), candidate='F1',
        preview_url='http://127.0.0.1:9681/'+OUT.name+'/index.html',
        actor_blocks=manifest['actor_blocks'], captures=len(preview['captures']), browser_errors=preview['errors'],
        visual_review=['剧场全貌', '正面组合', '左手与提线', '演员共演', '双人偶姿态'],
        animation=dict(hands=2, puppets=2, strings=10, delay_seconds=.18, targets=['头顶', '双腕', '双膝']),
        formal_machine_modified=False, jar_built=False,
        files={name: dict(bytes=(OUT/name).stat().st_size, sha256=digest(OUT/name)) for name in files})
    manifest['preview'] = dict(captures=record['captures'], browser_errors=record['browser_errors'], record='预览记录.json')
    manifest['files'] = record['files']
    (OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', 'utf8')
    (LOG/'completion.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    rules = ROOT/'AGENTS.md'
    backup = LOG/'before-memory.zip'
    with ZipFile(backup, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(rules, 'AGENTS.md')
    with ZipFile(backup) as archive:
        preserved = archive.read('AGENTS.md')
    record['memory_backup'] = dict(path=str(backup.relative_to(ROOT)), original_bytes=len(preserved),
        compressed_bytes=backup.stat().st_size, original_sha256=hashlib.sha256(preserved).hexdigest())
    memory = '''

## 2026-11-17 对话0005：支配剧场F1提线共演待审

- 负责人要求乌合之众位于支配剧场中央，双手各用丝线操纵一只千人人偶。F1入口为`deliveries/0005_支配剧场_提线共演_F1_20261117/index.html`，复用T2剧情大厅，保留P3乌合之众与D2剧情版人偶的原型及色板。
- P3按0.68重新采样，1683182格，根位置`(0,21,300)`；D2按0.25重新采样，每只11117格，两实例根位置`(-252,90,420)`与`(246,90,420)`。所有演员构件仍为一格立方体，动态绕关节旋转。原P3十只悬浮手保留，F03与F08作为两只提线手。
- 十条金色细丝由指尖连接人偶头顶、双腕与双膝。手的提拉、翻腕与倾转驱动对应人偶，延迟0.18秒；人偶躯干、头、双臂与双膝联动。网页支持播放暂停、时间拖动、速度、剖面、分组与近景，挂点每帧按世界矩阵更新。
- 演员模板、原色板与提线骨架分别保存为NPZ和JSON；网页复用T2建筑数据及NBT。演员`pixel:*`为预览色板，真实方块映射、W11正式结构和游戏动画接入继续独立制作。本轮组合外观待审，没有构建或安装JAR。
- 31张预览截图覆盖0、2、5、9、13秒及六组视角，浏览器错误0；已目视剧场全貌、正面、左侧提线、演员组合及双人偶。回执`logs/0005-theatre-f1-20261117/completion.json`，规则修改前直接压缩备份为同目录`before-memory.zip`。W07停止决定及既有评分保持。
'''
    with rules.open('a', encoding='utf8') as handle:
        handle.write(memory)
    (LOG/'completion.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print(json.dumps(dict(captures=record['captures'], errors=record['browser_errors'], completion=str(LOG/'completion.json'))))


if __name__ == '__main__':
    main()
