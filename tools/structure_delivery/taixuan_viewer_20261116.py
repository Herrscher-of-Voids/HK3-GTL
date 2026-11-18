import senti_weapon_viewer_20261116 as base
from taixuan_common_20261116 import *


def main():
    base.OUT=OUT
    html=base.HTML.replace('识之律者 · 三兵方块复刻 S1','太虚山 · 完整拂云观')
    html=html.replace('0005 / W09 / 武器独立复刻 S1','0005 / W09 / 太虚山独立复刻 T1')
    html=html.replace('识之律者 · 三兵与武器匣','太虚山 · 完整拂云观与云海山体')
    html=html.replace('识之律者武器','太虚山').replace('选择武器','观察构件')
    html=html.replace('0005_W09_识律武器多角度参考_20261116',REF.name)
    start=html.index('<p class="links">下载NBT：')
    end=html.index('</p>',start)+4
    html=html[:start]+'<p class="links"><a href="NBT/太虚山-完整拂云观与云海山体-T1.nbt">下载完整方块NBT</a></p>'+html[end:]
    html=html.replace('<label><input id="grid"','<label><input id="clouds" type="checkbox" checked>云海特效</label><label><input id="grid"')
    html=html.replace('<p id="stats"></p>','<p id="stats"></p><p class="links">31幅参考中的可见形制逐格重建；山势、背面、室内与连接路径包含补建设计。<a href="manifest.json">查看构件依据与补建记录</a></p>')
    js=base.JS.replace('SENTI','TAIXUAN').replace('SentiViewer','TaixuanViewer')
    js=js.replace("renderer.setClearColor('#17171c')","renderer.setClearColor('#23384a')")
    js=js.replace('0xfff8ec,1.25','0xd2e1ee,1.2').replace('0xfff5df,1.2','0xffedcd,1.35')
    js=js.replace('new THREE.AmbientLight(0xd2e1ee,1.2)','new THREE.AmbientLight(0xd2e1ee,1.2)')
    js=js.replace('group.name=part.id;','group.name=part.id;group.userData.modelId=part.modelId;')
    js=js.replace("let activeModel='case'","let activeModel='all'")
    js=js.replace("g.name===id","g.userData.modelId===id")
    js=js.replace("'三兵与武器匣'","'完整太虚山'")
    js=js.replace("'四件以独立静态姿态排列，可分别观察轮廓、厚度与持握细节。'","'完整拂云观、薄八卦台、分节青岩与回折山径。','山峰坐标和缺失视面按已见形制补建；逐图来源与补建范围保存在构件记录。'")
    js=js.replace("direction:[-.65,.25,1.6]","direction:[-.8,.55,1.35]")
    js=js.replace("left:{label:'左侧厚度'","left:{label:'左侧'").replace("right:{label:'右侧厚度'","right:{label:'右侧'")
    js=js.replace("activeModel==='all'?basicViews:","activeModel==='all'?{...basicViews,court:{label:'庭院关系',center:[0,186,-5],half:[155,70,163],direction:[-.3,.65,1]},gate:{label:'庭院低机位',center:[0,198,-30],half:[134,55,90],direction:[0,.1,1]},pixels:{label:'真实方块近景',center:[-42,192,-42],half:[12,11,12],direction:[-.4,.3,1]}}:")
    js=js.replace("pixels:{label:'真实方块近景'","route:{label:'山道连接',center:[20,125,211],half:[95,70,100],direction:[-.2,1.3,1]},pixels:{label:'真实方块近景'")
    js=js.replace("setModel('case')","setModel('all')")
    js=js.replace('识律-${activeModel}-${activeView}-S1.png','太虚山-${activeModel}-${activeView}-T1.png')
    cloud='''
  const pixels=new Uint8Array(32*32*4);
  for(let y=0;y<32;y++)for(let x=0;x<32;x++){
    const i=(y*32+x)*4;
    const a=Math.exp(-((x-16)**2/110+(y-17)**2/35))+.5*Math.exp(-((x-8)**2/30+(y-18)**2/24))+.6*Math.exp(-((x-23)**2/32+(y-14)**2/30));
    pixels.set([222,236,243,Math.min(255,Math.round(a*180))],i);
  }
  const cloudTexture=new THREE.DataTexture(pixels,32,32);cloudTexture.needsUpdate=true;cloudTexture.magFilter=THREE.NearestFilter;
  const cloudMaterial=new THREE.SpriteMaterial({map:cloudTexture,transparent:true,opacity:.20,depthWrite:false});
  const cloudLayer=new THREE.Group();
  for(let i=0;i<185;i++){
    const sprite=new THREE.Sprite(cloudMaterial),x=Math.sin(i*37.52)*370,z=Math.cos(i*19.31)*320;
    sprite.position.set(x,36+Math.sin(i*5.43)*25,z);sprite.scale.set(85+i%4*13,40+i%3*10,1);cloudLayer.add(sprite);
  }
  scene.add(cloudLayer);
  document.getElementById('clouds').onchange=e=>{cloudLayer.visible=e.target.checked;draw();};
'''
    js=js.replace("const layerInput=document.getElementById('layer')",cloud+"\n  const layerInput=document.getElementById('layer')")
    js=js.replace("activeModel=id;groups.forEach", "activeModel=id;cloudLayer.visible=id==='all'&&document.getElementById('clouds').checked;groups.forEach")
    js=js.replace('renderer.dispose();','cloudTexture.dispose();cloudMaterial.dispose();renderer.dispose();')
    base.HTML,base.JS=html,js
    base.main()


if __name__=='__main__':
    main()
