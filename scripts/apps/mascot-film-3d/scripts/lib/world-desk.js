// Thế giới "Thủ môn" (G2): bàn làm việc ban đêm → ban ngày. Đơn vị mét, gốc ở chỗ Bò đứng trên mặt bàn.
// Bố cục cân (góp ý của Minh 19/10): điện thoại khổng lồ dựng dọc ngay sau Bò (ban đêm màn hình sáng là nền ngay sau Bò xanh),
// chồng sổ bên trái, bảng CRM bên phải, mép bàn phía trước cho cú cứu thua.
// Bóng: đèn chính có diện tích (lệch hướng mỗi mẫu, 7°) + bản đồ bóng 4096 + vệt bóng tiếp xúc nhuộm xanh dưới chân Bò.
import * as THREE from 'three';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';
import { createBo } from './mascot3d.js';

const deg = THREE.MathUtils.degToRad;
const lerp = (a, b, k) => a + (b - a) * k;

// ---------------------------------------------------------------- đèn ban ngày + exposure giải bằng công thức (như G1)
export const LIGHT = {
  key: { elev: 50, az: -30, I: 2.6, jitterDeg: 7 },
  fill: { dir: [0.35, 0.15, 0.92], I: 1.1 },
  hemi: { sky: '#C8DAFF', ground: '#E6F0FF', I: 1.3 },
};
export function dirFrom(elev, az) {
  const e = deg(elev), a = deg(az);
  return new THREE.Vector3(Math.sin(a) * Math.cos(e), Math.sin(e), Math.cos(a) * Math.cos(e));
}
const KEY_DIR = dirFrom(LIGHT.key.elev, LIGHT.key.az);
const FILL_DIR = new THREE.Vector3(...LIGHT.fill.dir).normalize();
export const EXPO = (() => {
  const hemiB = 0.5 * (new THREE.Color(LIGHT.hemi.sky).b + new THREE.Color(LIGHT.hemi.ground).b);
  return (0.995 * Math.PI) / (LIGHT.key.I * KEY_DIR.z + LIGHT.fill.I * FILL_DIR.z + LIGHT.hemi.I * hemiB);
})();
export const INV_EXPO = 1 / EXPO;

// ---------------------------------------------------------------- bố cục (mét)
export const SET = {
  boWidth: 0.30,
  deskFront: 0.40,                       // mép bàn phía trước (z)
  phone: { x: 0, z: -0.42, w: 0.80, h: 1.60, d: 0.05, screenW: 0.76, screenH: 1.56 },
  crm: { x: 0.35, z: -0.02, yaw: -22, w: 0.21, h: 0.15 },        // bản 2: bảng đứng ngay bên phải Bò, luôn trong khung; đủ to để đọc giờ và số khách
  books: { x: -0.46, z: -0.06, n: 3, w: 0.24, d: 0.32, h: 0.026 },   // xa Bò: không che chân Bò ở các góc máy lệch trái
  wallZ: -1.25,
};
export const BOOKS_TOP = SET.books.n * SET.books.h;
/** Bản 2: ô tin mới trên màn hình điện thoại (toạ độ cục bộ của máy, mét: tâm hộp bo) và cỡ bong bóng ở đó (lần cỡ thật). */
export const PHONE_SLOT = { x: 0.22, y: 0.44, scale: 2.2 };

// ---------------------------------------------------------------- hình phụ
function roundedRect(w, h, r) {
  const s = new THREE.Shape(), x0 = -w / 2, x1 = w / 2;
  s.moveTo(x0 + r, 0); s.lineTo(x1 - r, 0); s.absarc(x1 - r, r, r, -Math.PI / 2, 0, false);
  s.lineTo(x1, h - r); s.absarc(x1 - r, h - r, r, 0, Math.PI / 2, false);
  s.lineTo(x0 + r, h); s.absarc(x0 + r, h - r, r, Math.PI / 2, Math.PI, false);
  s.lineTo(x0, r); s.absarc(x0 + r, r, r, Math.PI, 1.5 * Math.PI, false);
  return s;
}
function bubbleShape(w, h, r, tw, th) {
  const x0 = -w / 2, y0 = -h / 2, x1 = w / 2, y1 = h / 2, s = new THREE.Shape();
  s.moveTo(x0 + r + tw, y0);
  s.lineTo(x1 - r, y0); s.absarc(x1 - r, y0 + r, r, -Math.PI / 2, 0, false);
  s.lineTo(x1, y1 - r); s.absarc(x1 - r, y1 - r, r, 0, Math.PI / 2, false);
  s.lineTo(x0 + r, y1); s.absarc(x0 + r, y1 - r, r, Math.PI / 2, Math.PI, false);
  s.lineTo(x0, y0 + r); s.absarc(x0 + r, y0 + r, r, Math.PI, 1.5 * Math.PI, false);
  s.lineTo(x0 + r * 0.4, y0 - th); s.lineTo(x0 + r + tw, y0);
  return s;
}
function extrudeCentered(shape, thickness, bevel, segs = 4) {
  const g = new THREE.ExtrudeGeometry(shape, { depth: thickness - 2 * bevel, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelOffset: -bevel, bevelSegments: segs, curveSegments: 32 });
  g.translate(0, 0, -(thickness - 2 * bevel) / 2);
  return g;
}
export const BUBBLE = { w: 0.040, h: 0.028, r: 0.008, tw: 0.006, th: 0.006, thick: 0.016 };

// Bong bóng kiểu biểu tượng tin nhắn của V2 (src/v2w/scenes/t1/Bubbles.tsx, đơn vị viewBox): vỏ bo R28, đuôi trái, 2 vạch.
const V2B = { w0: 150, h0: 96, r: 28, tail: { baseNear: 29, baseFar: 61, tip: 13, depth: 26 }, bar: { padX: 36, thick: 14, dy: 15, ratio: 0.6 } };
const ICON = { u: BUBBLE.h / V2B.h0, thick: 0.007, bevel: 0.0015 };   // 1 đơn vị viewBox = u mét; rộng 150 u ≈ 44 mm (khe trán 53 mm)
/** Cỡ bong bóng biểu tượng (mét): nửa rộng, nửa cao hộp bo, nửa cao tính cả đuôi (để đặt đáy bóng đúng đáy lòng O). */
export const BUBBLE_ICON = { halfW: (V2B.w0 / 2) * ICON.u, halfH: (V2B.h0 / 2) * ICON.u, halfHTail: (V2B.h0 / 2 + V2B.tail.depth) * ICON.u };
/** Vỏ bong bóng V2 (đuôi trái) theo mét, tâm hộp bo ở gốc, y lên. */
function iconShape() {
  const { w0, h0, r, tail } = V2B, u = ICON.u, X = (x) => (x - w0 / 2) * u, Y = (y) => (h0 / 2 - y) * u, s = new THREE.Shape();
  s.moveTo(X(r), Y(0)); s.lineTo(X(w0 - r), Y(0)); s.absarc(X(w0 - r), Y(r), r * u, Math.PI / 2, 0, true);
  s.lineTo(X(w0), Y(h0 - r)); s.absarc(X(w0 - r), Y(h0 - r), r * u, 0, -Math.PI / 2, true);
  s.lineTo(X(tail.baseFar), Y(h0)); s.lineTo(X(tail.tip), Y(h0 + tail.depth)); s.lineTo(X(tail.baseNear), Y(h0));
  s.lineTo(X(r), Y(h0)); s.absarc(X(r), Y(h0 - r), r * u, -Math.PI / 2, -Math.PI, true);
  s.lineTo(X(0), Y(r)); s.absarc(X(r), Y(r), r * u, Math.PI, Math.PI / 2, true);
  return s;
}
/** Hai vạch chữ của V2 (vạch dưới dài 0,6), mặt phẳng theo mét. */
function iconBarsGeometry() {
  const { w0, h0, bar } = V2B, u = ICON.u, len = w0 - 2 * bar.padX;
  const parts = [len, len * bar.ratio].map((L, i) => {
    const g = new THREE.ShapeGeometry(roundedRect(L * u, bar.thick * u, (bar.thick / 2) * u), 12);
    const yTop = h0 / 2 + (i === 0 ? -bar.dy : bar.dy) - bar.thick / 2;   // đỉnh vạch, toạ độ viewBox (y xuống)
    g.translate((bar.padX + L / 2 - w0 / 2) * u, (h0 / 2 - yTop - bar.thick) * u, 0);
    return g;
  });
  return BufferGeometryUtils.mergeGeometries(parts);
}

// ---------------------------------------------------------------- chữ trong thế giới (texture phẳng, không chịu đèn)
const FONT = '"Be Vietnam Pro"';
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function canvasTexture(w, h) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { cv, ctx: cv.getContext('2d'), tex };
}

/** Màn hình điện thoại khổng lồ: đồng hồ trên cùng; tin nhắn dồn sang NỬA PHẢI (sau và trên đầu Bò) — nửa trái để trống
 *  làm nền trơn cho cột chữ (luật G1: vùng chữ là nền trơn). */
/** Ô tin kiểu V2 trên màn hình (px canvas): vỏ bo + đuôi trái + 2 vạch. fill nhạt (#E6F0FF) thì vạch #003C99, fill đậm thì vạch trắng. */
function drawIconRow(x, C, bx, by, bw, fill = C.blueDark, ratio = V2B.bar.ratio) {   // ratio: độ dài vạch dưới so với vạch trên
  const k = bw / V2B.w0, { r, h0, tail, bar } = V2B;
  x.fillStyle = fill;
  x.beginPath(); x.roundRect(bx, by, bw, h0 * k, r * k);
  x.moveTo(bx + tail.baseNear * k, by + h0 * k - 1); x.lineTo(bx + tail.tip * k, by + (h0 + tail.depth) * k); x.lineTo(bx + tail.baseFar * k, by + h0 * k - 1);
  x.fill();
  x.fillStyle = fill === C.blueDark ? C.white : C.blueDark;
  const len = (V2B.w0 - 2 * bar.padX) * k;
  [len, len * ratio].forEach((L, i) => { rr(x, bx + bar.padX * k, by + (h0 / 2 + (i === 0 ? -bar.dy : bar.dy) - bar.thick / 2) * k, L, bar.thick * k, (bar.thick / 2) * k); x.fill(); });
}

/** Bản 2: cột tin cũ (đã xử lý) ngay trên ô tin mới, cùng cỡ với tin mới. Texture 4 ô lặp dọc; cuộn bằng offset (đơn vị: 1/4 = 1 dòng).
 *  Trả mặt phẳng đặt trong toạ độ cục bộ của điện thoại (đè sát trước màn hình), đáy cách ô tin mới đúng một khe giữa hai dòng. */
function historyColumn(C, P) {
  const pxm = 1024 / P.screenW, bw = V2B.w0 * ICON.u * PHONE_SLOT.scale * pxm, k = bw / V2B.w0;
  const rowH = (V2B.h0 + V2B.tail.depth) * k, gap = 22 * k, pitch = rowH + gap, pad = 8;
  const { cv, ctx: x, tex } = canvasTexture(Math.round(bw + 2 * pad), Math.round(4 * pitch));
  x.fillStyle = C.white; x.fillRect(0, 0, cv.width, cv.height);
  [0.6, 0.85, 0.5, 0.75].forEach((ratio, j) => drawIconRow(x, C, pad, j * (cv.height / 4) + gap / 2, bw, C.blueLight, ratio));
  tex.wrapT = THREE.RepeatWrapping; tex.needsUpdate = true;
  const screenTop = P.h / 2 + P.screenH / 2;
  const bottom = (screenTop - PHONE_SLOT.y) * pxm - (V2B.h0 / 2) * k - gap / 2;   // px canvas từ đỉnh màn hình xuống đáy cột
  tex.repeat.set(1, bottom / cv.height);
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(cv.width / pxm, bottom / pxm), new THREE.MeshBasicMaterial({ map: tex }));
  mesh.position.set(PHONE_SLOT.x, screenTop - bottom / pxm / 2, P.d - 0.004 + 0.0009);
  return mesh;
}

function drawPhone(t, C, clock, icon, corner) {   // corner: màu góc ngoài vùng bo của màn hình = màu thân máy
  const { cv, ctx: x } = t, W = cv.width, H = cv.height;
  x.fillStyle = corner; x.fillRect(0, 0, W, H);
  x.fillStyle = C.white; rr(x, 0, 0, W, H, 64); x.fill();
  x.fillStyle = C.black; x.textAlign = 'center'; x.font = `800 128px ${FONT}`; x.fillText(clock, W / 2, 210);
  x.font = `500 34px ${FONT}`; x.fillStyle = C.blueDark; x.fillText('Tin nhắn mới', W / 2, 270);
  if (icon) {   // bản 2: cột tin cũ là mặt phẳng cuộn riêng (historyColumn); tin mới là bong bóng 3D xanh đậm hiện ngay dưới cột rồi bật ra
    t.tex.needsUpdate = true;
    return;
  }
  const rows = [[560, 380, 400, C.blueLight, 2], [520, 560, 440, C.blueLight, 3], [600, 790, 360, C.blueLight, 2],
    [540, 980, 420, C.blueLight, 3], [580, 1210, 380, C.blueLight, 2], [530, 1400, 430, C.blueLight, 3]];
  for (const [bx, by, bw, fill, lines] of rows) {
    x.fillStyle = fill; rr(x, bx, by, bw, 50 + lines * 44, 34); x.fill();
    x.fillStyle = C.blueDark;
    for (let i = 0; i < lines; i++) { rr(x, bx + 34, by + 34 + i * 44, (bw - 68) * (i === lines - 1 ? 0.55 : 1), 16, 8); x.fill(); }
  }
  t.tex.needsUpdate = true;
}

/** Bảng CRM: n dòng khách (tên giả của V2), nhãn "Đã trả lời".
 *  big (bản 2): chữ to đọc được ở cỡ bảng trên hình (~230 px ngang): giờ, số khách, 2 khách mới nhất. */
function drawCrm(t, C, names, n, clock, big = false) {
  const { cv, ctx: x } = t, W = cv.width, H = cv.height;
  if (big) {
    x.fillStyle = C.white; x.fillRect(0, 0, W, H);   // cả góc ngoài vùng bo cũng trắng như thân bảng (trong suốt thì ra chấm đen)
    x.textAlign = 'left'; x.fillStyle = C.blueDark; x.font = `600 58px ${FONT}`; x.fillText('Khách mới', 44, 84);
    x.fillStyle = C.blue; x.font = `800 104px ${FONT}`; x.fillText(String(n), 44, 186);
    x.textAlign = 'right'; x.fillStyle = C.black; x.font = `800 150px ${FONT}`; x.fillText(clock, W - 40, 172);
    x.textAlign = 'left';
    [0, 1].forEach((i) => {
      const y = 226 + i * 212, name = names[(n - 1 - i + names.length * 8) % names.length];
      x.fillStyle = C.blueLight; rr(x, 28, y, W - 56, 192, 40); x.fill();
      x.fillStyle = C.white; x.beginPath(); x.arc(110, y + 96, 50, 0, Math.PI * 2); x.fill();
      x.fillStyle = C.black; x.font = `600 70px ${FONT}`; x.fillText(name, 186, y + 120);
      const pill = 'Đã trả lời'; x.font = `600 56px ${FONT}`; const pw = x.measureText(pill).width + 56;
      x.fillStyle = C.blue; rr(x, W - 52 - pw, y + 58, pw, 76, 38); x.fill();
      x.fillStyle = C.white; x.fillText(pill, W - 52 - pw + 28, y + 115);
    });
    t.tex.needsUpdate = true;
    return;
  }
  x.clearRect(0, 0, W, H);
  x.fillStyle = C.white; rr(x, 0, 0, W, H, 36); x.fill();
  x.fillStyle = C.black; x.font = `800 46px ${FONT}`; x.textAlign = 'left'; x.fillText('Khách mới', 44, 82);
  // góc phải tiêu đề: giờ (thấy được ở cảnh cận bảng, cả cú tua đêm) và số khách
  x.textAlign = 'right';
  x.font = `800 44px ${FONT}`; x.fillStyle = C.black; x.fillText(clock, W - 44, 82);
  const cw = x.measureText(clock).width;
  x.font = `500 30px ${FONT}`; x.fillStyle = C.blueDark; x.fillText(`${n} ·`, W - 44 - cw - 14, 80); x.textAlign = 'left';
  // 5 khách mới nhất ở trên; danh sách tên ngắn hơn số khách (tua cả đêm tới ~22) nên quay vòng tên
  const shown = Array.from({ length: Math.min(5, n) }, (_, i) => names[(n - 1 - i) % names.length]);
  shown.forEach((name, i) => {
    const y = 116 + i * 96;
    x.fillStyle = C.blueLight; rr(x, 32, y, W - 64, 80, 22); x.fill();
    x.fillStyle = C.white; x.beginPath(); x.arc(84, y + 40, 24, 0, Math.PI * 2); x.fill();
    x.fillStyle = C.black; x.font = `500 32px ${FONT}`; x.fillText(name, 124, y + 51);
    const pill = 'Đã trả lời'; x.font = `500 26px ${FONT}`; const pw = x.measureText(pill).width + 40;
    x.fillStyle = C.blue; rr(x, W - 52 - pw, y + 20, pw, 40, 20); x.fill();
    x.fillStyle = C.white; x.fillText(pill, W - 52 - pw + 20, y + 49);
  });
  t.tex.needsUpdate = true;
}

function contactTexture() {
  const { cv, ctx: x, tex } = canvasTexture(256, 256);
  const g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0.0, 'rgb(96,120,176)');   // lõi bóng tiếp xúc ngả xanh (nhân với nền trắng ≈ #6078B0)
  g.addColorStop(0.35, 'rgb(150,168,210)');
  g.addColorStop(0.7, 'rgb(220,228,244)');
  g.addColorStop(1.0, 'rgb(255,255,255)');
  x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  tex.needsUpdate = true;
  return tex;
}

// ---------------------------------------------------------------- thế giới
export class DeskWorld {
  /** style.bg: 'room' (phòng có đèn, bản 1) | 'flat' (nền liền một màu như V2: đêm #003C99 → sáng trắng, đèn vật cố định).
   *  style.bubble: 'block' (khối trắng viền, bản 1) | 'icon' (biểu tượng tin nhắn V2: xanh đậm, 2 vạch trắng; hứng → xanh OPA). */
  constructor(renderer, BRAND, { names, style = {} }) {
    RectAreaLightUniformsLib.init();
    this.renderer = renderer;
    this.C = BRAND.colors;
    this.G = BRAND.geometry;
    this.S = SET.boWidth / (this.G.bbox[2] - this.G.bbox[0]);   // mét mỗi px logo
    this.names = names;
    this.style = { bg: style.bg ?? 'flat', bubble: style.bubble ?? 'icon' };   // mặc định = bản 2 (Minh duyệt 21/10)
    const flat = this.style.bg === 'flat', icon = this.style.bubble === 'icon';
    const C = this.C;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.02, 30);
    this.clearColor = new THREE.Color(C.black);
    const lit = (color, roughness = 0.9) => new THREE.MeshStandardMaterial({ color, roughness, metalness: 0 });

    // đèn
    this.hemi = new THREE.HemisphereLight(LIGHT.hemi.sky, LIGHT.hemi.ground, LIGHT.hemi.I);
    this.key = new THREE.DirectionalLight(0xffffff, LIGHT.key.I);
    this.key.castShadow = true;
    this.key.shadow.mapSize.set(4096, 4096);
    Object.assign(this.key.shadow.camera, { left: -1.2, right: 1.2, top: 1.2, bottom: -1.2, near: 0.1, far: 6 });
    this.key.shadow.bias = -0.0003; this.key.shadow.normalBias = 0.0015; this.key.shadow.radius = 1;
    this.fill = new THREE.DirectionalLight(0xffffff, LIGHT.fill.I);
    const P = SET.phone;
    this.phoneLight = new THREE.RectAreaLight(0xffffff, 0, P.screenW, P.screenH);
    this.crmLight = new THREE.RectAreaLight(0xffffff, 0, SET.crm.w, SET.crm.h);
    this.scene.add(this.hemi, this.key, this.key.target, this.fill, this.fill.target, this.phoneLight, this.crmLight);

    // bàn (khối có mép trước), sàn tối, tường
    this.deskMat = lit(C.white, 0.92);
    const desk = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.05, SET.deskFront - SET.wallZ), this.deskMat);
    desk.position.set(0, -0.025, (SET.deskFront + SET.wallZ) / 2); desk.receiveShadow = true;
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), lit(C.black, 1));
    floor.rotation.x = -Math.PI / 2; floor.position.y = -0.75;
    this.wallMat = lit(C.blueLight, 1);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(12, 6), this.wallMat);
    wall.position.set(0, 1.5, SET.wallZ); wall.receiveShadow = true;
    if (flat) {   // nền liền: bàn, sàn, tường cùng một màu không chịu đèn → không còn mảng xám đen loang
      this.fieldMat = new THREE.MeshBasicMaterial({ color: C.blueDark });
      for (const m of [desk, floor, wall]) m.material = this.fieldMat;
    }
    this.scene.add(desk, floor, wall);

    // điện thoại khổng lồ: thân đen, màn hình tự sáng
    this.phone = new THREE.Group();
    // nền liền: máy trắng (viền đen là nét đen duy nhất trên nền sáng và cắt ngang câu chốt ban ngày)
    const body = new THREE.Mesh(new THREE.ExtrudeGeometry(roundedRect(P.w, P.h, 0.09), { depth: P.d - 0.008, bevelEnabled: true, bevelThickness: 0.004, bevelSize: 0.004, bevelSegments: 3, curveSegments: 24 }), flat ? lit(C.white, 0.9) : lit(C.black, 0.7));
    body.castShadow = true; body.receiveShadow = true;
    this.phoneTex = canvasTexture(1024, 2102);
    this.phoneClock = null;
    const screenMat = new THREE.MeshBasicMaterial({ map: this.phoneTex.tex });
    const screen = new THREE.Mesh(new THREE.PlaneGeometry(P.screenW, P.screenH), screenMat);
    screen.position.set(0, P.h / 2, P.d - 0.004 + 0.0006);
    this.phone.add(body, screen);
    this.history = icon ? historyColumn(C, P) : null;
    if (this.history) this.phone.add(this.history);
    this.phone.position.set(P.x, 0, P.z); this.phone.rotation.x = deg(-3);
    this.scene.add(this.phone);
    this.phoneLight.position.set(P.x, P.h / 2, P.z + P.d + 0.01); this.phoneLight.lookAt(P.x, P.h / 2, 5);

    // bảng CRM (máy tính bảng dựng nghiêng)
    const R = SET.crm;
    this.crm = new THREE.Group();
    const tab = new THREE.Mesh(new THREE.ExtrudeGeometry(roundedRect(R.w, R.h, 0.03), { depth: 0.012, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.003, bevelSegments: 2, curveSegments: 16 }), lit(C.white, 0.85));
    tab.castShadow = true;
    this.crmTex = canvasTexture(940, 660);
    this.crmRows = -1;
    const crmScreen = new THREE.Mesh(new THREE.PlaneGeometry(R.w - 0.02, R.h - 0.02), new THREE.MeshBasicMaterial({ map: this.crmTex.tex }));
    crmScreen.position.set(0, R.h / 2, 0.0156);
    const tilt = new THREE.Group(); tilt.rotation.x = deg(-14); tilt.add(tab, crmScreen);
    this.crm.add(tilt); this.crm.position.set(R.x, 0, R.z); this.crm.rotation.y = deg(R.yaw);
    this.scene.add(this.crm);
    this.crmLight.position.set(R.x, R.h / 2, R.z + 0.03); this.crmLight.lookAt(R.x + 5 * Math.sin(deg(R.yaw)), R.h / 2, R.z + 5 * Math.cos(deg(R.yaw)));
    this.unlit = [screenMat, crmScreen.material, ...(this.history ? [this.history.material] : [])];

    // chồng sổ (bìa theo bảng màu)
    const B = SET.books;
    this.books = new THREE.Group();
    // nền liền: sổ đáy xanh OPA (#003C99 tan vào nền đêm, trông như tấm kính mờ)
    (flat ? [C.blue, C.white, C.blueLight] : [C.blueDark, C.white, C.blueLight]).slice(0, B.n).forEach((col, i) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(B.w, B.h - 0.002, B.d), lit(col, 0.8));
      m.position.set((i - 1) * 0.006, i * B.h + B.h / 2, (1 - i) * 0.005); m.rotation.y = deg((i - 1) * 3);
      m.castShadow = true; m.receiveShadow = true; this.books.add(m);
    });
    this.books.position.set(B.x, 0, B.z); this.books.rotation.y = deg(8);
    this.scene.add(this.books);

    // bong bóng tin nhắn: tự sáng (đọc được cả trước màn hình trắng lẫn nền tối). Bản 1 ('block'): mặt trắng, viền #003C99;
    // đã hứng: mặt chuyển #0068FF. Nhóm 0 của ExtrudeGeometry là hai mặt, nhóm 1 là thành và cạnh vát.
    // 'icon': vỏ biểu tượng tin nhắn V2 dày 7 mm, 2 vạch trắng ở cả hai mặt (lộn nhào vẫn thấy chữ).
    const bGeo = icon ? extrudeCentered(iconShape(), ICON.thick, ICON.bevel)
      : extrudeCentered(bubbleShape(BUBBLE.w, BUBBLE.h, BUBBLE.r, BUBBLE.tw, BUBBLE.th), BUBBLE.thick, 0.003);
    const barsGeo = icon ? iconBarsGeometry() : null;
    this.bubbles = Array.from({ length: 10 }, () => {
      const face = new THREE.MeshBasicMaterial({ color: C.white });
      const rim = new THREE.MeshBasicMaterial({ color: C.blueDark });
      const m = new THREE.Mesh(bGeo, [face, rim]);
      m.castShadow = true; m.visible = false; this.scene.add(m);
      if (icon) {
        const barMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(C.white).multiplyScalar(INV_EXPO), polygonOffset: true, polygonOffsetFactor: -2 });
        const front = new THREE.Mesh(barsGeo, barMat), back = new THREE.Mesh(barsGeo, barMat);
        front.position.z = ICON.thick / 2 + 0.0002;
        back.rotation.y = Math.PI; back.position.z = -ICON.thick / 2 - 0.0002;
        m.add(front, back);
      }
      return m;
    });

    // nền liền không nhận bóng đổ: vệt bóng tiếp xúc dưới đồ vật để chúng đứng trên nền, không lơ lửng.
    // Vệt là vật trong suốt (vẽ sau mọi vật đục, kể cả vùng xanh tràn) nên phải tắt khi vùng xanh tràn: this.decals.
    this.decals = [];
    if (flat) {
      const contactAt = (x, z, sx, sz, yaw) => {
        const c = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShaderMaterial({
          uniforms: { map: { value: contactTexture() }, uFade: { value: 0.85 } },
          vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
          fragmentShader: 'uniform sampler2D map; uniform float uFade; varying vec2 vUv; void main(){ gl_FragColor = vec4(mix(vec3(1.0), texture2D(map, vUv).rgb, uFade), 1.0); }',
          blending: THREE.MultiplyBlending, premultipliedAlpha: true, transparent: true, depthWrite: false }));
        c.rotation.set(-Math.PI / 2, 0, deg(yaw)); c.position.set(x, 0.0006, z); c.scale.set(sx, sz, 1); c.renderOrder = 2;
        this.scene.add(c); this.decals.push(c);
      };
      contactAt(P.x, P.z + P.d * 0.6, P.w * 1.15, 0.16, 0);
      contactAt(R.x, R.z + 0.02, R.w * 1.1, 0.14, R.yaw);   // rotation.z của vệt nằm = góc xoay quanh trục đứng (như vệt dưới Bò)
      contactAt(B.x, B.z, B.w * 1.35, B.d * 1.3, 8);
    }

    // hạt thở phì
    this.particleMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(C.blue).multiplyScalar(INV_EXPO) });
    this.particles = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 14, 10), this.particleMat, 32);
    this.scene.add(this.particles);

    // Bò + bóng tiếp xúc
    this.bo = createBo(BRAND, { look: 'C2', thick: 1.0, color: 'blue' });
    this.bo.mesh.renderOrder = 10;
    this.boGroup = new THREE.Group(); this.boGroup.add(this.bo.mesh); this.scene.add(this.boGroup);
    // nhân màu với mặt bàn; mờ dần bằng cách trộn về trắng (độ trong suốt sẽ làm tối thêm khi nhân)
    this.contact = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShaderMaterial({
      uniforms: { map: { value: contactTexture() }, uFade: { value: 1 } },
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: 'uniform sampler2D map; uniform float uFade; varying vec2 vUv; void main(){ gl_FragColor = vec4(mix(vec3(1.0), texture2D(map, vUv).rgb, uFade), 1.0); }',
      blending: THREE.MultiplyBlending, premultipliedAlpha: true, transparent: true, depthWrite: false }));
    this.contact.rotation.x = -Math.PI / 2; this.contact.renderOrder = 2;
    this.scene.add(this.contact);

    // vùng xanh tràn khung (cầu sang end card): vẽ sau cảnh, trước Bò, không thử độ sâu
    this.flood = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
      uniforms: { uColor: { value: new THREE.Color(C.blue).multiplyScalar(INV_EXPO) }, uC: { value: new THREE.Vector2() }, uR: { value: 0 }, uAspect: { value: 16 / 9 } },
      vertexShader: 'varying vec2 vUv; void main(){ vUv = position.xy; gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: `uniform vec3 uColor; uniform vec2 uC; uniform float uR, uAspect; varying vec2 vUv;
        void main(){ vec2 d = (vUv - uC) * vec2(uAspect, 1.0); if (length(d) > uR) discard; gl_FragColor = vec4(uColor, 1.0); }`,
      depthTest: false, depthWrite: false }));
    this.flood.frustumCulled = false; this.flood.renderOrder = 5; this.flood.visible = false;
    // Sau khi vẽ vùng xanh: xóa độ sâu để Bò (vẽ sau) không bị vật đã bị phủ (chồng sổ trước mặt) che thành vết khuyết.
    this.flood.onAfterRender = (r) => r.clearDepth();
    this.scene.add(this.flood);

    this.maskBlack = new THREE.MeshBasicMaterial({ color: 0x000000 });
    this._m = new THREE.Matrix4(); this._v = new THREE.Vector3(); this._q = new THREE.Quaternion(); this._s = new THREE.Vector3();
  }

  /** Áp trạng thái cảnh p tại một mẫu (s = lệch mẫu, null nếu không lệch). */
  apply(p, s) {
    const C = this.C, k = THREE.MathUtils.clamp(p.dayMix, 0, 1), flat = this.style.bg === 'flat';
    // ánh sáng đêm ↔ ngày
    // đêm: phòng gần tối hẳn, ánh sáng chính là màn hình (cường độ 4 làm mặt bàn trắng xóa ở bản đầu → 1,0).
    // nền liền ('flat'): đèn cho đồ vật luôn như ban ngày; đêm/ngày chỉ đổi màu nền (#003C99 → trắng), như trường đêm/ngày của V2.
    const kl = flat ? 1 : k;
    this.hemi.intensity = lerp(0.03, LIGHT.hemi.I, kl);
    this.key.intensity = lerp(0, LIGHT.key.I, kl);
    this.fill.intensity = lerp(0.04, LIGHT.fill.I, kl);
    this.phoneLight.intensity = lerp(1.0, 0.6, kl);
    this.crmLight.intensity = lerp(0.8, 0.3, kl);
    if (flat) {   // trộn trong sRGB như chuyển màu của V2 (trộn tuyến tính ra màu xám đục giữa chừng)
      const a = new THREE.Color(C.blueDark).getRGB({}, THREE.SRGBColorSpace), b = new THREE.Color(C.white).getRGB({}, THREE.SRGBColorSpace);
      this.clearColor.setRGB(lerp(a.r, b.r, k), lerp(a.g, b.g, k), lerp(a.b, b.b, k), THREE.SRGBColorSpace);
      this.fieldMat.color.copy(this.clearColor).multiplyScalar(INV_EXPO);
    } else {
      this.clearColor.set(C.black).lerp(new THREE.Color(C.blueLight), k);
    }
    const jr = deg(LIGHT.key.jitterDeg) * Math.sqrt(s ? s.lu : 0), ja = 2 * Math.PI * (s ? s.lv : 0);
    const kd = dirFrom(LIGHT.key.elev + THREE.MathUtils.radToDeg(jr * Math.sin(ja)), LIGHT.key.az + THREE.MathUtils.radToDeg(jr * Math.cos(ja)));
    this.key.target.position.set(0, 0.1, 0); this.key.position.copy(kd).multiplyScalar(3).add(this.key.target.position);
    this.fill.target.position.set(0, 0.1, 0); this.fill.position.copy(FILL_DIR).multiplyScalar(3).add(this.fill.target.position);
    for (const m of this.unlit) m.color.setScalar(INV_EXPO);

    // chữ trong thế giới (vẽ lại khi đổi)
    if (p.clock !== this.phoneClock) { drawPhone(this.phoneTex, C, p.clock, this.style.bubble === 'icon', flat ? C.white : C.black); this.phoneClock = p.clock; }
    if (this.history) this.history.material.map.offset.y = -(p.phoneScroll ?? 0) / 4;   // cột tin cũ cuộn lên p.phoneScroll dòng
    if (p.crmRows !== this.crmRows || p.clock !== this.crmClock) {
      drawCrm(this.crmTex, C, this.names, p.crmRows, p.clock, flat); this.crmRows = p.crmRows; this.crmClock = p.clock;
    }

    // Bò
    const b = p.bo;
    this.boGroup.position.set(b.x, b.y, b.z);
    this.boGroup.rotation.set(0, 0, 0); this.boGroup.rotateY(deg(b.yaw)); this.boGroup.rotateZ(deg(b.roll)); this.boGroup.rotateX(deg(b.pitch));
    this.bo.mesh.scale.set(this.S * b.breathe, this.S * b.breathe, this.S * b.breathe * (b.depth ?? 1)); // depth < 1: dẹt về dấu 2D
    this.bo.setPose({ hornL: deg(b.hornL), hornR: deg(b.hornR), invExpo: INV_EXPO });
    this.boGroup.updateMatrixWorld(true);
    const boM = this.bo.mesh.matrixWorld;

    // bóng tiếp xúc: đậm khi chạm bàn, nhạt và loe ra khi Bò bật lên; tắt khi Bò rời mặt bàn chính
    const h = Math.max(b.y - (b.groundY ?? 0), 0);
    const fade = Math.exp(-h / 0.03) * (b.contact ?? 1) * (p.flood && p.flood.r > 0 ? 0 : 1);
    this.contact.visible = fade > 0.01;
    this.contact.position.set(b.x, (b.groundY ?? 0) + 0.0008, b.z);
    this.contact.rotation.z = deg(b.yaw);
    const spread = 1 + h * 6;
    this.contact.scale.set(0.20 * spread, 0.075 * spread, 1);
    this.contact.material.uniforms.uFade.value = fade;

    // bong bóng
    this.bubbles.forEach((m, i) => {
      const q = p.bubbles[i];
      m.visible = !!(q && q.visible);
      if (!m.visible) return;
      if (q.local) {
        this._v.set(...q.pos).applyMatrix4(boM); m.position.copy(this._v);
        boM.decompose(this._s, this._q, new THREE.Vector3());
        m.quaternion.copy(this._q).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, deg(q.rotZ || 0))));
      } else {
        m.position.set(...q.pos); m.quaternion.setFromEuler(new THREE.Euler(...q.rot.map(deg)));
      }
      m.scale.setScalar(q.scale ?? 1);
      if (this.style.bubble === 'icon') {   // tin khách #003C99 → đã hứng #0068FF; thành bên tối hơn mặt 22 % cho ra khối
        m.material[0].color.set(C.blueDark).lerp(new THREE.Color(C.blue), q.caught).multiplyScalar(INV_EXPO);
        m.material[1].color.copy(m.material[0].color).multiplyScalar(0.78);
      } else {
        m.material[0].color.set(C.white).lerp(new THREE.Color(C.blue), q.caught).multiplyScalar(INV_EXPO);
        m.material[1].color.set(C.blueDark).multiplyScalar(INV_EXPO);
      }
    });

    // hạt thở phì (toạ độ vật của Bò, bán kính mét)
    for (let i = 0; i < this.particles.count; i++) {
      const q = p.particles[i];
      if (!q) { this._m.makeScale(0, 0, 0); this.particles.setMatrixAt(i, this._m); continue; }
      this._v.set(q[0], q[1], q[2]).applyMatrix4(boM);
      this._m.makeScale(q[3], q[3], q[3]).setPosition(this._v);
      this.particles.setMatrixAt(i, this._m);
    }
    this.particles.instanceMatrix.needsUpdate = true;

    // máy quay
    const c = p.cam;
    this.camera.fov = c.fov; this.camera.position.set(...c.pos); this.camera.lookAt(...c.target);
    this.camera.updateProjectionMatrix(); this.camera.updateMatrixWorld();
    this.focus = c.focus ?? this.camera.position.distanceTo(new THREE.Vector3(b.x, b.y + 0.13, b.z));
    this.aperture = c.aperture ?? 0.006;

    // vùng xanh tràn khung: tâm = lòng O của Bò chiếu lên màn hình; Bò đổi màu theo đúng vùng xanh nằm sau nó
    this.flood.visible = !!(p.flood && p.flood.r > 0);
    for (const d of this.decals) d.visible = !this.flood.visible;
    let floodC = [0, 0];
    if (this.flood.visible) {
      this._v.set(0, (this.G.bbox[3] - (this.G.hole.top + this.G.hole.bottom) / 2), 0).applyMatrix4(boM).project(this.camera);
      floodC = [this._v.x, this._v.y];
      this.flood.material.uniforms.uC.value.set(...floodC);
      this.flood.material.uniforms.uR.value = p.flood.r;
    }
    this.bo.setTone({ white: b.white ?? 0, flat: b.flat ?? 0, floodC, floodR: this.flood.visible ? p.flood.r : 0, res: this.res ?? [1920, 1080] });
  }

  /** Mặt nạ đo màu: R = Bò, G = pháp tuyến vật z; vật khác vẽ đen (tính cả che khuất). */
  renderMask(target) {
    const saved = [];
    this.scene.traverse((o) => { if (o.isMesh) { saved.push([o, o.material]); o.material = o === this.bo.mesh ? this.bo.maskMaterial : this.maskBlack; } });
    const r = this.renderer;
    r.setRenderTarget(target); r.setClearColor(0x000000, 1); r.clear(true, true, false);
    r.render(this.scene, this.camera);
    r.setRenderTarget(null);
    for (const [o, m] of saved) o.material = m;
  }
}
