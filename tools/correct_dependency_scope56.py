# -*- coding: utf-8 -*-
"""Revision56: undo bulk mirroring, retain corresponding updates and remove GTLExtend from development.
按负责人纠正范围：原libs对应包更新，额外镜像移出；GTLAdditions必需KFF保留。
"""
from pathlib import Path
from structure_delivery.project_paths import project_path
from datetime import datetime
import json,shutil,re
root=Path(__file__).resolve().parents[1]
now=datetime.now(); stamp=now.strftime('%Y-%m-%d_%H-%M-%S')
report=json.loads((root/'tools/dependency_sync_latest.json').read_text(encoding='utf-8'))
original='''appliedenergistics2-forge-15.4.10.jar
BuildingWands-forge-MC1.20.1-3.0.2.jar
cloth-config-11.1.136-forge.jar
constructionwand-1.20.1-2.11.jar
ExtendedAE-1.20-1.4.13-forge.jar
ftb-chunks-forge-2001.3.6.jar
ftb-essentials-forge-2001.2.4.jar
ftb-library-forge-2001.2.12.jar
ftb-quests-forge-2001.4.18.jar
ftb-teams-forge-2001.3.2.jar
ftb-ultimine-forge-2001.1.7.jar
ftb-xmod-compat-forge-2.1.3.jar
ftbbackups2-forge-1.20-1.0.23.jar
gtladditions-2.6.5Custom.jar
gtlcore-1.2.2.8-fix5.jar
GTLsupb-3.5.jar
gtmthings-1.3.5.fix.jar
Jade-1.20.1-Forge-11.13.2.jar
kubejs-forge-2001.6.5-build.16.jar
ldlib-forge-1.20.1-1.0.33.b.jar
Placebo-1.20.1-8.6.3.jar
polylib-forge-2000.0.3-build.143.jar
Re-Avaritia-forged-1.20.1-1.3.8.3.jar
rhino-forge-2001.2.3-build.10.jar
sgjourney-1.20.1-0.6.44.jar
Spear_of_Void-1.3.0fix4.jar
wmp-1.7.0.jar'''.splitlines()
mapping={x['old']:x['new'] for x in report['replacements']}
keep={mapping.get(name,name) for name in original}|{'kotlinforforge-4.11.0-all.jar'}
archive=root/'archive'/('dependency-scope-correction-'+stamp); archive.mkdir(parents=True)
for file in ['build.gradle','tools/sync_instance_dependencies.py','src/main/resources/assets/hk3gtl/changelog.json']:
    target=archive/file; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/file,target)
removed=[]
for file in (root/'libs').glob('*.jar'):
    if file.name not in keep:
        target=archive/'libs'/file.name; target.parent.mkdir(parents=True,exist_ok=True)
        assert file.resolve().parent==(root/'libs').resolve() and target.resolve().is_relative_to(archive.resolve())
        file.rename(target); removed.append(file.name)
assert {p.name for p in (root/'libs').glob('*.jar')}==keep
# Restore pre-mirroring dependency declarations, then apply only the matching JAR replacements.
s=(project_path(report['archive'])/'build.gradle').read_text(encoding='utf-8')
for old,new in mapping.items():s=s.replace(old,new).replace('dev:'+old[:-4]+'"','dev:'+new[:-4]+'"')
s=re.sub(r'^.*modImplementation\("dev:gtl_extend[^\n]*\n','',s,flags=re.M)
s=s.replace('modImplementation("dev:[星门之旅] Stargate Journey-1.20.1-0.6.44") { transitive = false }','modImplementation(files("libs/[星门之旅] Stargate Journey-1.20.1-0.6.44.jar"))')
s=re.sub(r'^.*forgeRuntimeLibrary\("org.jetbrains.kotlin:[^\n]*\n','',s,flags=re.M)
s=s.replace('// ── Kotlin 标准库（GTLAdditions 依赖） ──','// GTLAdditions 3.3 requires the KFF language provider and bundled Kotlin runtime.\n    modRuntimeOnly(files("libs/kotlinforforge-4.11.0-all.jar"))')
s=s.replace('modRuntimeOnly("curse.maven:jade-324717:5876199")','modRuntimeOnly(files("libs/Jade-1.20.1-Forge-11.13.3.jar"))')
s=s.replace('// 11.13.2 的 StringRenderOutputMixin 与 1.20.1 不兼容，回退到 11.12.2','// 对应原Jade依赖更新至实例11.13.3；旧配置保留于archive。 / Match the existing Jade dependency to the instance.')
s=s.replace('def requiredLocalModJars = [','def requiredLocalModJars = [\n        "kotlinforforge-4.11.0-all.jar",\n        "gtladditions-3.3.jar",\n        "gtlcore-1.2.3.2-fix2.jar",')
s+='\n// Change #8 '+stamp+' revision56: revert bulk dependency mirroring; remove GTLExtend; retain corresponding updates only.\n'
(root/'build.gradle').write_text(s,encoding='utf-8')
p=root/'src/main/resources/assets/hk3gtl/changelog.json'; d=json.loads(p.read_text(encoding='utf-8'))
d['entries'].insert(0,dict(version='0.5.0',revision=56,codename='HK3GTL-内测5',date=now.strftime('%Y-%m-%d'),time=now.strftime('%H:%M:%S'),summary='纠正依赖同步范围并移除开发环境GTLExtend。',reason='负责人仅要求对应更新，不要求全量镜像实例模组。',changes=['多余JAR和GTLExtend移出libs至archive','恢复原Maven依赖声明，只更新原本对应本地包；保留GTLAdditions3.3所需KFF','修正同步工具，后续只匹配已有libs依赖']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=dict(stamp=stamp,retained=sorted(keep),archived=removed,archive=str(archive))
(archive/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=root/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M')+'_依赖范围纠正与移除GTLExtend.html')
doc.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><h1>依赖范围纠正与移除GTLExtend</h1><p>变更记录#1 修订56 · '+stamp+' Asia/Hong_Kong</p><p>负责人明确纠正：只替换原有依赖对应版本，不复制整个实例；将GTLExtend从开发环境移除。执行：按此前工具输出的原libs清单保留对应新版，额外镜像及GTLExtend移至归档；恢复原Maven依赖声明，GTLAdditions所需KFF作为必要依赖保留。实例mods不参与本次清理。</p><p>保留28个JAR；移出'+str(len(removed))+'个JAR。归档：'+str(archive)+'</p><p>修改build.gradle、同步脚本、changelog及本记录。不存在GTLExtend Java引用。后续同步工具仅按已有libs对应匹配。验收为离线clean build与开发运行依赖核对；不以编译成功冒充游戏已启动。</p></html>',encoding='utf-8')
print('Retained',len(keep),'Archived',len(removed));print(archive);print(doc)
