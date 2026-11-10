# -*- coding: utf-8 -*-
"""复用船坞静态交付，仅替换A2说明和构图镜头。"""
from pathlib import Path
import shutil
import w02_19c_dock_scene_a2_20261110 as g
import package_w02_19c_dock_a1_20261110 as package


def main():
    package.main(g)
    replacements={
        'A1':'A2',
        '19C原形保持V6，仅整体平移；新增U形供料船坞、双手半成品、背部维护架、链井、双炮靶台与前控出货轨。26个静态构件。':
            '双炮与双掌朝向中央核心，构造线从掌心炮口发射；其他20个构件保持A1。26个静态构件，无动画。',
        '19C保持原形':'其余20构件保留',
        'V6的11个构件只整体平移，躯干、背部、节链、双臂和双炮均不改形。':
            '躯干、背部、节链、轮组、双臂及其余船坞设施逐格保持A1。',
        '连接双掌的静态构造线。':'两只手掌向内，静态构造线从掌心炮口发出。',
        '双炮对应处理工序':'双炮汇聚构造核心',
        '两座小型处理靶台沿现有炮口方向布置，保留双炮位置与角度。':
            '双炮前移60格、抬高20格避开肩轮，向内俯射；原分叉炮型、长度与配色保留。',
        '把19C放进一条看得懂的生产工序：六站供料，双炮处理，双手组装，前方出货。V6原形完整保留；船坞围绕它的工作位置生成。':
            '六站供料，双炮和双掌共同指向双手之间的半成品核心，前方完成出货。掌心炮口成为真正的构造光束起点。',
        '两侧供料加工 → 双炮材料处理 → 双手完成装配 → 前控与出货轨':
            '两侧供料加工 → 双炮与双掌汇聚核心 → 前控与出货轨',
        '19C的11个构件仅整体平移(0,+40,-70)，坐标差和材质逐格核对；新设施与19C无共享体素。':
            '相对A1只改变双炮、双掌、准直环与构造线6个构件，其余20构件逐格不变。双掌绕腕部内转；原炮位内转会碰肩轮，炮座因此前移60格并抬高20格。四条轴线统一指向(0,211,68)，光束止于核心表面。',
        '保留的V6独立小样':'保留的A1组合草案',
    }
    for file in [g.OUT/'index.html',g.OUT/'w02/三维评审.html']:
        text=file.read_text('utf8')
        for old,new in replacements.items():text=text.replace(old,new)
        text=text.replace('../'+g.PRIOR.name.replace('A1','A2'),'../'+g.PRIOR.name)
        text=text.replace('A2 · 60张多视角参考','A2 · 双炮双掌聚焦')
        file.write_text(text,'utf8')
    for file in [Path(__file__),Path(g.__file__),Path(package.__file__),g.ROOT/'tools/structure_delivery/w02_19c_geometry_v4_20261110.py']:
        shutil.copy2(file,g.OUT/'生成脚本'/file.name)


if __name__=='__main__':main()
