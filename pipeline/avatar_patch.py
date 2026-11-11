"""아바타: 지금의 귀여운 느낌은 그대로, 더 부드럽고 자연스럽게 + 걸음마다 튕기는 움직임 없애기 (2026-11-03)

- 몸통은 어깨가 둥글게 내려오고 허리가 살짝 들어간 한 덩어리(회전체)로, 밑단 고리·각진 띠를 없앴어요.
- 팔다리는 끝으로 갈수록 가늘어지는 원기둥 + 같은 굵기의 관절 구로 이음매가 보이지 않게.
- 머리는 조금 작게(0.92배), 눈은 조금 작고 눈썹·코를 더해 표정이 부드럽게, 볼터치는 옅게.
- 배낭·밑창·끈은 모서리를 둥글린 상자(RoundedBoxGeometry)로, 모든 둥근 면은 분할을 늘려 매끈하게.
- 걸음: 몸이 위아래로 '톡톡' 튀던 |cos| 대신 매끈한 사인 곡선(높이 1/3), 무릎·발목 꺾임도 부드러운 곡선,
  걷다 멈출 때 자세가 툭 바뀌지 않게 걸음 세기를 천천히 따라가요. 계단에서 몸이 튀던 것도 같은 방식으로.
부위 이름(rig·torso·head·lArm…)과 관절 위치는 그대로라 앉기·물 마시기·숨쉬기 동작이 그대로 맞아요.
"""

HIKER_JS = r'''// 2026-11-11 아바타를 더 부드럽고 정교하게 (휴대폰 포함): 천은 보송한 광택(sheen), 피부는 은은하게,
// 모든 면 가장자리에 그 자리 빛을 따라 살짝 밝아지는 부드러운 테두리빛, 발밑엔 은은한 그림자 (그림자를 끈 휴대폰에서도 땅에 붙어 보이게)
const HIKER_SOFT = { blobMat: null };
function hikerSoft(mat, amt){ mat.onBeforeCompile = sh => {
    sh.uniforms.rimA = { value: amt };
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform float rimA;')
      .replace('#include <opaque_fragment>', 'float rimF = pow(1.0 - saturate(dot(normalize(vNormal), normalize(vViewPosition))), 2.4);\n  outgoingLight += rimF*rimA*(reflectedLight.indirectDiffuse + reflectedLight.directDiffuse*0.6 + 0.02*diffuseColor.rgb);\n#include <opaque_fragment>'); };
  mat.customProgramCacheKey = () => 'hikerSoft' + amt; return mat; }
function hikerBlob(){ if(HIKER_SOFT.blobMat) return HIKER_SOFT.blobMat;
  const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'), gr = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(0,0,0,0.55)'); gr.addColorStop(0.45, 'rgba(0,0,0,0.28)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = gr; x.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c); HIKER_SOFT.blobMat = new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, opacity: 0.5, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
  return HIKER_SOFT.blobMat; }
function makeHiker(outfit){
  const g = new THREE.Group(), rig = new THREE.Group(), parts = {}; g.add(rig);
  const HQ = !(typeof GFX !== 'undefined' && GFX.tier === 0);   // 아주 낮은 화질 휴대폰은 보송한 광택만 빼요 (테두리빛·그림자는 그대로)
  const M = (c,r=0.75,m=0) => hikerSoft(new THREE.MeshStandardMaterial({color:c, roughness:r, metalness:m}), m > 0.3 ? 0.15 : 0.5);
  const CL = (c,r=0.8) => hikerSoft(HQ ? new THREE.MeshPhysicalMaterial({color:c, roughness:r, sheen:0.45, sheenRoughness:0.6, sheenColor:new THREE.Color(0xffffff).lerp(new THREE.Color(c), 0.6)}) : new THREE.MeshStandardMaterial({color:c, roughness:r}), 0.55);
  const SK = c => hikerSoft(HQ ? new THREE.MeshPhysicalMaterial({color:c, roughness:0.55, sheen:0.35, sheenRoughness:0.7, sheenColor:new THREE.Color(0xffd2c0)}) : new THREE.MeshStandardMaterial({color:c, roughness:0.58}), 0.45);
  const skinTone = [0xf3d2b4,0xeac39f,0xdcb08a,0xf6dcc4][(Math.random()*4)|0];
  const hairCol = [0x2a1d16,0x4a3020,0x1b1512,0x6a4428][(Math.random()*4)|0];
  const bootCol = [0x7a5232,0x5e4a3a,0x8a6a44,0x4a4440][(Math.random()*4)|0];
  const accent = [0xe0662c,0xd8b03a,0x3a8ac8,0xc83a3a][(Math.random()*4)|0];
  const mats = {jacket:CL(outfit.jacket,0.6), pants:CL(outfit.pants,0.85), hat:CL(outfit.hat,0.8), pack:CL(outfit.pack,0.7), packDark:CL(outfit.pack,0.8),
    skin:SK(skinTone), hair:M(hairCol,0.62), eye:M(0x1f1714,0.18), white:new THREE.MeshBasicMaterial({color:0xffffff}),
    blush:new THREE.MeshBasicMaterial({color:0xff9a90, transparent:true, opacity:0.26, depthWrite:false}), mouth:M(0x8a463a,0.6), trim:M(0xf4efe6,0.85),
    boot:M(bootCol,0.68), bootDark:M(0x3a2c22,0.8), sole:M(0x2a2624,0.95), mid:M(0xc4bcb0,0.8), lace:M(accent,0.6), metal:M(0x9aa0a6,0.35,0.7),
    strap:M(0x34373a,0.8), glove:M(0x3e4248,0.78), grip:M(0x7a5a3c,0.9), shaft:M(accent,0.35,0.5), shaft2:M(0xb9bec4,0.3,0.8), bottle:M(0x6fb6d8,0.2) };
  mats.packDark.color.multiplyScalar(0.72);
  const add = (geo, mat, x, y, z, parent=rig) => { const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); parent.add(m); return m; };
  const cap = (r,len,seg=16) => new THREE.CapsuleGeometry(r,len,8,seg);
  const sph = (r,w=28,h=20) => new THREE.SphereGeometry(r,w,h);
  const lathe = (pts, seg=32) => new THREE.LatheGeometry(pts.map(([r,y]) => new THREE.Vector2(r,y)), seg);
  const rbox = (w,h,d,r) => (typeof RoundedBoxGeometry !== 'undefined') ? new RoundedBoxGeometry(w,h,d,3,Math.min(r, w/2, h/2, d/2)) : new THREE.BoxGeometry(w,h,d);
  // 끝으로 갈수록 가늘어지는 팔다리 마디 (위쪽 피벗에서 아래로 len)
  const limb = (r0, r1, len, mat, parent) => { add(new THREE.CylinderGeometry(r0, r1, len, 24, 1, true), mat, 0, -len/2, 0, parent); add(sph(r1, 22, 16), mat, 0, -len, 0, parent); };

  // ── 몸통: 둥근 어깨 → 살짝 들어간 허리 → 부드러운 밑단 (한 덩어리)
  const body = new THREE.Group(); body.position.y = 0.6; rig.add(body); parts.torso = body;
  add(lathe([[0,-0.07],[0.15,-0.065],[0.196,-0.04],[0.207,0.0],[0.2,0.07],[0.196,0.15],[0.203,0.25],[0.198,0.31],[0.178,0.37],[0.138,0.415],[0.085,0.438],[0,0.445]]), mats.jacket, 0, 0, 0, body).scale.set(1,1,0.84);
  add(new THREE.TorusGeometry(0.098,0.034,16,32), mats.jacket, 0, 0.405, 0.004, body).rotation.x = Math.PI/2;   // 부드럽게 접힌 깃
  add(rbox(0.016,0.3,0.012,0.006), mats.strap, 0, 0.17, 0.168, body);                                          // 지퍼
  add(rbox(0.012,0.03,0.008,0.004), mats.metal, 0, 0.34, 0.165, body);                                         // 지퍼 손잡이
  for(const s of [-1,1]) add(rbox(0.07,0.006,0.01,0.003), mats.strap, s*0.09, 0.06, 0.168, body).rotation.z = s*0.18;   // 주머니 지퍼
  add(lathe([[0,-0.13],[0.12,-0.122],[0.18,-0.09],[0.205,-0.04],[0.207,0.0],[0,0.0]]), mats.pants, 0, -0.02, 0, body).scale.set(1,1,0.84);   // 엉덩이
  add(new THREE.CylinderGeometry(0.06,0.07,0.07,20), mats.skin, 0, 0.47, 0, body);                            // 목
  // ── 머리 (조금 작게)
  const head = new THREE.Group(); head.position.y = 0.62; head.scale.setScalar(0.92); body.add(head); parts.head = head;
  add(sph(0.26,40,30), mats.skin, 0, 0, 0, head).scale.set(1,0.95,0.97);
  add(new THREE.SphereGeometry(0.268,36,22,0,Math.PI*2,0,Math.PI*0.4), mats.hair, 0, 0.0, -0.012, head).scale.set(1,0.98,1);
  add(new THREE.SphereGeometry(0.268,36,22,Math.PI*0.82,Math.PI*1.36,Math.PI*0.38,Math.PI*0.2), mats.hair, 0, 0.0, -0.012, head).scale.set(1,0.98,1);
  for(const s of [-1,1]){
    const e = add(sph(0.036,20,16), mats.eye, s*0.088, -0.03, 0.229, head); e.scale.set(0.82,1.12,0.5);
    add(sph(0.011,10,8), mats.white, s*0.088-0.01, -0.008, 0.248, head);
    add(sph(0.005,8,6), mats.white, s*0.088+0.009, -0.046, 0.246, head);
    const br = add(new THREE.TorusGeometry(0.04,0.0075,8,20,Math.PI*0.62), mats.hair, s*0.09, 0.012, 0.232, head); br.rotation.set(-0.18, s*0.25, Math.PI*0.19 + (s>0 ? 0 : 0)); br.scale.set(1,0.55,1);   // 눈썹
    const b = add(new THREE.CircleGeometry(0.046,24), mats.blush, s*0.152, -0.088, 0.212, head); b.rotation.y = s*0.58; b.scale.y = 0.6;
    add(sph(0.05,18,14), mats.skin, s*0.252, -0.04, 0, head).scale.set(0.45,1,0.78);                          // 귀
  }
  add(new THREE.SphereGeometry(0.266,36,10,Math.PI*0.5-0.95,1.9,Math.PI*0.4,Math.PI*0.1), mats.hair, 0, 0.0, -0.004, head).scale.set(1,0.95,0.97);   // 모자 밑 앞머리
  const mouth = add(new THREE.TorusGeometry(0.022,0.0055,8,18,Math.PI), mats.mouth, 0, -0.098, 0.243, head); mouth.rotation.z = Math.PI; mouth.rotation.x = -0.2;
  add(sph(0.022,16,12), mats.skin, 0, -0.058, 0.252, head).scale.set(1,0.85,0.9);                             // 코
  // ── 여자 아바타: 모자 뒤로 내린 포니테일, 얼굴 옆 머리, 속눈썹
  const fem = new THREE.Group(); head.add(fem); parts.fem = fem;
  { const tail = add(cap(0.072,0.2,16), mats.hair, 0, -0.1, -0.3, fem); tail.rotation.x = 0.55; tail.scale.set(1,1,0.85);
    const tip = add(cap(0.05,0.1,14), mats.hair, 0, -0.27, -0.35, fem); tip.rotation.x = 0.25;
    add(new THREE.TorusGeometry(0.045,0.016,10,20), M(accent,0.6), 0, 0.0, -0.27, fem).rotation.x = 1.0;
    add(new THREE.SphereGeometry(0.2,28,18,0,Math.PI*2,Math.PI*0.35,Math.PI*0.4), mats.hair, 0, -0.06, -0.06, fem).scale.set(1.3,1.1,1.25);
    for(const s of [-1,1]){ const lk = add(cap(0.043,0.16,12), mats.hair, s*0.235, -0.1, 0.07, fem); lk.rotation.z = s*0.12; lk.scale.z = 0.7;
      const lash = add(rbox(0.046,0.007,0.01,0.003), mats.eye, s*0.104, 0.02, 0.237, fem); lash.rotation.z = s*0.35; } }
  fem.visible = outfit.g === 'f';
  // ── 등산용 볼캡
  const hat = new THREE.Group(); hat.position.y = 0.05; head.add(hat); parts.pom = hat;
  add(new THREE.SphereGeometry(0.272,40,20,0,Math.PI*2,0,Math.PI*0.5), mats.hat, 0, 0, 0, hat).scale.set(1,0.8,1.02);
  add(new THREE.CylinderGeometry(0.274,0.274,0.03,40,1,true), mats.hat, 0, 0.0, 0, hat);
  const brim = add(new THREE.CylinderGeometry(0.2,0.2,0.014,32,1,false,-Math.PI/2,Math.PI), mats.hat, 0, -0.005, 0.2, hat); brim.scale.set(1.05,1,0.95); brim.rotation.x = 0.14;
  add(sph(0.02,12,8), mats.hat, 0, 0.218, 0, hat);
  add(new THREE.CircleGeometry(0.035,20), mats.trim, 0, 0.1, 0.25, hat).rotation.x = -0.45;
  add(rbox(0.08,0.02,0.02,0.008), mats.strap, 0, 0.0, -0.268, hat);
  // ── 배낭 (둥근 모서리)
  const pack = new THREE.Group(); pack.position.set(0,0.17,-0.21); body.add(pack);
  add(rbox(0.32,0.38,0.19,0.07), mats.pack, 0, 0, 0, pack);
  add(rbox(0.3,0.1,0.2,0.05), mats.packDark, 0, 0.17, -0.005, pack);                                          // 덮개
  add(rbox(0.06,0.05,0.012,0.006), mats.strap, 0, 0.12, -0.106, pack);
  add(rbox(0.2,0.14,0.06,0.03), mats.packDark, 0, -0.07, -0.1, pack);                                         // 앞주머니
  add(new THREE.TorusGeometry(0.018,0.005,8,16), mats.lace, 0.05, -0.12, -0.13, pack);
  for(const s of [-1,1]) add(rbox(0.014,0.3,0.012,0.005), mats.strap, s*0.13, 0, -0.098, pack).rotation.z = s*0.06;
  add(new THREE.CylinderGeometry(0.032,0.032,0.13,18), mats.bottle, 0.18, -0.06, 0.0, pack);
  add(new THREE.CylinderGeometry(0.022,0.022,0.03,14), mats.strap, 0.18, 0.02, 0.0, pack);
  add(cap(0.05,0.24,18), mats.trim, 0, -0.22, -0.02, pack).rotation.z = Math.PI/2;                            // 매트
  for(const s of [-1,1]){ const st = add(cap(0.02,0.28,10), mats.strap, s*0.1, 0.15, 0.165, body); st.scale.z = 0.5; st.rotation.x = 0.12; }
  add(rbox(0.2,0.018,0.012,0.006), mats.strap, 0, 0.2, 0.185, body);
  // ── 팔: 어깨에서 손목까지 가늘어지는 소매
  function arm(s){
    const top = new THREE.Group(); top.position.set(s*0.226, 0.27, 0); body.add(top);
    add(sph(0.068,24,18), mats.jacket, 0, 0, 0, top);
    limb(0.066, 0.058, 0.15, mats.jacket, top);
    const joint = new THREE.Group(); joint.position.y = -0.15; top.add(joint);
    limb(0.058, 0.05, 0.1, mats.jacket, joint);
    add(lathe([[0.05,0],[0.054,-0.012],[0.052,-0.03],[0,-0.03]], 24), mats.jacket, 0, -0.095, 0, joint);       // 소매 끝
    const end = new THREE.Group(); end.position.y = -0.14; joint.add(end);
    add(sph(0.05,22,16), mats.glove, 0, -0.012, 0.004, end).scale.set(0.82,1.08,1);
    add(cap(0.016,0.03,10), mats.glove, -s*0.038, 0.004, 0.026, end).rotation.z = s*0.6;
    return {top, joint, end};
  }
  parts.lArm = arm(-1); parts.rArm = arm(1);
  { const b = new THREE.Group(); b.position.set(0.0,-0.05,0.04); b.rotation.x = 0.2; parts.lArm.end.add(b);
    add(new THREE.CylinderGeometry(0.034,0.034,0.17,20), new THREE.MeshStandardMaterial({color:0x5fb0e0, roughness:0.15, metalness:0.1, transparent:true, opacity:0.85}), 0, 0.02, 0, b);
    add(new THREE.CylinderGeometry(0.022,0.03,0.035,16), new THREE.MeshStandardMaterial({color:0xe2733a, roughness:0.5}), 0, 0.12, 0, b);
    add(new THREE.CylinderGeometry(0.035,0.035,0.05,20), new THREE.MeshStandardMaterial({color:0xf2efe8, roughness:0.6}), 0, -0.02, 0, b);
    b.scale.setScalar(1.25); b.visible = false; parts.bottle = b; }
  // ── 다리: 허벅지 → 무릎 → 정강이 (이음매 없이)
  function leg(s){
    const top = new THREE.Group(); top.position.set(s*0.095, 0.5, 0); rig.add(top);
    add(sph(0.086,24,18), mats.pants, 0, 0, 0, top);
    limb(0.086, 0.074, 0.17, mats.pants, top);
    const joint = new THREE.Group(); joint.position.y = -0.17; top.add(joint);
    limb(0.074, 0.066, 0.12, mats.pants, joint);
    const end = new THREE.Group(); end.position.y = -0.17; joint.add(end);
    // 등산화: 둥근 밑창 + 중창 + 가죽 갑피 + 앞코 + 발목 패딩 + 끈
    const bz = 0.045;
    add(rbox(0.13,0.032,0.255,0.014), mats.sole, 0, -0.088, bz, end);
    add(rbox(0.128,0.018,0.248,0.008), mats.mid, 0, -0.066, bz, end);
    const foot = add(cap(0.058,0.13,18), mats.boot, 0, -0.03, bz+0.005, end); foot.rotation.x = Math.PI/2; foot.scale.set(1.05,1,0.78);
    const toe = add(new THREE.SphereGeometry(0.06,20,14,0,Math.PI*2,Math.PI*0.35,Math.PI*0.45), mats.bootDark, 0, -0.04, bz+0.075, end); toe.rotation.x = Math.PI/2; toe.scale.set(1.05,1.15,0.75);
    add(new THREE.CylinderGeometry(0.066,0.07,0.1,22), mats.boot, 0, 0.0, 0, end);
    add(new THREE.TorusGeometry(0.064,0.018,12,24), mats.bootDark, 0, 0.05, 0, end).rotation.x = Math.PI/2;
    add(lathe([[0.066,0.1],[0.072,0.085],[0.074,0.06],[0.068,0.05]], 24), mats.pants, 0, 0.0, 0, end);       // 바짓단
    const tongue = add(rbox(0.06,0.11,0.02,0.008), mats.bootDark, 0, -0.005, 0.058, end); tongue.rotation.x = -0.35;
    for(let i=0;i<4;i++){ const l = add(rbox(0.075,0.008,0.008,0.003), mats.lace, 0, 0.03-i*0.028, 0.068+i*0.012, end); l.rotation.z = (i%2?1:-1)*0.25; }
    return {top, joint, end};
  }
  parts.lLeg = leg(-1); parts.rLeg = leg(1);
  // ── 등산 스틱 (오른손)
  const pole = new THREE.Group(); parts.rArm.end.add(pole); parts.pole = pole; pole.position.set(0,-0.01,0.01);
  add(new THREE.CylinderGeometry(0.017,0.014,0.13,14), mats.grip, 0, -0.03, 0, pole);
  add(sph(0.02,12,10), mats.strap, 0, 0.04, 0, pole);
  add(new THREE.TorusGeometry(0.035,0.005,6,18), mats.strap, 0.02, 0.0, 0, pole).rotation.y = Math.PI/2;
  add(new THREE.CylinderGeometry(0.0095,0.0095,0.32,10), mats.shaft, 0, -0.25, 0, pole);
  add(new THREE.CylinderGeometry(0.013,0.013,0.025,12), mats.strap, 0, -0.41, 0, pole);
  add(new THREE.CylinderGeometry(0.0078,0.0078,0.3,10), mats.shaft2, 0, -0.56, 0, pole);
  add(new THREE.CylinderGeometry(0.011,0.011,0.02,12), mats.strap, 0, -0.71, 0, pole);
  add(new THREE.CylinderGeometry(0.0062,0.0062,0.24,10), mats.shaft2, 0, -0.83, 0, pole);
  add(new THREE.CylinderGeometry(0.03,0.03,0.006,16), mats.strap, 0, -0.9, 0, pole);
  add(new THREE.ConeGeometry(0.007,0.04,10), mats.metal, 0, -0.97, 0, pole).rotation.x = Math.PI;
  g.traverse(o=>{ if(o.isMesh && o.material!==mats.blush && o.material!==mats.white) o.castShadow=true; });
  { const b = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 0.95), hikerBlob()); b.rotation.x = -Math.PI/2; b.position.y = 0.03; b.renderOrder = -1; g.add(b); parts.blob = b; }
  return { group:g, rig, parts, mats, setOutfit(o){ for(const k of ['jacket','pants','hat','pack']){ mats[k].color.setHex(o[k]); if(mats[k].sheenColor) mats[k].sheenColor.setHex(0xffffff).lerp(mats[k].color, 0.6); } mats.packDark.color.setHex(o.pack).multiplyScalar(0.72); parts.fem.visible = o.g === 'f'; } };
}
'''


def patch_avatar(P):
    # 둥근 상자
    P.rep("import { Sky } from 'three/addons/objects/Sky.js';",
          "import { Sky } from 'three/addons/objects/Sky.js';\nimport { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';", 1)
    P.sub(r"function makeHiker\(outfit\)\{.*?\n\}\nconst ss = THREE\.MathUtils\.smoothstep;",
          lambda _: HIKER_JS + "const ss = THREE.MathUtils.smoothstep;", flags=__import__('re').S)
    # 걸음: 매끈하게
    P.rep("const p=h.parts, s=Math.sin(phase), c=Math.cos(phase), a=Math.min(1,amt), t=performance.now()/1000;",
          "const p=h.parts, s=Math.sin(phase), c=Math.cos(phase), t=performance.now()/1000;\n"
          "  const now = t, dtA = Math.min(0.1, Math.max(0, now - (h.tA || now))); h.tA = now;\n"
          "  const a = (h.aS = h.aS == null ? Math.min(1,amt) : h.aS + (Math.min(1,amt) - h.aS)*Math.min(1, dtA*5));   // 걸음 세기를 천천히 따라가요", 1)
    P.rep("p.lLeg.top.rotation.x = s*0.65*a - up*0.35*a - Math.max(0,-s)*steep*0.5; p.rLeg.top.rotation.x = -s*0.65*a - up*0.35*a - Math.max(0,s)*steep*0.5;",
          "const sp = v => { const x = Math.max(0, v); return x*x*(1.6 - 0.6*x); };   // 0에서 꺾이지 않는 부드러운 반쪽 곡선\n"
          "  p.lLeg.top.rotation.x = s*0.6*a - up*0.35*a - sp(-s)*steep*0.5; p.rLeg.top.rotation.x = -s*0.6*a - up*0.35*a - sp(s)*steep*0.5;", 1)
    P.rep("p.lLeg.joint.rotation.x = Math.max(0,-c)*lift*a + up*0.2*a; p.rLeg.joint.rotation.x = Math.max(0,c)*lift*a + up*0.2*a;",
          "p.lLeg.joint.rotation.x = (0.08 + sp(-c)*0.92)*lift*a + up*0.2*a; p.rLeg.joint.rotation.x = (0.08 + sp(c)*0.92)*lift*a + up*0.2*a;\n"
          "  p.lLeg.end.rotation.x = -sp(-c)*0.35*a + sp(c)*0.12*a; p.rLeg.end.rotation.x = -sp(c)*0.35*a + sp(-c)*0.12*a;   // 발목: 들 때 발끝이 살짝 따라와요", 1)
    P.rep("p.lArm.top.rotation.set(-s*0.55*a*(1-reach) - reach*(1.2+Math.max(0,s)*0.6), 0, 0.12+0.05*a);",
          "p.lArm.top.rotation.set(-s*0.45*a*(1-reach) - reach*(1.2+sp(s)*0.6), 0, 0.12+0.04*a);", 1)
    P.rep("p.rArm.top.rotation.set(s*0.55*a*(1-reach) - reach*(1.0+Math.max(0,-s)*0.6), 0, -0.12-0.05*a);",
          "p.rArm.top.rotation.set(s*0.45*a*(1-reach) - reach*(1.0+sp(-s)*0.6), 0, -0.12-0.04*a);", 1)
    P.rep("h.rig.position.y = Math.abs(c)*0.06*a*(1-steep*0.5);\n  h.rig.rotation.z = s*0.05*a;",
          "h.rig.position.y = c*c*0.02*a*(1-steep*0.5);   // 두 발이 모일 때 아주 살짝 올라가는 매끈한 곡선 (튕김 없음)\n  h.rig.rotation.z = s*0.025*a; h.rig.rotation.y = s*0.05*a;", 1)
    P.rep("p.head.rotation.set(-c*0.04*a - steep*0.15", "p.head.rotation.set(-c*0.015*a - steep*0.15", 1)
    P.rep(", -s*0.05*a);\n  p.torso.rotation.x = steep*0.1;", ", -s*0.02*a);\n  p.torso.rotation.x = steep*0.1; p.torso.rotation.y = -s*0.07*a;", 1)
    # 계단에서 몸이 튀던 것 → 매끈하게, 발 높이 변화도 아주 짧게 따라가기
    P.rep("(onTrail ? stairAt[nt.i]*Math.abs(Math.sin(st.phase)) : 0), st.z);",
          "(onTrail ? stairAt[nt.i]*0.5*(1 - Math.cos(2*st.phase))*0.5 : 0), st.z);\n"
          "  { const ty = hiker.position.y; if(st.hyS == null || seated || st.sitting || Math.abs(ty - st.hyS) > 1.2) st.hyS = ty; else st.hyS += (ty - st.hyS)*Math.min(1, dt*16); hiker.position.y = st.hyS; }", 1)
    P.rep("p.lLeg.top.rotation.z = 0.12; p.rLeg.top.rotation.z = -0.12;", "p.lLeg.top.rotation.z = 0.12; p.rLeg.top.rotation.z = -0.12; p.lLeg.end.rotation.x = 0; p.rLeg.end.rotation.x = 0; p.torso.rotation.y = 0;", 1)
    # 1인칭 흔들림도 부드럽게
    P.rep("const bob = 0.4*Math.sin(st.phase*2)*", "const bob = 0.22*Math.sin(st.phase*2)*", 1)
