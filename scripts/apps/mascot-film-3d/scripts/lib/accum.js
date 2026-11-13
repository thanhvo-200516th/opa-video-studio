// Tích lũy nhiều mẫu mỗi khung (nhòe chuyển động, xóa phông, khử răng cưa) rồi hoàn thiện trên GPU.
// Mẫu render vào RGBA16F có depth, cộng dồn vào RGBA32F (cộng dồn bằng 16F bị sai số — probe lane T).
// Hoàn thiện: × 1/N × exposure -> (kẹp | Neutral) -> Lanczos-3 xuống 1/scale theo 2 lượt (tuyến tính)
// -> sRGB -> dither TPDF ±1 mức; lật dòng ngay trong shader để readPixels ra ảnh từ trên xuống.
import * as THREE from 'three';

export function halton(i, b) {
  let f = 1, r = 0;
  while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); }
  return r;
}

export function concentric(u, v) {
  const a = 2 * u - 1, b = 2 * v - 1;
  if (a === 0 && b === 0) return [0, 0];
  let r, th;
  if (Math.abs(a) > Math.abs(b)) { r = a; th = (Math.PI / 4) * (b / a); } else { r = b; th = Math.PI / 2 - (Math.PI / 4) * (a / b); }
  return [r * Math.cos(th), r * Math.sin(th)];
}

/** Lệch của mẫu i/N: dt (khung, trong màn trập), điểm ống kính (lx, ly ∈ đĩa đơn vị), lệch dưới điểm ảnh, lệch đèn. N là lũy thừa của 2. */
export function sampleOffsets(i, N, shutterFrames = 0.45) {
  const perm = (i * 7 + 3) % N; // 7 nguyên tố cùng nhau với N = 2^k: tách lệch thời gian khỏi lệch ống kính
  const [lx, ly] = N > 1 ? concentric(halton(i + 1, 5), halton(i + 1, 7)) : [0, 0]; // 1 mẫu (nháp): lỗ kim, không lệch
  return {
    dt: N > 1 ? shutterFrames * ((perm + 0.5) / N - 0.5) : 0,
    lx, ly,
    jx: N > 1 ? halton(i + 1, 2) - 0.5 : 0,
    jy: N > 1 ? halton(i + 1, 3) - 0.5 : 0,
    lu: halton(i + 1, 11), lv: halton(i + 1, 13),
  };
}

const _r = new THREE.Vector3(), _u = new THREE.Vector3();
/** Dời máy theo điểm trên ống kính (giữ mặt phẳng nét ở khoảng cách focus) + lệch dưới điểm ảnh. Gọi sau khi đặt tư thế máy. */
export function lensAndJitter(cam, s, aperture, focus, W, H) {
  cam.updateMatrixWorld();
  _r.setFromMatrixColumn(cam.matrixWorld, 0);
  _u.setFromMatrixColumn(cam.matrixWorld, 1);
  const ex = s.lx * aperture, ey = s.ly * aperture;
  cam.position.addScaledVector(_r, ex).addScaledVector(_u, ey);
  cam.updateMatrixWorld();
  cam.updateProjectionMatrix();
  const e = cam.projectionMatrix.elements;
  e[8] += (-e[0] * ex) / focus - (2 * s.jx) / W;
  e[9] += (-e[5] * ey) / focus - (2 * s.jy) / H;
  cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
}

const VS = 'void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }';
const LZ = 'float sinc(float x){ x *= 3.14159265; return abs(x) < 1e-5 ? 1.0 : sin(x) / x; } float L3(float x){ return abs(x) < 3.0 ? sinc(x) * sinc(x / 3.0) : 0.0; }';

function pass(fragmentShader, uniforms, extra = {}) {
  const m = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader, uniforms, depthTest: false, depthWrite: false, ...extra });
  const sc = new THREE.Scene();
  sc.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), m));
  return { m, sc };
}

export class Accumulator {
  constructor(renderer, { width = 1920, height = 1080, scale = 2 } = {}) {
    if (scale !== 1 && scale !== 2) throw new Error('scale chỉ hỗ trợ 1 hoặc 2');
    const W = width * scale, H = height * scale;
    Object.assign(this, { renderer, w: width, h: height, scale, W, H, n: 0 });
    this.rtS = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: true });
    this.rtA = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType, depthBuffer: false });
    this.rtT = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, depthBuffer: false });
    this.rtH = new THREE.WebGLRenderTarget(width, H, { type: THREE.HalfFloatType, depthBuffer: false });
    this.rtO = new THREE.WebGLRenderTarget(width, height, { type: THREE.UnsignedByteType, depthBuffer: false });
    this.quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const R = scale, c = ((R - 1) / 2).toFixed(1), k0 = -3 * R + 1, k1 = 3 * R;
    this.accum = pass('uniform sampler2D tex; void main(){ gl_FragColor = texelFetch(tex, ivec2(gl_FragCoord.xy), 0); }',
      { tex: { value: this.rtS.texture } },
      { blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendEquation: THREE.AddEquation, transparent: true });
    this.tone = pass(/* glsl */ `
      uniform sampler2D tex; uniform float invN, expo; uniform int mode;
      vec3 neutral(vec3 c){ const float sc = 0.76; const float de = 0.15; float x = min(c.r, min(c.g, c.b));
        float off = x < 0.08 ? x - 6.25 * x * x : 0.04; c -= off; float pk = max(c.r, max(c.g, c.b)); if (pk < sc) return c;
        const float d = 1.0 - sc; float np = 1.0 - d * d / (pk + d - sc); c *= np / pk; float g = 1.0 - 1.0 / (de * (pk - np) + 1.0);
        return mix(c, vec3(np), g); }
      void main(){ vec3 c = max(texelFetch(tex, ivec2(gl_FragCoord.xy), 0).rgb * invN * expo, 0.0);
        gl_FragColor = vec4(mode == 1 ? neutral(c) : clamp(c, 0.0, 1.0), 1.0); }`,
      { tex: { value: this.rtA.texture }, invN: { value: 1 }, expo: { value: 1 }, mode: { value: 0 } });
    this.lh = pass(/* glsl */ `uniform sampler2D tex; ${LZ}
      void main(){ ivec2 q = ivec2(gl_FragCoord.xy); vec3 a = vec3(0.0); float ws = 0.0;
        for (int k = ${k0}; k <= ${k1}; k++) { float w = L3((float(k) - ${c}) / ${R.toFixed(1)});
          a += w * texelFetch(tex, ivec2(clamp(${R} * q.x + k, 0, ${W - 1}), q.y), 0).rgb; ws += w; }
        gl_FragColor = vec4(a / ws, 1.0); }`, { tex: { value: this.rtT.texture } });
    this.lv = pass(/* glsl */ `uniform sampler2D tex; uniform uint frame; uniform float grain; ${LZ}
      uint hsh(uint x){ x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16; return x; }
      float rnd(uvec3 v){ return float(hsh(v.x ^ hsh(v.y ^ hsh(v.z)))) / 4294967296.0; }
      vec3 oetf(vec3 c){ return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(0.0031308, c)); }
      void main(){ ivec2 q = ivec2(gl_FragCoord.xy); int sy = ${R} * (${height - 1} - q.y); vec3 a = vec3(0.0); float ws = 0.0;
        for (int k = ${k0}; k <= ${k1}; k++) { float w = L3((float(k) - ${c}) / ${R.toFixed(1)});
          a += w * texelFetch(tex, ivec2(q.x, clamp(sy + k, 0, ${H - 1})), 0).rgb; ws += w; }
        vec3 col = oetf(clamp(a / ws, 0.0, 1.0)); uvec3 s = uvec3(uint(q.x), uint(q.y), frame);
        float g = grain * (rnd(s + uvec3(9u, 0u, 0u)) + rnd(s + uvec3(10u, 0u, 0u)) - 1.0);
        vec3 d = vec3(rnd(s) - rnd(s + uvec3(1u, 0u, 0u)), rnd(s + uvec3(2u, 0u, 0u)) - rnd(s + uvec3(3u, 0u, 0u)),
                      rnd(s + uvec3(4u, 0u, 0u)) - rnd(s + uvec3(5u, 0u, 0u)));
        gl_FragColor = vec4(clamp(col + (d + g) / 255.0, 0.0, 1.0), 1.0); }`,
      { tex: { value: this.rtH.texture }, frame: { value: 0 }, grain: { value: 0 } });
    this.out = new Uint8Array(width * height * 4);
  }

  begin() {
    const r = this.renderer;
    r.autoClear = false;
    r.setRenderTarget(this.rtA); r.setClearColor(0x000000, 0); r.clear(true, false, false);
    this.n = 0;
  }

  add(scene, camera, clearColor) {
    const r = this.renderer;
    r.setRenderTarget(this.rtS); r.setClearColor(clearColor, 1); r.clear(true, true, false);
    r.render(scene, camera);
    r.setRenderTarget(this.rtA); r.render(this.accum.sc, this.quadCam);
    this.n += 1;
  }

  /** expo: hệ số phơi sáng tuyến tính; tone: 0 = kẹp, 1 = Neutral; grain: biên độ hạt (mức 8-bit). */
  resolve({ expo = 1, tone = 0, frame = 0, grain = 0 } = {}) {
    const r = this.renderer;
    this.tone.m.uniforms.invN.value = 1 / Math.max(this.n, 1);
    this.tone.m.uniforms.expo.value = expo;
    this.tone.m.uniforms.mode.value = tone;
    r.setRenderTarget(this.rtT); r.render(this.tone.sc, this.quadCam);
    r.setRenderTarget(this.rtH); r.render(this.lh.sc, this.quadCam);
    this.lv.m.uniforms.frame.value = frame >>> 0;
    this.lv.m.uniforms.grain.value = grain;
    r.setRenderTarget(this.rtO); r.render(this.lv.sc, this.quadCam);
    r.setRenderTarget(null);
    return this.rtO;
  }

  read() {
    this.renderer.readRenderTargetPixels(this.rtO, 0, 0, this.w, this.h, this.out);
    return this.out;
  }
}
