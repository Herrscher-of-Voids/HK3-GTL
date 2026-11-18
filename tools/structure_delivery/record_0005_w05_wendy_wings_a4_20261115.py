from datetime import datetime
from pathlib import Path
import hashlib
import json


root = Path(__file__).resolve().parents[2]
delivery = 'deliveries/0005_W05_温蒂风翼渴望之心_A4原作翼形_20261115'
log_path = 'logs/0005-w05-wendy-wings-a4-20261115'
out, log = root / delivery, root / log_path
manifest = json.loads((out / 'manifest.json').read_text('utf8'))
capture = json.loads((log / 'preview-capture.json').read_text('utf8'))
clearance = manifest['geometry_clearance']
baselines = []
for version, folder in [('a2', '0005_W05_温蒂风翼渴望之心_A2_20261115'),
    ('a3', '0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115')]:
    name = f'geometry_0005_w05_wendy_wings_{version}_20261115.py'
    current = hashlib.sha256((root / 'tools/structure_delivery' / name).read_bytes()).hexdigest()
    archived = hashlib.sha256((root / 'deliveries' / folder / '生成脚本' / name).read_bytes()).hexdigest()
    baselines.append(dict(source=name, sha256=current, archived_source_preserved=current == archived))
receipt = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
    conversation='0005', conversation_id=manifest['conversation_id'], candidate='A4原作翼形重构',
    previous_candidate='A3扩展基座', preview=delivery + '/三维评审.html',
    size_wdh=manifest['size_wdh'], block_count=manifest['block_count'],
    geometry_clearance=clearance, inherited_source_files=baselines,
    screenshots=len(capture['screenshots']) + 1,
    visually_reviewed=['整体预览.png', '正面预览.png', '侧面预览.png', '背面预览.png',
        '俯视预览.png', '风翼近景.png', '翼根近景.png'],
    browser_errors=capture['errors'], failed_requests=capture['failed'],
    appearance_approved=False, runtime_blueprint_modified=False,
    jar_built=False, installed=False, desktop_used=False, game_verified=False,
    acceptance_score_changed=False)
(log / 'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', 'utf8')
entry = f'''

## 2026-11-15 对话0005：W05 A4原作翼形几何重构候选

- 负责人明确要求“改建筑几何”。本轮移除旧十四片等距白边羽板与两根粗翼骨，按游戏原帧校准重做左右成对、集中翼根、后掠且外缘不规则分叉的宽薄青绿翼面；新增两座收拢的后置翼根投射器。具体方块比例、尖齿、内置光线与投射设施是建筑转译，不宣称官方源模型复刻。
- A3的1001×841三层基座和其余宝石、约束轨、回流槽、泵、光带、风车、前控台均保留原函数与蓝图坐标；共19个继承构件，A2/A3源文件及旧候选保持。当前独立预览：`{delivery}/三维评审.html`。
- 实际整机宽{manifest['size_wdh'][0]}×深{manifest['size_wdh'][1]}×高{manifest['size_wdh'][2]}格、{manifest['block_count']:,}方块、{clearance['independent_components']}构件。全部{clearance['checked_component_pairs']}对独立构件体素交叠0，两翼各自六向连通分量为{[w['six_connected_components'] for w in clearance['wings']]}；上部投影超出顶层基座0列，最窄外沿余量{clearance['base_projection']['minimum_projected_border_margin_voxels']}格。
- 完整NBT/Schematic由同一最终方块数组导出；{len(capture['screenshots']) + 1}幅headless截图完成，浏览器错误与请求失败均0。外观仍待评审，未替换运行蓝图、未构建或安装JAR、未运行游戏，不增加评分或批准数。回执：`{log_path}/completion.json`。
'''
for path in [root / 'AGENTS.md', root / 'rule/当前多方块设计规则.md']:
    with path.open('a', encoding='utf8', newline='') as handle:
        handle.write(entry)
print(json.dumps(dict(receipt=str(log / 'completion.json'), baseline_sources_preserved=
    all(item['archived_source_preserved'] for item in baselines)), ensure_ascii=False))
