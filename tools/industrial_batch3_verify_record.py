"""Append actual batch 3 build evidence; documentation only. 批次3实际验证补记。"""
from pathlib import Path
from datetime import datetime
root = Path(__file__).resolve().parents[1]
stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
files = [root / 'doc/HK3GTL-内测5/09_测试发布/理之核心批次3实现与验收.html',
         root / 'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html',
         root / 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html']
for path in files:
    text = path.read_text(encoding='utf-8')
    section = '<section><h2>批次3构建验收补记</h2><p>'+stamp+'：clean build --offline通过，17项构建任务执行。新版研究、首信、注视度5/5、任务迁移8场景测试通过。已核对产物包含研究类、目录、核心模型、两份语言及revision41，不含根目录archive。完整日志：build-beta5-batch3.log。仍有85项旧API弃用警告；未运行整包验证Mixin与GUI，未安装到Prism实例。产物保留0.4.0-beta.1旧版本标识，仅作开发验证。</p><p>追加验证结果，不改变上述未完成事项。</p></section>'
    path.write_text(text.replace('</body>', section+'</body>'), encoding='utf-8')
print('Appended actual build and artifact evidence.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
