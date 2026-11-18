import json
import shutil
from pathlib import Path

import geometry_0005_w06_crystal_crown_a2_20261115 as geometry
import package_0005_w05_wendy_wings_a2_20261115 as shared


ROOT = Path(__file__).resolve().parents[2]
shared.geometry = geometry
shared.OUT = ROOT/'deliveries/0005_W06_冰晶冠冕凝态宫_A2_20261115'
shared.LOG = ROOT/'logs/0005-w06-crystal-crown-a2-20261115'
shared.VIEWS = [('front','前左全景','整体预览.png'),('right','前右全景','前右预览.png'),
    ('orthofront','正面','正面预览.png'),('side','侧面','侧面预览.png'),('back','背面','背面预览.png'),
    ('top','俯视','俯视预览.png'),('core','密封塔与悬浮核心','核心近景.png'),
    ('crown','六组分离冰晶冠冕','冠冕近景.png'),('heat','独立热端机组','热端近景.png'),('controller','前庭主控','主控近景.png')]
shared.main()
for name in ['index.html','三维评审.html','review-ui.json','data.js','生成脚本/viewer.mjs']:
    path = shared.OUT/name
    content = path.read_text('utf8').replace('W05','W06').replace('温蒂风翼与渴望之心','冰晶冠冕凝态宫').replace('温蒂风翼','冰晶冠冕')
    content = content.replace('风翼、风车和宝石的建筑形体为原创转译；宝石几何不宣称官方实体复刻。','冰晶冠冕、六棱密封塔与悬核为原创工业建筑转译，不宣称安娜源模型复刻。')
    content = content.replace('#48c9a3','#91dceb').replace('#19362f','#173039').replace('#9be2ca','#91dceb').replace('#a9dfca','#bfeef7')
    path.write_text(content,'utf8')
for path in [shared.OUT/'manifest.json',shared.LOG/'generation.json']:
    data = json.loads(path.read_text('utf8'))
    data.update(machine='W06',previous_candidate='deliveries/W06-W15_完整静态蓝图_A1_20261113/w06/index.html',
        original_translation=geometry.build.__module__ + ': 冰晶冠冕与凝态塔为原创转译，不宣称安娜源模型复刻。')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
shutil.copy2(Path(__file__),shared.OUT/'生成脚本'/Path(__file__).name)
