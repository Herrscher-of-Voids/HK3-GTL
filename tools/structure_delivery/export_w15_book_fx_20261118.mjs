import fs from 'node:fs/promises';
import {gzipSync} from 'node:zlib';
import * as THREE from '../../node_modules/three/build/three.module.js';

const source=await fs.readFile(new URL('./w15_book_fx_20261118.mjs',import.meta.url),'utf8');
const module=await import('data:text/javascript;base64,'+Buffer.from(source.replace(
  'return {group,tree,sea,update,stats};',
  'return {group,tree,sea,update,stats,flows,glyphs,worlds,curves,scale};')).toString('base64'));
const fx=module.createTreeSeaEffects(THREE),chunks=[];
const integer=value=>{const b=Buffer.allocUnsafe(4);b.writeInt32BE(value);chunks.push(b);};
const number=value=>{const b=Buffer.allocUnsafe(4);b.writeFloatBE(value);chunks.push(b);};
const color=value=>{
  const c=value.clone().convertLinearToSRGB();
  return (Math.min(255,Math.round(c.r*255))<<16)|(Math.min(255,Math.round(c.g*255))<<8)|Math.min(255,Math.round(c.b*255));
};
function lines(object){
  const positions=object.geometry.getAttribute('position'),colors=object.geometry.getAttribute('color');
  integer(positions.count);
  for(let i=0;i<positions.count;i++){
    number(positions.getX(i));number(positions.getY(i));number(positions.getZ(i));
    integer(color(colors?new THREE.Color().fromBufferAttribute(colors,i):object.material.color));
  }
}
function particles(object){
  const positions=object.geometry.getAttribute('position'),sizes=object.geometry.getAttribute('aSize'),seeds=object.geometry.getAttribute('aSeed');
  integer(positions.count);
  for(let i=0;i<positions.count;i++){
    number(positions.getX(i));number(positions.getY(i));number(positions.getZ(i));number(sizes.getX(i));number(seeds.getX(i));
  }
}
integer(0x57313546);
lines(fx.tree.children[0]);lines(fx.tree.children[3]);lines(fx.sea.children[2]);lines(fx.sea.children[0]);
particles(fx.tree.children[1]);particles(fx.tree.children[2]);particles(fx.tree.children[4]);
integer(fx.curves.length);
for(const path of fx.curves){
  integer(path.world?1:0);
  for(let i=0;i<=64;i++){
    const p=path.curve.getPoint(i/64);
    if(!path.world)p.multiply(fx.scale).add(new THREE.Vector3(0,190,-35));
    number(p.x);number(p.y);number(p.z);
  }
}
const flowSizes=fx.tree.children[5].geometry.getAttribute('aSize'),flowSeeds=fx.tree.children[5].geometry.getAttribute('aSeed');
integer(fx.flows.length);
fx.flows.forEach((flow,i)=>{
  integer(fx.curves.indexOf(flow.path));number(flow.phase);number(flow.speed);number(flowSizes.getX(i));number(flowSeeds.getX(i));
});
integer(fx.worlds.length);
for(const world of fx.worlds){
  number(world.group.position.x);number(world.y);number(world.group.position.z);number(world.phase);
  lines(world.group.children[0]);
}
const glyphObject=fx.sea.children.at(-1),glyphSizes=glyphObject.geometry.getAttribute('aSize'),glyphSeeds=glyphObject.geometry.getAttribute('aSeed');
integer(fx.glyphs.length);
fx.glyphs.forEach((glyph,i)=>{
  number(glyph.phase);number(glyph.angle);number(glyph.r);number(glyph.speed);number(glyphSizes.getX(i));number(glyphSeeds.getX(i));
});
const target=new URL('../../src/main/resources/assets/hk3gtl/wonder/w15_book_fx.bin.gz',import.meta.url);
await fs.mkdir(new URL('.',target),{recursive:true});
const bytes=gzipSync(Buffer.concat(chunks),{level:9});await fs.writeFile(target,bytes);
console.log(JSON.stringify({target:target.pathname,bytes:bytes.length,...fx.stats}));
