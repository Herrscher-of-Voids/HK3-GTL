"""修订75动态电路提示候选：生成GIF对照，不修改正式tooltip。

变更记录 #1：展示连续七彩、主题色和分层七彩三种候选；这些是效果示意，
并非游戏截图或已实现代码。时间与参数写入验证记录，供负责人选择。
"""
from pathlib import Path
from datetime import datetime
import colorsys
import math
import json
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parents[1]/'logs/revision75/tooltip-choices'
FONT='C:/Windows/Fonts/msyhbd.ttc'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frames=[]
    labels=['A 连续七彩流动','B 系列主题色流动','C 分层七彩与明亮脉冲']
    title_font=ImageFont.truetype(FONT,22)
    text_font=ImageFont.truetype(FONT,26)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    for frame in range(72):
        im=Image.new('RGB',(840,410),'#171922');d=ImageDraw.Draw(im)
        d.text((24,12),'电路等级 tooltip 动态候选',font=title_font,fill='white')
        d.text((24,47),'示意图：等待选择后再接入游戏；仅电路等级提示行使用动态色。',font=small,fill='#aab2c2')
        for row,label in enumerate(labels):
            y=87+row*102
            d.text((24,y),label,font=small,fill='#cdd4e4')
            d.rectangle((275,y-3,810,y+79),fill='#100615',outline='#6f417f',width=2)
            d.text((292,y+4),'文明存续处理器主机',font=small,fill='#ece2ff')
            x=292
            for index,char in enumerate('CEV 级电路'):
                phase=frame/72
                if row==0:
                    h=(index*.075-phase)%1;s=.78;v=1
                elif row==1:
                    h=(.93+.07*math.sin(index*.45-phase*math.tau))%1;s=.65;v=.8+.2*math.sin(index*.45-phase*math.tau)**2
                else:
                    h=(index*.09-phase*1.4)%1;s=.60;v=.82+.18*(.5+.5*math.sin(phase*math.tau*2-index*.45))
                color=tuple(round(c*255) for c in colorsys.hsv_to_rgb(h,s,v))
                if row==2:
                    d.text((x+1,y+30),char,font=text_font,fill=tuple(c//4 for c in color))
                d.text((x,y+28),char,font=text_font,fill=color)
                x+=d.textlength(char,font=text_font)
        frames.append(im)
    frames[0].save(OUT/'tooltip-candidates.gif',save_all=True,append_images=frames[1:],duration=60,loop=0,disposal=2)
    (OUT/'preview.json').write_text(json.dumps({'generated_at':datetime.now().astimezone().isoformat(),
        '说明':'候选效果示意，非游戏截图；尚未改写物品tooltip。','frames':72,'duration_ms':4320,'options':labels},ensure_ascii=False,indent=2),'utf8')
    print('三种动态候选已生成，正式tooltip未改。')


if __name__=='__main__':main()
