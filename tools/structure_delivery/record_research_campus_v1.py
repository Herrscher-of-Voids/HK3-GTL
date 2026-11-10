# -*- coding: utf-8 -*-
"""以最终核验记录生成本轮中文讨论记录，不改生产及游戏实例。"""
import datetime
import html
import json
from build_research_campus_additive_v1 import OUT, LOG, ZIP_NAME
from redesign69_geometry import ROOT


def main():
    entries = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    verification = json.loads((LOG/'final-verification.json').read_text(encoding='utf-8'))
    review = json.loads((LOG/'independent-review.json').read_text(encoding='utf-8'))
    assert verification['passed'] and review['passed']
    assert verification['archive_sha256'] == review['archive']['sha256']
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    articles = []
    for e in entries:
        w, h, d = e['size']
        audit = json.loads((OUT/e['key']/'设计与检查.json').read_text(encoding='utf-8'))['audit']
        data = json.loads((OUT/e['key']/'blueprint.json').read_text(encoding='utf-8'))
        sources = '，'.join(f'{k}：{v:,}块（{audit["namespace_percent"][k]}%）' for k, v in audit['namespace_counts'].items())
        ports = '；'.join(f'{p["id"]}={p["pos"]}，{p["purpose"]}，朝北' for p in data['ports'])
        articles.append(f'<section><h2>{e["key"].upper()} · {e["title"]}</h2><p>{html.escape(e["description"])}</p><p>尺寸：{w}×{d}×{h}（宽×深×高），{e["blocks"]:,}块。普通建材：{sources}；另含主控钻石块1、工业接口占位6。</p><p>局部主控及粘贴锚点：{e["controller"]}；Schematic Offset：{[-v for v in e["controller"]]}。局部原点[0,0,0]，推荐底部世界Y=-60。</p><p>接口占位：{ports}。工业接口壳为本项目当前约定的外观占位，不是可工作仓室。</p><p>各材质实际用量、资源出处和完整立方体核验见交付中的设计与检查.json；未声明生存配方已验证。</p></section>')
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>研究所五阶原地扩建重设计</title><style>body{max-width:1150px;margin:40px auto;padding:0 28px;background:#101b24;color:#e8f0f2;font:16px/1.9 'Microsoft YaHei',sans-serif}h1,h2{color:#b5dfd1}section{border-top:1px solid #3d5261;padding:16px 0}a{color:#add7ee}code{overflow-wrap:anywhere}p{overflow-wrap:anywhere}</style></head><body>'''
    page += f'<h1>研究所五阶：原地扩建重设计</h1><p>记录时间：{now.isoformat()}</p>'
    page += '<p>用户本轮认可现有四阶崩坏能采集塔，并要求五阶研究所也按同样方式逐级原地扩建，允许参考超算中心、研究院和中科院风格并自由设计。</p>'
    page += '<p>I01 V8四阶已单独原字节确认归档，4个形态仍只计作1台机器。S01–S05本轮均为待确认外观候选，未计入批准部署批次。</p>'
    page += '<p>名称沿用2026-09-28用户已确认的崩坏现象研究所、物质重构研究所、量子域研究所、世界维系研究所、文明认知穹顶。建筑从白色水平窗带实验楼，扩展为双翼、中庭、超算/档案院区、退台分院与液冷中心，最终形成外围知识分馆及透光资料穹顶。</p>'
    page += '<p>参考调查如实记录于建筑参考.json：已打开CSCS官方建筑事实表入口；本次PDF/照片页超时，中科院检索未得到适合直接采用的具体建筑资料，因此本稿不宣称复制任何特定机构建筑或使用其技术指标。</p>'
    page += ''.join(articles)
    page += '<section><h2>扩建、文件与验证</h2><p>以世界主控为同一锚点。四次升级前阶非主控方块的相对位置和状态均保持，删除或改写数均为0。六接口保留原位；结构六面连通；尺寸使用实际占用边界并逐轴达到总表下限。</p><p>NBT由Lodestone重新导出，DataVersion=3465；Sponge v2、blueprint、压缩预览载荷逐格回读一致；完整立方体材质从GTL十一周目资源及项目现有方块资源核验。五阶实际浏览器载入、旋转、俯视、剖切及接口近景已检查；独立只读审查通过。</p><p>通道有实体地板及两格以上净高，入口采用静态人物步行/跳步图复核。高架资料桥及升降核属于明确标注的服务空间，未把模型升降核声明为游戏内真实可工作的电梯。</p><p>当前仅为设计交付，未接入正式Pattern、配方或进行Minecraft成型与运行验收；本轮材料不限生存阶段，未声明生存配方可达。</p>'
    page += f'<p>结构包：{ZIP_NAME}；{verification["archive_bytes"]:,}字节；SHA256：<code>{verification["archive_sha256"]}</code>。</p>'
    page += '<p><a href="http://127.0.0.1:8369/index.html">五阶研究所预览</a></p></section></body></html>'
    target = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_研究所五阶原地扩建重设计.html')
    target.write_text(page, encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
