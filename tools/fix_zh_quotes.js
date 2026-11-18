const fs = require('fs');
const path = 'src/main/resources/assets/hk3gtl/lang/zh_cn.json';
let txt = fs.readFileSync(path, 'utf8');
const lines = txt.split('\n');
let fixed = 0;
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const m = line.match(/^(\s*"[^"]+":\s*)"(.*)"(,?)\s*$/);
  if (!m) continue;
  const inner = m[2];
  const quoteCount = (inner.match(/"/g) || []).length;
  if (quoteCount === 0) continue;
  let replaced = '';
  let openQuote = true;
  for (let j = 0; j < inner.length; j++) {
    const c = inner[j];
    if (c === '"') {
      const prev = j > 0 ? inner[j - 1] : '';
      if (prev === '\\') {
        replaced += c;
      } else {
        replaced += openQuote ? '『' : '』';
        openQuote = !openQuote;
      }
    } else {
      replaced += c;
    }
  }
  lines[i] = m[1] + '"' + replaced + '"' + m[3];
  fixed++;
}
fs.writeFileSync(path, lines.join('\n'));
console.log('fixed lines:', fixed);
