// Cảnh 3 · 00:13,5–00:22 (khung 405–660, cục bộ 0–255) · Giải pháp & tính năng. Nền trắng (ban ngày).
// f0: Bò xanh đứng đúng chỗ cảnh 2 để lại → bảng OPA Agent mở bằng mask (R10) → Bò bay vào đầu bảng, hoá trắng trên nền xanh.
// Chip "Pancake POS" cắm vào (1 kết nối), rồi 5 hàng minh hoạ bật đúng nhịp 5 tính năng bên phải.
// Cuối cảnh: cột chữ thoát R6 (100 → 86 → 0), các hàng thu lại, khung bảng hoá xanh rồi dời đều về đúng khung cảnh 4 (nối liền).
OPA.S3 = { DUR: 255, LAND: 36, CAM_S: 1.03, CAM_D: [16, -16], PANEL4: { pos: [492, 540], size: [792, 864], round: 56 } };

OPA.buildS3 = function (ctx) {
  var O = OPA, F = ctx.F, K = O.S3, DUR = K.DUR, B2 = O.S2;
  var S = O.comp('S3_GIAI_PHAP', 1920, 1080, DUR, F.scenes, 'white');
  S.comment = 'Canh 3 (13,5-22 s). Bang mo f6-34; Bo vao dau bang f0-36; chip noi f40; tinh nang f44/72/100/128/156; chot f180; R6 thoat f232-253; khung bang hoa xanh f232-242, doi ve khung canh 4 f242-254.';
  O.shape(S, 'BG nen trang', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'white', name: 'Nen' }]);
  var deco = O.shape(S, 'DECO khoi nen', [
    { t: 'ellipse', size: [520, 520], pos: [1840, 1010], fill: 'blueLight', name: 'Tron lon' },
    { t: 'rect', size: [180, 180], round: 46, pos: [890, 60], rot: 18, fill: 'blueLight', name: 'Vuong bo' }
  ]);
  O.anim(O.tr(deco, 'ADBE Position'), [[0, [0, 0]], [DUR, [-30, -16], 'LINEAR']]);
  O.anim(O.tr(deco, 'ADBE Opacity'), [[4, 0], [24, 100, 'BRAND'], [232, 100, 'HOLD'], [252, 0, 'EXIT']]);
  var cam = O.nul(S, 'CAM');

  // ----- Bảng OPA Agent, mở bằng khối matte lớn dần từ góc trên-trái (R10: Size + ease 15/100) -----
  var U = O.buildAgentPanel(ctx);
  var uL = O.place(S, U, { name: 'UI OPA Agent' });
  var um = O.shape(S, 'MASK mo bang', [{ t: 'rect', size: [800, 920], round: 46, pos: [78, 80], anchor: [-400, -460], fill: 'white', name: 'Khoi mo' }]);
  O.anim(O.item(um, 'Khoi mo', 'size'), [[6, [0, 0]], [34, [800, 920], 'MASK']]);
  O.anim(O.item(um, 'Khoi mo', 'anchor'), [[6, [0, 0]], [34, [-400, -460], 'MASK']]);
  um.moveBefore(uL);
  uL.setTrackMatte(um, TrackMatteType.ALPHA);
  um.enabled = false;
  uL.parent = cam; um.parent = cam;
  O.anim(O.tr(uL, 'ADBE Opacity'), [[232, 100], [242, 0, 'EXIT']]);  // tắt hẳn dưới khung xanh trước khi khung dời

  // ----- Bò từ cảnh 2: đứng yên đúng chỗ, bay vào đầu bảng; giữ xanh tới khung đáp (đầu bảng còn trắng), -----
  // ----- khung sau nhường Bò trắng của bảng khi vòng lan xanh đã đủ che (đổi trắng ngay khung đáp thì Bò mất 1 khung) -----
  var bo = O.place(S, ctx.art.mascot, { name: 'BO OPA bay vao bang' });
  O.setT(bo, { anchor: [1000, 1000], pos: B2.BO_POS, scale: B2.BO_SCALE });
  O.fxColor(bo.property('ADBE Effect Parade').addProperty('ADBE Fill'), 'blue');
  bo.parent = cam;  // máy quay ở khung 0 trùng toạ độ khung hình nên vị trí Bò khớp cảnh 2
  // Cất cánh từ tốc độ 0 (BRAND vọt ×4 ngay khung đầu thành giật sau lúc Bò đứng yên), đáp chậm như BRAND.
  O.EASE.LIFT = { o: [0, 15], i: [0, 80] };
  O.anim(O.tr(bo, 'ADBE Position'), [[0, B2.BO_POS], [K.LAND, [172, 162], 'LIFT']]);
  O.anim(O.tr(bo, 'ADBE Scale'), [[0, [B2.BO_SCALE, B2.BO_SCALE]], [K.LAND, [6.4, 6.4], 'LIFT']]);
  O.anim(O.tr(bo, 'ADBE Opacity'), [[K.LAND, 100], [K.LAND + 1, 0, 'HOLD']]);
  bo.motionBlur = true;

  // ----- Cột chữ (giữ nhịp đã duyệt) -----
  var X = 950, T = O.comp('TITLE_S3', 1920, 1080, DUR, F.titles, 'white');
  var cAcc = O.comp('TXT_S3_NHAN', 1920, 1080, DUR, F.edit, 'white');
  var acc = O.text(cAcc, 'Chỉ 1 kết nối —', { font: O.FONT.accent, size: 80, color: 'blue' });
  var rA = O.placeTop(acc, X + Math.round(0.12 * 80), 144);
  O.textAnim(acc, 'R2', { em: 80, inAt: 0, inDur: 30 });
  var cHead = O.comp('TXT_S3_HEADLINE', 1920, 1080, DUR, F.edit, 'white');
  var head = O.text(cHead, 'OPA tự động hóa toàn bộ\rQuy trình bán hàng\rTrên Pancake:', { font: O.FONT.head, size: 56, leading: 74, color: 'black' });
  O.fitWidth(head, 1824 - X, 44);
  var rH = O.placeTop(head, X, rA.top + rA.height + 34);
  O.textAnim(head, 'R1', { em: 56, inAt: 0, inDur: 30 });
  var feats = [
    ['Tự trả lời đúng tồn kho POS', 'chat'],
    ['Tự chốt đơn vào Pancake POS', 'receipt'],
    ['Xác minh chuyển khoản bằng ảnh', 'image'],
    ['Nhắc khách bỏ giỏ trong 24h', 'bell'],
    ['Nhân viên tiếp quản bất cứ lúc nào', 'person']
  ];
  var fIn = [44, 72, 100, 128, 156], y0 = rH.top + rH.height + 52, step = 72, fr = [];
  for (var i = 0; i < feats.length; i++) {
    var cy = y0 + i * step;
    var c = O.comp('TXT_S3_TINH_NANG_' + (i + 1), 1920, 1080, DUR, F.edit, 'white');
    var L = O.text(c, feats[i][0], { font: O.FONT.body, size: 40, color: 'black' });
    O.fitWidth(L, 1824 - (X + 66), 32);
    var r0 = O.rect(L, 0);
    O.tr(L, 'ADBE Position').setValue([X + 66 - r0.left, cy + 14]);
    fr.push(O.wrect(L, 0));
    O.textAnim(L, 'R5', { em: 40, inAt: 0, inDur: 30 });
    O.place(T, c, { start: fIn[i] });
    var ic = O.icon(T, 'ICON tinh nang ' + (i + 1), feats[i][1], [X + 24, cy], { size: 52, bg: 'blue', fg: 'white', glyph: 0.66 });
    O.popScale(O.tr(ic, 'ADBE Scale'), fIn[i] + 2);
  }
  var cEnd = O.comp('TXT_S3_CHOT', 1920, 1080, DUR, F.edit, 'white');
  var endL = O.text(cEnd, 'Và nhiều hơn thế nữa!', { font: O.FONT.head, size: 44, color: 'blue' });
  var rE = O.placeTop(endL, X, y0 + 5 * step + 8);
  O.textAnim(endL, 'R3', { em: 44, inAt: 0, inDur: 30 });
  O.accentBlock(T, cAcc, { start: 8, em: 80, measureT: 1.5, markKey: 'blue', inkKey: 'white', sweepAt: 30 });
  O.place(T, cHead, { start: 20 });
  O.place(T, cEnd, { start: 180 });
  var tL = O.place(S, T, { name: 'TITLE_S3' });
  tL.parent = cam;
  // R6 của mẫu (Scene 5 / Title 6): thu cả khối ở cấp Scene, tâm thu là tâm cột chữ.
  var cx = X + (1824 - X) / 2, cyT = (rA.top + rE.top + rE.height) / 2;
  O.setT(tL, { anchor: [cx, cyT], pos: [cx, cyT] });
  O.EASE.R6A = { o: [0, 0.01], i: [0, 100] };
  O.EASE.R6B = { o: [0, 100], i: [0, 15.1333287005183] };
  O.anim(O.tr(tL, 'ADBE Scale'), [[232, [100, 100]], [244, [86, 86], 'R6A'], [253, [0, 0], 'R6B']]);
  tL.motionBlur = true;

  // ----- Nối sang cảnh 4: khung bảng hoá xanh ngay tại chỗ, giao diện tắt hẳn bên dưới, rồi khung dời đều về đúng khung cảnh 4 -----
  // Toạ độ bảng ('Nen bang' 764×884 tại [478, 540], bo 46) qua máy quay (tâm 960, 540; trôi tuyến tính) ở khung 242, dư 4 px
  // để phủ cả phần máy quay trôi trong 232–242. Chỉ dời khi giao diện đã tắt (242): dời sớm thì mép bảng, sừng Bò ló ra.
  // Dời đều tới khung cuối để hai khung cuối vẫn còn chuyển động.
  var P4 = K.PANEL4, k0 = 242 / DUR, s0 = 1 + (K.CAM_S - 1) * k0;
  var toWorld = function (p) { return [960 + K.CAM_D[0] * k0 + (p[0] - 960) * s0, 540 + K.CAM_D[1] * k0 + (p[1] - 540) * s0]; };
  var p4 = O.shape(S, 'KHUNG xanh (sang canh 4)', [{ t: 'rect', size: P4.size, round: P4.round, pos: [0, 0], fill: 'blue', name: 'Khung' }]);
  O.setT(p4, { opacity: 0 });
  O.anim(O.tr(p4, 'ADBE Opacity'), [[232, 0], [242, 100, 'BRAND']]);
  O.anim(O.tr(p4, 'ADBE Position'), [[242, toWorld([478, 540])], [254, P4.pos, 'LINEAR']]);
  O.anim(O.item(p4, 'Khung', 'size'), [[242, [764 * s0 + 4, 884 * s0 + 4]], [254, P4.size, 'LINEAR']]);
  O.anim(O.item(p4, 'Khung', 'round'), [[242, 46 * s0 + 2], [254, P4.round, 'LINEAR']]);

  // Máy quay trôi đều từ khung 0 (Bò, bảng, cột chữ cùng gắn vào nên toạ độ đầu bảng vẫn khớp).
  var FOC = [960, 540];
  O.setT(cam, { anchor: FOC, pos: FOC });
  O.anim(O.tr(cam, 'ADBE Scale'), [[0, [100, 100]], [DUR, [100 * K.CAM_S, 100 * K.CAM_S], 'LINEAR']]);
  O.anim(O.tr(cam, 'ADBE Position'), [[0, FOC], [DUR, [FOC[0] + K.CAM_D[0], FOC[1] + K.CAM_D[1]], 'LINEAR']]);
  S.motionBlur = true; uL.motionBlur = true;
  O.report.measures.push({ scene: 'S3', accent: rA, headline: rH, features: fr, closing: rE });
  return S;
};

// ----- Bảng OPA Agent: mỗi hàng là một nhóm (null) để vào/ra cùng nhau; opacity đi theo null -----
OPA.buildAgentPanel = function (ctx) {
  var O = OPA, F = ctx.F, DUR = O.S3.DUR;
  var U = O.comp('UI_OPA_AGENT', 1920, 1080, DUR, F.art, 'white');
  U.comment = 'Bang dieu khien OPA Agent (minh hoa, du lieu gia). Moi hang minh hoa mot tinh nang ben phai, bat dung nhip.';
  // Đầu bảng trắng khi chờ; Bò đáp xuống thì màu xanh lan ra từ chỗ Bò (OPA kích hoạt bảng).
  O.shape(U, 'KHUNG bang', [
    { t: 'rect', size: [764, 884], round: 46, pos: [478, 540], fill: 'blueLight', name: 'Nen bang' },
    { t: 'rect', size: [764, 128], round: 46, pos: [478, 162], fill: 'white', name: 'Dau bang (cho)' },
    { t: 'rect', size: [764, 60], pos: [478, 196], fill: 'white', name: 'Dau bang vuong (cho)' }
  ]);
  var headBlue = O.shape(U, 'DAU BANG xanh (lan tu Bo)', [
    { t: 'rect', size: [764, 128], round: 46, pos: [478, 162], fill: 'blue', name: 'Dau bang' },
    { t: 'rect', size: [764, 60], pos: [478, 196], fill: 'blue', name: 'Dau bang vuong' }
  ]);
  var flood = O.shape(U, 'MASK lan mau dau bang', [{ t: 'ellipse', size: [1700, 1700], pos: [0, 0], fill: 'white', name: 'Vong lan' }], { pos: [172, 162] });
  O.anim(O.tr(flood, 'ADBE Scale'), [[O.S3.LAND, [0, 0]], [O.S3.LAND + 14, [100, 100], 'MASK']]);
  flood.moveBefore(headBlue);
  headBlue.setTrackMatte(flood, TrackMatteType.ALPHA);
  flood.enabled = false;
  var mascot = O.place(U, ctx.art.mascot, { name: 'MASCOT trang (dau bang)' });
  O.setT(mascot, { anchor: [1000, 1000], pos: [172, 162], scale: 6.4 });
  O.fxColor(mascot.property('ADBE Effect Parade').addProperty('ADBE Fill'), 'white');
  O.anim(O.tr(mascot, 'ADBE Opacity'), [[0, 0], [O.S3.LAND + 1, 100, 'HOLD']]);  // vòng lan đã ~200 px, che trọn Bò trắng
  O.tr(mascot, 'ADBE Scale').expression = 'var t = Math.max(0, time - ' + (O.S3.LAND / O.FPS) + '); var s = 6.4 * (1 + 0.03 * (1 - Math.cos(t * 2 * Math.PI / 2.4)) / 2); [s, s]';
  var nm = O.text(U, 'OPA Agent', { font: O.FONT.head, size: 44, color: 'white', name: 'TEN san pham' });
  O.placeTop(nm, 236, 136);
  nm.setTrackMatte(flood, TrackMatteType.ALPHA);  // chữ trắng hiện cùng lúc màu xanh lan tới

  // Nhóm hàng: null + các layer con; opacity của con theo null.
  // Tạo null ở tư thế nghỉ; keyframe vào cảnh đặt SAU khi gắn con (parent bù theo transform hiện tại của null).
  var row = function (name, pos) {
    var n = O.nul(U, name);
    O.setT(n, { anchor: [0, 0], pos: pos });
    return n;
  };
  var enter = function (n, pos, at, from) {
    O.anim(O.tr(n, 'ADBE Opacity'), [[at, 0], [at + 8, 100, 'BRAND']]);
    O.anim(O.tr(n, 'ADBE Position'), [[at, [pos[0] + from[0], pos[1] + from[1]]], [at + 10, pos, 'BRAND']]);
    O.anim(O.tr(n, 'ADBE Scale'), [[at, [94, 94]], [at + 10, [100, 100], 'BRAND']]);
  };
  var adopt = function (n, layers) {
    for (var k = 0; k < layers.length; k++) { layers[k].parent = n; O.followOpacity(layers[k], n); }
  };
  var exits = [];

  // Chip "Pancake POS" cắm vào sau khi Bò vào chỗ: 1 kết nối.
  var chipN = row('HANG chip ket noi', [712, 162]);
  var chip = [];
  chip.push(O.shape(U, 'CHIP nen', [{ t: 'rect', size: [250, 56], round: 28, pos: [0, 0], fill: 'white', name: 'Chip' }], { pos: [712, 162] }));
  var cht = O.text(U, 'Pancake POS', { font: O.FONT.semi, size: 28, color: 'blue', name: 'CHIP Pancake POS' });
  O.placeTop(cht, 640, 148);
  chip.push(cht);
  var plug = O.icon(U, 'ICON cam ket noi', 'plug', [612, 162], { size: 40, bg: 'blue', fg: 'white', glyph: 0.6 });
  O.popScale(O.tr(plug, 'ADBE Scale'), 48);
  chip.push(plug);
  var ring = O.shape(U, 'VONG ket noi (lap)', [{ t: 'rect', size: [250, 56], round: 28, pos: [0, 0], stroke: 'white', sw: 4, name: 'Vong' }], { pos: [712, 162] });
  O.tr(ring, 'ADBE Scale').expression = 'var t = time - 52 / 30; var p = t < 0 ? 0 : Math.min(1, (t % 1.5) / 0.6); var s = 100 + 26 * p; [s, s * 1.5 - 50]';
  adopt(chipN, chip);
  ring.parent = chipN;
  enter(chipN, [712, 162], 40, [60, 0]);
  // Vòng tỏa lặp mỗi 1,5 s; tắt trước khi các hàng thu lại.
  O.tr(ring, 'ADBE Opacity').expression = 'var t = time - 52 / 30; var p = t < 0 ? 1 : Math.min(1, (t % 1.5) / 0.6); (t < 0 || time > 7.4) ? 0 : 90 * (1 - p) * thisComp.layer("HANG chip ket noi").transform.opacity / 100';
  exits.push(chipN);

  // Hàng 1 — tự trả lời đúng tồn kho.
  var r1a = row('HANG 1a khach hoi', [134, 284]);
  var q = O.text(U, 'Còn size M không shop?', { font: O.FONT.body, size: 30, color: 'black', name: 'KHACH hoi' });
  var qr = O.rect(q, 0);
  O.tr(q, 'ADBE Position').setValue([160 - qr.left, 284 - qr.top - qr.height / 2]);
  var qb = O.shape(U, 'BONG khach', [{ t: 'rect', size: [qr.width + 52, 62], round: 24, pos: [134 + (qr.width + 52) / 2, 284], fill: 'white', name: 'Bong' }]);
  qb.moveAfter(q);
  adopt(r1a, [qb, q]);
  enter(r1a, [134, 284], 44, [-40, 0]);
  var r1b = row('HANG 1b OPA tra loi', [596, 384]);
  var rb = O.shape(U, 'BONG OPA tra loi', [
    { t: 'rect', size: [400, 96], round: 28, pos: [596, 384], fill: 'blue', name: 'Bong' },
    { t: 'rect', size: [230, 14], round: 7, pos: [540, 366], fill: 'white', name: 'Dong 1' },
    { t: 'rect', size: [170, 14], round: 7, pos: [510, 398], fill: 'white', name: 'Dong 2' }
  ]);
  var box = O.icon(U, 'ICON kho hang', 'box', [752, 384], { size: 64, bg: 'white', fg: 'blue' });
  O.popScale(O.tr(box, 'ADBE Scale'), 60);
  adopt(r1b, [rb, box]);
  enter(r1b, [596, 384], 54, [40, 0]);
  exits.push(r1a, r1b);

  // Hàng 2 — chốt đơn vào Pancake POS.
  var r2 = row('HANG 2 don vao POS', [478, 508]);
  var card = O.shape(U, 'THE don hang', [{ t: 'rect', size: [628, 96], round: 26, pos: [478, 508], fill: 'white', name: 'The' }]);
  var rc = O.icon(U, 'ICON hoa don', 'receipt', [214, 508], { size: 60, bg: 'blue', fg: 'white' });
  var od = O.text(U, 'Pancake POS', { font: O.FONT.semi, size: 30, color: 'black', name: 'DON vao POS' });
  O.placeTop(od, 262, 492);
  var ck2 = O.icon(U, 'TICH don', 'check', [744, 508], { size: 56, bg: 'blue', fg: 'white' });
  O.popScale(O.tr(ck2, 'ADBE Scale'), 84);
  adopt(r2, [card, rc, od, ck2]);
  enter(r2, [478, 508], 72, [0, 24]);
  exits.push(r2);

  // Hàng 3 — xác minh chuyển khoản bằng ảnh: vạch quét chạy dọc ảnh rồi bật tích.
  var r3 = row('HANG 3 anh chuyen khoan', [262, 650]);
  var img = O.shape(U, 'ANH chuyen khoan', [
    { t: 'rect', size: [240, 150], round: 22, pos: [262, 650], fill: 'white', name: 'The anh' },
    { t: 'rect', size: [196, 106], round: 12, pos: [262, 650], fill: 'blueLight', name: 'Anh' },
    { t: 'rect', size: [120, 12], round: 6, pos: [238, 628], fill: 'blue', name: 'So tien gia' },
    { t: 'rect', size: [80, 12], round: 6, pos: [218, 660], fill: 'blue', name: 'Ma gia' }
  ]);
  var scan = O.shape(U, 'VACH quet anh', [{ t: 'rect', size: [200, 4], pos: [0, 0], fill: 'blue', name: 'Vach' }], { pos: [262, 600] });
  O.anim(O.tr(scan, 'ADBE Position'), [[104, [262, 600]], [118, [262, 700], 'SOFT']]);
  var ck3 = O.icon(U, 'TICH anh', 'check', [372, 584], { size: 56, bg: 'blue', fg: 'white' });
  O.popScale(O.tr(ck3, 'ADBE Scale'), 116);
  adopt(r3, [img, scan, ck3]);
  enter(r3, [262, 650], 100, [0, 24]);
  exits.push(r3);

  // Hàng 4 — nhắc khách bỏ giỏ trong 24H: chuông rung.
  var r4 = row('HANG 4 nhac 24H', [612, 650]);
  var ch4 = O.shape(U, 'CHIP nhac', [{ t: 'rect', size: [300, 76], round: 38, pos: [612, 650], fill: 'white', name: 'Chip' }]);
  var bell = O.icon(U, 'ICON chuong', 'bell', [506, 650], { size: 56, bg: 'blue', fg: 'white' });
  O.anim(O.tr(bell, 'ADBE Rotate Z'), [[134, 0], [137, 14, 'BRAND'], [141, -11, 'SOFT'], [145, 8, 'SOFT'], [149, -5, 'SOFT'], [154, 0, 'SOFT']]);
  var h24 = O.text(U, '24H', { font: O.FONT.head, size: 34, color: 'blue', name: 'NHAN 24H' });
  O.placeTop(h24, 550, 634);
  var cart = O.icon(U, 'ICON gio hang', 'cart', [718, 650], { size: 56, bg: 'blueLight', fg: 'blue' });
  O.popScale(O.tr(cart, 'ADBE Scale'), 138);
  adopt(r4, [ch4, bell, h24, cart]);
  enter(r4, [612, 650], 128, [0, 24]);
  exits.push(r4);

  // Hàng 5 — nhân viên tiếp quản: nút gạt chạy từ phía Bò sang phía người.
  var r5 = row('HANG 5 nhan vien tiep quan', [478, 812]);
  var sw = O.shape(U, 'CONG TAC tiep quan', [
    { t: 'rect', size: [628, 110], round: 30, pos: [478, 812], fill: 'white', name: 'The' },
    { t: 'rect', size: [150, 64], round: 32, pos: [478, 812], fill: 'blue', name: 'Ray' },
    { t: 'path', v: [[294, 812], [370, 812]], closed: false, stroke: 'blueLight', sw: 8, name: 'Gach trai' },
    { t: 'path', v: [[586, 812], [662, 812]], closed: false, stroke: 'blueLight', sw: 8, name: 'Gach phai' }
  ]);
  var knob = O.shape(U, 'NUT gat', [{ t: 'ellipse', size: [52, 52], pos: [0, 0], fill: 'white', name: 'Nut' }], { pos: [436, 812] });
  O.anim(O.tr(knob, 'ADBE Position'), [[166, [436, 812]], [178, [520, 812], 'BRAND']]);
  var m2 = O.place(U, ctx.art.mascot, { name: 'MASCOT nho' });
  O.setT(m2, { anchor: [1000, 1000], pos: [236, 812], scale: 4.6 });
  var per = O.icon(U, 'ICON nhan vien', 'person', [720, 812], { size: 64, bg: 'blue', fg: 'white' });
  O.popScale(O.tr(per, 'ADBE Scale'), 176);
  adopt(r5, [sw, knob, m2, per]);
  enter(r5, [478, 812], 156, [0, 24]);
  exits.push(r5);

  // Ra cảnh: các hàng thu lại từ dưới lên, cách nhau 3 khung.
  for (var e = 0; e < exits.length; e++) {
    var n = exits[exits.length - 1 - e], at = 230 + e * 3;
    O.anim(O.tr(n, 'ADBE Opacity'), [[at, 100], [at + 10, 0, 'EXIT']]);
    O.anim(O.tr(n, 'ADBE Scale'), [[at, [100, 100]], [at + 10, [92, 92], 'EXIT']]);
  }
  return U;
};
