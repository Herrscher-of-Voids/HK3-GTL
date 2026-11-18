import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const source=await fs.readFile(path.join(root,'tools/structure_delivery/w15-proposal-viewer.mjs'),'utf8');
const rows=[];
const box=(group,x,y,z,w,h,d,material='dark')=>rows.push([group,x,y,z,w,h,d,material]);
const line=(group,a,b,width,material='white',step=6)=>{
  const length=Math.max(...a.map((v,i)=>Math.abs(v-b[i]))),n=Math.ceil(length/step);
  for(let i=0;i<=n;i++){
    const p=a.map((v,k)=>Math.round(v+(b[k]-v)*i/n));
    box(group,p[0]-Math.floor(width/2),p[1],p[2]-Math.floor(width/2),width,width,width,material);
  }
};
const ring=(group,cx,cy,cz,rx,rz,thick,material='white',vertical=false)=>{
  const count=Math.ceil(2*Math.PI*Math.max(rx,rz)/(thick*.6)),half=Math.floor(thick/2);
  for(let i=0;i<count;i++){
    const a=i*Math.PI*2/count,x=Math.round(cx+rx*Math.cos(a)),b=Math.round(rz*Math.sin(a));
    box(group,x-half,vertical?cy+b:cy,vertical?cz-half:cz+b-half,thick,thick,thick,material);
  }
};
vm.runInNewContext(source.slice(source.indexOf('// 八角承台'),source.indexOf('const ports=')),{box,line,ring,label:()=>{}});
const out=path.join(root,'logs/w06-w15-blueprints-20261113');
await fs.mkdir(out,{recursive:true});
await fs.writeFile(path.join(out,'w15-source-boxes.json'),JSON.stringify(rows));
console.log(JSON.stringify({source:'tools/structure_delivery/w15-proposal-viewer.mjs',boxes:rows.length,retired_fixed_ports_omitted:true}));
