# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-10-15 02:05:20 · 内测5修订157。
删除：无；新增：最新实例规则与修订记录；修改：本轮实际接入与兼容修复摘要。
用途：只更新开发变更记录及目标规则，不改获批结构、配方、存档或其他实例。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json

ROOT=Path(__file__).resolve().parents[2]
now=datetime.now(timezone(timedelta(hours=8)))
stamp=now.strftime('%Y-%m-%d %H:%M:%S')
path=ROOT/'src/main/resources/assets/hk3gtl/changelog.json'
content=json.loads(path.read_text(encoding='utf-8'))
entry={'revision':157,'date':now.strftime('%Y-%m-%d'),'time':now.strftime('%H:%M:%S'),
       'reason':'将内测5迁入负责人指定增强版2.7，修复资源扫描兼容并降低大型结构预览与验收占用',
       'changes':[
           '后续游戏验收唯一目标改为GregTech Leisure-增强版 2.7；按该整合包真实class65要求使用Java21，模组源码仍保持Java17字节码兼容。',
           '将琪亚娜模型来源记录移出models目录并更新生成器，避免TextureScaler将texture_size标量作为模型数组读取而触发资源重载、重复初始化及世界渲染崩溃。',
           '已批准21种结构使用正式NBT提供共享方块预览；支持稀疏预览的目标包省略空气预览对象，普通GT回退共享空气对象；实际Pattern保留全部严格空气、接口、尺寸和几何。',
           '正式结构验收每座完成后清理临时夹具并释放本轮区块，支持单建筑、单朝向及取消；保持专用作弊创造超平坦存档与主世界OP限制。',
           '增强版2.7的JECharacters重复包按整合包下载清单保留4.6.11，旧fix4.6.3备份移出；未替换其他第三方模组。',
           '整合包内存设置按运行采样调整并保存原值、备份及测试日志；构建与静态回归不代替游戏运行或多人长时稳定性。'
       ]}
content['entries']=[e for e in content['entries'] if e.get('revision')!=157]
content['entries'].insert(0,entry)
path.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rule=ROOT/'rule/崩坏三-gtl (hk3gtl) 项目规则.md'
text=rule.read_text(encoding='utf-8-sig')
marker='### 2026-10-15 负责人最新决定：增强版2.7为唯一测试实例'
if marker not in text:
    text += f'''\n\n{marker}

【变更记录 #7】{stamp}（内测5修订157 · 测试实例纠正）
- 删除：无，保留历史规则；旧GregTech-Leisure-1.4.5.2及GTL十一周目作为当前测试目标的约束失效。
- 新增：后续部署、启动、成型、GUI、配方与内存验收唯一实例为 `C:\\Users\\OWNER\\AppData\\Roaming\\PrismLauncher\\instances\\GregTech Leisure-增强版 2.7\\minecraft`。
- 修改：优先将最新定稿内测5实装到此实例，再测试并优化整个整合包内存占用；不得用其他实例或裁剪第三方内容代替验收。
- 用途：为负责人之后与朋友联机试玩准备同一实际整合包；备份后可修复已证实的重复模组、资源兼容和内存配置，不将单人短测说成多人长时通过。
- 来源：负责人本轮原话“我们应该用以下实例……GregTech Leisure-增强版 2.7作为模组的测试……我们优先将模组弄到这里面，然后测试并且优化整个整合包的内存占用”。
- 本条优先于所有较早实例路径和部署记录。I14仍是候选，四个指定ZIP的已批准结构继续有效，不为性能缩小或重新设计。
'''
    rule.write_text(text,encoding='utf-8')
print(json.dumps({'revision':157,'time':stamp,'rule_updated':marker in rule.read_text(encoding='utf-8')},ensure_ascii=False))
