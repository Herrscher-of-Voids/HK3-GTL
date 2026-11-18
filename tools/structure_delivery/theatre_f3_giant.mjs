export function setupGiantPose({THREE, scene, dominion, rig}) {
  const vector = values => new THREE.Vector3(...values);
  const radians = degrees => degrees * Math.PI / 180;
  const {root, bones} = dominion;
  const waistPivot = vector([0, 920, 0]);
  root.position.set(0, 21, -850);
  rig.actor_root.dominion = root.position.toArray();

  const waist = new THREE.Group();
  waist.name = 'giant_waist';
  waist.position.copy(waistPivot);
  root.add(waist);
  for (const id of ['torso', 'shoulder_-1', 'shoulder_1', 'dominion_p2_head']) {
    const bone = bones.get(id);
    bone.position.sub(waistPivot);
    waist.add(bone);
  }
  waist.rotation.x = radians(65);
  bones.get('dominion_p2_head').rotation.x = radians(8.4);
  scene.updateMatrixWorld(true);

  const arms = [];
  for (const side of [-1, 1]) {
    const sourceShoulder = vector([side * 148, 325, -3]).multiplyScalar(4);
    const sourceElbow = vector([side * 169, 262, 14]).multiplyScalar(4);
    const sourceWrist = vector([side * 188, 142, 39]).multiplyScalar(4);
    const shoulder = waist.localToWorld(sourceShoulder.clone().sub(waistPivot));
    const wrist = vector([side * 480, 731, 80]);
    const upperDirection = sourceElbow.clone().sub(sourceShoulder);
    const forearmDirection = sourceWrist.clone().sub(sourceElbow);
    const upperLength = upperDirection.length();
    const forearmLength = forearmDirection.length();
    const direction = wrist.clone().sub(shoulder);
    const distance = direction.length();
    direction.divideScalar(distance);
    const outward = vector([side, 0, 0]);
    outward.addScaledVector(direction, -outward.dot(direction)).normalize();
    const along = (upperLength ** 2 - forearmLength ** 2 + distance ** 2) / (2 * distance);
    const elbow = shoulder.clone().addScaledVector(direction, along)
      .addScaledVector(outward, Math.sqrt(upperLength ** 2 - along ** 2));

    const upper = bones.get(`main_upper_${side}`);
    upper.position.copy(root.worldToLocal(shoulder.clone()));
    upper.quaternion.setFromUnitVectors(upperDirection.normalize(), elbow.clone().sub(shoulder).normalize());
    const forearm = bones.get(`main_forearm_${side}`);
    forearm.position.copy(root.worldToLocal(elbow.clone()));
    forearm.quaternion.setFromUnitVectors(forearmDirection.normalize(), wrist.clone().sub(elbow).normalize());
    const hand = bones.get(`main_hand_${side}`);
    hand.position.copy(root.worldToLocal(wrist.clone()));
    hand.rotation.set(radians(90), 0, 0);
    arms.push({side, shoulder: shoulder.toArray(), elbow: elbow.toArray(), wrist: wrist.toArray(),
      upper_length: upperLength, forearm_length: forearmLength, shoulder_wrist_distance: distance,
      hand_rotation_x_degrees: 90, wall_contact_y: 619});
  }
  scene.updateMatrixWorld(true);
  return {root: root.position.toArray(), waist_pivot: waistPivot.toArray(),
    waist_world: waist.getWorldPosition(new THREE.Vector3()).toArray(),
    torso_rotation_x_degrees: 65, head_local_rotation_x_degrees: 8.4, arms};
}
