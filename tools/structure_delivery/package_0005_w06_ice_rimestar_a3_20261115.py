import json
import shutil
from pathlib import Path

import geometry_0005_w06_ice_rimestar_a3_20261115 as geometry
import package_0005_w05_wendy_wings_a2_20261115 as shared


ROOT=Path(__file__).resolve().parents[2]
shared.geometry=geometry
shared.OUT=ROOT/'deliveries/0005_W06_冰律陨冰凝态宫_A3_20261115'
shared.LOG=ROOT/'logs/0005-w06-ice-rimestar-a3-20261115'
shared.VIEWS=[('front','前左全景','整体预览.png'),('right','前右全景','前右预览.png'),
    ('orthofront','正面','正面预览.png'),('side','侧面','侧面预览.png'),('back','背面','背面预览.png'),
    ('top','俯视','俯视预览.png'),('core','陨冰倒锥与包合弧刃','核心近景.png'),
    ('crown','陨冰悬冠与纯冰尖徽','冠冕近景.png'),('heat','独立热端机组','热端近景.png'),('controller','前庭主控','主控近景.png')]
shared.main()
payload=shared.OUT/'data.js'
payload.write_text(payload.read_text('utf8').replace('window.W05_STATIC_PAYLOAD=','window.W06_STATIC_PAYLOAD=',1),'utf8')
for name in ['index.html','三维评审.html','review-ui.json','生成脚本/viewer.mjs']:
    path=shared.OUT/name
    text=path.read_text('utf8').replace('W05','W06').replace('温蒂风翼与渴望之心','冰律陨冰凝态宫').replace('温蒂风翼','冰律陨冰')
    text=text.replace('外观候选 A2','外观候选 A3')
    text=text.replace('<meta charset="utf-8">','<meta charset="utf-8"><link rel="icon" href="data:,">',1)
    text=text.replace('完整设计记录</a>','完整设计记录</a> · <a href="原作参考/index.html">纯冰／陨冰原作参考对照</a>')
    if name=='三维评审.html':
        text=text.replace('候选状态与文件</summary>','候选状态与文件</summary><p><a href="原作参考/index.html">纯冰／陨冰原作参考对照</a></p>')
    text=text.replace('风翼、风车和宝石的建筑形体为原创转译；宝石几何不宣称官方实体复刻。',geometry.build.__module__+ '：融合纯冰与陨冰形体的工业建筑转译，不宣称源模型复刻。')
    text=text.replace('#48c9a3','#91dceb').replace('#19362f','#173039').replace('#9be2ca','#91dceb').replace('#a9dfca','#bfeef7')
    path.write_text(text,'utf8')
for path in [shared.OUT/'manifest.json',shared.LOG/'generation.json']:
    data=json.loads(path.read_text('utf8'))
    data.update(machine='W06',candidate='A3',previous_candidate='deliveries/0005_W06_冰晶冠冕凝态宫_A2_20261115',
        reference_study='logs/0005-w06-ice-rimestar-references-20261115/',
        reference_identity=dict(pure_ice='第18章正式服剧情FHXHHtfZyvE：分叉冠、长白带、独立细矛与镂空环。',
            rimestar='第19章正式服剧情COQbCcI6Zo8及lpjSOOh7Epg：倒锥、包合弧刃、悬冠盘与小面积暗红核心。'),
        original_translation='比例、方块分层与工业设施为原创建筑转译，未使用角色源模型。')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
for source in [Path(__file__),ROOT/'tools/structure_delivery/geometry_0005_w06_crystal_crown_a2_20261115.py']:
    shutil.copy2(source,shared.OUT/'生成脚本'/source.name)
reference=ROOT/'logs/0005-w06-ice-rimestar-references-20261115'
portable=shared.OUT/'原作参考'
files=['index.html','ice/source-manifest.json','ice/ice-final-review-upscaled.jpg',
    'rimestar/source-assessment.json','rimestar/selected-frames.json','rimestar/original-rimestar-selected-frames.png']
files += ['ice/'+item['file'] for item in json.loads((reference/'ice/source-manifest.json').read_text('utf8'))['selected_images']]
selected=json.loads((reference/'rimestar/selected-frames.json').read_text('utf8'))
files += ['rimestar/'+item['native_crop'] for item in selected]
for file in files:
    destination=portable/file
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(reference/file,destination)
source=ROOT/'tools/structure_delivery/capture_0005_w05_wendy_wings_a4_20261115.mjs'
text=source.read_text('utf8').replace('0005_W05_温蒂风翼渴望之心_A4原作翼形_20261115','0005_W06_冰律陨冰凝态宫_A3_20261115')
text=text.replace('0005-w05-wendy-wings-a4-20261115','0005-w06-ice-rimestar-a3-20261115').replace('W05','W06')
text=text.replace("['wing', '风翼近景.png']","['crown', '冠冕近景.png']").replace("['wingroot', '翼根近景.png']","['heat', '热端近景.png']")
text=text.replace("await page.goto(pathToFileURL(path.join(out, '三维评审.html')).href,", "await page.goto('http://127.0.0.1:9681/' + encodeURIComponent(path.basename(out)) + '/' + encodeURIComponent('三维评审.html'),")
(ROOT/'tools/structure_delivery/capture_0005_w06_ice_rimestar_a3_20261115.mjs').write_text(text,'utf8')
