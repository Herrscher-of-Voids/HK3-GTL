import fs from 'fs';

const file = 'src/main/resources/assets/hk3gtl/lang/zh_cn.json';
let text = fs.readFileSync(file, 'utf8');
const lines = text.split('\n');
let fixed = 0;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  // Match JSON pattern: starts with spaces, then "key": "value"[,]
  const match = line.match(/^(\s*"[^"]+"\s*:\s*")(.+)("\s*,?\s*)$/);
  if (!match) continue;
  
  const prefix = match[1];
  const value = match[2];
  const suffix = match[3];

  // Walk through value and find unescaped ASCII double quotes
  let result = '';
  let quoteCount = 0;
  for (let j = 0; j < value.length; j++) {
    const c = value[j];
    if (c === '"' && (j === 0 || value[j-1] !== '\\')) {
      // This is an unescaped quote inside the value
      quoteCount++;
      // Odd = opening, Even = closing
      result += (quoteCount % 2 === 1) ? '\u201c' : '\u201d';
    } else {
      result += c;
    }
  }

  if (result !== value) {
    lines[i] = prefix + result + suffix;
    fixed++;
    console.log(`Fixed line ${i+1}`);
  }
}

if (fixed > 0) {
  fs.writeFileSync(file, lines.join('\n'), 'utf8');
  console.log(`Fixed ${fixed} lines.`);
}

try {
  JSON.parse(fs.readFileSync(file, 'utf8'));
  console.log('JSON is now valid!');
} catch(e) {
  console.log('JSON still invalid:', e.message);
}
