from datetime import datetime
from pathlib import Path
import hashlib
import json


root = Path(__file__).resolve().parents[2]
delivery = 'deliveries/0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115'
log_path = 'logs/0005-w05-wendy-wings-a3-20261115'
out, log = root/delivery, root/log_path
manifest = json.loads((out/'manifest.json').read_text('utf8'))
capture = json.loads((log/'preview-capture.json').read_text('utf8'))
clearance = manifest['geometry_clearance']
base = clearance['base_projection']
source = 'geometry_0005_w05_wendy_wings_a2_20261115.py'
original = root/'deliveries/0005_W05_温蒂风翼渴望之心_A2_20261115/生成脚本'/source
current = root/'tools/structure_delivery'/source
source_preserved = hashlib.sha256(original.read_bytes()).hexdigest() == hashlib.sha256(current.read_bytes()).hexdigest()
receipt = dict(created_at=datetime.now().astimezone().isoformat(timespec='seconds'),
    conversation='0005', conversation_id=manifest['conversation_id'], candidate='A3扩展基座',
    previous_candidate='A2', upper_source_preserved=source_preserved,
    preview=delivery+'/三维评审.html', size_wdh=manifest['size_wdh'], block_count=manifest['block_count'],
    geometry_clearance=clearance, screenshots=10,
    visually_reviewed=['整体预览.png', '正面预览.png', '侧面预览.png', '俯视预览.png'],
    browser_errors=capture['errors'], failed_requests=capture['failed'],
    appearance_approved=False, runtime_blueprint_modified=False, jar_built=False,
    installed=False, desktop_used=False, game_verified=False, acceptance_score_changed=False)
(log/'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', 'utf8')
entry = f'''

## 2026-11-15 对话0005：W05 A3扩展三层基座候选

- 负责人指出A2底座过小，要求扩大。本轮仅更换基座：顶层941×781、中层971×811、底层1001×841格；顶面保持蓝图Y=11，新厚度向下延伸至Y=-24。宝石、风翼、风车与全部上部机组保留A2原函数及原蓝图坐标；A2原件保留，当前源码与A2归档几何源哈希一致为{source_preserved}。
- 当前0005预览：`{delivery}/三维评审.html`。实际整机宽1001×深841×高476格、{manifest['block_count']:,}方块、35构件；上部投影超出顶层基座0列，最窄外沿余量{base['minimum_projected_border_margin_voxels']}格。595对独立构件占格交叠0，既有羽片、风车叶片净距保留；证据同目录`净空记录.json`。
- 完整NBT/Schematic与10幅headless截图已更新，页面错误和失败请求均0。仍是静态外观待评审候选；未替换运行蓝图、未构建安装JAR、未运行游戏，不增加分数或批准数。回执：`{log_path}/completion.json`。
'''
for path in (root/'AGENTS.md', root/'rule/当前多方块设计规则.md'):
    with path.open('a', encoding='utf8', newline='') as handle:
        handle.write(entry)
print(json.dumps(dict(receipt=str(log/'completion.json'), minimum_border=base['minimum_projected_border_margin_voxels'], upper_source_preserved=source_preserved), ensure_ascii=False))
