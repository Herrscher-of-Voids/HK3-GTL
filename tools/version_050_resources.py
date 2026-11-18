# -*- coding: utf-8 -*-
"""Revision53: UTF-8 branding resources; preserve historical entries and identifiers.
修订53：更新当前版本显示信息，不改历史版本文本及注册ID。
"""
from pathlib import Path
from datetime import datetime
import json
now=datetime.now(); stamp=now.strftime('%Y-%m-%d %H:%M:%S')
for lang in ['zh_cn','en_us']:
    p=Path('src/main/resources/assets/hk3gtl/lang')/(lang+'.json')
    d=json.loads((Path('archive/version-0.5.0-before')/p).read_text(encoding='utf-8'))
    d['hk3gtl.welcome.title']='HK3GTL-内测5'
    d['itemGroup.hk3gtl.main']='HK3GTL-内测5'
    d['hk3gtl.welcome.intro']='欢迎参与 HK3GTL-内测5。请在反馈问题时附上版本、复现步骤和截图。' if lang=='zh_cn' else 'Welcome to HK3GTL Beta 5. Please include the version, reproduction steps and screenshots when reporting issues.'
    d['hk3gtl.welcome.release.0_5_0.title']='HK3GTL-内测5 · 0.5.0'
    d['hk3gtl.welcome.release.0_5_0.1']='研究终端新增100段连续故事、开题条件诊断与材料预览。' if lang=='zh_cn' else 'Research terminal: 100 linked story chapters, start-condition diagnostics and material previews.'
    d['hk3gtl.welcome.release.0_5_0.2']='研究系统仍在开发，后续课题的实验接入尚未全部完成。' if lang=='zh_cn' else 'Research is still in development; experimental evidence integration for later topics is incomplete.'
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('src/main/resources/assets/hk3gtl/changelog.json')
d=json.loads((Path('archive/version-0.5.0-before')/p).read_text(encoding='utf-8'))
d['entries'].insert(0,dict(version='0.5.0',revision=53,codename='HK3GTL-内测5',date=stamp[:10],time=stamp[11:],summary='按负责人要求统一版本与显示名。',reason='正式使用0.5.0与HK3GTL-内测5作为当前开发版本标识。',changes=['Gradle版本0.5.0，Forge显示名HK3GTL-内测5','同步欢迎页、创造页签与发布产物名称','部署脚本改用hk3gtl-0.5.0.jar；旧历史记录和注册ID保留']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('doc/HK3GTL-内测5/讨论记录')/(now.strftime('%Y-%m-%d_%H-%M')+'_版本与模组名称统一.html')
p.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>版本与模组名称统一</title>
<h1>版本与模组名称统一</h1><p>变更记录#1 修订53 · STAMP Asia/Hong_Kong</p>
<p>负责人明确要求并授权：版本改为0.5.0，模组显示名称改为HK3GTL-内测5。</p>
<p>修改文件：gradle.properties、tools/deploy_research_terminal.py、中英语言文件与changelog.json；tools/version_050_resources.py记录资源同步方式。欢迎页、创造标签及构建产物名称同步。mods.toml沿用Gradle变量展开。modId继续为hk3gtl以兼容存档。旧版记录保留，不批量改写历史文本。来源为负责人本次指令，无第三方资源或许可新增。</p>
<p>验收：离线clean build、JAR内部META-INF/mods.toml精确核对名称和版本；部署至指定Prism实例，旧JAR归档以避免重复modId。游戏需要重启加载新版本。没有设计未决项；版本号变更不代表此前未完成的研究功能已经完成。</p></html>'''.replace('STAMP',stamp),encoding='utf-8')
print(p)
