import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const zhPath = path.join(root, "src/main/resources/assets/hk3gtl/lang/zh_cn.json");
const enPath = path.join(root, "src/main/resources/assets/hk3gtl/lang/en_us.json");
const markdownPath = path.join(root, "崩坏三-GTL/07_事件_文本_叙事/彩蛋事件总表.md");

function pad(num) {
  return String(num).padStart(3, "0");
}

function parseConditions(mdText) {
  const map = new Map();
  const lines = mdText.split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/\|\s*\d+\s*\|\s*(E-EG-\d{3})\s*\|\s*([^|]+?)\s*\|/);
    if (m) {
      map.set(m[1], m[2].trim());
    }
  }
  return map;
}

const zh = JSON.parse(fs.readFileSync(zhPath, "utf8"));
const en = JSON.parse(fs.readFileSync(enPath, "utf8"));
const conditionMap = parseConditions(fs.readFileSync(markdownPath, "utf8"));

zh["hk3gtl.event.condition_prefix"] = "触发条件：";
en["hk3gtl.event.condition_prefix"] = "Trigger Condition:";

for (let i = 1; i <= 100; i++) {
  const code = pad(i);
  const eventId = `E-EG-${code}`;
  const eventKey = `hk3gtl.event.eg${code}`;
  const condKey = `${eventKey}.condition`;
  const titleKey = `hk3gtl.narrative.e_eg_${code}.title`;
  const condition = conditionMap.get(eventId) ?? "满足隐藏条件";

  zh[condKey] = condition;
  en[condKey] = condition;

  if (!zh[titleKey]) zh[titleKey] = `彩蛋档案 ${eventId}`;
  if (!en[titleKey]) en[titleKey] = `Easter Egg Record ${eventId}`;
  if (!en[eventKey]) en[eventKey] = `§7Easter egg triggered: ${eventId}.`;
}

fs.writeFileSync(zhPath, JSON.stringify(zh, null, 2) + "\n", "utf8");
fs.writeFileSync(enPath, JSON.stringify(en, null, 2) + "\n", "utf8");
console.log("Updated Easter Egg language keys for zh_cn/en_us.");
