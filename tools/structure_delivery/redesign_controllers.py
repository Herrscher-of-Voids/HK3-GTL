# -*- coding: utf-8 -*-
"""绘制四台专用控制器的原创像素纹理，使用新目录保留旧资源并生成评审图。

仅控制器视觉资源发生变化；64 像素画布对应一个完整方块，不产生新物品或注册。
空闲、运行、暂停使用一致符号和不同状态灯，颜色不承担唯一身份识别。
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, shutil, base64, io

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2'
ASSETS=ROOT/'src/main/resources/assets/hk3gtl'

def face(key,state):
    im=Image.new('RGBA',(64,64),(22,24,43,255));d=ImageDraw.Draw(im)
    d.rectangle((0,0,63,63),outline='#a0a8bc',width=2)
    d.rectangle((3,3,60,60),fill='#38344e',outline='#6f7693',width=2)
    d.rectangle((7,7,56,51),fill='#0b1427',outline='#b89c70',width=2)
    for x in (4,59):
        for y in (4,59):d.rectangle((x-1,y-1,x+1,y+1),fill='#c0c6d3')
    col={'idle':'#57b4c9','active':'#94fff3','paused':'#e3bb65'}[state]
    dark='#30526e'
    if key=='i01':
        d.ellipse((15,11,49,45),outline=dark,width=2);d.ellipse((22,18,42,38),outline=col,width=2)
        d.line((32,11,32,45),fill=dark);d.line((15,28,49,28),fill=dark)
        d.line((32,28,44,16),fill=col,width=3);d.ellipse((26,30,30,34),fill=col)
        d.arc((19,14,45,42),195,275,fill=col,width=2)
    elif key=='i02':
        d.polygon([(16,39),(31,13),(45,39)],outline=col,width=2)
        d.line((11,28,24,28),fill='#c2e6e9',width=2)
        for end in (20,28,36):d.line((34,28,52,end),fill=col,width=2)
        d.line((17,44,48,44),fill=dark,width=2)
    elif key=='i03':
        d.rounded_rectangle((17,13,30,43),radius=2,outline=col,width=2)
        for y in (20,28,36):d.line((18,y,29,y),fill=col,width=2)
        d.line((30,23,43,23,43,33),fill=col,width=2)
        d.rectangle((36,33,50,43),outline=col,width=2)
        d.line((12,43,12,47,51,47),fill=dark,width=2)
    else:
        nodes=[(32,26),(18,16),(46,16),(18,40),(46,40)]
        for x,y in nodes[1:]:d.line((32,26,x,y),fill=col,width=2)
        for x,y in nodes:d.rectangle((x-3,y-3,x+3,y+3),fill='#253b57',outline=col)
        d.arc((13,10,51,48),190,350,fill=dark,width=2)
    for i,x in enumerate((10,19,28,37,46)):
        d.rectangle((x,55,x+5,58),fill=col if state=='active' or i<2 else dark)
    if state=='paused':
        d.rectangle((47,10,49,16),fill=col);d.rectangle((52,10,54,16),fill=col)
    return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    textures=OUT/'控制器贴图';textures.mkdir(exist_ok=True)
    base=Image.new('RGBA',(64,64),'#353047');d=ImageDraw.Draw(base)
    for offset in (0,3,8):d.rectangle((offset,offset,63-offset,63-offset),outline=('#828aa0' if offset==0 else '#514d67'),width=2)
    for x in (5,56):
        for y in (5,56):d.rectangle((x,y,x+2,y+2),fill='#aeb8c9')
    for y in range(20,46,4):d.line((18,y,45,y),fill='#222637',width=2)
    target=ASSETS/'textures/block/casings/industrial_controller_shell.png';target.parent.mkdir(parents=True,exist_ok=True);base.save(target)
    base.save(textures/'controller_shell.png')
    result={};sheet=Image.new('RGB',(1060,690),'#101827');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
    labels={'i01':'I01 采集塔 · 雷达','i02':'I02 光谱阵列 · 光束','i03':'I03 分馏中心 · 分流','s01':'S01 研究所 · 节点'}
    for row,(key,label) in enumerate(labels.items()):
        target=ASSETS/f'textures/block/overlay/{key}_v2';target.mkdir(parents=True,exist_ok=True)
        result[key]={}
        draw.text((15,row*165+60),label,font=font,fill='#dce9f5')
        for col,state in enumerate(('idle','active','paused')):
            im=face(key,state);suffix={'idle':'','active':'_active','paused':'_paused'}[state]
            im.save(target/f'overlay_front{suffix}.png');im.save(textures/f'{key}_{state}.png')
            sheet.paste(im.resize((128,128),Image.Resampling.NEAREST),(340+col*220,row*165+5))
            draw.text((350+col*220,row*165+134),{'idle':'空闲','active':'运行','paused':'暂停'}[state],font=font,fill='#91b8ca')
            stream=io.BytesIO();im.save(stream,format='PNG');result[key][state]='data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
        stream=io.BytesIO();base.save(stream,format='PNG');result[key]['shell']='data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
    sheet.save(OUT/'四机控制器对比.png')
    (OUT/'controllers.json').write_text(json.dumps(result),encoding='utf-8')
    print('生成四台控制器的三状态贴图、共用外壳及对比图。')

if __name__=='__main__':main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
