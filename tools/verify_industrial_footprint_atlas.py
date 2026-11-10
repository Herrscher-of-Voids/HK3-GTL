# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-09-23 · 检查69台新旧对应、分级、链接。
不启动游戏，也不将规划尺寸当成已成型机器。
"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import json, re
root=Path(__file__).resolve().parents[1]
base=root/'doc/HK3GTL-内测5'
page=base/'03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html'
html=page.read_text(encoding='utf-8')
rows=json.JSONDecoder().raw_decode(html.split('const machines=',1)[1])[0]
tree=(base/'02_工业计划/HK3GTL工业计划树状图_v5.html').read_text(encoding='utf-8')
nodes=json.loads(tree.split('const nodes=',1)[1].split('const labels=',1)[0].strip().rstrip(';'))
old={}
def walk(node):
 if 'dimensions' in node: old[node['id']]=node['dimensions']
 for child in node.get('children',[]):walk(child)
for node in nodes:walk(node)
assert len(rows)==69 and len(old)==69
assert len({row['id'] for row in rows})==69 and {r['id'] for r in rows}==set(old)
for row in rows:
 assert row['old']==old[row['id']]
 assert row['oldArea']==old[row['id']][0]*old[row['id']][1]
 width,length,height=row['size']
 assert width>=17 and length>=17 and height>=17
 assert row['area']==width*length
 expected='普通级' if max(width,length)<=31 else '中型' if max(width,length)<=64 else '大型' if max(width,length)<=95 else '超大型' if max(width,length)<=255 else '文明奇观级'
 assert row['grade']==expected,(row['id'],expected)
 if row['id'].startswith('W'): assert width>=256 and length>=256
 if row['id'] in {'I01-1','I02','S01','H01'}: assert row['old']==row['size']
assert Counter(row['grade'] for row in rows)=={'普通级':12,'中型':22,'大型':12,'超大型':7,'文明奇观级':16}
assert sum(row['id'].startswith('W') for row in rows)==15
assert sum(row['old']!=row['size'] for row in rows)==65
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.extend(v for k,v in attrs if k=='href' and v and not v.startswith(('#','http:','https:')))
for doc in [page,base/'index.html',base/'03_机器结构/多方块占地分级与全维度高度需求_v1.html',base/'03_机器结构/结构视觉标准与预览使用_v1.html',base/'03_机器结构/机器与文明级奇观.html',base/'02_工业计划/HK3GTL工业计划树状图_v5.html']:
 text=doc.read_text(encoding='utf-8')
 assert '内测5_69座多方块逐台占地规划与比例预览_v2.html' in text or doc==page
 parsed=Links();parsed.feed(text)
 for link in parsed.links:
  if '内测5_69座多方块逐台占地规划与比例预览_v2.html' in link or (doc==page and 'I02结构审核_v1/' in link):assert (doc.parent/link).exists(),(doc,link)
print('PASS 69 unique IDs, source old dimensions, unchanged anchors, all 15 W>=256x256, grade counts, 65 actual changes, relative links.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
