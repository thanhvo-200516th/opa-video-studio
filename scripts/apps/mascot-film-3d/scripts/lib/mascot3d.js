// Bò OPA 3D: đùn khối đúng path "mark" (brand.js), cạnh vát vào trong (viền ngoài giữ đúng vector),
// sừng cử động quanh chân sừng bằng trọng số theo đường vai (một mesh liền, không lộ đường nối).
// Đơn vị vật: px của viewBox 2000. Gốc ở giữa đáy chữ U, y hướng lên, z giữa bề dày; mặt trước nhìn về +z.
import * as THREE from 'three';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';
import { toCreasedNormals } from 'three/addons/utils/BufferGeometryUtils.js';

/** Toạ độ logo (px, y xuống) -> không gian vật (y lên, gốc giữa đáy). */
export function logoToObject(BRAND, [x, y]) {
  const g = BRAND.geometry;
  return [x - (g.bbox[0] + g.bbox[2]) / 2, g.bbox[3] - y];
}

/** Hình học Bò. thick: bội của t (bề dày nét chữ U); bevel: bội của t. */
export function buildMascotGeometry(BRAND, { thick = 1.0, bevel = 0.06, curveSegments = 64, bevelSegments = 3, creaseDeg = 20 } = {}) {
  const g = BRAND.geometry;
  const t = g.t;
  const D = thick * t;
  const b = bevel * t;
  const depth = Math.max(D - 2 * b, 1);
  const svg = new SVGLoader().parse(`<svg xmlns="http://www.w3.org/2000/svg"><path d="${g.mark}"/></svg>`);
  const shapes = SVGLoader.createShapes(svg.paths[0]);
  let geo = new THREE.ExtrudeGeometry(shapes, {
    depth, bevelEnabled: true, bevelThickness: b, bevelSize: b, bevelOffset: -b, bevelSegments, curveSegments,
  });
  geo.rotateX(Math.PI); // lật y (SVG xuống -> three lên) mà không đảo chiều mặt
  geo.translate(-(g.bbox[0] + g.bbox[2]) / 2, g.bbox[3], depth / 2);
  geo = toCreasedNormals(geo, THREE.MathUtils.degToRad(creaseDeg));

  // Trọng số sừng: khoảng cách có dấu tới đường vai (dương về phía ngọn sừng), chuyển mềm trong ±0,35t.
  const pos = geo.attributes.position;
  const w = new Float32Array(pos.count * 2);
  const delta = 0.35 * t;
  const sides = ['left', 'right'].map((k) => {
    const h = g.horns[k];
    const [A, B] = h.shoulder.map((p) => logoToObject(BRAND, p));
    const P = logoToObject(BRAND, h.pivot);
    let nx = -(B[1] - A[1]), ny = B[0] - A[0];
    const len = Math.hypot(nx, ny); nx /= len; ny /= len;
    if (ny < 0) { nx = -nx; ny = -ny; } // ngọn sừng ở phía trên chân sừng
    return { P, nx, ny };
  });
  const smooth = (e0, e1, x) => { const u = Math.min(Math.max((x - e0) / (e1 - e0), 0), 1); return u * u * (3 - 2 * u); };
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    sides.forEach((s, k) => { w[i * 2 + k] = smooth(-delta, delta, (x - s.P[0]) * s.nx + (y - s.P[1]) * s.ny); });
  }
  geo.setAttribute('hornW', new THREE.BufferAttribute(w, 2));
  geo.computeBoundingBox();
  return { geometry: geo, D, t, bevel: b, halfDepth: depth / 2, pivots: sides.map((s) => s.P) };
}

// ---------------------------------------------------------------- biến dạng sừng (dùng chung mọi vật liệu)
const DEFORM_GLSL = /* glsl */ `
attribute vec2 hornW;
uniform vec2 uHornAngle;   // (trái, phải) rad; dương = ngọn sừng xòe ra ngoài
uniform vec4 uHornPivot;   // (xT, yT, xP, yP) trong không gian vật
vec2 boRot(vec2 v, float a) { float c = cos(a), s = sin(a); return vec2(c * v.x - s * v.y, s * v.x + c * v.y); }
vec3 boHornP(vec3 p) {
  p.xy = uHornPivot.xy + boRot(p.xy - uHornPivot.xy, uHornAngle.x * hornW.x);
  p.xy = uHornPivot.zw + boRot(p.xy - uHornPivot.zw, -uHornAngle.y * hornW.y);
  return p;
}
vec3 boHornN(vec3 n) { n.xy = boRot(n.xy, uHornAngle.x * hornW.x - uHornAngle.y * hornW.y); return n; }
`;

function injectDeform(material, uniforms, key) {
  material.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = DEFORM_GLSL + shader.vertexShader
      .replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\nobjectNormal = boHornN(objectNormal);')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\ntransformed = boHornP(transformed);');
  };
  material.customProgramCacheKey = () => key;
  return material;
}

const HERO_VS = /* glsl */ `${DEFORM_GLSL}
varying vec3 vN;
varying vec3 vP;
void main() {
  vN = normalize(boHornN(normal));
  vP = boHornP(position);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(vP, 1.0);
}`;

// C2 (G2, theo góp ý của Minh 19/10: "góc chưa 3D, răng cưa"): mặt trước và mặt sau giữ đúng màu token, phẳng tuyệt đối;
// cạnh vát bo tròn và thành bên nhận sáng trong không gian vật (đèn bám theo Bò), đầu mút là token đậm (#003C99 với Bò xanh).
// Trọng số cạnh vát f tính từ z của điểm (0 trên mặt, 1 ở thành bên) thay vì từ pháp tuyến từng mặt nhỏ, nên ranh màu mượt,
// không khấc theo mặt lưới. Vệt sáng mảnh dọc cạnh vát hướng về đèn làm khối đọc ra 3D. uFlat = 1: phẳng hoàn toàn (khung khóa).
// Màu theo nền từng điểm ảnh (cầu sang end card): chỗ vùng xanh tràn khung nằm sau Bò -> bảng màu trắng; chỗ còn tường ->
// bảng màu xanh (luật MASCOT_ON áp theo nền ngay sau). uWhite ép trắng toàn bộ.
const C2_FS = /* glsl */ `
uniform vec3 uFrontB, uSideB, uHiB, uFrontW, uSideW, uHiW, uKey, uFill;
uniform float uHalfDepth, uBevel, uInvExpo, uFlat, uRim, uWhite, uFloodR, uAspect;
uniform vec2 uFloodC, uRes;
varying vec3 vN;
varying vec3 vP;
void main() {
  vec2 ndc = gl_FragCoord.xy / uRes * 2.0 - 1.0;
  float inFlood = uFloodR > 0.0 ? 1.0 - smoothstep(uFloodR - 0.03, uFloodR, length((ndc - uFloodC) * vec2(uAspect, 1.0))) : 0.0;
  float w = max(uWhite, inFlood);
  vec3 uFront = mix(uFrontB, uFrontW, w), uSide = mix(uSideB, uSideW, w), uHi = mix(uHiB, uHiW, w);
  vec3 n = normalize(vN);
  float f = 1.0 - clamp((abs(vP.z) - uHalfDepth) / uBevel, 0.0, 1.0);
  float e = 0.30 + 0.55 * max(dot(n, uKey), 0.0) + 0.20 * max(dot(n, uFill), 0.0);
  vec3 sideCol = mix(uSide, uFront, clamp((e - 0.30) / 0.70, 0.0, 1.0));
  vec3 col = mix(uFront, sideCol, smoothstep(0.0, 1.0, f));
  float rim = pow(max(dot(n, uKey), 0.0), 4.0) * smoothstep(0.0, 0.35, f) * (1.0 - smoothstep(0.55, 1.0, f));
  col = mix(col, uHi, uRim * rim);
  col = mix(col, uFront, uFlat);
  gl_FragColor = vec4(col * uInvExpo, 1.0);
}`;

/**
 * Tạo Bò. look:
 *  'A' — khối mờ, đèn của cảnh (MeshPhysical, specular 0): sáng tối thay đổi khi Bò xoay.
 *  'B' — khối mờ, đèn chính "bám theo Bò": chiếu sáng tính trong không gian vật, mặt trước luôn đúng màu.
 *  'C' — 3D tô phẳng: mặt trước đúng màu token, thành bên màu token đậm, cạnh vát chuyển mềm.
 * color: 'blue' (mặc định) hoặc 'white' (Bò trắng cho nền xanh/tối).
 */
export function createBo(BRAND, { look = 'B', color = 'blue', thick = 1.0 } = {}) {
  // C2: cạnh vát bo tròn rõ hơn (0,08t, 6 đoạn) và pháp tuyến mượt trên cạnh vát để vệt sáng chạy liền.
  const built = buildMascotGeometry(BRAND, look === 'C2' ? { thick, bevel: 0.08, bevelSegments: 6, creaseDeg: 40 } : { thick });
  const uniforms = {
    uHornAngle: { value: new THREE.Vector2(0, 0) },
    uHornPivot: { value: new THREE.Vector4(built.pivots[0][0], built.pivots[0][1], built.pivots[1][0], built.pivots[1][1]) },
    uInvExpo: { value: 1 },
  };
  const C = BRAND.colors;
  const front = new THREE.Color(color === 'white' ? C.white : C.blue);
  const side = new THREE.Color(color === 'white' ? C.blueLight : C.blueDark);

  let material;
  if (look === 'A') {
    material = injectDeform(new THREE.MeshPhysicalMaterial({ color: front, roughness: 0.65, metalness: 0, specularIntensity: 0 }), uniforms, 'bo-A');
  } else if (look === 'B') {
    // e(n) = kA + kK·max(n·Lk,0) + kF·max(n·Lf,0), chuẩn hóa để mặt trước (n = +z) đúng bằng 1.
    const Lk = new THREE.Vector3(-0.5, 0.5, 0.7071).normalize();
    const Lf = new THREE.Vector3(0.35, 0.05, 0.935).normalize();
    const kA = 0.22, kF = 0.25, kK = (1 - kA - kF * Lf.z) / Lk.z;
    material = new THREE.ShaderMaterial({
      uniforms: { ...uniforms, uAlbedo: { value: front }, uKey: { value: Lk }, uFill: { value: Lf }, uK: { value: new THREE.Vector3(kA, kK, kF) } },
      vertexShader: HERO_VS,
      fragmentShader: /* glsl */ `
        uniform vec3 uAlbedo, uKey, uFill, uK; uniform float uInvExpo; varying vec3 vN;
        void main() { vec3 n = normalize(vN);
          float e = uK.x + uK.y * max(dot(n, uKey), 0.0) + uK.z * max(dot(n, uFill), 0.0);
          gl_FragColor = vec4(uAlbedo * e * uInvExpo, 1.0); }`,
    });
  } else if (look === 'C') {
    material = new THREE.ShaderMaterial({
      uniforms: { ...uniforms, uFront: { value: front }, uSide: { value: side } },
      vertexShader: HERO_VS,
      fragmentShader: /* glsl */ `
        uniform vec3 uFront, uSide; uniform float uInvExpo; varying vec3 vN;
        void main() { float k = smoothstep(0.35, 0.92, normalize(vN).z);
          gl_FragColor = vec4(mix(uSide, uFront, k) * uInvExpo, 1.0); }`,
    });
  } else if (look === 'C2') {
    material = new THREE.ShaderMaterial({
      uniforms: {
        ...uniforms,
        uFrontB: { value: front.clone() }, uSideB: { value: side.clone() }, uHiB: { value: new THREE.Color(color === 'white' ? C.white : C.blueLight) },
        uFrontW: { value: new THREE.Color(C.white) }, uSideW: { value: new THREE.Color(C.blueLight) }, uHiW: { value: new THREE.Color(C.white) },
        uWhite: { value: 0 }, uFloodR: { value: 0 }, uFloodC: { value: new THREE.Vector2() }, uRes: { value: new THREE.Vector2(1920, 1080) }, uAspect: { value: 16 / 9 },
        uKey: { value: new THREE.Vector3(-0.5, 0.6, 0.62).normalize() }, uFill: { value: new THREE.Vector3(0.4, 0.1, 0.9).normalize() },
        uHalfDepth: { value: built.halfDepth }, uBevel: { value: built.bevel }, uFlat: { value: 0 }, uRim: { value: 0.45 },
      },
      vertexShader: HERO_VS,
      fragmentShader: C2_FS,
    });
  } else {
    throw new Error(`look không hợp lệ: ${look}`);
  }

  const mesh = new THREE.Mesh(built.geometry, material);
  mesh.castShadow = true;
  mesh.customDepthMaterial = injectDeform(new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking }), uniforms, 'bo-depth');
  // Mặt nạ đo màu: R = Bò, G = pháp tuyến vật theo z (mặt trước ~ 1).
  const maskMaterial = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: HERO_VS,
    fragmentShader: 'varying vec3 vN; void main(){ gl_FragColor = vec4(1.0, normalize(vN).z * 0.5 + 0.5, 0.0, 1.0); }',
  });
  const flatMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });

  return {
    mesh, material, maskMaterial, flatMaterial, uniforms, D: built.D, t: built.t,
    /** Tư thế: góc sừng (rad, dương = xòe ra), 1/exposure để vật liệu B/C ra đúng màu sau resolve. */
    setPose({ hornL = 0, hornR = 0, invExpo = 1 } = {}) {
      uniforms.uHornAngle.value.set(hornL, hornR);
      uniforms.uInvExpo.value = invExpo;
    },
    /** C2: ép trắng (0–1), độ phẳng (1 = phẳng như logo 2D), vùng xanh tràn khung (tâm NDC, bán kính) và cỡ khung render. */
    setTone({ white = 0, flat = 0, floodC = [0, 0], floodR = 0, res = [1920, 1080] } = {}) {
      const u = material.uniforms;
      if (!u || !u.uFlat) return;
      u.uWhite.value = white;
      u.uFlat.value = flat;
      u.uFloodC.value.set(floodC[0], floodC[1]);
      u.uFloodR.value = floodR;
      u.uRes.value.set(res[0], res[1]);
    },
  };
}
