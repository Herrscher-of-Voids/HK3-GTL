"""变更#1 2026-09-28：追加本轮交付及讨论记录，保留此前提案正文。"""
from pathlib import Path
import datetime,json
ROOT=Path(__file__).resolve().parents[2]
now=datetime.datetime.now().astimezone();stamp=now.strftime('%Y-%m-%d %H:%M:%S %z')
folder=ROOT/'doc/HK3GTL-内测5/03_机器结构'
page=folder/'机器与文明级奇观.html'
marker='redesign69-built-preview01'
text=page.read_text(encoding='utf-8')
section=f'''<section id="{marker}" style="padding:18px;border:2px solid #59bfb7;margin:18px 0"><h2>69座实体预览与详细方案 · 首版待审</h2><p>{stamp}。已按本页草案生成69份逐格结构、69个三维评审页与69份详细施工草案。下方早期文字的“尚未生成”是当时状态，当前以本次交付为准；正式结构接入仍待审批。</p><p><a href="69座重设计_实体预览01/index.html">打开全部69座预览与详细方案</a> · <a href="69座重设计_实体预览01/研究所总览.png">研究所总览</a> · <a href="69座重设计_实体预览01/奇观-1总览.png">奇观总览一</a> · <a href="69座重设计_实体预览01/奇观-2总览.png">奇观总览二</a></p><p>每台补充设备分区坐标与尺寸、围护和维护面、实体管线折点、材料ID与数量、主控接口及检修规划。全部宽长高逐轴达到总表下限，S01–S04正式名称仍待定。</p><p>检查边界：已导出并回读NBT/Sponge全部位置状态，已检查静态资源和分组图；未进行浏览器交互、游戏成型或性能测试。第一版中部分工业塔体与机房相似、奇观立面细节仍需建筑评审。H01复用既有舰体并换材、抬高，非从零全新舰体，旧体素含333个六邻域孤立方块，未擅自删除。</p><p>变更记录#实体预览1：追加实际交付入口，保留历史草案，不修改正式Pattern。</p></section>'''
if marker not in text:
 text=text.replace('<section id="redesign69-20260928">',section+'<section id="redesign69-20260928">',1)
 page.write_text(text,encoding='utf-8')
record=ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_69座逐格预览与详细方案交付.html')
validation=json.loads((ROOT/'logs/structure-redesign-20260928/preview01/validation.json').read_text(encoding='utf-8'))
record.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>69座预览与施工方案讨论记录</title><style>body{{max-width:1100px;margin:40px auto;background:#131e2b;color:#e4eef7;font:16px/1.8 'Microsoft YaHei'}}a{{color:#9ee8df}}</style><h1>69座预览与施工方案</h1><p>记录时间：{stamp}。这是本轮整理时间，不冒称用户消息原始时间。</p><h2>用户要求</h2><blockquote>直接按照重设计草图搭建69台机器预览，并将每台方案描述得更详细，便于后续搭建。</blockquote><h2>沿用的已确认约束</h2><ul><li>69座总表为范围；表外旧机器只列清单。</li><li>每次制作结构先阅读巨构提示词；宽、长、高逐轴不得低于占地总表。</li><li>主控正面中轴居中；白色外框，框内除主控外均为接口候选，最多两层。</li><li>统一整齐地板；提前预留检修通道；使用双包实际材质。</li><li>S01–S04正式命名待用户确定；预览授权不等于生产结构批准。</li></ul><h2>本轮实际产物</h2><p>69座逐格数据、69张材质等轴图、69份原版NBT、69份Sponge v2、69个三维页、69份详细方案，另有8张分组总览。总计{validation['blocks']:,}个实体位置，30种方块状态（含主控及接口两种标记），即28种普通建材。</p><p>生成器、查看器及检查脚本位于 tools/structure_delivery。详细说明与预览共享坐标和材料数据。H01复用现有舰体坐标，换完整方块材质并整体抬高5格；其他68座从本轮功能分区生成。</p><h2>实际检查</h2><p>69项ID与总表一致，实际尺寸检查、NBT和Sponge全部位置状态回读、压缩数据解码、坐标唯一性与范围、139页本地依赖检查通过。查看器和打包脚本JS语法检查通过。已查看覆盖69座的8张静态总览，并复查修正后的曲面。修复S05穹顶与I24/I34/W01观测盘阶梯曲面断裂；现有H01的333个六邻域孤立体素保留并明确列出。</p><h2>未确认与未验证</h2><p>这些是第一轮实体建筑草稿；部分塔体与机房轮廓偏相似，奇观细节与维护合理性需用户评审。未批准正式Pattern替换，未启动游戏，未部署，未进行浏览器交互或性能实测。静态图使用实际材质首帧投影，不是游戏截图。</p><p><a href="../03_机器结构/69座重设计_实体预览01/index.html">69座预览入口</a> · <a href="../../../logs/structure-redesign-20260928/preview01/validation.json">自动检查结果</a></p></html>''',encoding='utf-8')
print(str(record))
