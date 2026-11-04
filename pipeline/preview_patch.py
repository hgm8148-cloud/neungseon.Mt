"""의상 창 미리보기를 게임 속 3D 아바타·텐트로 (2D 그림 대신).

- drawPreview(cv, o): makeHiker 로 만든 실제 아바타를 작은 렌더러로 찍어 canvas 에 옮겨요.
  실패하면(WebGL 없음 등) 원래 2D 그림으로 돌아가요.
- 텐트 색: 정상 야영장에서 쓰는 텐트(CAMP.tents)를 복제해 같은 각도로 찍어요.
"""

PV_JS = r"""
// ---------- 의상 창 3D 미리보기 (pipeline/preview_patch.py) ----------
const PV3 = { r:null, sc:null, cam:null, h:null, tent:null, tm:null };
function pv3Init(){
  if(PV3.r) return true;
  try{
    const c = document.createElement('canvas');
    PV3.r = new THREE.WebGLRenderer({canvas:c, antialias:true, alpha:true, preserveDrawingBuffer:true});
    PV3.r.setPixelRatio(1); PV3.r.outputColorSpace = THREE.SRGBColorSpace;
    PV3.r.toneMapping = THREE.ACESFilmicToneMapping; PV3.r.toneMappingExposure = 1.05;
    PV3.sc = new THREE.Scene();
    PV3.sc.add(new THREE.HemisphereLight(0xeef4ff, 0x8a7458, 1.25));
    const k = new THREE.DirectionalLight(0xfff1de, 2.1); k.position.set(2.2, 3.2, 3.0); PV3.sc.add(k);
    const f = new THREE.DirectionalLight(0xbcd2ff, 0.7); f.position.set(-3, 1.5, -1.5); PV3.sc.add(f);
    PV3.cam = new THREE.PerspectiveCamera(24, 1, 0.05, 50);
    return true;
  }catch(e){ PV3.r = null; return false; }
}
function pv3Shot(cv, obj, az, el, pad){
  const W = cv.width * 2, H = cv.height * 2; PV3.r.setSize(W, H, false);
  PV3.sc.add(obj); obj.updateMatrixWorld(true);
  const bb = new THREE.Box3().setFromObject(obj), ctr = bb.getCenter(new THREE.Vector3()), sz = bb.getSize(new THREE.Vector3());
  PV3.cam.aspect = W / H; const fv = THREE.MathUtils.degToRad(PV3.cam.fov);
  const need = Math.max(sz.y * pad, Math.max(sz.x, sz.z) * pad / PV3.cam.aspect);
  const d = need / 2 / Math.tan(fv / 2) + Math.max(sz.x, sz.z) / 2;
  PV3.cam.position.set(ctr.x + Math.sin(az) * Math.cos(el) * d, ctr.y + Math.sin(el) * d, ctr.z + Math.cos(az) * Math.cos(el) * d);
  PV3.cam.lookAt(ctr); PV3.cam.updateProjectionMatrix();
  PV3.r.render(PV3.sc, PV3.cam); PV3.sc.remove(obj);
  const x = cv.getContext('2d'); x.clearRect(0, 0, cv.width, cv.height); x.imageSmoothingQuality = 'high';
  x.drawImage(PV3.r.domElement, 0, 0, cv.width, cv.height);
}
function pv3(cv, o){
  if(!cv || !pv3Init()) return false;
  try{
    if(!PV3.h){ PV3.h = makeHiker(o); }
    PV3.h.setOutfit(o);
    pv3Shot(cv, PV3.h.group, 0.42, 0.10, 0.9);
    return true;
  }catch(e){ return false; }
}
function tent3(svg){
  if(!svg || !pv3Init()) return;
  try{
    const host = svg.ownerSVGElement || svg; let cv = host.previousElementSibling;
    if(!cv || !cv.classList.contains('tentPv3')){ cv = document.createElement('canvas'); cv.className = 'tentPv3'; cv.width = 176; cv.height = 112; host.before(cv); }
    if(!PV3.tent){ const src = CAMP && CAMP.tents && CAMP.tents[0]; if(!src){ setTimeout(() => tent3(svg), 800); return; }
      PV3.tent = src.g.clone(true); PV3.tent.visible = true; PV3.tent.position.set(0, 0, 0); PV3.tent.rotation.set(0, 0, 0); PV3.tent.scale.set(1, 1, 1);
      PV3.tm = src.m.clone(); PV3.tm.emissiveIntensity = 0;
      PV3.tent.traverse(n => { if(n.isMesh && n.material === src.m) n.material = PV3.tm; if(n.isMesh && n.material === src.doorM){ n.material = src.doorM.clone(); n.material.emissiveIntensity = 0; } });
    }
    PV3.tm.color.setHex(me.tent);
    pv3Shot(cv, PV3.tent, 0.75, 0.30, 0.6);
    host.style.display = 'none';
  }catch(e){ setTimeout(() => tent3(svg), 800); }
}
"""

PV_CSS = ".tentPv3{width:88px;height:56px;flex:none;border-radius:10px;background:linear-gradient(#dfe7ec,#cdbfa8)}\n" \
         ".preview canvas{background:radial-gradient(120% 90% at 50% 30%,#eef3f6 0%,#d5dfe6 55%,#c7b9a2 100%)}\n"


def patch_preview(P):
    P.rep('function drawPreview(cv, o){', PV_JS + 'function drawPreview(cv, o){\n  if(pv3(cv, o)) return;', 1)
    P.rep("$(pv).setAttribute('fill', hex(me.tent));", "$(pv).setAttribute('fill', hex(me.tent)); tent3($(pv));", 1)
    P.rep('</style>', PV_CSS + '</style>', 1)
