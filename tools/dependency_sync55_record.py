# -*- coding: utf-8 -*-
"""Revision55 records exact local dependency provenance and archived replacements.
记录依赖更新来源、哈希、旧包归档和新增必需依赖；不变更玩法。
"""
from pathlib import Path
from datetime import datetime
import json,html,hashlib
now=datetime.now(); stamp=now.strftime('%Y-%m-%d %H:%M:%S')
r=json.loads(Path('tools/dependency_sync_latest.json').read_text(encoding='utf-8'))
kff=Path('libs/kotlinforforge-4.11.0-all.jar')
r['additional_required_dependency']=dict(file=kff.name,source='https://cdn.modrinth.com/data/ordsPcFz/versions/hmeyC41q/kotlinforforge-4.11.0-all.jar',sha256=hashlib.sha256(kff.read_bytes()).hexdigest(),reason='GTLAdditions 3.3 requires kotlinforforge >=4.11.0; absent in original instance')
Path('tools/dependency_sync_latest.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('src/main/resources/assets/hk3gtl/changelog.json'); data=json.loads(p.read_text(encoding='utf-8'))
data['entries']=[e for e in data['entries'] if e.get('revision')!=55]
data['entries'].insert(0,dict(version='0.5.0',revision=55,codename='HK3GTL-内测5',date=stamp[:10],time=stamp[11:],summary='同步实例最新模组并升级GTLAdditions至3.3。',reason='负责人指定下载JAR优先，实例mods作为项目依赖基准。',changes=['84个实例外部模组复制并校验SHA256，11个旧本地包归档替换','开发依赖更新GTLCore、GTMThings、ExtendedAE、FTB、KubeJS、JEI和Jade','补齐GTLAdditions3.3硬依赖Kotlin for Forge4.11.0，核对官方发行SHA512','保留项目独有的2个JAR，不加入HK3GTL自身循环依赖；历史包移至archive']))
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('gradle.properties'); s=p.read_text(encoding='utf-8'); s+='\n# Change #2 '+stamp+' revision55: align KubeJS with instance build.26; Gradle uses explicit local runtime jars.\n'; p.write_text(s,encoding='utf-8')
doc='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>实例依赖同步与GTLAdditions3.3更新</title><style>body{max-width:1100px;margin:auto;padding:30px;font:16px/1.8 sans-serif;background:#111827;color:#e5e7eb}td,th{border:1px solid #43526a;padding:8px}table{border-collapse:collapse}code{overflow-wrap:anywhere}</style>'
doc+='<h1>实例依赖同步与GTLAdditions 3.3更新</h1><p>变更记录#1 修订55 · '+stamp+' Asia/Hong_Kong</p>'
doc+='<h2>要求与确认</h2><p>负责人要求将下载的gtladditions-3.3.jar更新进项目，并将指定Prism实例mods里的最新模组复制到libs替换旧包。按modId匹配，下载GTLAdditions优先，实例作为其他模组来源；不根据文件名猜版本。</p>'
doc+='<h2>替换清单</h2><table><tr><th>旧包（已归档）</th><th>当前包</th></tr>'+''.join('<tr><td>'+html.escape(x['old'])+'</td><td>'+html.escape(x['new'])+'</td></tr>' for x in r['replacements'])+'</table>'
doc+='<p>同步84个外部模组，逐个校验SHA256。HK3GTL自身排除，避免循环依赖。项目独有保留：'+html.escape(', '.join(r['retained']))+'。</p>'
doc+='<h2>必要依赖与来源</h2><p>GTLAdditions3.3要求GTLCore≥1.2.3.2-fix2及Kotlin for Forge≥4.11.0。前者来自实例；实例没有后者，故从Modrinth发行API获取4.11.0原始JAR，核对SHA512后复制到libs与实例。来源：<a href="'+r['additional_required_dependency']['source']+'">Kotlin for Forge 4.11.0</a>。第三方JAR保持原样及许可声明；GTLAdditions声明LGPLv3.0。</p>'
doc+='<h2>构建范围与未决</h2><p>build.gradle同步已有依赖的实际来源与版本，gradle.properties同步KubeJS版本；不将84个包括客户端性能模组在内的全部镜像自动装入开发运行时。移除单独的旧Kotlin运行库，改用完整KFF发行包。首轮clean遇到Loom缓存写入冲突，重试构建成功；最终资源记录更新后再次clean build。编译通过不代表新版依赖在实际游戏内完成验收，需重启实例确认。</p>'
doc+='<h2>归档与文件</h2><p>'+html.escape(r['archive'])+'</p><p>实例旧GTLAdditions：'+html.escape(r['instance_backup'])+'</p><p>变更文件：libs/*.jar、build.gradle、gradle.properties、changelog.json、tools/sync_instance_dependencies.py、tools/dependency_sync_latest.json、tools/dependency_sync55_record.py及本HTML。完整来源与哈希见tools/dependency_sync_latest.json。</p></html>'
p=Path('doc/HK3GTL-内测5/讨论记录')/(now.strftime('%Y-%m-%d_%H-%M')+'_实例依赖同步与GTLAdditions33更新.html'); p.write_text(doc,encoding='utf-8'); print(p)
