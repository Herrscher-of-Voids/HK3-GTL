import fs from 'fs';

const file = 'src/main/resources/assets/hk3gtl/lang/zh_cn.json';
let text = fs.readFileSync(file, 'utf8');
const lines = text.split('\n');
let fixed = 0;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  // Match JSON key-value pattern: "key": "value",
  const match = line.match(/^(\s*"[^"]+"\s*:\s*")(.*)(",?\s*)$/);
  if (!match) continue;
  
  const prefix = match[1];
  let value = match[2];
  const suffix = match[3];
  
  // Find unescaped ASCII double quotes inside the value
  // They appear as pairs wrapping Chinese text like "魂钢"
  const original = value;
  // Replace paired ASCII quotes inside value with Chinese quotes
  value = value.replace(/(?<!\\)"([^"]{1,20})"(?![:,\s*$])/g, (m, inner) => {
    return `\u201c${inner}\u201d`;
  });
  
  if (value !== original) {
    lines[i] = prefix + value + suffix;
    fixed++;
    console.log(`Fixed line ${i+1}: ...${original.substring(Math.max(0, original.indexOf('"')-5), original.indexOf('"')+25)}...`);
    console.log(`  -> ...${value.substring(Math.max(0, value.indexOf('\u201c')-5), value.indexOf('\u201c')+25)}...`);
  }
}

if (fixed > 0) {
  fs.writeFileSync(file, lines.join('\n'), 'utf8');
  console.log(`\nFixed ${fixed} lines with unescaped quotes.`);
} else {
  console.log('No unescaped quotes found.');
}

// Re-validate
try {
  JSON.parse(fs.readFileSync(file, 'utf8'));
  console.log('JSON is now valid!');
} catch(e) {
  console.log('JSON still invalid:', e.message);
}
