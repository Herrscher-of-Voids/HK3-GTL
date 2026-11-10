/** Change #1 2026-09-23: isolated local I02 viewer using installed skill dependencies.
 * 只监听本机，只提供这一台结构与本地预览资源；不改变Skill或游戏配置。
 */
import path from 'node:path';
import fs from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const skill='C:/Users/OWNER/.codex/skills/minecraft-builder-skill';
const require=createRequire(path.join(skill,'package.json'));
const {createServer}=await import(pathToFileURL(path.join(skill,'node_modules/vite/dist/node/index.js')));
const dir=path.join(root,'doc/HK3GTL-内测5/03_机器结构/I02结构审核_v1');
const server=await createServer({root:path.join(dir,'viewer'),
  resolve:{alias:{'@mattzh72/lodestone':require.resolve('@mattzh72/lodestone'),'gl-matrix':require.resolve('gl-matrix')}},
  server:{host:'127.0.0.1',port:5182,strictPort:true,fs:{allow:[root,skill]}},
  plugins:[{name:'i02-nbt',configureServer(server){server.middlewares.use((req,res,next)=>{
    if(req.url==='/__minecraft_builder__/catalog.json'){
      res.setHeader('Content-Type','application/json; charset=utf-8');
      res.end(JSON.stringify({defaultId:'I02',entries:[{id:'I02',name:'I02 样本光谱分析阵列 · 待实景审核',url:'/__minecraft_builder__/build.nbt'}]}));
    }else if(req.url==='/__minecraft_builder__/build.nbt'){
      res.setHeader('Content-Type','application/octet-stream');fs.createReadStream(path.join(dir,'i02-spectrum-array-v1.nbt')).pipe(res);
    }else next();
  });}}]});
await server.listen();console.log('I02 preview: http://127.0.0.1:5182/');
