import * as THREE from 'three';

function mobius(radius,width){
  const vertices=[],indices=[],steps=240;
  for(let i=0;i<=steps;i++)for(const side of [-1,1]){
    const a=i/steps*Math.PI*2,v=side*width;
    vertices.push((radius+v*Math.cos(a/2))*Math.cos(a),v*Math.sin(a/2),(radius+v*Math.cos(a/2))*Math.sin(a));
  }
  for(let i=0;i<steps;i++)indices.push(i*2,i*2+1,i*2+3,i*2,i*2+3,i*2+2);
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geometry.setIndex(indices);geometry.computeVertexNormals();return geometry;
}

function glyphTexture(text){
  const canvas=document.createElement('canvas');canvas.width=256;canvas.height=128;
  const ctx=canvas.getContext('2d');ctx.font='bold 100px KaiTi, STKaiti, serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#fff';ctx.fillText(text,128,68);
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;return texture;
}

export function createEffects(scene,data,offset){
  const center=new THREE.Vector3(...data.core_center).add(offset),clip=new THREE.Plane(new THREE.Vector3(0,-1,0),1e6),objects=[];
  const add=(geometry,material)=>{const mesh=new THREE.Mesh(geometry,material);objects.push(mesh);scene.add(mesh);return mesh;};
  const stripGeometry=mobius(31,3.2),strips=[0xf3ba4f,0xe82236].map((color,i)=>{
    const strip=add(stripGeometry,new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide,transparent:true,opacity:.68,depthWrite:false,blending:THREE.AdditiveBlending,clippingPlanes:[clip]}));strip.position.copy(center);strip.rotation.z=i*Math.PI/2+.35;return strip;
  });
  const waveGeometry=new THREE.RingGeometry(.94,1,100),waves=Array.from({length:3},()=>{
    const wave=add(waveGeometry,new THREE.MeshBasicMaterial({color:0x070307,transparent:true,opacity:.6,depthWrite:false,side:THREE.DoubleSide,clippingPlanes:[clip]}));wave.position.copy(center);wave.rotation.x=-Math.PI/2;return wave;
  });
  const origins=data.effects.beam_origins.map(p=>new THREE.Vector3(...p).add(offset));
  const beamGeometry=new THREE.CylinderGeometry(4,4,1,12),beams=origins.map(origin=>{
    const vector=center.clone().sub(origin),beam=add(beamGeometry,new THREE.MeshBasicMaterial({color:0xff243c,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,clippingPlanes:[clip]}));
    beam.position.copy(origin).add(center).multiplyScalar(.5);beam.scale.y=vector.length();beam.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),vector.normalize());return beam;
  });
  const arcRecords=data.effects.feather_emitters.flatMap(({axis,speed,tips})=>tips.map(tip=>({axis:new THREE.Vector3(...axis),speed,tip:new THREE.Vector3(...tip)})));
  const arcGeometry=new THREE.BufferGeometry(),arcPositions=new Float32Array(arcRecords.length*6*6);
  arcGeometry.setAttribute('position',new THREE.BufferAttribute(arcPositions,3));
  const arcMaterial=new THREE.LineBasicMaterial({color:0xff8a48,transparent:true,opacity:.4,depthWrite:false,blending:THREE.AdditiveBlending,clippingPlanes:[clip]});
  const arcs=new THREE.LineSegments(arcGeometry,arcMaterial);arcs.frustumCulled=false;scene.add(arcs);objects.push(arcs);
  const glyphs=['识','破','灭','万象'].map((text,i)=>{
    const texture=glyphTexture(text),sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,color:0xffc251,transparent:true,opacity:.6,depthWrite:false,blending:THREE.AdditiveBlending}));sprite.userData={phase:i/4,texture};sprite.scale.set(20,10,1);scene.add(sprite);objects.push(sprite);return sprite;
  });
  const particleGeometry=new THREE.BufferGeometry(),vertices=[],phases=[];
  for(let i=0;i<900;i++){
    const a=i*2.3999632297,r=22+(i%70)*.9;vertices.push(Math.cos(a)*r,Math.sin(i*1.73)*28,Math.sin(a)*r);phases.push(i/900);
  }
  particleGeometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));particleGeometry.setAttribute('phase',new THREE.Float32BufferAttribute(phases,1));
  const uniforms={time:{value:0},pointScale:{value:1},layerY:{value:1e6},centerY:{value:center.y}};
  const particleMaterial=new THREE.ShaderMaterial({uniforms,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    vertexShader:`attribute float phase;uniform float time,pointScale,layerY,centerY;varying float alpha;void main(){float age=fract(phase+time*.065);vec3 p=position*(.4+age*1.3);p.y+=sin(time*.7+phase*40.)*3.;alpha=(1.-age)*step(centerY+p.y,layerY);gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);gl_PointSize=max(1.,pointScale*2.5);}`,
    fragmentShader:`varying float alpha;void main(){vec2 p=gl_PointCoord-.5;if(max(abs(p.x),abs(p.y))>.44)discard;gl_FragColor=vec4(1.,.58,.16,alpha*.6);}`});
  const particles=new THREE.Points(particleGeometry,particleMaterial);particles.position.copy(center);scene.add(particles);objects.push(particles);
  const rainGeometry=new THREE.BufferGeometry(),rain=[],rainColors=[];
  for(const {top,bottom_y,color} of data.effects.waterfalls)for(let y=bottom_y+3;y<top[1]-3;y+=4){
    rain.push(top[0],y,top[2],top[0],y+1.5,top[2]);const c=new THREE.Color(color);rainColors.push(c.r,c.g,c.b,c.r,c.g,c.b);
  }
  rainGeometry.setAttribute('position',new THREE.Float32BufferAttribute(rain,3));rainGeometry.setAttribute('color',new THREE.Float32BufferAttribute(rainColors,3));
  const rainMaterial=new THREE.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.5,depthWrite:false,blending:THREE.AdditiveBlending,clippingPlanes:[clip]});
  const rainLines=new THREE.LineSegments(rainGeometry,rainMaterial);rainLines.position.copy(offset);scene.add(rainLines);objects.push(rainLines);
  const inkGeometry=new THREE.BufferGeometry(),ink=[];
  for(let i=0;i<1400;i++){const x=487+Math.sin(i*72.13)*430,z=500+Math.sin(i*21.77)*420;ink.push(x,6.3,z);}
  inkGeometry.setAttribute('position',new THREE.Float32BufferAttribute(ink,3));
  const inkMaterial=new THREE.PointsMaterial({color:0xb98a3f,transparent:true,opacity:.36,size:1.25,sizeAttenuation:false,depthWrite:false,clippingPlanes:[clip]});
  const inkPoints=new THREE.Points(inkGeometry,inkMaterial);inkPoints.position.copy(offset);scene.add(inkPoints);objects.push(inkPoints);
  const backgroundScene=new THREE.Scene(),backgroundCamera=new THREE.OrthographicCamera(-1,1,1,-1,0,2),backgroundGeometry=new THREE.PlaneGeometry(2,2),backgroundUniforms={resolution:{value:new THREE.Vector2(1,1)},time:{value:0},work:{value:0},enabled:{value:1}};
  const backgroundMaterial=new THREE.ShaderMaterial({uniforms:backgroundUniforms,depthTest:false,depthWrite:false,
    vertexShader:`void main(){gl_Position=vec4(position.xy,1.,1.);}`,
    fragmentShader:`uniform vec2 resolution;uniform float time,work,enabled;float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}float line(float d,float w){return 1.-smoothstep(w,w+.003,abs(d));}void main(){vec2 uv=gl_FragCoord.xy/resolution,p=uv-vec2(.52,.55);p.x*=resolution.x/resolution.y;float r=length(p),a=atan(p.y,p.x);float ink=h(floor(uv*85.))+h(floor(uv*37.))*.5;vec3 color=mix(vec3(.012,.009,.014),vec3(.048,.012,.020),exp(-r*r*3.)*(.6+work*.4));color+=ink*.004;float seal=line(r-.33,.001)+line(r-.347,.001)+line(r-.29,.001)*step(.3,sin(a*16.));float spokes=line(sin(a*8.)*.1,.0015)*step(.294,r)*step(r,.327);color+=(seal+spokes)*vec3(.16,.105,.032)*enabled;gl_FragColor=vec4(color,1.);}`});
  backgroundScene.add(new THREE.Mesh(backgroundGeometry,backgroundMaterial));
  return {backgroundScene,backgroundCamera,
    update({time,flow,work,effects,section,pointScale,layerY,width,height}){
      const coreVisible=effects&&['all','core','chains'].includes(section),baseVisible=effects&&['all','base','mountains'].includes(section);
      clip.constant=layerY;strips.forEach((strip,i)=>{strip.visible=coreVisible;strip.rotation.y=flow*(i?-.19:.24);});
      waves.forEach((wave,i)=>{const phase=(time*.13+i/3)%1;wave.visible=coreVisible;wave.scale.setScalar(28+phase*135);wave.position.y=center.y+Math.sin(i*2)*4;wave.material.opacity=(1-phase)*.6;});
      const pulse=time%10,amplitude=work?Math.max(0,1-pulse/1.4):0;
      beams.forEach(beam=>{beam.visible=effects&&['all','core','weapons'].includes(section)&&amplitude>0;beam.material.opacity=amplitude*.65;});
      arcRecords.forEach(({axis,speed,tip},index)=>{
        const q=new THREE.Quaternion().setFromAxisAngle(axis,flow*speed),start=tip.clone().applyQuaternion(q),end=start.clone().normalize().multiplyScalar(19),side=new THREE.Vector3().crossVectors(start,axis).normalize();
        for(let segment=0;segment<6;segment++)for(let endpoint=0;endpoint<2;endpoint++){
          const t=(segment+endpoint)/6,jitter=Math.sin(time*18+index*2.1+(segment+endpoint)*4.7)*1.6*Math.sin(Math.PI*t),p=start.clone().lerp(end,t).addScaledVector(side,jitter).add(center);
          p.toArray(arcPositions,index*36+segment*6+endpoint*3);
        }
      });arcGeometry.attributes.position.needsUpdate=true;arcs.visible=coreVisible;arcMaterial.opacity=(work?.6:.28)*(.8+.2*Math.sin(time*9));
      glyphs.forEach((glyph,i)=>{const age=(time*.06+glyph.userData.phase)%1,a=i*Math.PI/2+time*.14,r=35+age*105;glyph.position.copy(center).add(new THREE.Vector3(Math.cos(a)*r,age*45-10,Math.sin(a)*r));glyph.visible=coreVisible&&glyph.position.y<=layerY;glyph.material.opacity=(1-age)*.65;});
      particles.visible=coreVisible;uniforms.time.value=time;uniforms.pointScale.value=pointScale;uniforms.layerY.value=layerY;
      rainLines.visible=effects&&['all','mountains'].includes(section);rainLines.position.y=offset.y-(time*13)%4;inkPoints.visible=baseVisible;inkMaterial.opacity=.2+.12*Math.sin(time*.7);
      backgroundUniforms.resolution.value.set(width,height);backgroundUniforms.time.value=time;backgroundUniforms.work.value=+work;backgroundUniforms.enabled.value=+effects;
    },
    dispose(){objects.forEach(object=>{scene.remove(object);if(object.isSprite)object.userData.texture.dispose();else object.geometry.dispose();object.material.dispose();});backgroundGeometry.dispose();backgroundMaterial.dispose();}
  };
}
