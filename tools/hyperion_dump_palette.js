#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const LITEMATIC_PATH = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.resolve(__dirname, '..', '休伯利安号 .litematic');
if (!fs.existsSync(LITEMATIC_PATH)) {
  throw new Error('找不到休伯利安源文件，请通过第一个参数提供 .litematic 路径：' + LITEMATIC_PATH);
}

class NbtParser {
  constructor(buf) { this.buf = buf; this.pos = 0; }
  readUByte()  { return this.buf.readUInt8(this.pos++); }
  readByte()   { return this.buf.readInt8(this.pos++); }
  readShort()  { const v = this.buf.readInt16BE(this.pos); this.pos += 2; return v; }
  readUShort() { const v = this.buf.readUInt16BE(this.pos); this.pos += 2; return v; }
  readInt()    { const v = this.buf.readInt32BE(this.pos); this.pos += 4; return v; }
  readLong()   { const v = this.buf.readBigInt64BE(this.pos); this.pos += 8; return v; }
  readFloat()  { const v = this.buf.readFloatBE(this.pos); this.pos += 4; return v; }
  readDouble() { const v = this.buf.readDoubleBE(this.pos); this.pos += 8; return v; }
  readString() { const len = this.readUShort(); const s = this.buf.toString('utf8', this.pos, this.pos + len); this.pos += len; return s; }
  readPayload(t) {
    switch (t) {
      case 1: return this.readByte();
      case 2: return this.readShort();
      case 3: return this.readInt();
      case 4: return this.readLong();
      case 5: return this.readFloat();
      case 6: return this.readDouble();
      case 7: { const len = this.readInt(); const a = this.buf.slice(this.pos, this.pos + len); this.pos += len; return a; }
      case 8: return this.readString();
      case 9: { const et = this.readUByte(); const c = this.readInt(); const l = []; for (let i=0;i<c;i++) l.push(this.readPayload(et)); return l; }
      case 10: { const o = {}; while(true){ const t=this.readUByte(); if(t===0)break; const n=this.readString(); o[n]=this.readPayload(t); } return o; }
      case 11: { const len = this.readInt(); const a = new Int32Array(len); for(let i=0;i<len;i++) a[i] = this.readInt(); return a; }
      case 12: { const len = this.readInt(); const a = new BigInt64Array(len); for(let i=0;i<len;i++) a[i] = this.readLong(); return a; }
      default: throw new Error(`Unknown tag ${t}`);
    }
  }
  parseRoot() { const t = this.readUByte(); this.readString(); return this.readPayload(t); }
}

const buf = zlib.gunzipSync(fs.readFileSync(LITEMATIC_PATH));
const root = new NbtParser(buf).parseRoot();
const regions = root.Regions || {};

for (const name of Object.keys(regions)) {
  const r = regions[name];
  console.log(`\n=== Region "${name}" palette (${r.BlockStatePalette.length} entries) ===`);
  r.BlockStatePalette.forEach((bs, i) => {
    const propStr = bs.Properties ? '[' + Object.entries(bs.Properties).map(([k,v])=>`${k}=${v}`).join(',') + ']' : '';
    console.log(`  [${i}] ${bs.Name}${propStr}`);
  });
}
