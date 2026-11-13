// Bộ icon phẳng (thay emoji ✅ 👉 và minh họa tính năng) + mascot Bò OPA từ đúng path của mascot/opa-mascot-parts.svg.
// Icon vẽ trong ô 100×100 quanh tâm (0,0); 'FG' = màu nét/hình, 'BG' = màu nền tròn (dùng để khoét).
OPA.ICON = {
  check: [{ t: 'path', v: [[-24, 2], [-7, 19], [25, -16]], closed: false, stroke: 'FG', sw: 12, name: 'Dau tich' }],
  bang: [{ t: 'rect', size: [13, 40], round: 6, pos: [0, -9], fill: 'FG', name: 'Than' }, { t: 'ellipse', size: [14, 14], pos: [0, 25], fill: 'FG', name: 'Cham' }],
  chat: [{ t: 'rect', size: [60, 44], round: 13, pos: [0, -5], fill: 'FG', name: 'Bong' }, { t: 'path', v: [[-16, 12], [-24, 30], [0, 14]], fill: 'FG', name: 'Duoi' }],
  receipt: [
    { t: 'path', v: [[-22, -30], [22, -30], [22, 30], [11, 22], [0, 30], [-11, 22], [-22, 30]], fill: 'FG', name: 'Hoa don' },
    { t: 'rect', size: [26, 6], round: 3, pos: [0, -15], fill: 'BG', name: 'Dong 1' },
    { t: 'rect', size: [26, 6], round: 3, pos: [0, -2], fill: 'BG', name: 'Dong 2' },
    { t: 'rect', size: [14, 6], round: 3, pos: [-6, 11], fill: 'BG', name: 'Dong 3' }],
  image: [
    { t: 'rect', size: [62, 48], round: 9, pos: [0, 0], fill: 'FG', name: 'Khung anh' },
    { t: 'path', v: [[-24, 17], [-7, -4], [5, 9], [13, 1], [24, 17]], fill: 'BG', name: 'Nui' },
    { t: 'ellipse', size: [11, 11], pos: [14, -11], fill: 'BG', name: 'Mat troi' }],
  bell: [
    { t: 'path', v: [[0, -28], [19, -9], [21, 13], [30, 22], [-30, 22], [-21, 13], [-19, -9]],
      i: [[-11, 0], [-3, -9], [0, -7], [0, 0], [0, 0], [-1, 4], [0, 9]], o: [[11, 0], [1, 7], [1, 4], [0, 0], [0, 0], [0, -7], [3, -9]], fill: 'FG', name: 'Chuong' },
    { t: 'ellipse', size: [14, 14], pos: [0, 28], fill: 'FG', name: 'Qua lac' }],
  person: [
    { t: 'ellipse', size: [28, 28], pos: [0, -14], fill: 'FG', name: 'Dau' },
    { t: 'path', v: [[-25, 26], [0, 4], [25, 26]], i: [[0, 0], [-15, 0], [0, -13]], o: [[0, -13], [15, 0], [0, 0]], fill: 'FG', name: 'Vai' }],
  box: [
    { t: 'rect', size: [50, 44], round: 6, pos: [0, 5], fill: 'FG', name: 'Thung' },
    { t: 'rect', size: [10, 44], pos: [0, 5], fill: 'BG', name: 'Bang dinh' },
    { t: 'rect', size: [58, 12], round: 4, pos: [0, -20], fill: 'FG', name: 'Nap' }],
  phone: [{ t: 'rect', size: [34, 58], round: 9, pos: [0, 0], stroke: 'FG', sw: 7, name: 'Vo' },
    { t: 'rect', size: [12, 5], round: 2, pos: [0, -19], fill: 'FG', name: 'Loa' }, { t: 'ellipse', size: [7, 7], pos: [0, 19], fill: 'FG', name: 'Nut' }],
  pin: [
    { t: 'path', v: [[0, 30], [-20, -4], [0, -26], [20, -4]], i: [[0, 0], [6, 14], [-11, 0], [0, -12]], o: [[0, 0], [0, -12], [11, 0], [-6, 14]], fill: 'FG', name: 'Ghim' },
    { t: 'ellipse', size: [14, 14], pos: [0, -5], fill: 'BG', name: 'Lo' }],
  arrow: [
    { t: 'path', v: [[-24, 0], [18, 0]], closed: false, stroke: 'FG', sw: 11, name: 'Than mui ten' },
    { t: 'path', v: [[3, -15], [20, 0], [3, 15]], closed: false, stroke: 'FG', sw: 11, name: 'Mui' }],
  cart: [
    { t: 'path', v: [[-30, -22], [-18, -22], [-10, 14], [22, 14], [28, -10], [-14, -10]], closed: false, stroke: 'FG', sw: 9, name: 'Gio' },
    { t: 'ellipse', size: [13, 13], pos: [-6, 27], fill: 'FG', name: 'Banh 1' },
    { t: 'ellipse', size: [13, 13], pos: [18, 27], fill: 'FG', name: 'Banh 2' }],
  plug: [
    { t: 'rect', size: [40, 30], round: 8, pos: [0, 4], fill: 'FG', name: 'Dau cam' },
    { t: 'rect', size: [8, 20], round: 3, pos: [-10, -18], fill: 'FG', name: 'Chan 1' },
    { t: 'rect', size: [8, 20], round: 3, pos: [10, -18], fill: 'FG', name: 'Chan 2' },
    { t: 'rect', size: [10, 18], pos: [0, 26], fill: 'FG', name: 'Day' }]
};

// Icon trong nền tròn. o: {bg:'blue', fg:'white', size:64 (đường kính nền), glyph: tỉ lệ glyph trên nền (0.62)}
OPA.icon = function (comp, name, type, center, o) {
  var O = OPA, src = O.ICON[type], items = [];
  var size = o.size || 64, k = (o.glyph || 0.62) * size / 100;
  if (o.bg) items.push({ t: 'ellipse', size: [size, size], pos: [0, 0], fill: o.bg, name: 'Nen tron' });
  for (var i = 0; i < src.length; i++) {
    var s = src[i], it = {}, key;
    for (key in s) if (s.hasOwnProperty(key)) it[key] = s[key];
    if (it.fill === 'FG') it.fill = o.fg; else if (it.fill === 'BG') it.fill = o.bg || o.hole || 'white';
    if (it.stroke === 'FG') it.stroke = o.fg;
    // Phóng toạ độ glyph theo k (giữ nguyên tiếp tuyến tương đối theo cùng tỉ lệ).
    if (it.v) { it.v = scalePts(it.v, k); if (it.i) it.i = scalePts(it.i, k); if (it.o) it.o = scalePts(it.o, k); }
    if (it.size) it.size = [it.size[0] * k, it.size[1] * k];
    if (it.pos) it.pos = [it.pos[0] * k, it.pos[1] * k];
    if (it.sw) it.sw = it.sw * k;
    it.name = (it.name || it.t) + ' ' + i;
    items.push(it);
  }
  var L = O.shape(comp, name, items);
  O.setT(L, { anchor: [0, 0], pos: center });
  return L;
  function scalePts(a, f) { var r = []; for (var j = 0; j < a.length; j++) r.push([a[j][0] * f, a[j][1] * f]); return r; }
};

// Mascot Bò OPA: comp 2000×2000 đúng hệ toạ độ SVG gốc; 4 phần là shape layer, sừng có khớp ở chân sừng.
// Màu mặc định xanh #0068FF; cần bản trắng thì thêm effect Fill (trắng) lên layer comp này ở cảnh.
OPA.buildMascot = function (ctx) {
  var O = OPA;
  var C = O.comp('ART_MASCOT_BO_OPA', 2000, 2000, 1080, ctx.F.art, 'white');
  C.comment = 'Bo OPA dung path tu mascot/opa-mascot-parts.svg (khong sua tay). Khong them mat, mieng; khong doi ti le.';
  var P = MASCOT.parts;
  var mk = function (id, label) { var d = P[id]; return [{ t: 'path', v: d.v, i: d.i, o: d.o, closed: d.closed, fill: 'blue', name: label }]; };
  var hl = O.shape(C, 'SUNG trai (a-horn-left)', mk('a-horn-left', 'Sung trai'));
  O.setT(hl, { anchor: MASCOT.pivots['a-horn-left'], pos: MASCOT.pivots['a-horn-left'] });
  var hr = O.shape(C, 'SUNG phai (b-horn-right)', mk('b-horn-right', 'Sung phai'));
  O.setT(hr, { anchor: MASCOT.pivots['b-horn-right'], pos: MASCOT.pivots['b-horn-right'] });
  O.shape(C, 'MOM chu U (c-muzzle)', mk('c-muzzle', 'Mom'));
  return C;
};

// Bò hiện ở cảnh cuối, theo động tác "reveal" của V2: mõm chữ U bật lên từ dưới (lò xo damping 12, nảy một nhịp),
// hai sừng mọc từ chân sừng (scale từ 0 tại tâm xoay, xoay về 0°), rồi thở 1,00 → 1,03 chu kỳ 2,4 s, sừng nghiêng ±2° đối xứng.
// Comp riêng để không ảnh hưởng mascot tĩnh dùng ở cảnh 2–3. Khung cục bộ 0 = khung đầu của cảnh 5.
OPA.buildMascotReveal = function (ctx, at) {
  var O = OPA, P = MASCOT.parts, base = [1000, 1632.8];
  var C = O.comp('ART_MASCOT_BO_OPA_HIEN', 2000, 2000, 180, ctx.F.art, 'blue');
  C.comment = 'Bo OPA hien (canh 5): mom bat len f' + at + ', sung moc f' + (at + 10) + '/f' + (at + 13) + ', tho tu f' + (at + 34) + '.';
  var breath = O.nul(C, 'THO (scale deu moi truc)');
  O.setT(breath, { anchor: base, pos: base });
  var mk = function (id, label) { var d = P[id]; return [{ t: 'path', v: d.v, i: d.i, o: d.o, closed: d.closed, fill: 'blue', name: label }]; };
  var hl = O.shape(C, 'SUNG trai (a-horn-left)', mk('a-horn-left', 'Sung trai'));
  O.setT(hl, { anchor: MASCOT.pivots['a-horn-left'], pos: MASCOT.pivots['a-horn-left'] });
  var hr = O.shape(C, 'SUNG phai (b-horn-right)', mk('b-horn-right', 'Sung phai'));
  O.setT(hr, { anchor: MASCOT.pivots['b-horn-right'], pos: MASCOT.pivots['b-horn-right'] });
  var mz = O.shape(C, 'MOM chu U (c-muzzle)', mk('c-muzzle', 'Mom'));
  O.setT(mz, { anchor: base, pos: base });
  var parts = [hl, hr, mz];
  for (var k = 0; k < parts.length; k++) parts[k].parent = breath;
  // Mõm bật lên 300 đơn vị theo nghiệm lò xo thật.
  var sp = O.springKeys(at, 300, 0), keys = [];
  for (var i = 0; i < sp.length; i++) keys.push([sp[i][0], [base[0], base[1] + sp[i][1]], sp[i][2]]);
  O.anim(O.tr(mz, 'ADBE Position'), keys);
  // Sừng mọc từ gốc, lệch nhau 3 khung, xoay về 0°.
  var horns = [[hl, at + 10, -16], [hr, at + 13, 16]];
  for (var h = 0; h < horns.length; h++) {
    O.popScale(O.tr(horns[h][0], 'ADBE Scale'), horns[h][1]);
    O.anim(O.tr(horns[h][0], 'ADBE Rotate Z'), [[horns[h][1], horns[h][2]], [horns[h][1] + 14, 0, 'BRAND']]);
    O.tr(horns[h][0], 'ADBE Rotate Z').expression = 'var t = time - ' + ((at + 34) / O.FPS) + '; value + (t > 0 ? ' + (h ? '-' : '') + '2 * Math.sin(t * 2 * Math.PI / 2.4) : 0)';
  }
  O.tr(breath, 'ADBE Scale').expression = 'var t = Math.max(0, time - ' + ((at + 34) / O.FPS) + '); var s = 100 + 1.5 * (1 - Math.cos(t * 2 * Math.PI / 2.4)); [s, s]';
  return C;
};
