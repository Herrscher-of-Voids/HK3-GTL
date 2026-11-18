import * as THREE from 'three';

export function buildNativeDetails(scene,data,textures,plane){
  const objects=[],geometries=[],customMaterials=[];
  const barsMaterial=new THREE.MeshLambertMaterial({map:textures[63].east,transparent:true,alphaTest:.1,side:THREE.DoubleSide,clippingPlanes:[plane]});
  const barsGeometry=new THREE.PlaneGeometry(1,1);customMaterials.push(barsMaterial);geometries.push(barsGeometry);
  const torchTexture=textures[67].east.clone();torchTexture.repeat.set(.125,.625);torchTexture.offset.set(.4375,0);torchTexture.needsUpdate=true;
  const torchMaterial=new THREE.MeshLambertMaterial({map:torchTexture,clippingPlanes:[plane],emissive:0xffb75b,emissiveIntensity:.2});
  const torchGeometry=new THREE.BoxGeometry(.125,.625,.125);customMaterials.push(torchMaterial);geometries.push(torchGeometry);
  for(const block of data.native_blocks){
    const root=new THREE.Group();root.position.fromArray(block.pos);
    if(block.state===64){
      const x=new THREE.Mesh(barsGeometry,barsMaterial),z=new THREE.Mesh(barsGeometry,barsMaterial);x.position.set(.5,.5,.5);z.position.copy(x.position);z.rotation.y=Math.PI/2;root.add(x,z);
    }else{
      const shaft=new THREE.Mesh(torchGeometry,torchMaterial),direction=[[1,0],[-1,0],[0,1],[0,-1]][block.state-68];
      shaft.position.set(.5-direction[0]*.23,.54,.5-direction[1]*.23);shaft.rotation.z=-direction[0]*Math.PI/8;shaft.rotation.x=direction[1]*Math.PI/8;root.add(shaft);
    }
    scene.add(root);objects.push({object:root,modelId:block.modelId,material:block.state-1});
  }
  return {
    update(groupVisible,materialVisible){
      objects.forEach(item=>item.object.visible=groupVisible(item.modelId)&&materialVisible(item.material));
    },
    dispose(){geometries.forEach(geometry=>geometry.dispose());customMaterials.forEach(material=>material.dispose());torchTexture.dispose();},
  };
}
