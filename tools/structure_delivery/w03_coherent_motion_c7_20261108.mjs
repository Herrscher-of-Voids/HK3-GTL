/** C7：共用刚体运动，防止独立翻转破坏构件净空。 */
import * as THREE from 'three';

async function boot() {
  while (!window.C3_READY) await new Promise(resolve => setTimeout(resolve, 50));
  const bytes = Uint8Array.from(atob(window.W03_MOTION), c => c.charCodeAt(0));
  const config = JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
  window.W03_MOTION = null;
  const api = window.reviewApi, renderer = api.renderer;
  const pivot = new THREE.Vector3(...config.pivot_export);
  const movingScene = new THREE.Scene();
  api.scene.traverse(o => { if (o.isLight) movingScene.add(o.clone()); });
  const groups = config.components.map(info => {
    const group = new THREE.Group(); group.position.set(...info.pivot_export); movingScene.add(group); return group;
  });
  const originalMeshes = [];
  api.scene.traverse(o => { if (o.userData.indices) originalMeshes.push(o); });
  const moved = [], originals = [], zero = new THREE.Matrix4().makeScale(0, 0, 0);
  const matrix = new THREE.Matrix4();
  for (const source of originalMeshes) {
    const material = window.REVIEW.materials.indexOf(source.userData.material);
    if (material < 0) throw new Error('运动组件找不到原始材质');
    config.assignments[material][source.userData.face].forEach((indices, ring) => {
      if (!indices.length) return;
      const translation = config.components[ring].render_translation_xyz, origin = groups[ring].position;
      const shift = new THREE.Matrix4().makeTranslation(-origin.x + translation[0], -origin.y + translation[1], -origin.z + translation[2]);
      const mesh = new THREE.InstancedMesh(source.geometry, source.material, indices.length);
      mesh.frustumCulled = false;
      const saved = new Float32Array(indices.length * 16);
      indices.forEach((index, i) => {
        source.getMatrixAt(index, matrix);
        saved.set(matrix.elements, i * 16);
        mesh.setMatrixAt(i, matrix.clone().premultiply(shift));
        source.setMatrixAt(index, zero);
      });
      source.instanceMatrix.needsUpdate = true;
      mesh.instanceMatrix.needsUpdate = true;
      groups[ring].add(mesh);
      moved.push({mesh, source, indices}); originals.push({source, indices, saved});
    });
  }
  const rotations = config.components[0].rotations.map(r => ({...r, axis:new THREE.Vector3(...r.axis).normalize()}));
  if (!config.components.every(c => JSON.stringify(c.rotations) === JSON.stringify(config.components[0].rotations)
      && JSON.stringify(c.pivot_export) === JSON.stringify(config.pivot_export))) throw new Error('同步运动约束失配');
  const turn = new THREE.Quaternion(), shared = new THREE.Quaternion();
  const spearIndex = config.components.findIndex(c => c.id === 'spears');
  const aimGeometry = new THREE.BufferGeometry();
  const aimPositions = [], aimColors = [];
  config.spears.forEach((s, i) => {
    const color = new THREE.Color().setHSL(i / 6, .8, .7);
    aimPositions.push(...s.tail.map((v, k) => v - config.source_pivot_blueprint[k]), 0, 0, 0);
    aimColors.push(color.r, color.g, color.b, color.r, color.g, color.b);
  });
  aimGeometry.setAttribute('position', new THREE.Float32BufferAttribute(aimPositions, 3));
  aimGeometry.setAttribute('color', new THREE.Float32BufferAttribute(aimColors, 3));
  const aimMaterial = new THREE.LineBasicMaterial({vertexColors:true, transparent:true, opacity:.85, depthTest:false});
  const aimLines = new THREE.LineSegments(aimGeometry, aimMaterial);
  aimLines.visible = false; aimLines.renderOrder = 10; groups[spearIndex].add(aimLines);
  const oldSetView = api.setView;
  const sweptBox = config.conservative_swept_bounds_export;
  const corners = [];
  for (const x of [sweptBox.min[0], sweptBox.max[0]])
    for (const y of [sweptBox.min[1], sweptBox.max[1]])
      for (const z of [sweptBox.min[2], sweptBox.max[2]]) corners.push(new THREE.Vector3(x, y, z));
  api.setView = name => {
    oldSetView(name);
    if (!['front', 'right', 'back', 'top', 'orthofront', 'orthoside'].includes(name)) return;
    const center = new THREE.Vector3().addVectors(new THREE.Vector3(...sweptBox.min), new THREE.Vector3(...sweptBox.max)).multiplyScalar(.5);
    const shift = center.clone().sub(api.controls.target);
    api.controls.target.copy(center); api.camera.position.add(shift); api.controls.update();
    api.camera.updateMatrixWorld(); api.camera.updateProjectionMatrix();
    const projected = corners.map(v => v.clone().project(api.camera));
    const maximum = Math.max(...projected.flatMap(v => [Math.abs(v.x), Math.abs(v.y)]));
    api.camera.zoom *= .86 / maximum;
    api.camera.updateProjectionMatrix(); api.renderer.render(api.scene, api.camera);
  };
  const target = new THREE.WebGLRenderTarget(1, 1, {minFilter:THREE.NearestFilter, magFilter:THREE.NearestFilter});
  target.depthTexture = new THREE.DepthTexture(1, 1, THREE.UnsignedIntType);
  const copyScene = new THREE.Scene(), copyCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const copyMaterial = new THREE.ShaderMaterial({
    uniforms:{colorBuffer:{value:target.texture}, depthBuffer:{value:target.depthTexture}},
    vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}',
    fragmentShader:'uniform sampler2D colorBuffer;uniform sampler2D depthBuffer;varying vec2 vUv;void main(){gl_FragColor=texture2D(colorBuffer,vUv);gl_FragDepthEXT=texture2D(depthBuffer,vUv).x;\n#include <colorspace_fragment>\n}',
    depthWrite:true, depthTest:true, depthFunc:THREE.AlwaysDepth, toneMapped:false
  });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), copyMaterial);
  quad.frustumCulled = false; copyScene.add(quad);
  const actualRender = renderer.render.bind(renderer), size = new THREE.Vector2();
  const stats = {static_passes:0, animation_frames:0, geometry_uploads:moved.length,
    component_counts:groups.map(g => g.children.reduce((n, o) => n + (o.isInstancedMesh ? o.count : 0), 0)),
    fixed_outer_ring:false, base_geometry_sha256_unchanged:true};
  if (JSON.stringify(stats.component_counts) !== JSON.stringify(config.moving_quads)) throw new Error('全动组件表面拆分不完整');
  let dirty = true, seconds = 0, playing = true, timer = 0, last = performance.now(), disposed = false, sliced = false;
  const bar = document.createElement('div');
  bar.style = 'position:absolute;bottom:8px;left:12px;right:12px;z-index:40;padding:10px;background:#172132ed;border:1px solid #9d7fc3;border-radius:7px;color:white;display:flex;align-items:center;gap:10px;flex-wrap:wrap';
  bar.innerHTML = '<button id="motionPlay" type="button">暂停全动</button><button id="motionReset" type="button">复位</button><button id="motionAim" type="button">显示六矛指向线</button><label style="flex:1;min-width:160px">运动周期 <input id="motionTime" aria-label="运动时间" type="range" min="0" max="360" value="0" step="0.1" style="width:100%"></label><output id="motionReadout">0.0 秒</output><span>同步公转 · 立体摆转 · 完整构件净空联动</span>';
  document.getElementById('stage').append(bar);
  const play = bar.querySelector('#motionPlay'), range = bar.querySelector('#motionTime'), readout = bar.querySelector('#motionReadout');
  function apply() {
    shared.identity();
    for (const r of rotations) {
      const angle = r.period_seconds ? r.amplitude_degrees * Math.sin(2 * Math.PI * seconds / r.period_seconds) : seconds * r.degrees_per_second;
      shared.multiply(turn.setFromAxisAngle(r.axis, angle * Math.PI / 180));
    }
    groups.forEach(group => group.quaternion.copy(shared));
    range.value = seconds; readout.textContent = seconds.toFixed(1) + ' 秒';
  }
  function updateFilters() {
    const slice = +document.getElementById('layer').value < window.REVIEW.data.size[1] - 1;
    if (slice !== sliced) {
      sliced = slice;
      // 分层时回到C4原位，避免旧切片高度错误裁剪运动模型。
      for (const {source, indices, saved} of originals) {
        indices.forEach((index, i) => source.setMatrixAt(index, slice ? matrix.fromArray(saved, i * 16) : zero));
        source.instanceMatrix.needsUpdate = true;
      }
      dirty = true;
    }
    groups.forEach(g => g.visible = !slice);
    for (const item of moved) item.mesh.visible = item.source.visible;
  }
  function draw() {
    if (disposed) return;
    updateFilters(); renderer.getDrawingBufferSize(size);
    if (target.width !== size.x || target.height !== size.y) { target.setSize(size.x, size.y); dirty = true; }
    const autoClear = renderer.autoClear, priorTarget = renderer.getRenderTarget();
    if (dirty) {
      renderer.setRenderTarget(target); renderer.autoClear = true;
      actualRender(api.scene, api.camera); dirty = false; stats.static_passes++;
    }
    renderer.setRenderTarget(priorTarget); renderer.autoClear = false; renderer.clear();
    actualRender(copyScene, copyCamera); actualRender(movingScene, api.camera);
    renderer.autoClear = autoClear; stats.animation_frames++;
  }
  // 原有相机与材质控件仍触发重绘；只有这些变化才重建静态画面。
  renderer.render = (scene, camera) => {
    if (scene === api.scene && camera === api.camera) { dirty = true; draw(); }
    else actualRender(scene, camera);
  };
  function schedule() {
    clearTimeout(timer);
    if (!playing || document.hidden || disposed) return;
    timer = setTimeout(() => {
      const now = performance.now(); seconds = (seconds + Math.min(.15, (now - last) / 1000)) % config.cycle_seconds;
      last = now; apply(); draw(); schedule();
    }, 1000 / config.frame_rate_limit);
  }
  function pause(value) {
    playing = !value; play.textContent = playing ? '暂停全动' : '继续全动';
    last = performance.now(); schedule();
  }
  function seek(value) { seconds = Math.max(0, Math.min(config.cycle_seconds, value)); apply(); draw(); }
  play.onclick = () => pause(playing);
  bar.querySelector('#motionAim').onclick = event => {
    aimLines.visible = !aimLines.visible;
    event.target.textContent = aimLines.visible ? '隐藏六矛指向线' : '显示六矛指向线'; draw();
  };
  bar.querySelector('#motionReset').onclick = () => { seek(0); last = performance.now(); };
  range.oninput = () => { pause(true); seek(+range.value); };
  document.addEventListener('visibilitychange', () => { last = performance.now(); schedule(); });
  window.addEventListener('pagehide', () => {
    disposed = true; clearTimeout(timer); target.dispose(); copyMaterial.dispose(); quad.geometry.dispose();
    moved.forEach(({mesh}) => mesh.dispose()); aimGeometry.dispose(); aimMaterial.dispose();
  }, {once:true});
  window.W03Motion = {config, stats, groups, originalMeshes, pivot, pause, seek,
    snapshot:() => ({seconds, playing, sliced, quaternions:groups.map(g => g.quaternion.toArray()),
                    pivots:groups.map(g => g.position.toArray()), stats:{...stats}})};
  const note = document.querySelector('.candidate-note');
  note.textContent = 'C7净空修订：浮空总成同步公转＋X/Z各±8°立体摆转，保持C4全部相对布局；整体上移64格避开底座。五环／36星／核心／完整光柱／六矛／24晶体随动，六矛始终向上指芯。';
  document.querySelector('header > div').textContent = '同步立体外观候选 · 共用刚体运动 · 全周期净空另附证明 · 未批准／未部署';
  apply(); api.setView('front'); draw(); schedule(); window.C7_READY = true;
}
boot().catch(error => { console.error(error); const e = document.createElement('p'); e.textContent = '全动预览初始化失败：' + error.message; document.getElementById('stage').append(e); });
