export function createTreeSeaEffects(THREE) {
  const group=new THREE.Group(),tree=new THREE.Group(),sea=new THREE.Group();
  group.add(tree,sea);tree.name='虚数之树与光根';sea.name='量子海与世界残片';
  const V=(x,y,z)=>new THREE.Vector3(x,y,z),gold=new THREE.Color('#bb7921'),pale=new THREE.Color('#ffdc78');
  let seed=151118;
  const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
  const range=(a,b)=>a+(b-a)*random();
  const curves=[],tips=[],segments=[],colors=[],dust=[],dustSizes=[],dustSeeds=[];
  function trace(curve,depth=0,fiber=false,world=false) {
    curves.push({curve,world});
    const steps=Math.max(10,Math.ceil(curve.getLength()*(world?.24:1.1)));
    const color=gold.clone().lerp(pale,.18+depth*.1);
    color.multiplyScalar(fiber?.38:1.12-depth*.055);
    for(let i=0;i<steps;i++) {
      const a=curve.getPoint(i/steps),b=curve.getPoint((i+1)/steps);
      segments.push(...a.toArray(),...b.toArray());colors.push(...color.toArray(),...color.toArray());
      if(i%(fiber?9:3)===0){dust.push(...a.toArray());dustSizes.push(range(.8,1.8));dustSeeds.push(random()*6.28);}
    }
  }
  function fork(start,direction,length,depth) {
    const end=start.clone().addScaledVector(direction,length),bend=V(range(-1,1),range(-.2,.6),range(-1,1)).multiplyScalar(length*.2);
    const curve=new THREE.CubicBezierCurve3(start,start.clone().addScaledVector(direction,length*.32).add(bend),end.clone().addScaledVector(direction,-length*.28).add(bend.clone().multiplyScalar(.6)),end);
    trace(curve,depth);
    if(depth===4){tips.push(end);return;}
    const count=depth===0?3:2;
    for(let i=0;i<count;i++) {
      const t=i===0?1:range(.62,.9),at=curve.getPoint(t),next=curve.getTangent(t);
      next.applyAxisAngle(V(0,1,0),(i-(count-1)/2)*.7+range(-.55,.55));
      next.x+=range(-.25,.25);next.z+=range(-.25,.25);next.y+=range(-.03,.18);
      fork(at,next.normalize(),length*range(.58,.73),depth+1);
    }
  }
  const spine=new THREE.CubicBezierCurve3(V(0,0,0),V(7,25,-8),V(-8,55,7),V(2,80,-1));
  for(let strand=0;strand<48;strand++) {
    const points=[];
    for(let i=0;i<=80;i++) {
      const t=i/80,p=spine.getPoint(t),r=(1-t)*range(2.3,5.3),a=strand*2.39996+t*3.5;
      points.push(p.add(V(Math.cos(a)*r,0,Math.sin(a)*r)));
    }
    trace(new THREE.CatmullRomCurve3(points),0,true);
  }
  for(let i=0;i<13;i++) {
    const t=.27+i*.056,a=i*2.399963+range(-.25,.25);
    fork(spine.getPoint(t),V(Math.cos(a)*range(.75,1),range(.35,.74),Math.sin(a)*range(.7,1)).normalize(),range(42,61)*(1-.18*t),0);
  }
  fork(spine.getPoint(1),V(.12,1,.03).normalize(),24,1);
  let maxX=1,maxY=1,maxZ=1;
  for(let i=0;i<segments.length;i+=3){maxX=Math.max(maxX,Math.abs(segments[i]));maxY=Math.max(maxY,segments[i+1]);maxZ=Math.max(maxZ,Math.abs(segments[i+2]));}
  const scale=V(325/maxX,390/maxY,245/maxZ),origin=V(0,190,-35);
  const worldPoint=p=>p.multiply(scale).add(origin);
  for(const values of [segments,dust])for(let i=0;i<values.length;i+=3){values[i]*=scale.x;values[i+1]=values[i+1]*scale.y+190;values[i+2]=values[i+2]*scale.z-35;}
  tips.forEach((p,i)=>tips[i]=worldPoint(p.clone()));
  for(let i=0;i<18;i++) {
    const a=i*Math.PI*2/18,r=range(260,580),z=-35+Math.sin(a)*r*.72;
    const mouth=V(Math.cos(a)*5,190,-35+Math.sin(a)*5),under=V(Math.cos(a)*9,94,-35+Math.sin(a)*9);
    trace(new THREE.CubicBezierCurve3(mouth,V(mouth.x,162,mouth.z),V(under.x,115,under.z),under),1,true,true);
    trace(new THREE.CubicBezierCurve3(under,V(Math.cos(a)*r*.25,73,-35+Math.sin(a)*r*.18),V(Math.cos(a)*r*.7,46,z*.85),V(Math.cos(a)*r,31,z)),2,false,true);
  }
  for(const sign of [-1,1])for(let j=0;j<4;j++) {
    const x=-8+j*5,endZ=sign*(410+j*4);
    trace(new THREE.CubicBezierCurve3(V(x,194,-35),V(x,198,sign*160),V(x,200,sign*350),V(x,194,endZ)),1,true,true);
    trace(new THREE.CubicBezierCurve3(V(x,194,endZ),V(x,155,endZ+sign*22),V(x*7,55,endZ+sign*20),V(x*12,32,endZ+sign*12)),2,false,true);
  }
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(segments,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  const lineMaterial=new THREE.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.72,depthWrite:false,blending:THREE.AdditiveBlending});
  tree.add(new THREE.LineSegments(geometry,lineMaterial));
  const uniforms={uTime:{value:0},uPower:{value:1}};
  const pointVertex=`attribute float aSize;attribute float aSeed;varying float vSeed;uniform float uTime;
  void main(){vSeed=aSeed;vec4 p=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*p;
  float s=projectionMatrix[3][3]>.5?projectionMatrix[1][1]*1100.:1100./max(1.,-p.z);gl_PointSize=clamp(aSize*s,1.,18.);}`;
  const pointFragment=`varying float vSeed;uniform float uTime;uniform float uPower;
  void main(){vec2 p=gl_PointCoord-.5;float d=length(p)*2.;if(d>1.)discard;
  float a=exp(-d*d*7.)*.5+exp(-d*d*50.)*.8;vec3 c=mix(vec3(1.,.53,.09),vec3(1.,.86,.43),exp(-d*d*28.));
  gl_FragColor=vec4(c,a*(.78+.22*sin(uTime*.7+vSeed))*uPower);}`;
  function points(parent,coords,sizes,seeds,fragment=pointFragment) {
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(coords,3));
    g.setAttribute('aSize',new THREE.Float32BufferAttribute(sizes,1));g.setAttribute('aSeed',new THREE.Float32BufferAttribute(seeds,1));
    const p=new THREE.Points(g,new THREE.ShaderMaterial({uniforms,vertexShader:pointVertex,fragmentShader:fragment,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}));
    p.frustumCulled=false;parent.add(p);return p;
  }
  points(tree,dust,dustSizes,dustSeeds);
  const nodePositions=[],nodeSizes=[],nodeSeeds=[],diamonds=[];
  tips.forEach((p,i)=>{
    if(i%3)return;
    nodePositions.push(...p.toArray());nodeSizes.push(range(3.5,6));nodeSeeds.push(random()*6.28);
    const size=range(1.5,3.4),a=p.clone().add(V(0,size,0)),b=p.clone().add(V(size*.6,0,0)),c=p.clone().add(V(0,-size,0)),d=p.clone().add(V(-size*.6,0,0));
    for(const [u,v] of [[a,b],[b,c],[c,d],[d,a]])diamonds.push(...u.toArray(),...v.toArray());
  });
  points(tree,nodePositions,nodeSizes,nodeSeeds);
  tree.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(diamonds,3)),new THREE.LineBasicMaterial({color:0xffd983,transparent:true,opacity:.6,depthWrite:false,blending:THREE.AdditiveBlending})));
  const leafPositions=[],leafSizes=[],leafSeeds=[];
  tips.forEach((p,i)=>{
    const count=i%7===0?5:i%5===0?1:3;
    for(let j=0;j<count;j++) {
      const spread=i%4===0?15:8;
      leafPositions.push(THREE.MathUtils.clamp(p.x+range(-spread,spread),-321,321),Math.min(577,p.y+range(-7,9)),THREE.MathUtils.clamp(p.z+range(-spread,spread),-277,207));
      leafSizes.push(range(5,11));leafSeeds.push(random()*6.28);
    }
  });
  const leafFragment=`varying float vSeed;uniform float uTime;uniform float uPower;void main(){vec2 p=gl_PointCoord-.5;
  float a=vSeed+sin(uTime*.23+vSeed)*.13;mat2 turn=mat2(cos(a),-sin(a),sin(a),cos(a));p=turn*p;
  float d=abs(p.x)*1.75+abs(p.y)*1.03;if(d>.47)discard;float edge=1.-smoothstep(.34,.47,d);
  vec3 c=mix(vec3(.93,.47,.065),vec3(1.,.81,.3),fract(vSeed*2.7));float vein=1.-smoothstep(.008,.027,abs(p.x));
  c+=vec3(.08,.065,.025)*vein;gl_FragColor=vec4(c,edge*(.3+.28*fract(vSeed))*(.75+uPower*.25));}`;
  const leaves=points(tree,leafPositions,leafSizes,leafSeeds,leafFragment);leaves.material.blending=THREE.NormalBlending;
  leaves.material.vertexShader=pointVertex.replace('vec4 p=modelViewMatrix*vec4(position,1.);','vec3 at=position;at.x+=sin(uTime*.25+aSeed)*1.6;at.y+=cos(uTime*.18+aSeed)*1.1;vec4 p=modelViewMatrix*vec4(at,1.);');
  const flows=Array.from({length:580},()=>({path:curves[Math.floor(random()*curves.length)],phase:random(),speed:range(.025,.065)}));
  const flow=points(tree,new Float32Array(flows.length*3),flows.map(()=>range(2,4)),flows.map(()=>random()*6.28));
  const wavePositions=[],waveColors=[];
  for(let ring=0;ring<29;ring++) {
    const r=28+ring*21,c=new THREE.Color().setHSL(.58+ring/29*.13,.72,.36+ring%7*.025);
    const at=a=>{const d=r+Math.sin(a*5+r*.028)*5+Math.cos(a*9-r*.02)*2;return [Math.cos(a)*d,29+Math.sin(a*4+r*.04)*3+(ring%3)*2,Math.sin(a)*d*.746];};
    for(let j=0;j<240;j++){wavePositions.push(...at(j*Math.PI/120),...at((j+1)*Math.PI/120));waveColors.push(...c.toArray(),...c.toArray());}
  }
  const waveGeo=new THREE.BufferGeometry();waveGeo.setAttribute('position',new THREE.Float32BufferAttribute(wavePositions,3));waveGeo.setAttribute('color',new THREE.Float32BufferAttribute(waveColors,3));
  const waveMaterial=new THREE.ShaderMaterial({uniforms,vertexColors:true,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`varying vec3 vColor;uniform float uTime;void main(){vColor=color;vec3 p=position;float r=length(p.xz);p.y+=sin(r*.033-uTime*.4)*2.;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,
    fragmentShader:`varying vec3 vColor;uniform float uPower;void main(){gl_FragColor=vec4(vColor,(.035+uPower*.045));}`});
  sea.add(new THREE.LineSegments(waveGeo,waveMaterial));
  const surfaceGeo=new THREE.RingGeometry(0,630,144,30);surfaceGeo.rotateX(-Math.PI/2);surfaceGeo.scale(1,1,470/630);surfaceGeo.translate(0,27,0);
  sea.add(new THREE.Mesh(surfaceGeo,new THREE.ShaderMaterial({uniforms,transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.NormalBlending,
    vertexShader:`varying vec3 p;uniform float uTime;void main(){p=position;p.y+=sin(p.x*.013+uTime*.32)*3.+cos(p.z*.017-uTime*.25)*2.;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,
    fragmentShader:`varying vec3 p;uniform float uTime;uniform float uPower;void main(){vec2 q=p.xz/vec2(630.,470.);float r=length(q);float a=atan(q.y,q.x);
    float drift=sin(p.x*.011+p.z*.017+uTime*.19)*.5+cos(p.x*.018-p.z*.009-uTime*.23)*.5;
    float v=sin(r*28.-uTime*.43+sin(a*4.+r*5.)*1.8+drift);float w=smoothstep(.2,.95,v);float edge=1.-smoothstep(.88,1.,r);
    vec3 c=mix(vec3(.07,.095,.28),vec3(.14,.29,.58),.5+drift*.25);c+=vec3(.1,.12,.2)*w;
    gl_FragColor=vec4(c,(.19+w*.10)*edge*(.78+uPower*.22));}`})));
  const spirals=[];
  for(let arm=0;arm<7;arm++)for(let j=0;j<150;j++) {
    const at=t=>{const r=55+t*555,a=arm*Math.PI*2/7+t*2.5;return [Math.cos(a)*r,21+Math.sin(t*11+arm)*4,Math.sin(a)*r*.746];};
    spirals.push(...at(j/150),...at((j+1)/150));
  }
  sea.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(spirals,3)),new THREE.LineBasicMaterial({color:0x9c86f0,transparent:true,opacity:.1,depthWrite:false,blending:THREE.AdditiveBlending})));
  const worlds=[];
  for(let i=0;i<9;i++) {
    const a=i*2.39996+.6,radius=range(13,25),w=new THREE.Group();w.position.set(Math.cos(a)*range(555,620),range(51,74),Math.sin(a)*range(415,460));
    const lines=[],n=80;
    for(let axis=0;axis<3;axis++)for(let j=0;j<n;j++) {
      const at=t=>{const p=V(Math.cos(t)*radius,Math.sin(t)*radius,0);if(axis===1)p.applyAxisAngle(V(1,0,0),Math.PI/2);if(axis===2)p.applyAxisAngle(V(0,1,0),Math.PI/2);return p.toArray();};
      lines.push(...at(j*Math.PI*2/n),...at((j+1)*Math.PI*2/n));
    }
    w.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute(lines,3)),new THREE.LineBasicMaterial({color:i%2?0x9bb9ff:0xc0a6ff,transparent:true,opacity:.32,depthWrite:false,blending:THREE.AdditiveBlending})));
    sea.add(w);worlds.push({group:w,y:w.position.y,phase:i*.87});
  }
  const glyphs=Array.from({length:240},()=>({phase:random(),angle:random()*Math.PI*2,r:range(180,575),z:range(-300,300),speed:range(.025,.06)}));
  const glyphFragment=`varying float vSeed;uniform float uTime;uniform float uPower;void main(){vec2 p=gl_PointCoord-.5;vec2 q=floor(gl_PointCoord*5.);
  float border=step(.31,max(abs(p.x),abs(p.y)))*step(max(abs(p.x),abs(p.y)),.47);float bar=step(abs(p.y),.09)*step(abs(p.x),.4);
  float stem=step(abs(p.x),.09)*step(abs(p.y),.39);float ink=max(border,max(bar,stem*step(.5,fract(vSeed))));
  if(ink<.1)discard;gl_FragColor=vec4(mix(vec3(.3,.56,1.),vec3(1.,.83,.4),fract(vSeed)),(.4+.4*uPower)*ink);}`;
  const glyph=points(sea,new Float32Array(glyphs.length*3),glyphs.map(()=>range(3,5)),glyphs.map(()=>random()*6.28),glyphFragment);
  function update(time,working) {
    const power=working?1:.58;uniforms.uTime.value=time;uniforms.uPower.value=power;
    lineMaterial.opacity=working?.66:.46;
    const flowPositions=flow.geometry.attributes.position.array;
    flows.forEach((item,i)=>{
      let t=THREE.MathUtils.euclideanModulo(item.phase+time*item.speed*(working?1:.32),1);if(item.path.world)t=1-t;
      const p=item.path.curve.getPoint(t);if(!item.path.world)worldPoint(p);p.toArray(flowPositions,i*3);
    });flow.geometry.attributes.position.needsUpdate=true;
    const glyphPositions=glyph.geometry.attributes.position.array;
    glyphs.forEach((item,i)=>{
      const t=THREE.MathUtils.euclideanModulo(item.phase+time*item.speed*(working?1:.22),1),a=item.angle+t*.9;
      let p;
      if(t<.7){const q=t/.7,r=item.r*(1-q);p=V(Math.cos(a)*r,45+q*43,Math.sin(a)*r*.746-35*q);}
      else {const q=(t-.7)/.3;p=V(Math.sin(a)*7,88+q*102,-35+Math.cos(a)*7);}
      p.toArray(glyphPositions,i*3);
    });glyph.geometry.attributes.position.needsUpdate=true;
    worlds.forEach(w=>{w.group.position.y=w.y+Math.sin(time*.25+w.phase)*5;w.group.rotation.y=time*.025;});
  }
  update(0,true);
  const stats={treeCurves:curves.length,treeLineSegments:segments.length/6,treeDust:dustSizes.length,worldNodes:nodeSizes.length,worldLeaves:leafSizes.length,flowParticles:flows.length,seaContours:29,worldBubbles:worlds.length,risingGlyphs:glyphs.length,bounds:{min:[-630,15,-470],max:[630,580,470]}};
  return {group,tree,sea,update,stats};
}
