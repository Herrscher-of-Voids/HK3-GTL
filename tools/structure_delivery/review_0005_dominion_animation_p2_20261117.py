from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_乌合之众_原作像素重建_P2_20261117/references/animation'
EXCLUDED = [(6, 8), (12, 18), (29, 31), (39, 42), (50, 53), (68, 71), (76, 76),
    (79, 84), (98, 100), (103, 109), (124, 130), (135, 143), (148, 149), (151, 154),
    (164, 170), (174, 178), (182, 202), (206, 207)]
NOTES = {
    1: ['低照度只保留悬浮掌、指长与筒腕的整体轮廓。'],
    2: ['极低仰视可见实心掌心、屈指与腕后圆筒口。'],
    3: ['胸腹明显前凸。腿甲是厚长盾状，腿面有三点黑孔。', '主臂前臂厚鼓，金色球形肘接头有圆形黑孔。'],
    4: ['手掌为蓝紫灰实心壳，金指三节。', '腕后为短而宽的空心筒，金色薄边包覆筒口；筒壁有四瓣金饰。'],
    5: ['正面全体明确显示大肩、窄腰、双盾状腿甲与外圈独立手。', '金眉沿边包到面部，红眼位于眉下，鼻梁及下脸收成长V尖。'],
    6: ['俯视可见圆截面指节、逐节深色关节间隙和长短不同的四指。', '前景存在失焦，仅记录大轮廓与指节朝向。'],
    7: ['火焰光照改变表面颜色。头盔顶面与后颅使用蓝紫灰，金色为边框和面甲。'],
    8: ['掌背有纵向细叶凹纹，指根环为金色，关节内核为深紫灰。', '高俯上身可见头盔后颅、V形领口、胸甲厚度和独立肩关节圆腔。'],
    9: ['线描仅用于手指向掌心屈曲、握持时拇指相对位置与包围关系。'],
    10: ['低仰近景显示胸甲前凸圆弧、四瓣金纹及金纹内部深色长叶槽。', '肩甲由鼓起厚壳及上翘三角尖构成，腋下保留金边黑色圆腔。'],
    11: ['悬手从多个距离包围本体，掌心实心、手指呈抓握姿态。', '腕筒侧形为前窄后宽的短扩口轮廓，金饰贴合筒壁。'],
    12: ['逆光背视仅记录外轮廓。背上部中央金纹呈U形，腰背有交叉星形金饰。', '双肩后缘为宽大的外挑尖角，肩下主臂有独立圆鼓甲壳。'],
    13: ['清楚正面近景显示金面具下端细长V尖及眼槽内红色双眼。'],
    14: ['头盔侧面可见前伸金色椭圆厚檐，檐内为黑色凹面。', '侧视后颅呈蓝紫灰圆鼓体，有一圈金色叶形闭合细边。'],
    15: ['绿色特效照明下保留头盔、红眼、V形面甲与领甲的几何关系。'],
}


def main():
    data = json.loads((OUT / 'references.json').read_text('utf8'))
    records = data['references'] + data.get('excluded', [])
    records.sort(key=lambda r: r['id'])
    excluded_ids = {i for start, end in EXCLUDED for i in range(start, end + 1)}
    selected, excluded = [], []
    for ref in records:
        ref['reviewed'] = True
        index = int(ref['id'][1:])
        ref['selected'] = index not in excluded_ids
        if ref['selected']:
            ref['observations'] = NOTES[ref['scene']]
            ref['scope'] = '轮廓参考' if ref['scene'] in (1, 9, 12) else '形制与细节参考'
            selected.append(ref)
        else:
            ref['exclusion_reason'] = '主体切镜、主体被遮挡或失焦、强特效遮挡，或仅见招式变形状态。'
            ref['observations'] = []
            excluded.append(ref)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    for start in range(0, len(selected), 12):
        sheet = Image.new('RGB', (1920, 918), '#14161c')
        draw = ImageDraw.Draw(sheet)
        for i, ref in enumerate(selected[start:start + 12]):
            x, y = i % 4 * 480, i // 4 * 306
            sheet.paste(Image.open(OUT / ref['thumbnail']), (x, y))
            draw.text((x + 8, y + 273), f"{ref['id']} {ref['time_seconds']:g}s {ref['scope']}", font=font, fill='#e9ddbc')
        sheet.save(OUT / f'selected-{start // 12 + 1:02d}.jpg', quality=94)
    data.update(reviewed_at=datetime.now(timezone.utc).isoformat(), candidate_count=len(records),
        count=len(selected), excluded_count=len(excluded), scene_groups=len({r['scene'] for r in selected}),
        counting='全部207张候选已实际查看联系图；保留帧按内容筛选。连续运动帧数量与独立视角数量分开，不将每张原帧计作独立角度。',
        references=selected, excluded=excluded)
    (OUT / 'references.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf8')
    study = dict(reviewed_candidates=len(records), selected=len(selected), excluded=len(excluded),
        source='官方动画 Everlasting Flames',
        source_url='https://www.youtube.com/watch?v=n1rjfW-5HAE',
        viewed_contact_sheets=[f'contact-{i:02d}.jpg' for i in range(1, 19)],
        observations=NOTES,
        keyframes={
            '头盔侧面': ['A179', 'A180', 'A181'],
            '高俯头胸': ['A101'],
            '胸甲肩壳': ['A131', 'A132', 'A133', 'A134'],
            '背部逆光轮廓': ['A157', 'A158', 'A159', 'A160', 'A161', 'A162', 'A163'],
            '主臂与腿甲': ['A019', 'A020', 'A021', 'A022', 'A122', 'A123'],
            '浮手掌背与腕筒': ['A032', 'A033', 'A034', 'A035', 'A036', 'A037', 'A038', 'A085', 'A086', 'A087', 'A102'],
        },
        missing=['清楚完整背面', '完整正交侧面', '背部内层结构', '主臂腋下封闭连接细节'])
    (OUT / 'study.json').write_text(json.dumps(study, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(selected=len(selected), excluded=len(excluded), scene_groups=data['scene_groups']), ensure_ascii=False))


if __name__ == '__main__':
    main()
