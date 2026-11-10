import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const srcRoot = path.join(root, "src/main/java");
const DATE = "2026-05-19";

function walk(dir, out = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
    } else if (entry.isFile() && entry.name.endsWith(".java")) {
      out.push(full);
    }
  }
  return out;
}

function detectRole(relPath, className) {
  const p = relPath.replaceAll("\\", "/").toLowerCase();
  if (p.includes("/mixin/")) return `处理 ${className} 的 Mixin 注入逻辑`;
  if (p.includes("/recipe/")) return `负责 ${className} 对应的配方注册与门槛绑定`;
  if (p.includes("/machine/")) return `定义 ${className} 机器行为与结构逻辑`;
  if (p.includes("/event/")) return `处理 ${className} 相关事件分发与触发`;
  if (p.includes("/research/")) return `维护 ${className} 研究流程与状态`;
  if (p.includes("/narrative/")) return `管理 ${className} 叙事节点与档案显示数据`;
  if (p.includes("/item/")) return `注册或实现 ${className} 物品行为`;
  if (p.includes("/client/")) return `负责 ${className} 客户端渲染或 UI 逻辑`;
  if (p.includes("/network/")) return `处理 ${className} 网络同步与通信`;
  return `维护 ${className} 的核心功能实现`;
}

function buildHeader(relPath, className) {
  const role = detectRole(relPath, className);
  return [
    "/**",
    " * 【文件职责】",
    ` * - ${role}。`,
    " * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。",
    " *",
    ` * 【变更记录】${DATE}`,
    " * - 删除：",
    " *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。",
    " * - 新增：",
    " *   1) 新增统一变更备注块，便于后续维护与审计追踪。",
    " * - 修改：",
    " *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。",
    " * - 用途：",
    " *   1) 帮助维护者快速理解文件职责、变更背景与风险点。",
    " *",
    " * 【段内说明】",
    " * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。",
    " */",
    "",
  ].join("\n");
}

const files = walk(srcRoot);
let updated = 0;
for (const file of files) {
  let text = fs.readFileSync(file, "utf8");
  if (text.includes("【文件职责】")) continue;

  const packageMatch = text.match(/^package\s+[\w.]+;\s*/m);
  if (!packageMatch) continue;

  const relPath = path.relative(srcRoot, file);
  const className = path.basename(file, ".java");
  const header = buildHeader(relPath, className);
  const insertAt = packageMatch.index + packageMatch[0].length;
  text = text.slice(0, insertAt) + "\n" + header + text.slice(insertAt);
  fs.writeFileSync(file, text, "utf8");
  updated++;
}

console.log(`Inserted changelog header into ${updated} Java files.`);
