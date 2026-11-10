# -*- coding: utf-8 -*-
"""Revision54 2026-09-23: output-hook registration, bilingual notification and HTML audit.
注册实际输出兼容钩子，记录字节码证据与验证边界；不读取或改写玩家存档。
"""
from pathlib import Path
from datetime import datetime
import json
now=datetime.now(); stamp=now.strftime('%Y-%m-%d %H:%M:%S')
p=Path('src/main/resources/hk3gtl.mixins.json'); d=json.loads(p.read_text(encoding='utf-8'))
if 'Hk3ResearchOutputMixin' not in d['mixins']: d['mixins'].append('Hk3ResearchOutputMixin')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for lang,text in [('zh_cn','首次液态崩坏能采样已记录：可返回研究所开始「崩坏能识别」。'),('en_us','First liquid Honkai sample recorded: return to the institute to start Honkai Energy Detection.')]:
    p=Path('src/main/resources/assets/hk3gtl/lang')/(lang+'.json'); d=json.loads(p.read_text(encoding='utf-8'))
    d['hk3gtl.research.sampling_recorded']=text
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('src/main/resources/assets/hk3gtl/changelog.json'); d=json.loads(p.read_text(encoding='utf-8'))
d['entries'].insert(0,dict(version='0.5.0',revision=54,codename='HK3GTL-内测5',date=stamp[:10],time=stamp[11:],summary='修复GTLCore真实液态采样输出未登记研究实验。',reason='实际实例GTLCore的onRecipeFinish使用RecipeRunnerHelper.handleRecipeOutput，绕过原handleRecipeIO监听。',changes=['新增Hk3ResearchOutputMixin监听handleRecipeOutput成功返回','原生GTCEu和GTLCore共用幂等精确ID结算入口，首次登记提示玩家','保持真实产出要求，不扫描库存补发凭据，不改变支付或研究完成状态']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('doc/HK3GTL-内测5/讨论记录')/(now.strftime('%Y-%m-%d_%H-%M')+'_液态采样实验记录兼容修复.html')
p.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>液态采样实验记录兼容修复</title>
<h1>液态采样实验记录兼容修复</h1><p>变更记录#1 修订54 · STAMP Asia/Hong_Kong</p>
<h2>要求与证据</h2><p>负责人提供输出仓204500mB液态崩坏能截图，研究所仍无法检测。按实际Prism实例GTLCore 1.2.3.2-fix2字节码核对：RecipeLogicMixin.onRecipeFinish调用RecipeRunnerHelper.handleRecipeOutput，未经过采集塔原handleRecipeIO覆盖方法。因此成功产出与实验记录脱节。</p>
<h2>执行方案</h2><p>在GTLCore真实输出方法的RETURN true处调用采集塔公共结算入口，保留精确初采配方ID、在线归属及首信情报检查。原生GTCEu路径继续兼容，共用recordExperiment的幂等逻辑，首次登记才通知。没有改变输入、输出、耗电、研究点或研究完成状态。没有复制第三方实现。</p>
<h2>涉及文件</h2><ul><li>Hk3ResearchOutputMixin.java（新增）</li><li>Hk3HonkaiAbsorptionMachine.java（追加备注#5与共用结算入口）</li><li>hk3gtl.mixins.json</li><li>zh_cn.json、en_us.json、changelog.json</li><li>tools/research_output_hook54.py</li></ul>
<h2>验证与后续</h2><p>静态核对旧开发依赖与实际实例方法签名一致；实际实例方法返回值是提交输出结果，并非模拟匹配。执行clean build及现有研究回归；检查产物含Mixin配置与类后部署。重启实例后让当前塔再成功完成一轮初采，观察首次记录提示，再尝试研究所开题。已有液体保留，无须倒掉或重建。旧库存不能证明历史来源，故不按库存量自动补发。未宣称实际实例修复后已通过验收。</p>
<h2>来源与归档</h2><p>用户截图及指定实例GTLCore JAR的只读字节码检查；不新增美术资源或第三方许可内容。原文件保留在archive/research-output-hook-revision54。无设计未决项，游戏运行验证待进行。</p></html>'''.replace('STAMP',stamp),encoding='utf-8')
print(p)
