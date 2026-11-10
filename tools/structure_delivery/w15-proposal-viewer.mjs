/** 2026-09-25：W15待审建筑体量示意；坐标单位为方块，不生成正式逐格结构或修改机器。 */
import * as THREE from 'three';
import {OrbitControls} from 'orbit-controls';
const stage=document.getElementById('stage'),scene=new THREE.Scene();scene.background=new THREE.Color('#101725');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(stage.clientWidth,stage.clientHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;stage.append(renderer.domElement);
const camera=new THREE.OrthographicCamera(-390,390,390,-390,.1,4000);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.maxPolarAngle=Math.PI*.495;controls.minZoom=.55;controls.maxZoom=9;
scene.add(new THREE.HemisphereLight(0xc9e1ff,0x161529,2.8));const sun=new THREE.DirectionalLight(0xffefd5,3.6);sun.position.set(-220,600,-180);scene.add(sun);const rim=new THREE.DirectionalLight(0x9988ff,2);rim.position.set(350,200,450);scene.add(rim);
const colors={dark:'#39344e',white:'#c9ced0',blue:'#215178',gold:'#b9a47a',light:'#86dfe2',glass:'#3c9db3',metal:'#657480',marker:'#4ef0e3',port:'#e6ba70'};
const mats={};for(const [key,color] of Object.entries(colors))mats[key]=new THREE.MeshStandardMaterial({color,roughness:key==='gold'?.4:.72,metalness:key==='gold'?.65:.18,transparent:key==='glass',opacity:key==='glass'?.27:1,emissive:['light','marker'].includes(key)?color:'#000000',emissiveIntensity:.18});
const groups={};for(const key of ['foundation','axis','evidence','sea','throne','tree','crown','service']){groups[key]=new THREE.Group();scene.add(groups[key]);}
const boxGeometry=new THREE.BoxGeometry(1,1,1),parts=[],labels=[];
// 所有体量使用轴对齐长方体；曲线由离散方块段表达。仅示意外轮廓与分区，不声称逐格明细已制作。
function box(group,x,y,z,w,h,d,mat='dark'){const m=new THREE.Mesh(boxGeometry,mats[mat]);m.position.set(x+w/2,y+h/2,z+d/2);m.scale.set(w,h,d);m.userData={base:y,top:y+h};groups[group].add(m);parts.push(m);return m;}
function line(group,a,b,width,mat='white',step=6){const length=Math.max(...a.map((v,i)=>Math.abs(v-b[i]))),n=Math.ceil(length/step);for(let i=0;i<=n;i++){const p=a.map((v,k)=>Math.round(v+(b[k]-v)*i/n));box(group,p[0]-Math.floor(width/2),p[1],p[2]-Math.floor(width/2),width,width,width,mat);}}
function ring(group,cx,cy,cz,rx,rz,thick,mat='white',vertical=false){const count=Math.ceil(2*Math.PI*Math.max(rx,rz)/(thick*.6)),half=Math.floor(thick/2);for(let i=0;i<count;i++){const a=i*Math.PI*2/count;const x=Math.round(cx+rx*Math.cos(a)),b=Math.round(rz*Math.sin(a));box(group,x-half,vertical?cy+b:cy,vertical?cz-half:cz+b-half,thick,thick,thick,mat);}}
function label(text,pos,kind='zone'){const el=document.createElement('div');el.className='label '+kind;el.textContent=text;stage.append(el);labels.push({el,pos:new THREE.Vector3(...pos),kind});}
// 八角承台用中央板和裁角侧条组合，最外轮廓X/Z均0..512，不铺513平方的实心体。
box('foundation',64,0,0,385,5,513);box('foundation',0,0,64,64,5,385);box('foundation',449,0,64,64,5,385);
for(let i=0;i<8;i++){const inset=64-i*8;box('foundation',inset,0,i*8,513-2*inset,5,8);box('foundation',inset,0,505-i*8,513-2*inset,5,8);}
// 外环回廊与分离的检修边带。
for(const [x,z,w,d] of [[64,20,385,9],[64,484,385,9],[20,64,9,385],[484,64,9,385]]){box('foundation',x,8,z,w,7,d,'white');box('foundation',x,15,z,w,2,d,'gold');}
for(const [x,z] of [[56,56],[424,56],[56,424],[424,424]]){
 box('foundation',x,5,z,33,12,33);box('foundation',x+4,17,z+4,25,3,25,'white');box('foundation',x+12,20,z+12,9,24,9,'blue');box('foundation',x+13,44,z+13,7,3,7,'light');
}
// 朝觐主路入口一次上升32格，此后主路、侧廊、控制器和圣座前厅均在同一标高。
for(let s=0;s<32;s++)box('axis',244,s+1,s,25,1,1,'white');
box('axis',244,29,32,25,4,272,'white');
for(const x of [240,271]){box('axis',x,29,32,2,4,272,'gold');for(let z=40;z<288;z+=24)box('axis',x,33,z,2,2,4,'light');}
for(const z of [64,192,288]){box('axis',112,29,z,289,4,9,'white');box('axis',112,29,z-2,289,2,2,'gold');}
for(const x of [204,300])box('axis',x,29,64,9,4,241,'white');
// 三重朝觐门：留出正中视线；门楣高度不遮挡后方树冠。
for(const [z,height,spread] of [[48,60,34],[176,72,40],[280,88,48]]){
 for(const x of [256-spread,256+spread-6]){box('axis',x,5,z,7,height-5,9,'white');box('axis',x+2,33,z-1,3,height-33,2,'gold');}
 box('axis',256-spread,height,z,spread*2+1,5,9,'white');box('axis',249,height+5,z,15,5,9,'light');
}
// 十四组证据座是W15的展示/校验分区，不能替代前十四座真实奇观的运行记录。
for(let i=0;i<7;i++)for(const side of [-1,1]){
 const cx=side<0?160:352,cz=86+i*32;
 box('evidence',cx-16,16,cz-12,33,13,25);box('evidence',cx-16,29,cz-12,33,4,25,'white');
 box('evidence',Math.min(cx,256),29,cz-3,Math.abs(cx-256),4,7,'white');
 for(const x of [cx-12,cx+9])box('evidence',x,33,cz+5,4,19,4,'white');
 box('evidence',cx-12,52,cz+5,25,3,4,'gold');box('evidence',cx-6,33,cz-3,13,8,7,'blue');box('evidence',cx-3,41,cz-1,7,3,3,'light');
 label('W'+String(i+1+(side>0?7:0)).padStart(2,'0'),[cx,57,cz],'evidence');
}
// 海为不填水的玻璃深井和世界泡框架；正中保留朝觐道路，玻璃不承担入口门。
for(const cx of [112,400]){
 for(const r of [62,54,44])ring('sea',cx,12,348,r,r,6,r===62?'white':r===54?'gold':'blue');
 for(let x=-48;x<=48;x+=8)for(let z=-48;z<=48;z+=8)if(x*x+z*z<49*49)box('sea',cx+x,8,348+z,8,2,8,'glass');
 for(const [dx,dz] of [[0,0],[-24,-10],[18,22]]){
  for(const y of [13,26]){box('sea',cx+dx-6,y,342+dz,13,2,2,'light');box('sea',cx+dx-6,y,355+dz,13,2,2,'light');}
  for(const xx of [-6,5])for(const zz of [-6,7])box('sea',cx+dx+xx,15,348+dz+zz,2,11,2,'blue');
 }
}
// 中央圣座：架空承台、空席王座、背后树形骨架；入口平台不与王座座面混作工作层。
box('throne',208,24,288,97,9,97,'white');box('throne',214,33,344,85,3,41,'gold');
for(let s=0;s<16;s++)box('throne',240,34+s,334+s,33,1,1,'white');
box('throne',240,36,350,33,16,21);box('throne',238,52,348,37,3,25,'white');
box('throne',240,55,365,33,57,6,'white');box('throne',246,56,363,21,48,2,'dark');
for(const x of [232,275]){box('throne',x,36,350,6,29,24,'white');box('throne',x,65,350,6,3,24,'gold');}
box('throne',254,88,360,5,18,3,'gold');box('throne',247,94,360,19,5,3,'gold');
box('throne',255,33,300,3,2,3,'marker');label('主控 C · (256,34,300)',[256,39,300],'port');
// 双树干从后部基础生长到左右冠架，所有枝条落到真实主干或冠环。
for(const x of [248,259])box('tree',x,5,394,6,148,13,'white');
box('tree',254,18,397,5,150,7,'gold');
for(const side of [-1,1]){
 const branches=[[[256,62,400],[256+side*62,100,402],[256+side*116,122,400]],[[256,100,400],[256+side*42,139,400],[256+side*88,163,400]],[[256,134,400],[256+side*28,170,400],[256+side*48,184,400]]];
 for(const points of branches){for(let i=0;i<points.length-1;i++)line('tree',points[i],points[i+1],7,'white',4);for(let i=0;i<points.length-1;i++)line('tree',points[i].map((v,k)=>k===2?v-4:v),points[i+1].map((v,k)=>k===2?v-4:v),3,'gold',3);}
 for(const [x,z,h] of [[168,366,112],[128,408,144],[96,448,176]]){
  const px=side<0?x:512-x;box('crown',px-6,5,z-6,13,7,13);box('crown',px-3,12,z-3,7,h-24,7,'white');
  box('crown',px-1,22,z-4,3,h-32,2,'gold');box('crown',px-1,h-12,z-1,3,12,3,'light');
 }
}
ring('crown',256,109,403,95,78,5,'gold',true);ring('crown',256,108,408,104,81,3,'white',true);
box('tree',254,184,398,5,9,5,'light');
// 根系连接四面分区：后翼为维护/档案汇聚，不额外虚构第二个主控。
for(const side of [-1,1])for(const z of [320,440])line('tree',[256,20,400],[256+side*145,20,z],7,'metal',5);
for(const x of [184,304]){box('service',x,5,448,25,24,33);box('service',x-2,29,446,29,4,37,'white');box('service',x+4,12,447,17,10,2,'blue');}
box('service',208,29,456,97,4,9,'white');box('service',244,29,384,25,4,81,'white');
// 实際接口为1格；彩色小座只为方案辨识。标记不代表已存在的W15注册。
const ports=[['I1',208,34,296,'物品输入'],['I2',208,34,304,'物品输入'],['O1',304,34,296,'物品输出'],['O2',304,34,304,'物品输出']];
for(const [id,x,y,z,purpose] of ports){box('service',x-2,29,z-2,5,4,5,'dark');box('service',x,y,z,1,1,1,'port');label(id+' '+purpose,[x,y+8,z],'port');}
for(const [x,id] of [[184,'R1'],[328,'R2']]){box('service',x,10,480,1,1,1,'port');box('service',x-2,5,481,5,4,4,'white');for(let s=0;s<4;s++)box('service',x-2,5+s,488-s,5,1,1,'white');label(id+' 预留维护位',[x,20,480],'port');}
label('三重朝觐门 · 25格中轴',[256,78,150]);label('空席圣座',[256,120,358]);label('分枝冠架 · 顶高193格',[256,198,400]);label('量子海象征深井',[103,29,348]);label('十四组文明证据庭',[155,64,187]);
label('宽 X · 513 格',[256,2,-18],'dimension');label('长 Z · 513 格',[-18,2,256],'dimension');
const grid=new THREE.GridHelper(640,40,0x354257,0x202d40);grid.position.set(256,-.3,256);scene.add(grid);
const outline=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(513,0,0),new THREE.Vector3(513,0,513),new THREE.Vector3(0,0,513)]),new THREE.LineBasicMaterial({color:0x6d899f}));scene.add(outline);
const views={front:[[900,560,-700],[256,48,260]],back:[[-600,470,920],[256,58,290]],top:[[256,1300,256],[256,0,256]],elevation:[[256,106,-1200],[256,106,256]],throne:[[440,185,150],[256,85,362]],service:[[-320,270,750],[256,35,380]]};
function setView(name){const v=views[name]??views.front;camera.position.set(...v[0]);controls.target.set(...v[1]);camera.zoom=name==='throne'?2.4:1;camera.updateProjectionMatrix();controls.update();document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('selected',b.dataset.view===name));document.getElementById('viewName').textContent={front:'整体体量 · 前侧',back:'后侧树冠与维护翼',top:'俯视 · 平面布局',elevation:'正视 · 高度与轴线',throne:'中央圣座 · 局部',service:'后场维护与根系'}[name];}
function update(){const max=+document.getElementById('cut').value;for(const m of parts)m.visible=m.userData.base<=max;for(const [key,g] of Object.entries(groups)){const control=document.querySelector('[data-group="'+key+'"]');g.visible=control?control.checked:true;}document.getElementById('cutValue').textContent=max;}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));document.querySelectorAll('[data-group]').forEach(b=>b.onchange=update);document.getElementById('cut').oninput=update;
document.getElementById('save').onclick=()=>{renderer.render(scene,camera);const a=document.createElement('a');a.download='W15-方案体量示意.png';a.href=renderer.domElement.toDataURL('image/png');a.click();};
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);const half=330;camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();}new ResizeObserver(resize).observe(stage);resize();
const projected=new THREE.Vector3();function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera);for(const l of labels){const show=l.kind==='dimension'||(l.kind==='port'?document.getElementById('ports').checked:l.kind==='evidence'?document.getElementById('evidenceLabels').checked:document.getElementById('labels').checked);projected.copy(l.pos).project(camera);l.el.style.display=show&&projected.z<1?'block':'none';l.el.style.left=(projected.x*.5+.5)*stage.clientWidth+'px';l.el.style.top=(-projected.y*.5+.5)*stage.clientHeight+'px';}}setView('front');frame();
// 核验体量包围盒；标签和地面网格不属于建筑尺寸。
const bounds={min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};
for(const m of parts)for(let i=0;i<3;i++){const p=m.position.getComponent(i),s=m.scale.getComponent(i);bounds.min[i]=Math.min(bounds.min[i],p-s/2);bounds.max[i]=Math.max(bounds.max[i],p+s/2);}
const withinBounds=bounds.min.every(v=>v>=0)&&bounds.max.every((v,i)=>v<=[513,193,513][i]);
if(!withinBounds)throw Error('建筑体量超出方案边界：'+JSON.stringify(bounds));
window.reviewApi={setView,renderer,scene,camera};window.REVIEW_READY=true;window.proposalInfo={size:[513,193,513],primitives:parts.length,bounds,withinBounds,production:false};
