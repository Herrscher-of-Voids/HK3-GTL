import json
import shutil
from pathlib import Path

import geometry_0005_w05_wendy_wings_a3_20261115 as geometry
import package_0005_w05_wendy_wings_a2_20261115 as shared


ROOT = Path(__file__).resolve().parents[2]
shared.geometry = geometry
shared.OUT = ROOT/'deliveries/0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115'
shared.LOG = ROOT/'logs/0005-w05-wendy-wings-a3-20261115'
shared.main()
for name in ('index.html', '三维评审.html'):
    path = shared.OUT/name
    path.write_text(path.read_text('utf8').replace('外观候选 A2', '外观候选 A3'), 'utf8')
for path in (shared.OUT/'manifest.json', shared.LOG/'generation.json'):
    data = json.loads(path.read_text('utf8'))
    data['candidate'] = 'A3'
    data['previous_candidate'] = 'deliveries/0005_W05_温蒂风翼渴望之心_A2_20261115'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf8')
for source in (Path(__file__), ROOT/'tools/structure_delivery/geometry_0005_w05_wendy_wings_a2_20261115.py'):
    shutil.copy2(source, shared.OUT/'生成脚本'/source.name)
source = ROOT/'tools/structure_delivery/capture_0005_w05_wendy_wings_a2_20261115.mjs'
capture = source.read_text('utf8').replace('0005_W05_温蒂风翼渴望之心_A2_20261115', '0005_W05_温蒂风翼渴望之心_A3扩展基座_20261115').replace('0005-w05-wendy-wings-a2-20261115', '0005-w05-wendy-wings-a3-20261115')
(ROOT/'tools/structure_delivery/capture_0005_w05_wendy_wings_a3_20261115.mjs').write_text(capture, 'utf8')
