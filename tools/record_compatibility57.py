# -*- coding: utf-8 -*-
"""#1 2026-09-23 03:47:00: 记录本地兼容补丁及边界，不改业务代码。
Record the local compatibility patch and validation limits; no gameplay changes.
重复运行拒绝重复写入修订57。Refuse duplicate revision insertion.
"""
from datetime import datetime
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
now = datetime.now()
stamp = now.strftime('%Y-%m-%d %H:%M:%S')
log = root / 'src/main/resources/assets/hk3gtl/changelog.json'
data = json.loads(log.read_text(encoding='utf-8'))
assert not any(e.get('version') == '0.5.0' and e.get('revision') == 57 for e in data['entries'])
data['entries'].insert(0, dict(
    version='0.5.0', revision=57, codename='HK3GTL-内测5',
    date=now.strftime('%Y-%m-%d'), time=now.strftime('%H:%M:%S'),
    summary='记录GTLAdditions3.3升级后GTMAdvancedHatch的本地接口兼容补丁。',
    reason='旧附属调用已移除CommonUtils，导致GTCEu转换失败；新GTLCore提供同签名格式化方法。',
    changes=['工具仅修改指定SHA256的GTMAdvancedHatch旧接口引用，其他JAR条目逐字节核对不变',
             '替换为GTLCore NumberUtils.formatDouble；原附属完整备份，保留MIT元数据及资源',
             '不向HK3GTL注入第三方包名，不恢复GTLExtend，不全量同步实例；此补丁需要部署到实例附属JAR',
             '静态接口与归档完整性验证通过；游戏重启、JEI显示和研究采样仍需实机验收']))
log.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
body = f'''<section id="compatibility57"><h2>修订57：GTMAdvancedHatch旧接口兼容</h2>
<p>{stamp}，Asia/Hong_Kong。要求：对应更新已有依赖，移除开发环境GTLExtend，修复更新后无法启动的问题。</p>
<p>结论：crash-2026-09-23_03.40.32-fml.txt的直接异常是找不到
com.gtladd.gtladditions.utils.CommonUtils。逐JAR检查，引用来自GTMAdvancedHatch-1.20.1-0.1.10 fix2.jar
的GTRecipeWidgetMixin；仅用于EU/t与电压比值的文本格式化。</p>
<p>方案：仅把该类常量池的CommonUtils引用改为org.gtlcore.gtlcore.utils.NumberUtils。
两者都是静态formatDouble(double):String，采用千进制缩写与最多两位小数。显示统一采用当前GTLCore格式；
不改配方能耗或计算。新方法对极大值的后缀上限与旧实现不完全相同，但本调用输入来自long能耗与电压的比值。</p>
<p>新增：tools/patch_advanced_hatch57.py（默认生成候选，--apply备份并部署）、本记录与修订日志。
修改：实例附属JAR的单个类引用。删除：无。原包放在实例hk3gtl-mod-backups；不添加外国包名占位类。</p>
<p>验收：已核对目标API和javap调用指令；候选JAR只有一个条目变化，其余资源、许可证、内嵌依赖保持原样。
完整构建结果见build-compatibility57.log。此处静态修复不等于游戏启动、JEI或研究系统验收通过。</p>
<p>待确认：重启实例后是否还有后续兼容异常；进入世界后完成一次液态采样，检查RN-HED登记。
不采用批量删模组、降级GTLAdditions或禁用整套高级仓。既有运行中的客户端需重启才会使用新包。</p>
<p>来源：用户本地GTLAdditions3.3、已归档2.6.5Custom、GTLCore1.2.3.2-fix2、GTMAdvancedHatch fix2。
后者mods.toml标记MIT，本地补丁保留所有原版权与许可证条目；未上传第三方修改包。</p></section>'''
record = root / 'doc/HK3GTL-内测5/讨论记录' / (now.strftime('%Y-%m-%d_%H-%M') + '_GTLAdditions3.3与高级仓兼容修复.html')
record.parent.mkdir(parents=True, exist_ok=True)
record.write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>高级仓兼容修复</title><body>' + body + '</body></html>', encoding='utf-8')
report = root / 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
text = report.read_text(encoding='utf-8')
assert '</body>' in text
report.write_text(text.replace('</body>', body + '</body>'), encoding='utf-8')
print(record)
