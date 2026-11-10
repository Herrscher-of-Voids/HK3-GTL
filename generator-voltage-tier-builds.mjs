#!/usr/bin/env node
/**
 * GTL 电压阶段工业文明建筑生成器
 * 为每个电压阶段生成代表性建筑，展示该阶段的核心材料、方块与工业风格
 *
 * 输出：32 个 .schem 文件 (Steam→MAX→HBV→CEV)
 */

import { Structure, BlockState } from '@mattzh72/lodestone'
import { writeFileSync, readFileSync, mkdirSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const OUTPUT_DIR = join(__dirname, 'deliveries', 'voltage-tier-builds-' + new Date().toISOString().slice(0,10).replace(/-/g,''))

// 加载电压阶段系列配置
const seriesPath = join(__dirname, 'deliveries', 'gtl-voltage-20260929', 'series.json')
const SERIES = JSON.parse(readFileSync(seriesPath, 'utf8'))

console.log(`已加载 ${SERIES.length} 个阶段配置`)

// 构建 API：在结构中设置方块
function setBlock(structure, pos, blockId, properties = {}, nbt = undefined) {
  const [x, y, z] = pos.map(v => Math.trunc(v))
  const hasProps = properties && Object.keys(properties).length > 0
  const name = hasProps ? `${blockId}[${Object.entries(properties).map(([k,v]) => `${k}=${v}`).join(',')}]` : blockId
  structure.addBlock([x, y, z], blockId, hasProps ? properties : undefined, nbt)
}

function fill(structure, from, to, blockId, properties, nbt) {
  const [x0, y0, z0] = from.map(Math.trunc)
  const [x1, y1, z1] = to.map(Math.trunc)
  const [xMin, xMax] = [Math.min(x0,x1), Math.max(x0,x1)]
  const [yMin, yMax] = [Math.min(y0,y1), Math.max(y0,y1)]
  const [zMin, zMax] = [Math.min(z0,z1), Math.max(z0,z1)]
  for (let x = xMin; x <= xMax; x++) {
    for (let y = yMin; y <= yMax; y++) {
      for (let z = zMin; z <= zMax; z++) {
        setBlock(structure, [x, y, z], blockId, properties, nbt)
      }
    }
  }
}

function hollowBox(structure, from, to, blockId, properties, nbt) {
  const [x0, y0, z0] = from.map(Math.trunc)
  const [x1, y1, z1] = to.map(Math.trunc)
  const [xMin, xMax] = [Math.min(x0,x1), Math.max(x0,x1)]
  const [yMin, yMax] = [Math.min(y0,y1), Math.max(y0,y1)]
  const [zMin, zMax] = [Math.min(z0,z1), Math.max(z0,z1)]
  for (let x = xMin; x <= xMax; x++) {
    for (let y = yMin; y <= yMax; y++) {
      for (let z = zMin; z <= zMax; z++) {
        const onEdge = x === xMin || x === xMax || y === yMin || y === yMax || z === zMin || z === zMax
        if (onEdge) setBlock(structure, [x, y, z], blockId, properties, nbt)
      }
    }
  }
}

// 形状模板
const SHAPES = {
  // Steam (00): 棚屋 - 小型作坊
  shed: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 地基
    fill(s, [0,0,0], [w-1,0,d-1], pal.secondary)
    // 墙体
    hollowBox(s, [0,1,0], [w-1,h-2,d-1], pal.main)
    // 烟囱角柱
    fill(s, [1,1,1], [1,h-1,1], pal.accent)
    fill(s, [w-2,1,d-2], [w-2,h-1,d-2], pal.accent)
    // 管道横梁
    fill(s, [2,2,1], [w-3,2,1], pal.pipe)
    fill(s, [2,2,d-2], [w-3,2,d-2], pal.pipe)
    // 屋顶框架
    for (let i = 2; i < w-2; i += 2) {
      setBlock(s, [i,h-1,2], pal.pipe)
      setBlock(s, [i,h-1,d-3], pal.pipe)
    }
  },

  // ULV (01): 庭院 - 开放式工作区
  courtyard: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 地板带围墙低基
    fill(s, [0,0,0], [w-1,0,d-1], pal.main)
    hollowBox(s, [0,1,0], [w-1,1,d-1], pal.secondary)
    // 四角支柱
    for (const [x,z] of [[1,1], [w-2,1], [1,d-2], [w-2,d-2]]) {
      fill(s, [x,2,z], [x,h-1,z], pal.accent)
    }
    // 管道横框
    fill(s, [2,3,1], [w-3,3,1], pal.pipe)
    fill(s, [2,3,d-2], [w-3,3,d-2], pal.pipe)
    fill(s, [1,3,2], [1,3,d-3], pal.pipe)
    fill(s, [w-2,3,2], [w-2,3,d-3], pal.pipe)
    // 顶部框架
    hollowBox(s, [1,h-1,1], [w-2,h-1,d-2], pal.secondary)
  },

  // LV (02): 锯齿 - 斜顶厂房
  sawtooth: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 地基
    fill(s, [0,0,0], [w-1,1,d-1], pal.main)
    // 侧墙
    hollowBox(s, [0,2,0], [w-1,h-3,d-1], pal.secondary)
    // 锯齿形柱阵
    for (let x = 2; x < w-2; x += 3) {
      fill(s, [x,2,2], [x,h-2,2], pal.accent)
      fill(s, [x,2,d-3], [x,h-2,d-3], pal.accent)
    }
    // 管道走廊
    fill(s, [3,3,1], [w-4,3,1], pal.pipe)
    fill(s, [3,h-2,d/2], [w-4,h-2,d/2], pal.pipe)
    // 齿轮箱夹层
    for (let x = 4; x < w-4; x += 4) {
      setBlock(s, [x,h/2,d/2], pal.accent)
    }
  },

  // MV (03): 双塔 - 对称反应塔
  twins: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2)
    // 地基平台
    fill(s, [0,0,0], [w-1,1,d-1], pal.secondary)
    // 左塔
    hollowBox(s, [3,2,3], [cx-3,h-2,d-4], pal.main)
    fill(s, [4,3,4], [4,h-3,4], pal.accent)
    // 右塔
    hollowBox(s, [cx+2,2,3], [w-4,h-2,d-4], pal.main)
    fill(s, [w-5,3,4], [w-5,h-3,4], pal.accent)
    // 中央连接走廊
    fill(s, [cx-2,h/2,d/2-1], [cx+1,h/2+1,d/2], pal.pipe)
    // 管道束
    for (let y = 3; y < h-2; y += 2) {
      setBlock(s, [5,y,d/2], pal.pipe)
      setBlock(s, [w-6,y,d/2], pal.pipe)
    }
  },

  // HV (04): 阶梯 - 多层加工平台
  terraces: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 三层阶梯
    for (let tier = 0; tier < 3; tier++) {
      const y0 = tier * Math.floor(h/3)
      const y1 = y0 + Math.floor(h/3) - 1
      const inset = tier * 2
      hollowBox(s, [inset,y0,inset], [w-1-inset,y1,d-1-inset], pal.main)
      // 每层角柱
      for (const [x,z] of [[inset+1,inset+1], [w-2-inset,d-2-inset]]) {
        fill(s, [x,y0,z], [x,y1,z], pal.accent)
      }
    }
    // 管道连接各层
    const cx = Math.floor(w/2)
    fill(s, [cx,0,d/2], [cx,h-1,d/2], pal.pipe)
    // 格栅装饰
    for (let x = 2; x < w-2; x += 3) {
      setBlock(s, [x,h/2,1], pal.accent)
    }
  },

  // EV (05): 十字 - 四向对称结构
  cruciform: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 中央核心塔
    hollowBox(s, [cx-3,0,cz-3], [cx+3,h-1,cz+3], pal.secondary)
    fill(s, [cx-1,1,cz-1], [cx+1,h-2,cz+1], pal.main)
    // 四向臂
    for (const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]) {
      const arm_len = Math.floor(Math.min(w,d)/2) - 4
      for (let i = 4; i < 4+arm_len; i++) {
        const x = cx + dx*i, z = cz + dz*i
        hollowBox(s, [x-1,h/3,z-1], [x+1,h/3+2,z+1], pal.pipe)
        if (i % 3 === 0) setBlock(s, [x,h/3+1,z], pal.accent)
      }
    }
    // 玻璃观察窗
    if (pal.glass) {
      for (let y = h/2-1; y <= h/2+1; y++) {
        setBlock(s, [cx-2,y,cz], pal.glass)
        setBlock(s, [cx+2,y,cz], pal.glass)
      }
    }
  },

  // IV (06): 装配线 - 长条生产线
  assembly: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 底座
    fill(s, [0,0,0], [w-1,1,d-1], pal.secondary)
    // 主框架 - 长边墙
    hollowBox(s, [0,2,0], [w-1,h-2,d-1], pal.main)
    // 装配线单元 - 沿长轴重复
    for (let x = 3; x < w-3; x += 4) {
      // 工位框架
      hollowBox(s, [x,2,d/2-2], [x+2,h-3,d/2+2], pal.accent)
      // 管道支架
      fill(s, [x+1,3,1], [x+1,3,d-2], pal.pipe)
      // 玻璃观察窗
      if (pal.glass) {
        setBlock(s, [x+1,h/2,d/2-1], pal.glass)
        setBlock(s, [x+1,h/2,d/2+1], pal.glass)
      }
    }
    // 顶部轨道
    fill(s, [2,h-1,d/2], [w-3,h-1,d/2], pal.pipe)
  },

  // LuV (07): 环 - 环形加速器/反应堆
  ring: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    const r = Math.min(cx, cz) - 3
    // 地基
    fill(s, [0,0,0], [w-1,1,d-1], pal.secondary)
    // 环形主体
    for (let x = 0; x < w; x++) {
      for (let z = 0; z < d; z++) {
        const dist = Math.sqrt((x-cx)**2 + (z-cz)**2)
        if (Math.abs(dist - r) < 1.5) {
          fill(s, [x,2,z], [x,h/2,z], pal.main)
          if (Math.abs(dist - r) < 0.7) {
            setBlock(s, [x,h/2+1,z], pal.accent)
          }
        }
      }
    }
    // 超导线圈节点
    const nodes = 8
    for (let i = 0; i < nodes; i++) {
      const angle = (i / nodes) * 2 * Math.PI
      const x = Math.round(cx + r * Math.cos(angle))
      const z = Math.round(cz + r * Math.sin(angle))
      fill(s, [x,2,z], [x,h-2,z], pal.accent)
    }
    // 玻璃观察段
    if (pal.glass) {
      for (let i = 0; i < nodes; i++) {
        const angle = (i / nodes + 0.5/nodes) * 2 * Math.PI
        const x = Math.round(cx + r * Math.cos(angle))
        const z = Math.round(cz + r * Math.sin(angle))
        setBlock(s, [x,h/2,z], pal.glass)
      }
    }
  },

  // ZPM (08): 双环 - 聚变反应堆
  'double-ring': (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    const r1 = Math.min(cx, cz) - 4
    const r2 = r1 * 0.6
    // 外环
    for (let x = 0; x < w; x++) {
      for (let z = 0; z < d; z++) {
        const dist = Math.sqrt((x-cx)**2 + (z-cz)**2)
        if (Math.abs(dist - r1) < 1.2) {
          fill(s, [x,h/3,z], [x,h/3+2,z], pal.main)
        }
        if (Math.abs(dist - r2) < 1) {
          fill(s, [x,h/2,z], [x,h/2+2,z], pal.secondary)
        }
      }
    }
    // 聚变线圈
    if (pal.accent) {
      for (let i = 0; i < 12; i++) {
        const angle = (i/12) * 2 * Math.PI
        const x = Math.round(cx + r1 * Math.cos(angle))
        const z = Math.round(cz + r1 * Math.sin(angle))
        fill(s, [x,0,z], [x,h-1,z], pal.accent)
      }
    }
    // 聚变玻璃
    if (pal.glass) {
      for (let i = 0; i < 8; i++) {
        const angle = (i/8 + 0.5/8) * 2 * Math.PI
        const x = Math.round(cx + r2 * Math.cos(angle))
        const z = Math.round(cz + r2 * Math.sin(angle))
        setBlock(s, [x,h/2+1,z], pal.glass)
      }
    }
  },

  // UV (09): 王冠 - 辐射状对称尖塔
  crown: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 中央塔
    hollowBox(s, [cx-2,0,cz-2], [cx+2,h-1,cz+2], pal.secondary)
    fill(s, [cx-1,h/2,cz-1], [cx+1,h-2,cz+1], pal.main)
    // 六棱尖刺
    const spikes = 6
    const baseR = Math.min(cx, cz) - 5
    for (let i = 0; i < spikes; i++) {
      const angle = (i/spikes) * 2 * Math.PI
      const x = Math.round(cx + baseR * Math.cos(angle))
      const z = Math.round(cz + baseR * Math.sin(angle))
      // 尖刺柱
      for (let dy = 0; dy < h/2; dy++) {
        const shrink = Math.floor(dy / 3)
        const x0 = x - (1-shrink), x1 = x + (1-shrink)
        const z0 = z - (1-shrink), z1 = z + (1-shrink)
        if (x0 <= x1 && z0 <= z1) {
          fill(s, [x0,h/2+dy,z0], [x1,h/2+dy,z1], pal.accent)
        }
      }
      // 连接梁
      const steps = Math.max(Math.abs(x-cx), Math.abs(z-cz))
      for (let t = 0; t <= steps; t++) {
        const bx = Math.round(cx + (x-cx)*t/steps)
        const bz = Math.round(cz + (z-cz)*t/steps)
        setBlock(s, [bx,h/2-1,bz], pal.pipe)
      }
    }
    // 玻璃顶盖
    if (pal.glass) {
      for (let dx = -3; dx <= 3; dx++) {
        for (let dz = -3; dz <= 3; dz++) {
          if (Math.abs(dx) + Math.abs(dz) <= 4) {
            setBlock(s, [cx+dx,h-1,cz+dz], pal.glass)
          }
        }
      }
    }
  },

  // UHV (10): 龙门架 - 大型起重结构
  gantry: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 双轨基座
    fill(s, [0,0,0], [w-1,1,d-1], pal.secondary)
    fill(s, [2,2,0], [2,2,d-1], pal.pipe)
    fill(s, [w-3,2,0], [w-3,2,d-1], pal.pipe)
    // 门架立柱
    for (let z = 4; z < d-4; z += Math.floor(d/4)) {
      // 左柱
      fill(s, [1,0,z], [1,h-2,z], pal.main)
      fill(s, [3,0,z], [3,h-2,z], pal.main)
      // 右柱
      fill(s, [w-2,0,z], [w-2,h-2,z], pal.main)
      fill(s, [w-4,0,z], [w-4,h-2,z], pal.main)
      // 横梁
      fill(s, [3,h-2,z], [w-4,h-2,z], pal.accent)
      fill(s, [4,h-3,z], [w-5,h-3,z], pal.pipe)
    }
    // 高能外壳装饰
    for (let x = 5; x < w-5; x += 4) {
      setBlock(s, [x,h/2,d/2], pal.accent)
    }
  },

  // UEV (11): 螺旋 - 双螺旋塔
  spiral: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    const r = Math.min(cx, cz) - 4
    // 中央轴
    fill(s, [cx,0,cz], [cx,h-1,cz], pal.secondary)
    // 双螺旋
    const turns = 3
    for (let y = 0; y < h; y++) {
      const angle1 = (y/h) * turns * 2 * Math.PI
      const angle2 = angle1 + Math.PI
      const x1 = Math.round(cx + r * Math.cos(angle1))
      const z1 = Math.round(cz + r * Math.sin(angle1))
      const x2 = Math.round(cx + r * Math.cos(angle2))
      const z2 = Math.round(cz + r * Math.sin(angle2))
      setBlock(s, [x1,y,z1], pal.main)
      setBlock(s, [x2,y,z2], pal.main)
      // QFT 线圈节点
      if (y % 5 === 0) {
        setBlock(s, [x1,y,z1], pal.accent)
        setBlock(s, [x2,y,z2], pal.accent)
      }
    }
    // 连接横撑
    for (let y = Math.floor(h/4); y < h; y += Math.floor(h/4)) {
      hollowBox(s, [cx-r,y,cz-r], [cx+r,y,cz+r], pal.pipe)
    }
  },

  // UIV (12): 传送门 - 对称拱门
  portal: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 基座平台
    fill(s, [0,0,0], [w-1,2,d-1], pal.secondary)
    // 门框立柱（避免超出边界）
    const pillarW = Math.min(Math.floor(w/3), cx-5)
    fill(s, [cx-pillarW,3,cz-2], [cx-pillarW,h-8,cz+2], pal.main)
    fill(s, [cx+pillarW,3,cz-2], [cx+pillarW,h-8,cz+2], pal.main)
    // 拱顶（限制高度避免溢出）
    const archR = pillarW
    for (let x = cx-archR; x <= cx+archR; x++) {
      const offset = Math.abs(x - cx)
      const dy = Math.round(Math.sqrt(Math.max(0, archR**2 - offset**2)))
      const targetY = h - 8 + dy
      if (targetY < h && dy > 0) {
        fill(s, [x,targetY,cz-1], [x,targetY,cz+1], pal.main)
      }
    }
    // 重力子约束装置
    for (let y = h/2; y < h-10; y += 3) {
      setBlock(s, [cx-archR,y,cz], pal.accent)
      setBlock(s, [cx+archR,y,cz], pal.accent)
    }
    // 聚变玻璃填充
    if (pal.glass) {
      for (let y = h/2; y < h-10; y++) {
        for (let x = cx-archR+2; x <= cx+archR-2; x++) {
          setBlock(s, [x,y,cz], pal.glass)
        }
      }
    }
  },

  // UXV (13): 三叉 - 三向分支
  triad: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 中央核心
    hollowBox(s, [cx-3,0,cz-3], [cx+3,h-1,cz+3], pal.secondary)
    fill(s, [cx-1,h/2,cz-1], [cx+1,h-2,cz+1], pal.main)
    // 三个分支塔（120度间隔）
    const branches = 3
    const branchLen = Math.floor(Math.min(w,d)/2) - 6
    for (let i = 0; i < branches; i++) {
      const angle = (i/branches) * 2 * Math.PI + Math.PI/6
      const dx = Math.cos(angle), dz = Math.sin(angle)
      for (let j = 5; j < 5+branchLen; j++) {
        const x = Math.round(cx + dx*j)
        const z = Math.round(cz + dz*j)
        hollowBox(s, [x-1,h/3,z-1], [x+1,h/3+4,z+1], pal.main)
        if (j % 4 === 0) {
          setBlock(s, [x,h/3+2,z], pal.accent)
        }
      }
      // 终端 QFT 线圈
      const ex = Math.round(cx + dx*(5+branchLen))
      const ez = Math.round(cz + dz*(5+branchLen))
      fill(s, [ex,h/3,ez], [ex,h/3+4,ez], pal.accent)
    }
    // 管道连接
    for (let i = 0; i < branches; i++) {
      const angle = (i/branches) * 2 * Math.PI + Math.PI/6
      const x = Math.round(cx + 4*Math.cos(angle))
      const z = Math.round(cz + 4*Math.sin(angle))
      fill(s, [cx,h/2,cz], [x,h/2,z], pal.pipe)
    }
  },

  // OpV (14): 恒星 - 放射状对称核心
  stellar: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 核心球体（近似）
    const coreR = 4
    for (let x = cx-coreR; x <= cx+coreR; x++) {
      for (let y = h/2-coreR; y <= h/2+coreR; y++) {
        for (let z = cz-coreR; z <= cz+coreR; z++) {
          const dist = Math.sqrt((x-cx)**2 + (y-h/2)**2 + (z-cz)**2)
          if (dist <= coreR) {
            setBlock(s, [x,y,z], pal.main)
          }
          if (Math.abs(dist - coreR) < 0.7) {
            setBlock(s, [x,y,z], pal.secondary)
          }
        }
      }
    }
    // 12条辐射射线
    const rays = 12
    const rayLen = Math.min(cx, cz) - 6
    for (let i = 0; i < rays; i++) {
      const angle = (i/rays) * 2 * Math.PI
      const dx = Math.cos(angle), dz = Math.sin(angle)
      for (let j = coreR+1; j < coreR+rayLen; j++) {
        const x = Math.round(cx + dx*j)
        const z = Math.round(cz + dz*j)
        fill(s, [x,h/2-1,z], [x,h/2+1,z], pal.accent)
        // 恒星约束外壳节点
        if (j % 5 === 0) {
          hollowBox(s, [x-1,h/2-2,z-1], [x+1,h/2+2,z+1], pal.secondary)
        }
      }
    }
    // 聚变玻璃护罩
    if (pal.glass) {
      for (let y = h/2-coreR-1; y <= h/2+coreR+1; y++) {
        const ringR = coreR + 2
        for (let i = 0; i < rays; i++) {
          const angle = (i/rays + 0.5/rays) * 2 * Math.PI
          const x = Math.round(cx + ringR * Math.cos(angle))
          const z = Math.round(cz + ringR * Math.sin(angle))
          setBlock(s, [x,y,z], pal.glass)
        }
      }
    }
  },

  // MAX (15): 嵌套 - 多层嵌套结构
  nested: (s, pal) => {
    const [w, h, d] = s.getSize()
    const layers = 4
    for (let layer = 0; layer < layers; layer++) {
      const inset = layer * 3
      const y0 = layer * Math.floor(h/layers)
      const y1 = (layer+1) * Math.floor(h/layers) - 1
      hollowBox(s, [inset,y0,inset], [w-1-inset,y1,d-1-inset],
                layer % 2 === 0 ? pal.main : pal.secondary)
      // 角柱
      if (layer < layers-1) {
        fill(s, [inset+1,y0,inset+1], [inset+1,y1,inset+1], pal.accent)
        fill(s, [w-2-inset,y0,d-2-inset], [w-2-inset,y1,d-2-inset], pal.accent)
      }
    }
    // 中央穿透管道
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    fill(s, [cx,0,cz], [cx,h-1,cz], pal.pipe)
    // 次元桥接外壳
    for (let layer = 1; layer < layers; layer++) {
      const y = layer * Math.floor(h/layers)
      const inset = layer * 3
      for (let x = inset+3; x < w-inset-3; x += 4) {
        setBlock(s, [x,y,d/2], pal.accent)
      }
    }
  },

  // HBV+ (16-30): 使用简化模板
  // 海渊 (16-19): 深层结构
  intake: (s, pal) => {
    SHAPES.nested(s, pal)
    const [w,h,d] = s.getSize()
    // 添加深度感的垂直通道
    for (let x = 3; x < w-3; x += 4) {
      fill(s, [x,1,d/2-1], [x,h-2,d/2-1], pal.pipe)
    }
  },

  // 海渊 HCV (17): 壁垒 - 防御堡垒
  bastion: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 厚实外墙
    hollowBox(s, [0,0,0], [w-1,h-1,d-1], pal.main)
    hollowBox(s, [1,1,1], [w-2,h-2,d-2], pal.secondary)
    // 四角塔楼
    for (const [x,z] of [[2,2], [w-3,2], [2,d-3], [w-3,d-3]]) {
      fill(s, [x,0,z], [x+2,h-1,z+2], pal.accent)
    }
    // 中央通道
    fill(s, [w/2-2,0,2], [w/2+2,h/2,d-3], 'minecraft:air')
  },

  // 海渊 HRV (18): 谐振器 - 音叉状结构
  resonator: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2)
    // 基座
    fill(s, [0,0,0], [w-1,2,d-1], pal.secondary)
    // 双叉臂
    fill(s, [cx-Math.floor(w/4),3,d/2-2], [cx-Math.floor(w/4),h-2,d/2+2], pal.main)
    fill(s, [cx+Math.floor(w/4),3,d/2-2], [cx+Math.floor(w/4),h-2,d/2+2], pal.main)
    // 连接横梁
    for (let y = h/2; y < h-3; y += 4) {
      fill(s, [cx-Math.floor(w/4),y,d/2], [cx+Math.floor(w/4),y,d/2], pal.pipe)
    }
    // 谐振节点
    for (let y = 5; y < h-2; y += 6) {
      setBlock(s, [cx-Math.floor(w/4),y,d/2], pal.accent)
      setBlock(s, [cx+Math.floor(w/4),y,d/2], pal.accent)
    }
  },

  // 海渊 HDV (19): 倒塔 - 倒置金字塔
  inverted: (s, pal) => {
    const [w, h, d] = s.getSize()
    for (let y = 0; y < h; y++) {
      const shrink = Math.floor(y * Math.min(w,d) / (3*h))
      if (shrink < Math.min(w,d)/2 - 2) {
        hollowBox(s, [shrink,y,shrink], [w-1-shrink,y,d-1-shrink], pal.main)
      }
    }
    // 中央支柱
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    fill(s, [cx,0,cz], [cx,h-1,cz], pal.accent)
  },

  // 虚数 QSV (20): 双焦 - 双焦点椭圆
  bifocal: (s, pal) => {
    const [w, h, d] = s.getSize()
    const f1x = Math.floor(w*0.3), f2x = Math.floor(w*0.7)
    const cz = Math.floor(d/2)
    // 两个焦点核心
    fill(s, [f1x-2,h/2-2,cz-2], [f1x+2,h/2+2,cz+2], pal.main)
    fill(s, [f2x-2,h/2-2,cz-2], [f2x+2,h/2+2,cz+2], pal.main)
    // 椭圆环（简化）
    const a = (f2x - f1x) * 1.3
    const b = a * 0.7
    const cx = Math.floor(w/2)
    for (let angle = 0; angle < 2*Math.PI; angle += 0.2) {
      const x = Math.round(cx + a * Math.cos(angle))
      const z = Math.round(cz + b * Math.sin(angle))
      if (x >= 0 && x < w && z >= 0 && z < d) {
        fill(s, [x,h/2-1,z], [x,h/2+1,z], pal.secondary)
      }
    }
    // 连接梁
    fill(s, [f1x,h/2,cz], [f2x,h/2,cz], pal.pipe)
  },

  // 虚数 QCV (21): 透镜 - 光学聚焦结构
  lens: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 双凸透镜轮廓（简化为柱）
    for (let x = cx-Math.floor(w/3); x <= cx+Math.floor(w/3); x++) {
      const offset = Math.abs(x - cx)
      const thick = Math.max(2, 6 - Math.floor(offset/3))
      fill(s, [x,h/2-thick,cz-2], [x,h/2+thick,cz+2], pal.main)
    }
    // 光轴管道
    fill(s, [0,h/2,cz], [w-1,h/2,cz], pal.pipe)
    // 聚焦点
    setBlock(s, [cx,h/2,cz], pal.accent)
  },

  // 虚数 QEV (22): 纠缠 - 量子纠缠对
  entangled: (s, pal) => {
    const [w, h, d] = s.getSize()
    const q1x = Math.floor(w*0.25), q2x = Math.floor(w*0.75)
    const cz = Math.floor(d/2)
    // 两个量子核心
    for (let dy = -3; dy <= 3; dy++) {
      for (let dz = -3; dz <= 3; dz++) {
        if (Math.abs(dy) + Math.abs(dz) <= 4) {
          setBlock(s, [q1x,h/2+dy,cz+dz], pal.main)
          setBlock(s, [q2x,h/2+dy,cz+dz], pal.main)
        }
      }
    }
    // 纠缠波动连接
    for (let x = q1x; x <= q2x; x++) {
      const wave = Math.round(3 * Math.sin((x-q1x) / (q2x-q1x) * 4 * Math.PI))
      setBlock(s, [x,h/2+wave,cz], pal.pipe)
    }
    // 稳定框架
    hollowBox(s, [q1x-5,h/2-5,cz-5], [q1x+5,h/2+5,cz+5], pal.secondary)
    hollowBox(s, [q2x-5,h/2-5,cz-5], [q2x+5,h/2+5,cz+5], pal.secondary)
  },

  // 虚数 QAV (23): 方尖碑 - 高耸锥体
  obelisk: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    for (let y = 0; y < h; y++) {
      const ratio = (h - y) / h
      const size = Math.floor(Math.min(w,d) * ratio / 3)
      if (size > 0) {
        hollowBox(s, [cx-size,y,cz-size], [cx+size,y,cz+size], pal.main)
      }
    }
    // 核心能量柱
    fill(s, [cx,0,cz], [cx,h-1,cz], pal.accent)
    // 铭文层
    for (let y = h/4; y < h; y += h/8) {
      const size = Math.floor(Math.min(w,d) * (h-y) / h / 3)
      if (size > 0) {
        hollowBox(s, [cx-size,y,cz-size], [cx+size,y,cz+size], pal.secondary)
      }
    }
  },

  // 量子 IMV (24): 港口 - 多停靠平台
  harbor: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 主码头
    fill(s, [0,0,0], [w-1,3,d-1], pal.secondary)
    // 三个停靠位
    for (let i = 0; i < 3; i++) {
      const z = Math.floor(d * (i+1) / 4)
      // 停靠桥墩
      hollowBox(s, [w/2-6,4,z-4], [w/2+6,h/2,z+4], pal.main)
      // 能源接口
      fill(s, [w/2-1,h/2+1,z-1], [w/2+1,h/2+3,z+1], pal.accent)
      // 连接通道
      fill(s, [4,4,z], [w-5,4,z], pal.pipe)
    }
  },

  // 量子 ICV (25): 编织 - 交错网格
  weave: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 纵向线
    for (let x = 3; x < w-3; x += 4) {
      for (let z = 3; z < d-3; z += 4) {
        fill(s, [x,0,z], [x,h-1,z], pal.main)
      }
    }
    // 横向编织
    for (let y = 2; y < h-2; y += 4) {
      for (let x = 0; x < w; x += 4) {
        fill(s, [x,y,0], [x,y,d-1], pal.pipe)
      }
      for (let z = 0; z < d; z += 4) {
        fill(s, [0,y,z], [w-1,y,z], pal.pipe)
      }
    }
    // 节点强化
    for (let x = 3; x < w-3; x += 8) {
      for (let y = 2; y < h-2; y += 8) {
        for (let z = 3; z < d-3; z += 8) {
          setBlock(s, [x,y,z], pal.accent)
        }
      }
    }
  },

  // 量子 IRV (26): 晶格 - 晶体结构
  lattice: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    // 立方晶格
    const spacing = 6
    for (let x = spacing; x < w-spacing; x += spacing) {
      for (let y = spacing; y < h-spacing; y += spacing) {
        for (let z = spacing; z < d-spacing; z += spacing) {
          // 晶格节点
          setBlock(s, [x,y,z], pal.accent)
          // 连接键
          if (x + spacing < w-spacing) fill(s, [x,y,z], [x+spacing,y,z], pal.pipe)
          if (y + spacing < h-spacing) fill(s, [x,y,z], [x,y+spacing,z], pal.pipe)
          if (z + spacing < d-spacing) fill(s, [x,y,z], [x,y,z+spacing], pal.pipe)
        }
      }
    }
    // 外壳
    hollowBox(s, [2,2,2], [w-3,h-3,d-3], pal.secondary)
  },

  // 量子 IWV (27): 织机 - 经纬交织架
  loom: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 框架
    hollowBox(s, [0,0,0], [w-1,h-1,d-1], pal.secondary)
    // 经线（垂直）
    for (let x = 4; x < w-4; x += 3) {
      fill(s, [x,1,d/2-4], [x,h-2,d/2+4], pal.main)
    }
    // 纬线（水平）
    for (let y = 4; y < h-4; y += 3) {
      fill(s, [4,y,d/2], [w-5,y,d/2], pal.pipe)
    }
    // 织轴
    fill(s, [2,h/2,2], [2,h/2,d-3], pal.accent)
    fill(s, [w-3,h/2,2], [w-3,h/2,d-3], pal.accent)
  },

  // 终焉 WFV (28): 世界盘 - 扁平圆盘
  'world-disc': (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    const r = Math.min(cx, cz) - 3
    // 圆盘主体
    for (let x = 0; x < w; x++) {
      for (let z = 0; z < d; z++) {
        const dist = Math.sqrt((x-cx)**2 + (z-cz)**2)
        if (dist <= r) {
          fill(s, [x,h/2-2,z], [x,h/2+2,z], pal.main)
        }
        // 边缘环
        if (Math.abs(dist - r) < 1) {
          fill(s, [x,h/2-3,z], [x,h/2+3,z], pal.secondary)
        }
      }
    }
    // 中央枢纽
    fill(s, [cx-4,h/2-4,cz-4], [cx+4,h/2+4,cz+4], pal.accent)
    // 辐条
    for (let i = 0; i < 8; i++) {
      const angle = i * Math.PI / 4
      for (let d = 5; d < r; d++) {
        const x = Math.round(cx + d * Math.cos(angle))
        const z = Math.round(cz + d * Math.sin(angle))
        setBlock(s, [x,h/2,z], pal.pipe)
      }
    }
  },

  // 终焉 WSV (29): 穹顶 - 半球形护罩
  dome: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    const r = Math.min(Math.min(cx, cz), h) - 3
    // 半球
    for (let x = 0; x < w; x++) {
      for (let y = 0; y < h; y++) {
        for (let z = 0; z < d; z++) {
          const dist = Math.sqrt((x-cx)**2 + (y)**2 + (z-cz)**2)
          if (Math.abs(dist - r) < 1.2 && y <= r) {
            setBlock(s, [x,y,z], pal.main)
          }
        }
      }
    }
    // 支撑拱肋
    for (let i = 0; i < 8; i++) {
      const angle = i * Math.PI / 4
      for (let t = 0; t <= r; t++) {
        const x = Math.round(cx + t * Math.cos(angle))
        const z = Math.round(cz + t * Math.sin(angle))
        const y = Math.round(Math.sqrt(Math.max(0, r*r - t*t)))
        if (y < h) setBlock(s, [x,y,z], pal.accent)
      }
    }
    // 顶部观测窗
    if (pal.glass) {
      for (let dx = -2; dx <= 2; dx++) {
        for (let dz = -2; dz <= 2; dz++) {
          if (dx*dx + dz*dz <= 4) {
            setBlock(s, [cx+dx,r,cz+dz], pal.glass)
          }
        }
      }
    }
  },

  // 终焉 CIV (30): 城堡 - 多塔城墙
  citadel: (s, pal) => {
    const [w, h, d] = s.getSize()
    // 外城墙
    hollowBox(s, [0,0,0], [w-1,h*2/3,d-1], pal.secondary)
    hollowBox(s, [1,1,1], [w-2,h*2/3-1,d-2], pal.main)
    // 角楼
    for (const [x,z] of [[3,3], [w-4,3], [3,d-4], [w-4,d-4]]) {
      fill(s, [x-1,0,z-1], [x+1,h-2,z+1], pal.accent)
    }
    // 中央堡垒
    const cx = Math.floor(w/2), cz = Math.floor(d/2)
    hollowBox(s, [cx-6,0,cz-6], [cx+6,h-1,cz+6], pal.main)
    fill(s, [cx-2,h/2,cz-2], [cx+2,h-1,cz+2], pal.accent)
    // 连接通道
    fill(s, [cx-8,h/3,cz-1], [cx+8,h/3+2,cz+1], pal.pipe)
    fill(s, [cx-1,h/3,cz-8], [cx+1,h/3+2,cz+8], pal.pipe)
  },

  // 终焉 CEV (31): 永恒 - 无限符号∞
  eternity: (s, pal) => {
    const [w, h, d] = s.getSize()
    const cy = Math.floor(h/2)
    const c1x = Math.floor(w*0.3), c2x = Math.floor(w*0.7)
    const cz = Math.floor(d/2)
    const r = Math.floor(Math.min(w,d) / 6)
    // 左环
    for (let angle = 0; angle < 2*Math.PI; angle += 0.15) {
      const x = Math.round(c1x + r * Math.cos(angle))
      const z = Math.round(cz + r * Math.sin(angle))
      const y = Math.round(cy + r * 0.3 * Math.sin(angle))
      fill(s, [x,y-1,z], [x,y+1,z], pal.main)
    }
    // 右环
    for (let angle = 0; angle < 2*Math.PI; angle += 0.15) {
      const x = Math.round(c2x + r * Math.cos(angle))
      const z = Math.round(cz + r * Math.sin(angle))
      const y = Math.round(cy + r * 0.3 * Math.sin(angle))
      fill(s, [x,y-1,z], [x,y+1,z], pal.main)
    }
    // 中央交叉
    fill(s, [c1x+r,cy-2,cz], [c2x-r,cy+2,cz], pal.accent)
    // 能量核心
    setBlock(s, [Math.floor(w/2),cy,cz], pal.accent)
  },
}

// 为各阶段分配形状
const SHAPE_MAP = {
  'shed': 0, 'courtyard': 1, 'sawtooth': 2, 'twins': 3, 'terraces': 4,
  'cruciform': 5, 'assembly': 6, 'ring': 7, 'double-ring': 8, 'crown': 9,
  'gantry': 10, 'spiral': 11, 'portal': 12, 'triad': 13, 'stellar': 14,
  'nested': 15, 'intake': 16, 'layered': 17, 'megastructure': 18, 'hypercube': 19
}

// 主生成循环
mkdirSync(OUTPUT_DIR, { recursive: true })
let built = 0, skipped = 0

for (const stage of SERIES) {
  const { id, name, size, shape, palette } = stage
  if (!size || !Array.isArray(size) || size.length !== 3) {
    console.warn(`❌ ${id} ${name}: 缺少有效 size`)
    skipped++
    continue
  }
  if (!shape || !SHAPES[shape]) {
    console.warn(`❌ ${id} ${name}: 未知形状 "${shape}"`)
    skipped++
    continue
  }
  if (!palette || !palette.main) {
    console.warn(`❌ ${id} ${name}: 缺少 palette.main`)
    skipped++
    continue
  }

  try {
    const structure = new Structure(size, [], [])
    SHAPES[shape](structure, palette)

    const filename = `${id}-${name.replace(/\s+/g, '-')}.schem`
    const filepath = join(OUTPUT_DIR, filename)
    const nbtData = structure.writeNbt({ name: `${id}_${name}` })
    writeFileSync(filepath, nbtData)

    console.log(`✅ ${id} ${name.padEnd(20)} [${size.join('×')}] ${shape}`)
    built++
  } catch (err) {
    console.error(`❌ ${id} ${name}: ${err.message}`)
    skipped++
  }
}

console.log(`\n完成：${built} 个建筑已生成，${skipped} 个跳过`)
console.log(`输出目录：${OUTPUT_DIR}`)
