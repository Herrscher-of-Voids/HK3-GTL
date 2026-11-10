/** 原休伯利安入口继续使用5199端口，改为提供新版静态评审页。 */
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'deliveries/休伯利安_1145格原稿_新版预览_20261108'),log=path.join(root,'logs/hyperion-modern-preview-20261108');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.txt':'text/plain; charset=utf-8','.png':'image/png','.nbt':'application/octet-stream','.bin':'application/octet-stream','.litematic':'application/octet-stream'};
const server=http.createServer(async(req,res)=>{
 try{
  if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);res.end();return;}
  let rel=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname).replace(/^\/+/, '');
  if(!rel)rel='三维评审.html';
  if(rel==='favicon.ico'){res.writeHead(204);res.end();return;}
  const file=path.resolve(out,rel);
  if(!file.startsWith(out+path.sep)){res.writeHead(403);res.end();return;}
  const bytes=await fs.readFile(file);res.writeHead(200,{'Content-Type':mime[path.extname(file)]??'application/octet-stream','Content-Length':bytes.length,'Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:bytes);
 }catch{res.writeHead(404);res.end('未找到预览文件');}
});
let port=5199;
try{await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',resolve);});}
catch(error){if(error.code!=='EADDRINUSE')throw error;port=5200;await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',resolve);});}
const url='http://127.0.0.1:'+port+'/';
await fs.writeFile(path.join(log,'server.json'),JSON.stringify({url,pid:process.pid,out,entry:'三维评审.html'},null,2));
console.log('休伯利安新版三维预览：'+url);
process.on('SIGINT',()=>server.close(()=>process.exit(0)));
