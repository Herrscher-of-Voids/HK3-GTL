import fs from 'fs';

const text = fs.readFileSync('src/main/resources/assets/hk3gtl/lang/zh_cn.json', 'utf8');
try {
  JSON.parse(text);
  console.log('JSON is valid');
} catch(e) {
  console.log('JSON Error:', e.message);
  const lines = text.split('\n');
  // find problematic area
  let charCount = 0;
  for (let i = 0; i < lines.length; i++) {
    charCount += lines[i].length + 1;
    if (charCount >= 16614) {
      console.log(`Around line ${i+1}:`);
      for (let j = Math.max(0, i-1); j <= Math.min(lines.length-1, i+1); j++) {
        console.log(`  ${j+1}: ${lines[j]}`);
      }
      // find unescaped quotes
      const line = lines[i];
      for (let k = 0; k < line.length; k++) {
        if (line[k] === '"' && k > 0 && line[k-1] !== '\\' && line[k-1] !== ':' && line[k-1] !== ' ' && line[k-1] !== ',') {
          console.log(`  Suspicious quote at col ${k+1}: ...${line.substring(Math.max(0,k-10), k+10)}...`);
        }
      }
      break;
    }
  }
}
