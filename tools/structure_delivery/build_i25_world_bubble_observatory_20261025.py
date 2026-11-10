# -*- coding: utf-8 -*-
"""生成 I25 戴森天球解析仪的离线候选交付。"""
from __future__ import annotations

import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/structure_delivery"))
from build_redesign69 import export, render
from material_resources import Resources
from i25_world_bubble_observatory_geometry_20261025 import (
    CONTROL, PORT, QEV, W, H, D, audit, build,
)

OUT = ROOT / "deliveries/I25_世界泡坐标解析中心_量子天球研究院_重制首版_20261025"
STRUCTURE = OUT / "i25"
NAME = "hk3gtl-i25-world-bubble-observatory-20261025"
INSTANCE = Path.home() / "AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft"
VIEWER = ROOT / "deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22"
FONT = "C:/Windows/Fonts/msyh.ttc"


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec="seconds")


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resource_materials(states):
    resources = Resources(instance=INSTANCE, project_resources=ROOT / "src/main/resources")
    packs = []
    options = INSTANCE / "options.txt"
    if options.is_file():
        for line in options.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("resourcePacks:"):
                try:
                    packs = json.loads(line.partition(":")[2])
                except json.JSONDecodeError:
                    packs = []
                break
    try:
        for entry in packs:
            if not str(entry).startswith("file/"):
                continue
            archive_path = INSTANCE / "resourcepacks" / str(entry)[5:]
            if not archive_path.is_file():
                continue
            archive = zipfile.ZipFile(archive_path)
            resources.archives.append((archive_path, archive))
            for name in archive.namelist():
                if name.startswith("assets/"):
                    resources.index[name] = (archive_path, archive)
        result = []
        for state in states:
            material = resources.material(state)
            assert material["complete_cube"] and not material["tinted"], state
            result.append(material)
        return result, dict(resources.sources), packs
    finally:
        resources.close()


def report_images(data, materials, check):
    colors = {}
    for material in materials:
        texture = Image.open(io.BytesIO(base64.b64decode(material["faces"]["up"].split(",")[1]))).convert("RGB")
        colors[material["state"]] = tuple(round(value) for value in ImageStat.Stat(texture).mean)
    scale, left, top = 10, 70, 110
    image = Image.new("RGB", (W * scale + 470, D * scale + top + 60), "#111b2a")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 24)
    small = ImageFont.truetype(FONT, 17)
    draw.text((left, 25), "I25 · 戴森天球解析仪 · 实体俯视布局", font=font, fill="#e7f2f4")
    tops = {}
    for block in data["blocks"]:
        x, y, z = block["pos"]
        if (x, z) not in tops or y > tops[(x, z)][0]:
            tops[(x, z)] = (y, block["state"])
    for (x, z), (_, state) in tops.items():
        draw.rectangle((left + x * scale, top + z * scale, left + (x + 1) * scale - 1, top + (z + 1) * scale - 1), fill=colors[state])
    draw.rectangle((left - 1, top - 1, left + W * scale, top + D * scale), outline="#71818e", width=2)
    for item in [{"id": "主控", "pos": data["controller"]}, *data["ports"]]:
        x, y, z = item["pos"]
        px, pz = left + x * scale + 5, top + z * scale + 5
        draw.ellipse((px - 7, pz - 7, px + 7, pz + 7), fill="#ffe38a", outline="#1b2229", width=2)
        draw.line((px, pz, left + W * scale + 18, pz), fill="#a18e59", width=1)
    lx = left + W * scale + 35
    draw.text((lx, top), "设计构成", font=font, fill="#ffe2a0")
    lines = [
        f"{W} × {D} × {H}（宽×深×高）",
        "最低标准：41 × 49 × 33",
        f"{check['blocks']:,} 个实体方块",
        f"世界泡正球：直径{data['world_bubble_diameter']}格",
        f"戴森壳：半径{data['dyson_shell_radius']}格",
        f"截角二十面体：{data['dyson_shell_geometry']['pentagonal_faces']}五边形 + {data['dyson_shell_geometry']['hexagonal_faces']}六边形",
        f"连续观测口：{data['dyson_shell_geometry']['observation_aperture_faces']}面",
        "六路静态能量导束",
        "六层十二边研究裙座 + 六边轴承座",
        f"{len(check['palette'])} 种真实方块材料",
        f"QEV外壳 {check['outer_qev_shell_blocks']:,} > 玻璃 {check['glass_blocks']:,}",
        f"主控：整宽第{data['controller'][0] + 1}格",
        "端口齐平嵌入各舱外壳",
    ]
    for i, line in enumerate(lines):
        draw.text((lx, top + 45 + i * 32), line, font=small, fill="#c6d6dc")
    image.save(OUT / "俯视布局.png")

    items = [{"id": "CONTROLLER", "pos": data["controller"], "face": data["controller_face"]}, *data["ports"]]
    local = Image.new("RGB", (840, 90 + ((len(items) + 2) // 3) * 230), "#111b2a")
    ld = ImageDraw.Draw(local)
    ld.text((22, 18), f"主控与{len(data['ports'])}个接口 · 真实齐平替换", font=font, fill="#ffe2a0")
    occupied = {tuple(block["pos"]): block["state"] for block in data["blocks"]}
    for i, item in enumerate(items):
        x0 = 25 + (i % 3) * 270
        y0 = 75 + (i // 3) * 230
        x, y, z = item["pos"]
        ld.text((x0, y0), item["id"], font=small, fill="#ffe2a0")
        ld.text((x0, y0 + 27), str(item["pos"]), font=small, fill="#c6d6dc")
        for row in range(-2, 3):
            for col in range(-2, 3):
                if item["face"] in ("north", "south"):
                    pos = (x + col, y + row, z)
                else:
                    pos = (x, y + row, z + col)
                px, py = x0 + (col + 2) * 31, y0 + 58 + (2 - row) * 31
                state = occupied.get(pos)
                fill = colors.get(state, (20, 32, 43))
                ld.rectangle((px, py, px + 29, py + 29), fill=fill, outline="#5e6e76")
                if row == 0 and col == 0:
                    ld.rectangle((px + 2, py + 2, px + 27, py + 27), outline="#fff0ab", width=2)
    local.save(OUT / "主控与接口局部.png")


def viewer_page(data, check):
    page = (VIEWER / "三维评审.html").read_text(encoding="utf-8")
    title = html.escape(data["title"])
    controller_note = f"主控位于整宽{W}的第{data['controller'][0] + 1}格，齐平嵌入北侧分析舱外壳；{len(data['ports'])}个接口均为本体齐平替换。"
    palette_note = "主体采用QEV暖铜、石墨灰与钢蓝灰；青蓝透明整块只用于六路静态导束与少量刻度。"
    page = re.sub(r"<title>.*?</title>", f"<title>I25 · {title}</title>", page, count=1, flags=re.S)
    page = re.sub(r"<header>.*?</header>", f'<header><a href="../index.html">← I25交付总览</a><h1>I25 · {title} · 候选待审</h1><div>{W}×{D}×{H}（宽深高） · {check["blocks"]:,}方块 · 可旋转、剖切及逐口定位</div></header>', page, count=1, flags=re.S)
    page = re.sub(r'<div class="locator">.*?</div>', f'<div class="locator"><b>主控 {data["controller"]}</b><p>{controller_note}</p><p>黄色轮廓始终显示；钻石块是位置标记。</p><button data-view="controller">定位主控</button></div>', page, count=1, flags=re.S)
    page = re.sub(r'(<b id="layerValue">)\d+', rf'\g<1>{H - 1}', page, count=1)
    page = re.sub(r'<input id="layer"[^>]*>', f'<input id="layer" type="range" min="0" max="{H - 1}" value="{H - 1}">', page, count=1)
    page = re.sub(r'<details open><summary>本次结构修改</summary>.*?</details>', f'<details open><summary>本次结构修改</summary><p>黑色世界泡正球悬于截角二十面体戴森壳中央；外壳由12个五边形面与20个六边形面拼接，正面七面构成连续观测口。六路青蓝静态导束由球面伸向五边形采集节点，以疏落冰蓝脉冲和节点灯表示能量被牵引、汇集；这是建筑表达，不是动态模拟。底部改为六层十二边研究裙座、六边轴承座与六根共轴承力支柱，分析舱沿同一平台接入。{palette_note}{controller_note}</p></details>', page, count=1, flags=re.S)
    page = re.sub(r'<details><summary>结构文件与边界</summary>.*?</details>', f'<details><summary>结构文件与边界</summary><a href="{NAME}.nbt">NBT</a> · <a href="{NAME}.schem">Schematic</a> · <a href="设计与检查.json">记录</a><p>本版为待审建筑候选；已检查逐格结构、主控与接口位置、静态完整方块材质及导出一致性。未获外观批准，未接入正式Pattern、配方或实例；游戏运行与增强版2.9.2兼容性仍需单独验证。</p></details>', page, count=1, flags=re.S)
    page = re.sub(r'<!-- 变更记录#1：.*?-->', '<!-- I25戴森天球解析仪离线候选，不代表正式接入。 -->', page, count=1, flags=re.S)
    assert not any(stale in page for stale in ("I22", "I19", "WSV", "V14", "RN-WME", "沿用", "整版外观批准"))
    return page


def index_page(data, check):
    rows = "".join(f"<tr><td><code>{html.escape(state)}</code></td><td>{count:,}</td></tr>" for state, count in check["palette"].items())
    zones = "".join(f"<article><h3>{html.escape(zone['name'])}</h3><p>{html.escape(zone['description'])}</p></article>" for zone in data["zones"])
    benchmark = check["lower_tier_max_benchmark"]
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(data['title'])}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#0f1824;color:#e7eef2;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1440px;margin:auto;padding:28px}}header{{background:#182d3c;border-left:5px solid #63c7d1;padding:26px}}h1{{margin:0;line-height:1.45}}h2{{color:#a8e2e5}}a{{color:#9ce1ea}}.metrics,.zones{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:20px 0}}.metrics>div,article{{background:#182735;border:1px solid #334d5a;padding:15px}}.notice{{background:#2b3027;border-left:4px solid #c9ad63;padding:15px}}img{{display:block;max-width:100%;height:auto;margin:18px auto;background:#111b2a}}iframe{{width:100%;height:860px;border:1px solid #476370}}table{{border-collapse:collapse;width:100%}}td{{padding:8px;border-bottom:1px solid #334d5a}}code{{overflow-wrap:anywhere}}small{{color:#abc1c8}}@media(max-width:750px){{main{{padding:12px}}iframe{{height:660px}}}}</style></head><body><main>
<header><small>HK3GTL / I25 / 量子天球研究院</small><h1>{html.escape(data['title'])}</h1><p>直径{data['world_bubble_diameter']}格的黑色正球悬于截角二十面体戴森采样壳内；六路青蓝静态导束从球面引至五边形采集节点。下方六层十二边研究裙座、六边轴承座与共轴支柱承接整套观测设施。</p></header>
<div class="metrics"><div><b>{W} × {D} × {H}</b><br>宽×深×高；内测5最低41×49×33</div><div><b>{check['blocks']:,} 方块</b><br>实体方块数高于{html.escape(benchmark['structure'])}的{benchmark['block_count']:,}块基准</div><div><b>QEV / V07</b><br>外壳 {check['outer_qev_shell_blocks']:,} 块；玻璃 {check['glass_blocks']:,} 块</div><div><b>{len(check['palette'])}种材料</b><br>{html.escape(benchmark['structure'])}材料基准：{benchmark['materials']}种</div></div>
<p class="notice">本版为戴森天球解析仪建筑候选，不写正式 Pattern、不接入实例；I24异常谱与I44信号进入后，I25只输出有效坐标或无效/误差记录，实际锁定仍由I44负责。</p>
<p><a href="i25/三维评审.html">打开三维评审</a> · <a href="i25/{NAME}.nbt">NBT</a> · <a href="i25/{NAME}.schem">Schematic</a> · <a href="verification.json">结构检查</a> · <a href="设计依据.json">设计依据</a></p>
<img src="i25/等轴预览.png" alt="I25戴森天球解析仪实际逐格材质等轴预览">
<h2>主体构成</h2><p>黑色世界泡是悬于天球中央的等径正球样本；12个五边形测量节点与20个六边形屏蔽面构成截角二十面体采样壳，正面七面开口显露样本。六条青蓝整块玻璃导束自球面伸向五边形采集节点，间隔冰蓝脉冲和端点灯形成由内向外的能量牵引读向；这是静态建筑表现，不代表动态吸能或已验证机器功能。深钢灰五边形使用装配线机壳，浅钢灰六边形使用强固机壳，QEV暖铜棱梁逐面连接。底部为六层十二边研究裙座、六边轴承座和六根共轴支柱，外圈分析舱接入同一承载平台；不作放射分区换色，也不捕获、不锁定、不生成世界泡。</p>
<h2>俯视布局与分区</h2><img src="俯视布局.png" alt="戴森天球解析仪实体俯视布局"><div class="zones">{zones}</div>
<h2>控制器与接口</h2><p>主控坐标 {data['controller']}，位于整宽{W}的第{data['controller'][0] + 1}格，齐平嵌入承轴基座外壳。{len(data['ports'])}个工业接口自然嵌入设备本体；每个标记周围保留四面连续QEV、内侧计算背板和外侧四格净空。</p><img src="主控与接口局部.png" alt="主控与接口真实材质局部"><p>结构文件使用 <code>minecraft:diamond_block</code> 表示主控位置，使用 <code>hk3gtl:industrial_port_casing</code> 表示接口位置；预览显示它们各自真实方块纹理，黄色框只用于定位。</p>
<h2>离线三维评审</h2><iframe src="i25/三维评审.html" title="I25戴森天球解析仪三维评审" loading="lazy"></iframe>
<h2>材料统计</h2><table>{rows}</table><p><small>材质来自当前增强版实例及项目源码资源；只核验静态完整立方体模型，不声称动态光照、配方、生存获取或游戏内运行已经通过。</small></p>
<p><a href="i25/设计与检查.json">逐格设计与检查</a> · <a href="manifest.json">候选清单</a> · <a href="资源来源.json">资源来源</a></p><footer><small>生成时间：{check['time']}（Asia/Hong_Kong） · 状态：candidate_waiting_user_review · 未部署到实例。</small></footer></main></body></html>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    STRUCTURE.mkdir(parents=True, exist_ok=True)
    data = build()
    data["name"] = NAME
    data["title"] = "世界泡坐标解析中心·戴森天球解析仪"
    assert data["size"] == [W, H, D]
    check = audit(data)
    states = sorted({block["state"] for block in data["blocks"]})
    materials, source_map, packs = resource_materials(states)
    states, groups, hashes = export(data, STRUCTURE)
    assert all((STRUCTURE / f"{NAME}.{suffix}").is_file() for suffix in ("nbt", "schem"))
    for suffix in ("nbt", "schem"):
        (STRUCTURE / f"hk3gtl-i25-world-bubble-singularity-cutaway-20261025.{suffix}").unlink(missing_ok=True)
    payload = {"data": {key: value for key, value in data.items() if key != "blocks"}, "palette": states,
               "groups": groups, "materials": materials, "audit": check, "names": {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9)).decode("ascii")
    (STRUCTURE / "data.js").write_text("window.HK3_PAYLOAD=" + json.dumps(encoded) + ";\n", encoding="utf-8")
    decoded = json.loads(gzip.decompress(base64.b64decode(encoded)))
    decoded_cells = {((idx % W), (idx // (W * D)), ((idx // W) % D)): state
                     for state, group in zip(decoded["palette"], decoded["groups"]) for idx in group}
    assert decoded_cells == {tuple(block["pos"]): block["state"] for block in data["blocks"]}
    check.update({"time": now(), "hashes": hashes, "material_resource_sources": source_map,
                  "enabled_file_resource_packs": packs, "material_complete_cube": all(m["complete_cube"] and not m["tinted"] for m in materials),
                  "nbt_schem_viewer_exact_cell_readback": True, "approval": "待用户审阅，不计入已批准批次",
                  "deployment_eligible": False, "deployment_policy": "实例已更新到增强版2.9.2；本版仅为建筑候选，批准后另行验证并接入。"})
    render(data, materials, STRUCTURE, round_spheres=True)
    report_images(data, materials, check)
    shutil.copy2(VIEWER / "viewer.bundle.js", STRUCTURE / "viewer.bundle.js")
    (STRUCTURE / "三维评审.html").write_text(viewer_page(data, check), encoding="utf-8")
    save(STRUCTURE / "设计与检查.json", {"data": {key: value for key, value in data.items() if key != "blocks"}, "audit": check})
    save(OUT / "设计依据.json", [
        {"path": "doc/HK3GTL-内测5/03_机器结构/内测5_69座多方块逐台占地规划与比例预览_v2.html", "fact": "I25最低标准41×49×33（宽×深×高）；设计按最低标准扩展。"},
        {"path": "doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json", "fact": "I25分析I24异常谱和I44增强信号，输出有效或无效坐标记录，不负责实际锁定。"},
        {"path": "doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html", "fact": "结构外壳按QEV/V07映射制作。"},
        {"path": "doc/HK3GTL-内测5/03_机器结构/I01-I24设计交付", "fact": "参考既有多方块的体量、留白、材质与自然接口规则，不复制旧I25轮廓。"},
        {"path": "rule/当前多方块设计规则.md", "fact": "主控居中、接口融合本体、材料用量按构件功能分配；非完整块仅按负责人授权用于少量细节并须真实预览。"},
    ])
    save(OUT / "资源来源.json", {"instance": str(INSTANCE), "project_resources": str(ROOT / "src/main/resources"), "packs": packs, "states": source_map})
    save(OUT / "manifest.json", {"generator": Path(__file__).name, "key": "i25", "title": data["title"],
        "candidate_version": data["candidate_version"], "status": "candidate_waiting_user_review", "candidate_approved": False,
        "target_voltage": "QEV", "target_voltage_mapping": "V07", "size_xyz": data["size"], "size_wdh": [W, D, H],
        "baseline_wdh": [41, 49, 33], "block_count": check["blocks"], "controller": data["controller"],
        "ports": data["ports"], "palette": check["palette"], "unique_material_count": len(check["palette"]),
        "structure_name": NAME, "nbt_file": f"i25/{NAME}.nbt", "schem_file": f"i25/{NAME}.schem",
        "world_bubble_diameter": data["world_bubble_diameter"], "dyson_shell_radius": data["dyson_shell_radius"],
        "dyson_shell_geometry": data["dyson_shell_geometry"], "world_bubble_anchor": data["world_bubble_anchor"],
        "energy_extraction": data["energy_extraction"],
        "bubble_shell_blocks": check["bubble_shell_blocks"],
        "outer_qev_shell_blocks": check["outer_qev_shell_blocks"], "glass_blocks": check["glass_blocks"],
        "lower_tier_max_benchmark": check["lower_tier_max_benchmark"],
        "nbt_sha256": hashes["nbt"], "schem_sha256": hashes["schem"],
        "claim_boundary": "仅建筑候选；未部署、未获批准、未声称Pattern、配方、生存或游戏运行通过。"})
    save(OUT / "verification.json", check)
    script_dir = OUT / "生成脚本"
    script_dir.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), script_dir / Path(__file__).name)
    shutil.copy2(ROOT / "tools/structure_delivery/i25_world_bubble_observatory_geometry_20261025.py", script_dir / "i25_world_bubble_observatory_geometry_20261025.py")
    (OUT / "index.html").write_text(index_page(data, check), encoding="utf-8")
    bundle = OUT.with_suffix(".zip")
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(OUT.parent).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        assert all(archive.read(path.relative_to(OUT.parent).as_posix()) == path.read_bytes() for path in OUT.rglob("*") if path.is_file())
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    bundle.with_suffix(".zip.sha256").write_text(digest + "\n", encoding="ascii")
    print(json.dumps({"out": str(OUT), "size_xyz": data["size"], "blocks": check["blocks"], "palette": check["palette"], "zip_sha256": digest, "verified": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
