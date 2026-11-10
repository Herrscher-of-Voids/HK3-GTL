  // 工业设施仅表现布局体量；龙与刀使用各自完整体素表面。
  const sceneryGroups={base:new THREE.Group(),energy:new THREE.Group(),labels:new THREE.Group()};
  for(const group of Object.values(sceneryGroups)){group.position.copy(offset);scene.add(group);}
  const colors={black:0x202029,dark:0x32313c,red:0xC93F63,muted:0x792d46,gold:0xa78d60,white:0xd6c9d0,light:0xff9ebf};
  const simpleMaterials=new Map();
  function simpleMaterial(color,glow=false){
    const key=color+':'+glow;
    if(!simpleMaterials.has(key))simpleMaterials.set(key,new THREE.MeshLambertMaterial({color,emissive:glow?color:0,emissiveIntensity:glow?.45:0}));
    return simpleMaterials.get(key);
  }
  function mesh(geometry,pos,color,group='base',rotation=null,glow=false){
    const item=new THREE.Mesh(geometry,simpleMaterial(color,glow));item.position.set(...pos);
    if(rotation)item.rotation.set(...rotation);sceneryGroups[group].add(item);return item;
  }
  function box(pos,size,color,group='base',ry=0){return mesh(new THREE.BoxGeometry(...size),pos,color,group,[0,ry,0]);}
  function ring(pos,radius,tube,color,group='base'){
    return mesh(new THREE.TorusGeometry(radius,tube,6,96),pos,color,group,[Math.PI/2,0,0],group==='energy');
  }
  function cylinder(pos,radius,height,color,group='base'){
    return mesh(new THREE.CylinderGeometry(radius,radius,height,48),pos,color,group);
  }
  function line(a,b,radius,color,group='energy'){
    const av=new THREE.Vector3(...a),bv=new THREE.Vector3(...b),dir=bv.clone().sub(av);
    const item=mesh(new THREE.CylinderGeometry(radius,radius,dir.length(),8),av.add(bv).multiplyScalar(.5).toArray(),color,group,null,true);
    item.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());return item;
  }
  function deck(width,depth,y,height,color){
    const x=width/2,z=depth/2,c=65,shape=new THREE.Shape();
    const points=[[-x+c,-z],[x-c,-z],[x,-z+c],[x,z-c],[x-c,z],[-x+c,z],[-x,z-c],[-x,-z+c]];
    points.forEach(([a,b],i)=>i?shape.lineTo(a,b):shape.moveTo(a,b));shape.closePath();
    const hole=new THREE.Path();hole.absarc(0,-252.5,143,0,Math.PI*2,true);shape.holes.push(hole);
    // 形状局部二维的负Y转为世界正Z。
    return mesh(new THREE.ExtrudeGeometry(shape,{depth:height,bevelEnabled:false,curveSegments:96}),[0,y,-17.5],color,'base',[-Math.PI/2,0,0]);
  }
  deck(940,905,0,13,colors.black);deck(914,879,13,11,colors.dark);
  // 雷池为共同核心，刀尖保持悬空；暗金磁轭与绯红绕组交替排列。
  cylinder([0,5,235],140,8,colors.black);cylinder([0,10,235],118,3,colors.muted,'energy');
  for(const [r,y] of [[140,31],[110,44],[85,17]])ring([0,y,235],r,4,colors.gold);
  for(const r of [40,65,92])ring([0,17,235],r,1.8,colors.red,'energy');
  cylinder([0,32,235],17,40,colors.red,'energy');cylinder([0,54,235],9,6,colors.white,'energy');
  line([0,58,235],[0,91,235],2,colors.light);
  for(let i=0;i<16;i++){
    const a=i*Math.PI/8,x=Math.sin(a)*127,z=235+Math.cos(a)*127;
    box([x,32,z],[11,34,27],colors.black,'base',a);
    box([x,39,z],[13,12,20],colors.red,'base',a);
    box([x,49,z],[9,4,25],colors.gold,'base',a);
  }
  // 两列低矮超导储能设施沿龙体两侧后退，给胸腹和龙首留出空腔。
  for(const sign of [-1,1]){
    for(let i=0;i<5;i++){
      const x=sign*260,z=-340+i*92;
      box([x,38,z],[70,28,66],colors.black);
      box([x,76,z],[49,53,48],colors.dark);
      for(const y of [56,72,88])ring([x,y,z],29,4,colors.red);
      box([x,107,z],[58,9,55],colors.gold);
      box([sign*174,28,z],[44,8,22],colors.muted);
    }
    box([sign*95,29,-10],[18,10,520],colors.black);
    box([sign*95,36,-10],[5,5,520],colors.red,'energy');
    line([sign*95,37,250],[sign*105,38,300],3,colors.red);
    line([sign*105,38,300],[0,48,235],3,colors.red);
  }
  // 静态能量联系示意：从后部设施向龙腹、再由龙颌导至雷池前缘。
  for(const sign of [-1,1]){
    line([sign*95,39,-180],[sign*60,185,-100],2.2,colors.muted);
    line([sign*60,185,-100],[sign*31,247,0],1.6,colors.red);
  }
  line([0,330,151],[0,168,185],2.5,colors.red);
  line([0,168,185],[0,55,235],2.5,colors.light);
  // 前庭控制器及同面八接口，嵌入单面装甲墙，不悬空。
  box([0,12,405],[152,24,58],colors.black);
  box([0,24,414],[44,26,10],colors.muted);
  for(const x of [-1,0,1])for(const y of [-1,0,1])
    box([x+.5,18+y+.5,419.2],[.96,.96,1.2],x===0&&y===0?colors.light:colors.gold);
  for(const sign of [-1,1]){
    box([sign*56,46,399],[9,76,10],colors.black);
    box([sign*56,48,405],[3,64,2],colors.red);
  }
  box([0,83,399],[139,10,14],colors.red);box([0,94,399],[156,8,18],colors.black);
  for(let i=0;i<5;i++)box([0,4+i*2,432-i*5],[120-i*8,4,5],colors.dark);
  function label(text,pos){
    const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=144;
    const context=canvas.getContext('2d');context.fillStyle='rgba(24,16,28,.88)';context.fillRect(0,0,1024,144);
    context.fillStyle='#f8cadb';context.font='56px "Microsoft YaHei",sans-serif';context.textAlign='center';context.fillText(text,512,93);
    const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
    const sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,depthTest:false}));sprite.scale.set(160,22.5,1);sprite.position.set(...pos);
    sceneryGroups.labels.add(sprite);
  }
  label('俱利伽罗：导流龙体',[215,441,100]);label('鸣雷见：终端约束刀',[-255,382,262]);
  label('共同雷池',[175,69,290]);label('主控与周围8接口',[0,55,435]);
