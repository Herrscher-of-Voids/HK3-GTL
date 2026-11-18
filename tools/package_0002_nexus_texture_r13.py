# -*- coding: utf-8 -*-
"""沿用R7控制器流程，将天枢完整NBT投影接入独立正面。"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import shutil
import sys

import nbtlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/structure_delivery'))
import build_controller_texture_candidates_20261026 as faces

OUT = ROOT / 'deliveries/0002贴图材质_全部接入与天枢_R13_20261115'
LOG = ROOT / 'logs/textures-runtime-integration-0002-r13-20261115'
NBT = ROOT / 'src/main/resources/data/hk3gtl/structures/ae_nexus_a1.nbt'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = nbtlib.load(NBT)
    points = np.asarray([list(map(int, block['pos'])) for block in data['blocks']], dtype=np.int16)
    picture, pattern = faces.candidate_face(points, [], [17, 3, 2], 'idle')
    texture = ASSETS / 'textures/block/ae_nexus_controller_r13/front.png'
    model = ASSETS / 'models/block/ae_nexus_controller_r13.json'
    texture.parent.mkdir(parents=True, exist_ok=True)
    picture.save(texture)
    shutil.copy2(texture, OUT / 'front.png')
    faces.geometry_image(points, OUT / 'whole-structure-projection.png')
    model.write_text(json.dumps({
        'parent': 'minecraft:block/cube',
        'textures': {
            **dict.fromkeys(('south', 'east', 'west', 'up', 'down', 'particle'),
                            'hk3gtl:block/casings/industrial_controller_shell'),
            'north': 'hk3gtl:block/ae_nexus_controller_r13/front'
        }
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    java = ROOT / 'src/main/java/com/sirin/hk3gtl/common/machine/ae/Hk3NexusMachines.java'
    java.write_bytes(java.read_bytes().replace(b'"block/research_point_computer"',
                                              b'"block/ae_nexus_controller_r13"'))
    manifest = {
        'revision': 'R13', 'conversation': '0002',
        'conversationId': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
        'updatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
        'sourceApplied': True, 'artApproved': False,
        'status': '已接入；天枢新正面待负责人查看',
        'method': '直接复用R7控制器candidate_face：完整结构坐标生成原生64×64轮廓与深度棱线投影，沿用同套金属边框及青色屏幕。',
        'helper': 'tools/structure_delivery/build_controller_texture_candidates_20261026.py',
        'actualSize': list(picture.size), 'resized': False,
        'apiProposalDiscarded': True,
        'discardedProposal': 'logs/textures-runtime-integration-0002-r13-20261115/discarded-api-proposal',
        'texture': texture.relative_to(ROOT).as_posix(), 'textureSha256': sha(texture),
        'model': model.relative_to(ROOT).as_posix(), 'geometryPatternSha256': pattern,
        'geometry': {
            'source': NBT.relative_to(ROOT).as_posix(), 'sha256': sha(NBT),
            'sizeXyz': list(map(int, data['size'])), 'blocks': len(points),
            'controllerXyz': [17, 3, 2],
            'approval': 'logs/0005-ae-nexus-integration-a1-20261114/geometry-integration.json',
            'entireStructureIncluded': True, 'cropped': False,
            'note': '全部实体坐标参与投影，统一缩入屏幕；不是游戏截图。'
        },
        'renderer': '独立静态模型，正面为完整结构投影；其余五面及粒子采用工业接口机械方块材质，研究计算机R12保持。',
        'runtimeStatesAdded': False, 'gameTested': False
    }
    for path in (OUT / 'manifest.json', LOG / 'nexus-texture.json'):
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sheet = Image.new('RGB', (700, 390), '#121b27')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    for x, label, path in (
        (30, '天枢 R13 · 同流程新正面', texture),
        (370, 'I01 R7 · 既有控制器', ASSETS / 'textures/block/overlay/i01_appearance_0002_r7/overlay_front.png')
    ):
        draw.text((x, 20), label, font=font, fill='#e5edf5')
        with Image.open(path) as image:
            sheet.paste(image.resize((288, 288), Image.Resampling.NEAREST), (x, 65))
    sheet.save(OUT / 'controller-comparison.png')
    (OUT / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0002 全部材质接入与天枢 R13</title><style>body{margin:0;background:#121b27;color:#e5edf5;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1000px;margin:30px auto;padding:0 20px}a{color:#86deea}img{display:block;max-width:100%;height:auto;margin:20px auto;image-rendering:pixelated}.front{width:512px}small{color:#abc0d2}</style><main><h1>0002 · 全部材质接入与天枢 R13</h1><p>天枢沿用R7其他控制器的整机几何投影流程：已批准A1完整结构6733块全部参与，原生64×64；金属边框和青色投影保持同套风格。此前API稿已弃用，最终贴图直接由结构坐标绘制。</p><p><a href="0002贴图材质-0.5.0-textures-r13.jar">0002贴图材质-0.5.0-textures-r13.jar</a> · 生产包已构建，未安装、未启动游戏。</p><p><a href="front.png">正面PNG</a> · <a href="whole-structure-projection.png">完整NBT投影</a> · <a href="controller-comparison.png">与R7控制器对照</a> · <a href="manifest.json">来源与绑定</a> · <a href="../0002贴图材质_全库材质清单_R10采用_20261115/index.html">全部材质清单</a></p><img class="front" src="front.png" alt="天枢控制器整机投影"><img src="controller-comparison.png" alt="天枢与I01同套控制器对照"><small>独立静态模型，研究计算机保持R12；未新增机器状态。源码接入与构建不等于游戏成型、运行或实机验收。对话0002：01a1d68a-a994-7ac0-a48a-54c0f98fd54e。</small></main></html>''', encoding='utf-8')
    print(json.dumps({'size': list(picture.size), 'blocks': len(points), 'sha256': sha(texture)}))


if __name__ == '__main__':
    main()
