/** 使用独立无界面浏览器验证离线三维页并截图，不接触现有浏览器或游戏窗口。 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,'doc/HK3GTL-内测5/03_机器结构/W15_凌霄圣座重设计方案_v1');
const logs=path.join(root,'logs/w15-proposal');
await fs.mkdir(logs,{recursive:true});
const profile=await fs.mkdtemp(path.join(logs,'browser-'));
const edge=spawn('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',[
  '--headless=new','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--no-first-run',
  '--no-default-browser-check','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{windowsHide:true,stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let socket;
try{
  let port;
  for(let i=0;i<100;i++){try{port=+(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{await sleep(150)}}
  if(!port)throw Error('独立浏览器未启动');
  const tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
  let sequence=0;const pending=new Map(),errors=[];
  socket.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id){const p=pending.get(msg.id);if(p){pending.delete(msg.id);msg.error?p.reject(Error(JSON.stringify(msg.error))):p.resolve(msg.result);}}else if(msg.method==='Runtime.exceptionThrown')errors.push(msg.params.exceptionDetails);};
  const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));});
  await call('Page.enable');await call('Runtime.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1600,height:1050,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(path.join(out,'三维方案.html')).href});
  let ready=false;
  for(let i=0;i<150;i++){
    const r=await call('Runtime.evaluate',{expression:'window.REVIEW_READY===true',returnByValue:true});
    if(r.result.value){ready=true;break;}await sleep(200);
  }
  if(!ready)throw Error('三维页未就绪：'+JSON.stringify(errors));
  const screenshots=[];
  for(const [view,file] of [['front','01_整体效果'],['top','02_俯视比例'],['elevation','03_正视比例'],['throne','04_圣座局部'],['back','05_后场树冠']]){
    await call('Runtime.evaluate',{expression:`window.reviewApi.setView('${view}')`});await sleep(650);
    const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    await fs.writeFile(path.join(out,file+'.png'),Buffer.from(shot.data,'base64'));screenshots.push(file+'.png');
  }
  const state=await call('Runtime.evaluate',{expression:`JSON.stringify({ready:window.REVIEW_READY,proposal:window.proposalInfo,canvas:[document.querySelector('canvas').width,document.querySelector('canvas').height],meshes:window.reviewApi.renderer.info.render.calls})`,returnByValue:true});
  const report={ready,state:JSON.parse(state.result.value),errors,screenshots};
  await fs.writeFile(path.join(logs,'viewer-check.json'),JSON.stringify(report,null,2),'utf8');
  if(errors.length)throw Error('预览存在脚本错误：'+JSON.stringify(errors));
  console.log(JSON.stringify(report));
  await call('Browser.close').catch(()=>{});
}finally{
  socket?.close();edge.kill();
}
