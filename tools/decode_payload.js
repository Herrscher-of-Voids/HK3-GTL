const fs = require('fs');
const zlib = require('zlib');
const path = require('path');

const dataJsPath = path.join(
  __dirname, '..', 'doc', 'HK3GTL-内测5', '03_机器结构',
  '69座重设计_实体预览01', 'i01-1', 'data.js'
);

const src = fs.readFileSync(dataJsPath, 'utf8');
const b64 = src.match(/window\.HK3_PAYLOAD="([^"]+)"/)[1];
const buf = Buffer.from(b64, 'base64');
const json = zlib.gunzipSync(buf).toString('utf8');
const data = JSON.parse(json);

console.log('顶层键:', Object.keys(data));
console.log('size:', data.size);
console.log('palette 前3项:', JSON.stringify(data.palette?.slice(0,3), null, 2));
console.log('blocks 前2项:', JSON.stringify(data.blocks?.slice(0,2), null, 2));
if (data.materials) console.log('materials 前2项:', JSON.stringify(data.materials?.slice(0,2), null, 2));
if (data.zones) console.log('zones:', JSON.stringify(data.zones, null, 2));
if (data.ports) console.log('ports 前2项:', JSON.stringify(data.ports?.slice(0,2), null, 2));
