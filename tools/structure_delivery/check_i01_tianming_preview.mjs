import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const out=path.join(root,process.argv[2]||'deliveries/I01-1_潮汐采集场_自由设计预览');
const profile=await fs.mkdtemp(path.join(root,'logs/i01-tianming-preview-edge-'));
const edge=spawn('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',[
  '--headless=new','--enable-unsafe-swiftshader','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'
],{windowsHide:true,stdio:'ignore'});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let socket;
try{
  let port;
  for(let i=0;i<100;i++)try{port=+(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break;}catch{await sleep(150)}
  if(!port)throw Error('独立浏览器未启动');
  const tabs=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket=new WebSocket(tabs.find(tab=>tab.type==='page').webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject});
  let nextId=0;const pending=new Map(),errors=[];
  socket.onmessage=event=>{
    const msg=JSON.parse(event.data);
    if(msg.id){const entry=pending.get(msg.id);if(entry){pending.delete(msg.id);msg.error?entry.reject(Error(JSON.stringify(msg.error))):entry.resolve(msg.result)}}
    else if(msg.method==='Runtime.exceptionThrown')errors.push(msg.params.exceptionDetails.text);
  };
  const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++nextId;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}))});
  await call('Page.enable');await call('Runtime.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(path.join(out,'三维评审.html')).href});
  let ready=false;
  for(let i=0;i<100;i++){
    const state=await call('Runtime.evaluate',{expression:'window.REVIEW_READY===true',returnByValue:true});
    if(state.result.value){ready=true;break}await sleep(200);
  }
  if(!ready)throw Error('三维页未就绪：'+JSON.stringify(errors));
  const state=await call('Runtime.evaluate',{expression:'JSON.stringify({blocks:window.REVIEW.data.blocks.length,canvas:[document.querySelector("canvas").width,document.querySelector("canvas").height],views:document.querySelectorAll("[data-view]").length})',returnByValue:true});
  await call('Runtime.evaluate',{expression:'window.reviewApi.setView("front")'});await sleep(500);
  const screenshot=await call('Page.captureScreenshot',{format:'png'});
  await fs.writeFile(path.join(out,'三维页实测.png'),Buffer.from(screenshot.data,'base64'));
  await call('Runtime.evaluate',{expression:'document.getElementById("layer").value=12;document.getElementById("layer").dispatchEvent(new Event("input"));window.reviewApi.setView("back")'});
  const report={ready,state:JSON.parse(state.result.value),errors,layer:12,backView:true};
  await fs.writeFile(path.join(out,'viewer-check.json'),JSON.stringify(report,null,2),'utf8');
  if(errors.length)throw Error('三维页脚本错误：'+JSON.stringify(errors));
  console.log(JSON.stringify(report));
  await call('Browser.close').catch(()=>{});
}finally{socket?.close();edge.kill()}
