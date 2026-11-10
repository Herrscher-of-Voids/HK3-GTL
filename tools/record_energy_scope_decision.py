# -*- coding: utf-8 -*-
"""记录能源扩展授权与六份规则读取身份，不更改正式游戏资源。
【变更记录 #1】2026-10-19 12:23:43（香港时间，文档批次172）
删除：无；新增：真实时间、规则指纹和负责人原答复的HTML记录。
修改：历史能源阻塞页仅追加覆盖关系；用途：保留旧范围与新授权的可追溯边界。
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/energy-production-r172'
RULES = ['rules.md', '系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md',
         'hk3gtl java文件变更备注规范.md', '当前多方块设计规则.md', '巨构提示词.txt']


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat(timespec='seconds')
    LOG.mkdir(parents=True, exist_ok=True)
    identity = LOG / '续接规则读取身份.json'
    previous = json.loads(identity.read_text(encoding='utf-8')) if identity.exists() else None
    data = {'read_at': stamp, 'context_gatherer': '当前可用工具中未提供；实际文件、源码及独立代理核对替代',
            'files': [{'path': str(ROOT/'rule'/name), 'bytes': (ROOT/'rule'/name).stat().st_size,
                       'sha256': hashlib.sha256((ROOT/'rule'/name).read_bytes()).hexdigest()} for name in RULES],
            'history': ([previous] if previous else []),
            '_record': f'【记录 #1】{stamp}：新增六规则全文读取指纹；仅接续凭据，不计业务完成。'}
    identity.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    title = '能源扩展真实燃料工艺与15条独立配方范围确认'
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{now:%Y-%m-%d_%H-%M-%S}_{title}.html'
    assert not discussion.exists()
    question = ('能源系统目前有规格冲突：只允许普通／浓缩两类燃料，同时要求每台反应堆至少15条独立配方。'
                '完整差距已列在 logs/energy-production-r171/能源生产整系统阻塞审计与闭环决策_r171.html。'
                '最终按哪种范围推进？这需要你决定，因为会改变燃料范围或15条验收要求；我会继续其他可开发系统。')
    answer = '扩展真实燃料工艺，仍要求每台15条独立配方；新贴图另行审批'
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>body{{max-width:1040px;margin:30px auto;padding:0 24px;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;color:#193b45;background:#eff5f4}}header{{padding:24px;background:#173e47;color:white}}section{{padding:18px 24px;background:white;margin:16px 0;border:1px solid #ccdadd}}a{{color:#126978}}blockquote{{border-left:4px solid #367b76;padding:12px 18px;background:#eef8f6}}</style></head><body><header><h1>{title}</h1><p>{stamp} · Asia/Hong_Kong（UTC+08:00）</p></header><section><h2>用户实际答复</h2><p>原提问：{html.escape(question)}</p><blockquote>{answer}</blockquote><p>本记录采用实际生成时间。原答复精确发送时间未知，不以本时间冒充发送时间。</p></section><section><h2>当前已确认</h2><p>允许扩展有实际物质、制备、燃烧、热量与废物后果、回收用途的崩坏能燃料工艺；I19、I20、I21、I22各自仍至少15条真正独立的可执行配方。仅改变数量、工时、EU/t、电路或元数据的变体不计数。普通与浓缩燃料继续保留，原12条工业线继续保留。</p><p>新增物品的设计沿用已有授权；新增或修改物品贴图必须另行提交候选审批。本次燃料范围答复不批准新方块、机壳、反应堆建筑、控制器或Pattern。</p></section><section><h2>覆盖关系与实际执行</h2><p>覆盖先前“反应堆永远只保留普通/浓缩两类燃料”的范围上限；保留历史原文作为当时状态。当前正式游戏包仍为修订171。本轮能源扩展正处于可审核候选合同编制，不把设计数量当成已注册运行配方，不提高能源系统2/16能力分数。</p><p>并行生成21形态电压主色候选；已经批准的原结构归档和正式资源保持原字节，需用户确认新候选后再替换。</p></section><section><h2>证据与下一步</h2><p><a href="../../../logs/energy-production-r171/能源生产整系统阻塞审计与闭环决策_r171.html#scope-approved">历史阻塞及新决定追加</a> · <a href="../../../logs/energy-production-r172/续接规则读取身份.json">六份规则读取凭据</a> · <a href="../09_测试发布/内测5全库逐份代码文档对照审计_20261017.html#energy_production">现有全系统审计</a></p><p>把不同燃料来源、制备、热量、尾气/乏料、净损耗及回收路线放入同一批次合同，逐项查证目标2.9实际原料来源，再送审新贴图。建筑审批、代码能力、单人/多人运行与最后整包内存验收分别记账。</p></section><footer>【记录 #1】{stamp}：删除无；新增负责人真实答复与旧范围覆盖关系；用途为防止接续时再次把已解决的燃料范围写成阻塞。</footer></body></html>'''
    discussion.write_text(page, encoding='utf-8')
    old = ROOT/'logs/energy-production-r171/能源生产整系统阻塞审计与闭环决策_r171.html'
    source = old.read_text(encoding='utf-8')
    marker = 'id="scope-approved"'
    if marker not in source:
        addition = f'<section class="box" id="scope-approved"><h2>负责人范围决定追加 · {stamp}</h2><div class="good">用户实际答复：“{answer}”。燃料扩展范围冲突已解决，选择上文路线B。</div><p>本页早先关于两类燃料上限的文字为01:43历史状态，当前已被本决定覆盖。仍保留每台15条独立配方验收；新贴图和未批准反应堆结构分别审批，代码、真实产电IO和热管理缺口仍存在，能源分数维持2/16。</p><p>【追加记录 #2】{stamp}：删除无；新增用户答复与覆盖关系；修改当前阻塞为工艺候选、结构审批和实际实现，防止继续重复询问已确认范围。</p></section>'
        source = source.replace('</main></body>', addition+'</main></body>')
        old.write_text(source, encoding='utf-8')
    print(json.dumps({'discussion':str(discussion),'recorded_at':stamp},ensure_ascii=False))


if __name__ == '__main__':
    main()
