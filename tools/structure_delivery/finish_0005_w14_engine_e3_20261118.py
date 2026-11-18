# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W14_原生维度地貌_E3_20261118'
LOG = ROOT / 'logs/0005-w14-native-dimensions-e3-20261118'


def main():
    manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
    preview = json.loads((OUT / '预览记录.json').read_text('utf8'))
    material_count = sum(item['blocks'] > 0 for item in manifest['material_counts'])
    receipt = dict(recorded_at=datetime.now().astimezone().isoformat(), machine='W14', candidate='E3', status='下层模块外观候选待审',
        size_wdh=manifest['actual_size_wdh'], blocks=manifest['blocks'], components=manifest['components'],
        surface_quads=manifest['surface_quads'], actual_material_count=material_count, controller=manifest['controller'],
        dimensions=manifest['dimensions'], nbt=manifest['nbt'], nbt_entity_count=0, block_crystals=manifest['block_crystals'],
        requested_changes=['七条斜腿下方封到底盘，七片地貌铺至隔墙及外坝内沿',
            '月球、火星、金星使用Ad Astra 1.15.20对应石与砂',
            '地狱组合五种原版群系及绯红、诡异菌树',
            '末地主岛含龙池、十根黑曜石柱、两座铁笼和纯方块末影水晶',
            '主世界改草原，按1.20.1普通橡树配置逐格生成正常尺寸橡树'],
        correction='负责人明确多方块不使用实体末影水晶；扇区与维度球的20个水晶全部改为5×5×7方块结构，实体渲染与NBT实体生成已删除。',
        preview=dict(captures=len(preview['captures']), errors=preview['errors'], failed=preview['failed'],
            observed=['俯视七分区满铺', '整体隔墙到底', '正常橡树近景', '末地主岛与中央龙池',
                '纯方块末影水晶', '绯红森林', '诡异森林', '月球陨石坑', '火箭尾焰']),
        implementation=dict(geometry='完整整数格NPZ与NBT', animation='网页候选，待接入游戏', upper_body='待融合',
            jar='本轮未构建', installation='本轮未安装', game='本轮未启动'))
    (LOG / 'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', 'utf8')

    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 32)
    board = Image.new('RGB', (2400, 1712), '#14202d')
    draw = ImageDraw.Draw(board)
    figures = [('俯视预览.png', '七条隔墙到底，七维度填满扇区'), ('地狱扇区.png', '地狱五群系与两种菌树'),
        ('末地主岛全貌.png', '末地主岛：十柱、龙池、纯方块水晶'), ('方块末影水晶近景.png', '玻璃框与GT品红核心，全部由方块搭建')]
    for index, (file, title) in enumerate(figures):
        x, y = (index % 2) * 1200, (index // 2) * 856
        draw.text((x + 24, y + 12), title, font=font, fill='#e4ebf5')
        image = Image.open(OUT / file).convert('RGB').resize((1200, 800), Image.Resampling.LANCZOS)
        board.paste(image, (x, y + 56))
    board.save(OUT / '评审总览.png')

    entry = f'''

## 2026-11-18 对话0005：W14原生维度地貌与纯方块水晶E3

- 负责人要求斜腿下方封到底盘，七种地貌填满扇区；E3新增七条连续装甲隔墙，地貌贴合两侧隔墙与外坝内沿。入口为`deliveries/0005_W14_原生维度地貌_E3_20261118/index.html`，E1与E2保留历史。
- 月球、火星、金星均使用Ad Astra 1.15.20原生对应石与砂；具体ID、贴图来源与哈希见`materials.json`。主世界为草原，按Minecraft1.20.1普通橡树配置逐格生成一比一橡树，树干1格宽、高4至6格。地狱以连续地形组合下界荒地、绯红森林、诡异森林、灵魂沙峡谷、玄武岩三角洲，并加入原版尺度菌树、菌光体、熔岩、玄武岩柱与骨块化石。
- 末地扇区与外围维度球均设微缩主岛、龙池、十根圆形黑曜石柱及两座铁笼。负责人纠正多方块不使用实体末影水晶后，两套景观共20座水晶全部改为5×5×7整数方块结构，浅色染色玻璃菱形外框与GT品红无框灯核心；铁笼同步扩至9×9×10。实体模型、纹理引用及实体生成已移除，最终NBT读回`entities`数量为0。
- 当前实际1761×1719×331（宽×深×高），{manifest['blocks']:,}去重实体格、72构件、{material_count}种实际方块；唯一主控仍为源坐标(0,44,610)，朝南，其余实体格均可换合法接口。完整NBT为`{manifest['nbt']['file']}`，{manifest['nbt']['bytes']}字节，SHA-256为`{manifest['nbt']['sha256']}`。
- 27张离线截图覆盖整体、满铺七区、隔墙落底、普通橡树、龙池、纯方块水晶、两种菌树与尾焰；页面错误及请求失败为空。回执`logs/0005-w14-native-dimensions-e3-20261118/completion.json`。当前为下层模块候选，尾焰仍为网页演示，上层主体待融合；本轮未构建JAR、安装或启动游戏，评分与批准数量保持，W07继续停止。
'''
    with (ROOT / 'rule/当前多方块设计规则.md').open('a', encoding='utf8') as stream:
        stream.write(entry)
    print(json.dumps(dict(blocks=manifest['blocks'], materials=material_count, entities=0, captures=len(preview['captures']))))


if __name__ == '__main__':
    main()
