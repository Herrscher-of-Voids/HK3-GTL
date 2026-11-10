import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const log=path.join(root,'logs/deepseek-design-brief-20261107');
const file=path.join(root,'deliveries/HK3GTL_模组框架世界观与多方块设计资料包_DeepSeek版_20261029/index.html');
const require=createRequire('C:/Users/OWNER/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const {chromium}=require('playwright');
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const errors=[],external=[],failed=[];
const page=await browser.newPage({viewport:{width:1440,height:1100}});
page.on('pageerror',e=>errors.push(e.message));
page.on('requestfailed',r=>failed.push(r.url()));
page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
await page.addInitScript(()=>{Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.__copied=text;}}});});
const check=(valid,message)=>{if(!valid)throw new Error(message);};
const checks={};
try{
  await page.goto(pathToFileURL(file).href);
  await page.waitForFunction(()=>window.BRIEF_READY);
  await page.evaluate(async()=>{await Promise.all([...document.images].map(im=>{im.loading='eager';return im.decode();}));});
  checks.document=await page.evaluate(()=>({title:document.title,rows:document.querySelectorAll('[data-machine]').length,
    tiers:document.querySelectorAll('#voltages tbody tr').length,tiles:document.querySelectorAll('.texture').length,
    images:document.querySelectorAll('.gallery img').length,broken:[...document.images].filter(i=>!i.naturalWidth).length,
    lineItems:document.querySelectorAll('.line-grid>div').length,overflow:document.documentElement.scrollWidth>innerWidth}));
  check(checks.document.rows===74&&checks.document.tiers===17&&checks.document.tiles===16&&checks.document.images===6,'目录/电压/内嵌图片数量错误');
  check(!checks.document.broken&&!checks.document.overflow,'图像损坏或桌面溢出');
  check(checks.document.lineItems===14,'L1–L14产线不完整');
  await page.screenshot({path:path.join(log,'desktop-preview.png')});
  await page.locator('#copyAll').click();
  checks.copyAll=await page.evaluate(()=>({characters:window.__copied.length,
    matches:window.__copied===document.getElementById('fullText').textContent,
    hasLore:window.__copied.includes('二审者终焉琪亚娜'),hasW03Boundary:window.__copied.includes('W03')&&window.__copied.includes('Gork原案V7已交付')&&window.__copied.includes('完整边界修复候选')&&window.__copied.includes('名义尺寸不得作为裁切窗口')&&window.__copied.includes('W03各候选均未批准、未部署'),
    latest:window.__copied.includes('增强版3.0')&&window.__copied.includes('批准57个形态')&&window.__copied.includes('既定范围74项'),
    roles:window.__copied.includes('十三位律者')&&window.__copied.includes('W03对应西琳')&&window.__copied.includes('W15对应凌虛晴'),
    noStale:!['2.9.2','批准归档49','正式结构文件46','84/88','十四位律者','I43 V1为待审'].some(s=>window.__copied.includes(s)),
    hasH01:window.__copied.includes('H01 仿制'),hasFCL:window.__copied.includes('FCL'),
    hasFreeze:window.__copied.includes('主控居中融合V2（2026-10-23）')}));
  check(checks.copyAll.characters>20000&&Object.values(checks.copyAll).every(Boolean),'完整复制缺少必要上下文或保留旧口径');
  await page.locator('#copyContract').click();
  check(await page.evaluate(()=>window.__copied===document.getElementById('contract').textContent),'模板复制失败');
  checks.allMachinePrompts=await page.evaluate(()=>{
    const select=document.getElementById('machine'),prompts={};
    for(const option of select.options){
      select.value=option.value;select.dispatchEvent(new Event('change'));
      const text=document.getElementById('machinePrompt').value;
      if(!text.includes(option.value)||!text.includes('增强版3.0')||!text.includes('既定74项')||!text.includes('不固定输入输出')||text.includes('undefined')||text.includes('2.9.2'))throw new Error('单台模板未同步：'+option.value);
      prompts[option.value]=text;
    }
    if(!prompts['I43'].includes('外观已批准 V1')||!prompts['I44'].includes('外观已批准 V2')||!prompts['I45'].includes('外观已批准 V2'))throw new Error('正式版本状态错误');
    if(!prompts['W02'].includes('已批准建筑实际体量参考')||!prompts['W02'].includes('外观已批准 V2'))throw new Error('W02批准状态未同步');
    for(let i=1;i<=15;i++){const p=prompts['W'+String(i).padStart(2,'0')];if(!p.includes('按美观自由选用')||!p.includes('不强制电压或律者机壳主导'))throw new Error('奇观美观优先规则缺失：'+i);}
    if(!prompts['W03'].includes('W03实体对应西琳')||!prompts['W15'].includes('正常建筑内无银幕'))throw new Error('角色或临时银幕规则缺失');
    for(const id of ['MX-C01','MX-C02','MX-C03','MX-C04'])if(!prompts[id].includes('未冻结新尺寸下限')||!prompts[id].includes('建筑文件已接入'))throw new Error('MAX状态或下限错误');
    if(!prompts.honkai_network_injector.includes('结构重构待完成'))throw new Error('网络注入器状态错误');
    return {passed:true,count:Object.keys(prompts).length};
  });
  await page.locator('#search').fill('I43');
  check(await page.locator('[data-machine]:visible').count()===1,'搜索I43未唯一命中');
  check(await page.locator('[data-machine="I43"]').innerText().then(t=>t.includes('外观已批准 V1')),'I43未同步批准状态');
  await page.locator('#search').fill('W02');
  await page.locator('[data-pick="W02"]').click();
  check(await page.locator('#machine').inputValue()==='W02','目录没有正确生成单台任务');
  await page.locator('#targetNotes').fill('不要使用四爪抓球或环城；强调环境试验。');
  await page.locator('#copyMachine').click();
  checks.machinePrompt=await page.evaluate(()=>({characters:window.__copied.length,
    exact:window.__copied===document.getElementById('machinePrompt').value,
    machine:window.__copied.includes('W02'),tier:window.__copied.includes('WSV'),
    boundary:window.__copied.includes('外观已批准 V2'),preference:window.__copied.includes('强调环境试验')}));
  check(Object.values(checks.machinePrompt).every(Boolean),'单台任务丢失目标、边界或偏好');
  await page.locator('#machine').selectOption('I01-1');
  check((await page.locator('#machinePrompt').inputValue()).includes('冻结：主控居中融合V2'),'冻结版本提示缺失');
  await page.locator('#machine').selectOption('I44');
  await page.locator('#targetNotes').fill('');
  await page.locator('#search').fill('');
  await page.locator('#group').selectOption('文明奇观');
  check(await page.locator('[data-machine]:visible').count()===15,'奇观筛选数量错误');
  await page.locator('#group').selectOption('');
  await page.locator('#search').fill('honkai_network_injector');
  check(await page.locator('[data-machine]:visible').count()===1,'网络注入器搜索错误');
  await page.locator('#search').fill('');
  await page.locator('#group').selectOption('MAX复制系统');
  check(await page.locator('[data-machine]:visible').count()===4,'四台MAX目录不完整');
  await page.locator('#group').selectOption('');
  await page.locator('#references').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(log,'references-preview.png')});
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:path.join(log,'mobile-preview.png'),fullPage:false});
  checks.mobile=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth}));
  check(checks.mobile.width===checks.mobile.documentWidth,'移动端页面横向溢出');
  checks.external_requests=external;checks.failed_requests=failed;checks.errors=errors;
  check(!external.length&&!failed.length&&!errors.length,'离线请求或JavaScript有错误');
  await fs.writeFile(path.join(log,'browser-verification.json'),JSON.stringify({passed:true,protocol:'file:',headless:true,desktop_used:false,game_started:false,checks},null,2));
  console.log(JSON.stringify({passed:true,checks}));
}finally{await browser.close();}
