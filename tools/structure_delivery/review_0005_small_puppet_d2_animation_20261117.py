from collections import Counter
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117/references/animation'
GROUPS = [
    (1, 27, 'A01', '正面头肩', ['脸', '蒙眼', '额纹', '双侧金锥', '侧发', '白肩'], '前景武器和琪亚娜遮挡躯干'),
    (50, 67, 'A02', '后脑近景与斜侧全身', ['后脑', '金锥', '金色后缘', '裙', '白腿'], '战斗碎裂，颈腰连接被破坏'),
    (77, 83, 'A03', '远景群像', ['全身轮廓', '裙腿比例'], '主体远，动作透视与运动模糊'),
    (87, 92, 'A04', '正面头肩', ['额纹', '蒙眼', '侧发', '胸裙'], '前景琪亚娜遮挡下部'),
    (93, 108, 'A05', '斜俯前后双向', ['后脑', '后领', '胸裙', '金手', '黑袖'], '多人互相遮挡，部分躯干碎裂'),
    (109, 130, 'A06', '正脸超近景', ['蒙眼弧度', '鼻', '脸颊', '尖下颌', '侧面金饰'], '琪亚娜手挡住鼻嘴，额纹出画'),
    (131, 151, 'A07', '俯斜头部', ['额纹', '发际', '后脑分缝', '金锥分片', '裙边'], '后段头部破裂，手遮下半脸'),
    (152, 164, 'A08', '正侧面与裙腿', ['白褶衬裙', '黑金裙片', '腿', '机械膝', '白肩'], '琪亚娜和武器遮挡，部分头身断开'),
    (165, 172, 'A09', '手背与头部近景', ['金手分节', '手背菱框眼纹', '侧发', '额纹', '蒙眼'], '168至169帧武器遮满画面'),
    (173, 179, 'A10', '侧面头肩', ['侧头', '金手', '黑袖'], '前景虚焦脸，后景目标有遮挡'),
    (186, 209, 'A11', '低仰裙底与腿', ['裙底轮廓', '腿部连接', '膝片'], '强眩光、透视和运动模糊，按局部连接使用'),
    (210, 231, 'A12', '前侧后群像', ['后脑', '金锥', '侧发', '裙', '金手', '腿'], '群像重叠，多个姿态可交叉观察'),
    (236, 242, 'A13', '空中正侧全身', ['完整轮廓', '裙腿比例', '鞋'], '主体远，空中屈腿'),
    (243, 247, 'A14', '前侧脸与空中群像', ['侧脸', '蒙眼', '金锥', '侧发', '裙腿'], '武器横穿，最近头部部分出画'),
    (252, 262, 'A15', '远景正侧全身', ['全身轮廓', '姿态', '裙腿'], '激光穿过身体，细节分辨率低'),
]
EXCLUDED = [
    (28, 46, '大乌合之众机械躯体局部，未见目标小人偶'),
    (47, 49, '琪亚娜脸为主体，未见目标小人偶'),
    (68, 76, '琪亚娜与遮挡腿为主体，目标仅远背景'),
    (84, 86, '琪亚娜占画面主体，目标细节不足'),
    (168, 169, '武器遮挡目标'),
    (180, 185, '琪亚娜脸与服装为主体'),
    (232, 235, '琪亚娜与烟雾为主体'),
    (248, 251, '激光强曝光覆盖目标'),
]
SILHOUETTE = [(77, 83), (152, 156), (186, 209), (236, 242), (252, 262)]
FULL_REVIEW = {23, 64, 67, 98, 109, 126, 143, 161, 165, 186, 201, 210, 218, 240, 245, 252}


def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf8')


def main():
    data = json.loads((OUT/'candidates.json').read_text('utf8'))
    for sheet in data['contact_sheets']:
        sheet['reviewed'] = True
        sheet['review_mode'] = '逐页查看20帧联系图，末页2帧'
    for ref in data['references']:
        n = int(ref['id'][3:])
        ref['reviewed'] = True
        ref['review_mode'] = '联系图与1920×1080完整帧' if n in FULL_REVIEW else '20帧联系图'
        ref['model_role'] = '动画版比对补充，主体模型采用游戏剧情版'
        reasons = [reason for start, end, reason in EXCLUDED if start <= n <= end]
        ref['selected'] = not reasons
        ref['excluded_reason'] = reasons[0] if reasons else ''
        ref['quality'] = '排除' if reasons else '轮廓与连接参考' if any(a <= n <= b for a, b in SILHOUETTE) else '局部细节参考'
        for start, end, group, angle, parts, obstruction in GROUPS:
            if start <= n <= end:
                ref.update(shot_group=group, angle=angle, visible_parts=parts, obstruction=obstruction)
                break
    save('candidates.json', data)
    counts = Counter(ref['quality'] for ref in data['references'])
    save('references.json', dict(
        subject='《薪炎永燃》动画版金发黑蒙眼千人人偶',
        model_role='动画版比对补充，当前主体采用游戏剧情黑色连体衣版',
        source_count=1, candidate_count=len(data['references']), reviewed_count=len(data['references']),
        selected_count=sum(r['selected'] for r in data['references']), excluded_count=counts['排除'],
        detail_reference_count=counts['局部细节参考'], silhouette_reference_count=counts['轮廓与连接参考'],
        full_resolution_review_count=len(FULL_REVIEW), contact_sheet_count=len(data['contact_sheets']),
        shot_group_count=len(GROUPS),
        counting_note='262张候选完整帧逐页查看，保留212张有效原帧：158张局部细节参考、54张轮廓与连接参考。全部来自1条官方动画，包含相邻连续帧与同一镜头动作；15个人工镜头组不等于212个独立角度。裁切和联系图不计新图片。',
        sources=[dict(id='official-everlasting-flames', url='https://www.youtube.com/watch?v=n1rjfW-5HAE',
                      title='Everlasting Flames - Honkai Impact 3rd Animated Short', publisher='Honkai Impact 3rd',
                      provenance='官方发布动画；使用既有1920×1080缓存按帧提取')],
        windows=data['windows'],
        shot_groups=[dict(id=g[2], frame_start=f'D2A{g[0]:03d}', frame_end=f'D2A{g[1]:03d}', angle=g[3],
                          visible_parts=g[4], obstruction=g[5]) for g in GROUPS],
        contact_sheets=data['contact_sheets'], references=data['references']))
    save('study.json', dict(
        subject='动画版千人人偶形制观察',
        model_role='版本比对补充；游戏剧情版服装以游戏清单为准',
        observations=[
            dict(part='前额与脸', refs=['D2A023', 'D2A109', 'D2A126', 'D2A143'],
                 observed='白瓷前额由发际切成窄高楔形。额纹为三个细长空心叶环连接，中心小圆点。蒙眼下方脸颊收向窄尖下颌，嘴为短机械折线。',
                 d1_difference='旧下巴过圆；前额与金纹过宽，三叶纹填得过粗。'),
            dict(part='蒙眼与侧金饰', refs=['D2A109', 'D2A126', 'D2A245'],
                 observed='黑蒙眼包覆眼区并向脸侧回折，表面有弧度与浅折线；下缘绕鼻梁抬起。两侧金边有三枚短尖和较大的下侧金片。',
                 d1_difference='应按脸壳塑造包覆体积和鼻梁凹口。'),
            dict(part='金发与双锥', refs=['D2A023', 'D2A064', 'D2A067', 'D2A143', 'D2A218', 'D2A245'],
                 observed='浅奶金短后脑壳分瓣、留细缝；双侧金锥短胖并向外张开，有分片环缝和圆接点。两束长侧发贴脸延伸至胸口，末端渐尖。后脑下缘有金色回折和双菱形小扣。',
                 d1_difference='双锥控制在短胖附件比例，后脑须保留分瓣，侧发厚度与尖端逐层变化。'),
            dict(part='动画服装', refs=['D2A098', 'D2A161', 'D2A165', 'D2A210', 'D2A240'],
                 observed='白分瓣领、白球肩、黑长袖。黑金短伞裙下缘有长水滴金框、金扣，内为白褶衬裙。',
                 d1_difference='本组短裙属于动画版；当前游戏剧情版黑连体衣模型不得混入短裙。'),
            dict(part='金手与关节', refs=['D2A098', 'D2A165', 'D2A166'],
                 observed='金手五指独立，指节三段，指根留暗缝；手背有竖向菱框和椭圆眼纹。',
                 d1_difference='按分指、弯折指节和手背眼纹建体积，避免手掌整块化。'),
            dict(part='腿与鞋', refs=['D2A161', 'D2A162', 'D2A186', 'D2A201', 'D2A240', 'D2A252'],
                 observed='动画版腿为白瓷长腿，独立圆椭圆膝片配短黑槽和分片缝，鞋用黑白金。低仰段可见连接，强透视段只用于局部结构。',
                 d1_difference='游戏版腿色、叶片和连接方式采用游戏资料。'),
        ],
        proportion=dict(status='未冻结数值', evidence=['D2A210', 'D2A240', 'D2A252'],
                        note='全身原帧包含屈腿、空中动作和显著透视，未把动画联系图换算为严格正交比例。'),
        coverage=dict(clear=['正脸', '斜侧脸', '后脑', '金锥', '后领', '金手', '裙腿'],
                      remaining='完整无遮挡的正常连接躯干背部近景较少；战斗断开的腰颈与紫色丝线属于受击状态。'),
        key_frames=[dict(id=r['id'], file=r['file'], time_seconds=r['time_seconds'], angle=r['angle'], parts=r['visible_parts'])
                    for r in data['references'] if int(r['id'][3:]) in FULL_REVIEW]))
    print(json.dumps(dict(reviewed=262, selected=212, excluded=50, detail=158, silhouette=54,
                          full_resolution=16, shot_groups=15), ensure_ascii=False))


if __name__ == '__main__':
    main()
