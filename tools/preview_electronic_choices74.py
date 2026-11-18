"""修订74审美确认预览：只读取指定实例原图，输出候选图，不改正式资源。

变更记录 #1：由运行时记录实时时间；新增具名原图候选及局部/整体染色对照。
用途：负责人选择后再应用；预览仅展示动画首帧，不代表游戏验收。
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import colorsys
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/revision74/choices'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')
FONT = 'C:/Windows/Fonts/msyh.ttc'
BG, PANEL, TEXT, MUTED = '#151b25', '#202938', '#edf2fb', '#aebcd0'
SOURCES = []


def font(n):
    return ImageFont.truetype(FONT, n)


def load(namespace, name):
    resource = f'assets/{namespace}/textures/item/{name}.png'
    if namespace == 'gtceu':
        path = INSTANCE / 'mods/gtceu-1.20.1-1.4.4.jar'
        with zipfile.ZipFile(path) as z:
            data = z.read(resource)
        source = str(path) + '!/' + resource
    else:
        path = INSTANCE / 'kubejs' / resource
        data = path.read_bytes()
        source = str(path)
    im = Image.open(BytesIO(data)).convert('RGBA')
    SOURCES.append({'source': source, 'sha256': hashlib.sha256(data).hexdigest(), 'size': list(im.size)})
    return im


def sheet(title, subtitle, labels, rows, height):
    im = Image.new('RGB', (1040, 145 + rows * height), BG)
    d = ImageDraw.Draw(im)
    d.text((24, 15), title, font=font(27), fill=TEXT)
    d.text((24, 57), subtitle, font=font(15), fill=MUTED)
    for i, label in enumerate(labels):
        d.text((250 + i * 190, 101), label, font=font(19), fill=TEXT)
    return im


def tile(sheet, im, col, row, height, label, source_name):
    y = 142 + row * height
    d = ImageDraw.Draw(sheet)
    d.rounded_rectangle((239 + col * 190, y, 415 + col * 190, y + height - 7), 7, fill=PANEL)
    first = im.crop((0, 0, im.width, im.width))
    side = min(96, height - 39)
    first = first.resize((side, side), Image.Resampling.NEAREST)
    sheet.paste(first, (279 + col * 190, y + 5), first)
    d.text((246 + col * 190, y + height - 30), source_name, font=font(11), fill=MUTED)
    if col == 0:
        d.text((24, y + 20), label, font=font(21), fill=TEXT)
        frames = im.height // im.width
        d.text((24, y + 56), '原图 · 首帧' if frames > 1 else '原图 · 静态', font=font(15), fill=MUTED)


def recolor(im, whole=False, ram=False):
    result = im.copy()
    hue, target_s, _ = colorsys.rgb_to_hsv(164/255, 91/255, 218/255)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            # A用原图调色板识别功能区，保留无彩色金属与金铜触点；RAM只染低饱和硅片。
            selected = ((max(r,g,b) - min(r,g,b) > 3 and v > .25) if ram
                        else (s > .12 and not 0.035 <= h <= .20))
            if whole or selected:
                ns = max(s, target_s * .85) if selected else target_s * .55
                rgb = colorsys.hsv_to_rgb(hue, ns, v)
                result.putpixel((x,y), tuple(round(t*255) for t in rgb) + (a,))
    assert result.getchannel('A').tobytes() == im.getchannel('A').tobytes()
    assert [max(p[:3]) for p in result.getdata()] == [max(p[:3]) for p in im.getdata()]
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (ROOT/'src/main/resources/assets/hk3gtl').rglob('*') if p.is_file()}
    families = [('gtceu','nano','G1 纳米'), ('gtceu','quantum','G2 量子'),
                ('gtceu','crystal','G3 晶体'), ('gtceu','wetware','G4 湿件'),
                ('kubejs','bioware','L1 生物'), ('kubejs','optical','L2 光学'),
                ('kubejs','exotic','L3 奇异'), ('kubejs','cosmic','L4 宇宙'),
                ('kubejs','supracausal','L5 超因果')]
    im = sheet('电路原图候选｜未换色', 'G = GTCEu JAR；L = 指定整包 KubeJS 原资产。每行是一套四形态，动画只显示首帧。',
               ['处理器','处理器组装件','计算机','主机'], len(families), 132)
    for row, (ns, family, label) in enumerate(families):
        for col, form in enumerate(['processor','assembly','computer','mainframe']):
            name = family + ('_processor_' + form if ns == 'gtceu' and col else '_' + form)
            tile(im, load(ns,name), col,row,132,label,name)
    im.save(OUT/'01-circuit-original-candidates.png')
    im = sheet('基板与 RAM 原图候选｜未换色', 'B1–B5 为板材候选；R1–R5 为晶圆/晶片配对候选。可分别选择，不强制同一行。',
               ['基板','印刷电路板','RAM 晶圆','RAM 晶片'],5,142)
    boards = [('gtceu','wetware'),('kubejs','optical'),('kubejs','exotic'),('kubejs','cosmic'),('kubejs','supracausal')]
    for row,(ns,family) in enumerate(boards):
        for col, suffix in enumerate(['circuit_board','printed_circuit_board','ram_wafer','ram_chip']):
            name = ('ram_wafer' if col==2 else 'ram_chip') if row==0 and col>=2 else family+'_'+suffix
            tile(im,load(ns,name),col,row,142,f'B{row+1} / R{row+1} '+['湿件 / GT RAM','光学','奇异','宇宙','超因果'][row],name)
    im.save(OUT/'02-board-ram-original-candidates.png')
    rows = [('nano_processor','纳米处理器',False),('wetware_printed_circuit_board','湿件印刷电路板',False),
            ('ram_wafer','GT RAM 晶圆',True),('ram_chip','GT RAM 晶片',True)]
    im = sheet('换色范围对照｜统一紫色示例', 'A：仅功能区着色，保留金属/触点/灰色阴影；B：整体染色。两者均不重画、不改变透明度及HSV明度。',
               ['原图','A 保留金属色','B 整体染色'],len(rows),158)
    for row,(name,label,ram) in enumerate(rows):
        original=load('gtceu',name)
        for col,img in enumerate([original,recolor(original,ram=ram),recolor(original,whole=True,ram=ram)]):
            tile(im,img,col,row,158,label,['未改色','功能区换色','全部区域偏紫'][col])
    im.save(OUT/'03-recolor-scope-comparison.png')
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in (ROOT/'src/main/resources/assets/hk3gtl').rglob('*') if p.is_file()}
    assert before == after, '正式资源发生变化'
    report={'generated_at':datetime.now().astimezone().isoformat(timespec='seconds'),
            '说明':'只生成候选预览；本次未修改正式资产。保持原像素布局和透明度；HSV明度保持不等于感知亮度完全一致。',
            'checked_resource_files':len(before),'formal_resources_unchanged':True,'sources':SOURCES}
    (OUT/'preview-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'preview_count':3,'formal_resources_unchanged':True,'checked_files':len(before)}))


if __name__ == '__main__':
    main()
