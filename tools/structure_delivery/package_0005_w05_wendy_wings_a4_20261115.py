import json
import shutil
from pathlib import Path

import geometry_0005_w05_wendy_wings_a4_20261115 as geometry
import package_0005_w05_wendy_wings_a2_20261115 as shared


ROOT = Path(__file__).resolve().parents[2]
shared.geometry = geometry
shared.OUT = ROOT / 'deliveries/0005_W05_温蒂风翼渴望之心_A4原作翼形_20261115'
shared.LOG = ROOT / 'logs/0005-w05-wendy-wings-a4-20261115'
shared.VIEWS = [(key, '整体分叉薄翼' if key == 'wing' else label, file)
    for key, label, file in shared.VIEWS]
shared.VIEWS.append(('wingroot', '集中翼根与后置投射座', '翼根近景.png'))
shared.main()
for name in ['index.html', '三维评审.html']:
    path = shared.OUT / name
    text = path.read_text('utf8').replace('外观候选 A2', '外观候选 A4')
    text = text.replace('风翼、风车和宝石的建筑形体为原创转译；宝石几何不宣称官方实体复刻。',
        '新翼面据游戏实录重构轮廓，具体方块比例与后置投射设施仍为建筑转译；不宣称官方源模型复刻。')
    text = text.replace('完整设计记录</a>', '完整设计记录</a> · <a href="../0005_W05_温蒂游戏翼形参考校准_20261115/index.html">原作参考校准</a>')
    path.write_text(text, 'utf8')
for path in [shared.OUT / 'manifest.json', shared.LOG / 'generation.json']:
    data = json.loads(path.read_text('utf8'))
    data.update(candidate='A4', previous_candidate='deliveries/0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115',
        reference_study='deliveries/0005_W05_温蒂游戏翼形参考校准_20261115/参考清单.json')
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
for source in [Path(__file__), ROOT / 'tools/structure_delivery/geometry_0005_w05_wendy_wings_a2_20261115.py',
    ROOT / 'tools/structure_delivery/geometry_0005_w05_wendy_wings_a3_20261115.py']:
    shutil.copy2(source, shared.OUT / '生成脚本' / source.name)
source = ROOT / 'tools/structure_delivery/capture_0005_w05_wendy_wings_a3_20261115.mjs'
capture = source.read_text('utf8').replace('0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115',
    '0005_W05_温蒂风翼渴望之心_A4原作翼形_20261115').replace('0005-w05-wendy-wings-a3-20261115',
    '0005-w05-wendy-wings-a4-20261115')
capture = capture.replace("['controller', '主控近景.png']", "['controller', '主控近景.png'], ['wingroot', '翼根近景.png']")
(ROOT / 'tools/structure_delivery/capture_0005_w05_wendy_wings_a4_20261115.mjs').write_text(capture, 'utf8')
