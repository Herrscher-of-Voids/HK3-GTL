from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'deliveries/0005_W12_作者蓝图原案_A1_20261116'
OUT = ROOT / 'deliveries/0005_W12_三环分层扩腔_A2_20261116'
(OUT / '生成脚本').mkdir(parents=True, exist_ok=True)
source = (OLD / '生成脚本/viewer.mjs').read_text('utf8').replace('全域能量约束壁-A1.png', '全域能量约束壁-A2.png')
(OUT / '生成脚本/viewer.mjs').write_text(source, 'utf8')
effects = (OLD / '生成脚本/effects.mjs').read_text('utf8')
effects = effects.replace('const beamVertices=[],towerVertices=[],records=[];', 'const beamVertices=[],towerVertices=[],lanceVertices=[],records=[];')
effects = effects.replace('  add(2,center,center,720);', '''  for(const direction of data.effects.lance_directions){
    const n=new THREE.Vector3(...direction),[inner,outer]=data.effects.lance_energy_radii;
    lanceVertices.push(...center.clone().addScaledVector(n,inner).toArray(),...center.clone().addScaledVector(n,outer).toArray());
  }
  add(2,center,center,720);''')
effects = effects.replace('scene.add(beams,towerBeams);', '''scene.add(beams,towerBeams);
  const lanceGeometry=new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(lanceVertices,3));
  const lanceMaterial=beamMaterial.clone();lanceMaterial.color.set(0xffe3a1);
  const lanceBeams=new THREE.LineSegments(lanceGeometry,lanceMaterial);scene.add(lanceBeams);''')
effects = effects.replace('arcs.visible=effects&&coreVisible;', 'arcs.visible=effects&&coreVisible;lanceBeams.visible=effects&&coreVisible;lanceMaterial.opacity=(work?.7:.35)*(.8+.2*Math.sin(time*2.4));')
effects = effects.replace('[wave,points,beams,towerBeams,butterflies,arcs]', '[wave,points,beams,towerBeams,lanceBeams,butterflies,arcs]')
(OUT / '生成脚本/effects.mjs').write_text(effects, 'utf8')
shutil.copy2(OLD / 'style.css', OUT / 'style.css')
html = (OLD / 'index.html').read_text('utf8').replace('A1', 'A2').replace('AUTHOR BLUEPRINT A2', 'LAYERED RINGS A2').replace('作者原案 A2', '三环分层 A2')
start = html.index('<p class="note">')
end = html.index('</aside>', start)
html = html[:start] + '''<p class="note">三环半径25／36／47格，核心名义球腔直径110格。完整方块环间全相位净空至少3.27格。十二实体矛外移，金色能量束连接白洞；靠芯锁链移锚，长廊清出球形开口。</p>
<p class="note">唯一主控(531,50,10)，其余实体格自由替换合法通用接口、朝向自选。外围链廊、冠环与塔等固定交叠另待修订。</p>
<p class="links"><a href="changes.json">本版修改</a> · <a href="continuous-clearance.json">全相位净空</a> · <a href="geometry.json">完整几何</a> · <a href="manifest.json">交付记录</a> · <a href="W12-全域能量约束壁-A2.nbt">NBT</a></p>
''' + html[end:]
(OUT / 'index.html').write_text(html, 'utf8')
capture = (ROOT / 'tools/structure_delivery/capture_0005_w12_author_blueprint_20261116.mjs').read_text('utf8')
capture = capture.replace('0005_W12_作者蓝图原案_A1_20261116', '0005_W12_三环分层扩腔_A2_20261116')
capture = capture.replace("  {scene:'core',view:'core',file:'三重十字_待机.png'},", "  {scene:'core',view:'core',effects:false,file:'三重十字_待机.png'},\n  {scene:'core',view:'coreClose',effects:false,file:'三环分层_完整方块.png'},\n  {scene:'core',view:'coreFront',effects:false,file:'三重十字_正面.png'},\n  {scene:'all',view:'coreClose',effects:false,file:'核心与邻件_待机.png'},\n  {scene:'all',view:'coreClose',time:37,effects:false,file:'核心与邻件_37秒.png'},")
(OUT / '生成脚本/capture.mjs').write_text(capture, 'utf8')
shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
