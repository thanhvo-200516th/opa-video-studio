// Cảnh 2 · 00:05–00:13,5 (khung 150–405, cục bộ 0–255) · Xoáy sâu nỗi đau. Nền đêm #003C99.
// Nhịp 1 (f24): hộp thư cuộn liên tục, tin mới dồn tới, chấm đỏ chưa đọc → "Hàng chục cuộc chat bỏ dở".
// Nhịp 2 (f96): câu hỏi lặp lại, câu trả lời y hệt nhau lần lượt bật ra → "Trả lời lặp đi lặp lại".
// Nhịp 3 (f168): phiếu POS mở bằng mask (R10), số điện thoại và địa chỉ bay từ tin nhắn vào ô → "Lên đơn POS thủ công".
// Cuối cảnh: rung quá tải, Bò OPA trắng lao vào, đĩa sáng mở từ sau lưng Bò sang ngày (nối cảnh 3).
OPA.S2 = { DUR: 255, SLOT: 106, YB: 908, BO_POS: [1180, 560], BO_SCALE: 26, BO_LAND: 248, IRIS_AT: 242 };

OPA.buildS2 = function (ctx) {
  var O = OPA, F = ctx.F, K = O.S2, DUR = K.DUR;
  var S = O.comp('S2_NOI_DAU', 1920, 1080, DUR, F.scenes, 'blueDark');
  S.comment = 'Canh 2 (5-13,5 s). Gach dau dong vao f24/f96/f168 (R5), rut f220. Bo lao vao f236-248, dia sang f242-254. Mo tu man trang f0-10 (noi canh 1).';

  O.shape(S, 'BG nen dem', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'blueDark', name: 'Nen' }]);
  var deco = O.shape(S, 'DECO khoi nen', [
    { t: 'ellipse', size: [440, 440], pos: [1830, 40], fill: 'blue', name: 'Tron lon' },
    { t: 'rect', size: [240, 240], round: 60, pos: [1880, 1010], rot: -12, fill: 'blue', name: 'Vuong bo' },
    { t: 'ellipse', size: [70, 70], pos: [1090, 64], fill: 'blue', name: 'Cham' }  // xa góc hộp thư, không giống huy hiệu
  ]);
  O.anim(O.tr(deco, 'ADBE Position'), [[0, [0, 0]], [DUR, [-46, 20], 'LINEAR']]);
  var cam = O.nul(S, 'CAM');

  var U = O.buildInbox(ctx);
  var P = O.buildPosForm(ctx);
  var uL = O.place(S, U, { name: 'UI hop thu' });
  var pL = O.place(S, P, { name: 'UI phieu POS' });
  // R10: phiếu mở bằng kích thước khối matte (ease 15/100 của mẫu), trồi nhẹ lên.
  var pm = O.shape(S, 'MASK mo phieu POS', [{ t: 'rect', size: [440, 340], round: 34, pos: [0, 0], fill: 'white', name: 'Khoi mo' }]);
  O.setT(pm, { pos: [734, 800] });
  O.anim(O.item(pm, 'Khoi mo', 'size'), [[168, [0, 0]], [196, [440, 340], 'MASK']]);
  pm.moveBefore(pL);
  pL.setTrackMatte(pm, TrackMatteType.ALPHA);
  pm.enabled = false;  // khối matte chỉ làm mặt nạ, không hiện
  // Viền xanh chạy theo mép khối mở (mép ngoài nét trùng mép khối): phiếu luôn có viền, không thành lỗ trắng trên hộp thư.
  var pv = O.shape(S, 'VIEN mo phieu POS', [{ t: 'rect', size: [434, 334], round: 31, pos: [0, 0], stroke: 'blue', sw: 6, name: 'Vien' }]);
  O.setT(pv, { pos: [734, 800] });
  O.anim(O.item(pv, 'Vien', 'size'), [[168, [0, 0]], [196, [434, 334], 'MASK']]);
  O.anim(O.tr(pv, 'ADBE Opacity'), [[167, 0], [168, 100, 'HOLD'], [196, 100, 'HOLD'], [202, 0, 'EXIT']]);
  pv.moveBefore(pL);
  O.anim(O.tr(pL, 'ADBE Position'), [[168, [960, 576]], [196, [960, 540], 'BRAND']]);
  var kids = [uL, pL, pm, pv];
  for (var k = 0; k < kids.length; k++) kids[k].parent = cam;
  // Quá tải: rung tăng dần từ 7,5 s (khung 225) tới khi Bò lao vào.
  uL.property('ADBE Transform Group').property('ADBE Position').expression = 'var a = linear(time, 7.5, 7.95, 0, 7); wiggle(15, a)';
  pL.property('ADBE Transform Group').property('ADBE Position').expression = 'var a = linear(time, 7.5, 7.95, 0, 8); wiggle(17, a)';

  // ----- Ba gạch đầu dòng -----
  var T = O.comp('TITLE_S2', 1920, 1080, DUR, F.titles, 'blueDark');
  T.comment = 'Ba muc song song, xu ly nhu nhau: icon "!" ALERT bat lo xo + chu R5 tu phai.';
  var bullets = ['Hàng chục cuộc chat bỏ dở', 'Trả lời lặp đi lặp lại', 'Lên đơn POS thủ công'];
  var ins = [24, 96, 168], rows = [384, 540, 696], X = 1094, rects = [];
  for (var b = 0; b < 3; b++) {
    var c = O.comp('TXT_S2_Y' + (b + 1), 1920, 1080, DUR, F.edit, 'blueDark');
    var L = O.text(c, bullets[b], { font: O.FONT.semi, size: 50, color: 'white' });
    O.fitWidth(L, 1824 - X, 40);
    var r0 = O.rect(L, 0);
    O.tr(L, 'ADBE Position').setValue([X - r0.left, rows[b] + 18]);
    rects.push(O.wrect(L, 0));
    O.textAnim(L, 'R5', { em: 50, inAt: 0, inDur: 30, outAt: 220 - ins[b], outDur: 26 });
    O.place(T, c, { start: ins[b] });
    var ic = O.icon(T, 'ICON canh bao ' + (b + 1), 'bang', [1036, rows[b]], { size: 62, bg: 'alert', fg: 'white' });
    O.popScale(O.tr(ic, 'ADBE Scale'), ins[b] + 2);
    O.anim(O.tr(ic, 'ADBE Opacity'), [[220, 100], [234, 0, 'EXIT']]);
  }
  var tL2 = O.place(S, T, { name: 'TITLE_S2' });
  tL2.parent = cam;

  // ----- Nối sang cảnh 3: đĩa sáng bật sau lưng Bò, Bò trắng → xanh đúng khung đó, rồi đĩa nở phủ kín khung -----
  // Charge kiểu V2: cúi đầu 8° khi lao, dừng có rung tắt dần. Đĩa đi cùng đường lao (cùng key) nên luôn che trọn Bò.
  var charge = [[236, [2300, K.BO_POS[1]]], [K.BO_LAND, K.BO_POS, 'BRAND']];
  var iris = O.shape(S, 'DIA SANG mo sang ngay', [{ t: 'ellipse', size: [440, 440], pos: [0, 0], fill: 'white', name: 'Dia' }]);
  O.setT(iris, { scale: 0 });
  O.anim(O.tr(iris, 'ADBE Position'), charge);
  // Bật 130 % trong 1 khung (Bò rộng nhất 107 % cỡ đĩa, đo 21/10: sừng không thò ra nền đêm), rồi nở đều,
  // 600 % vừa phủ góc xa nhất đúng khung cuối (không có hai khung trắng đứng yên liền nhau).
  O.anim(O.tr(iris, 'ADBE Scale'), [[K.IRIS_AT, [0, 0]], [K.IRIS_AT + 1, [130, 130], 'LINEAR'], [254, [600, 600], 'LINEAR']]);
  var bo = O.place(S, ctx.art.mascot, { name: 'BO OPA lao vao' });
  O.setT(bo, { anchor: [1000, 1000], pos: [2300, K.BO_POS[1]], scale: K.BO_SCALE });
  var fx = bo.property('ADBE Effect Parade').addProperty('ADBE Fill');
  O.fxColor(fx, 'white');
  O.fxColorSwitch(fx, 'white', 'blue', (K.IRIS_AT + 1) / O.FPS);  // đúng khung đĩa bật: không lúc nào trắng trên trắng
  O.anim(O.tr(bo, 'ADBE Position'), charge);
  O.anim(O.tr(bo, 'ADBE Rotate Z'), [[236, -8], [K.BO_LAND, -8, 'SOFT'], [K.BO_LAND + 3, 3, 'BRAND'], [DUR, 0, 'SOFT']]);
  bo.motionBlur = true;

  // ----- Máy quay: hạ cánh từ cú đẩy của cảnh 1 (tiếp tục chiều đẩy vào), rồi trôi chậm -----
  var FOC = [560, 420];
  O.setT(cam, { anchor: FOC, pos: FOC });
  // Sau khi hạ cánh: một đường trôi chậm và đều (tốc độ không đổi), không dừng giữa chừng.
  // Trôi nhẹ sang phải-lên để mép trái hộp thư luôn cách lề (rà chéo: trôi trái đẩy hộp thư sát mép).
  O.anim(O.tr(cam, 'ADBE Scale'), [[0, [80, 80]], [30, [100, 100], 'BRAND'], [DUR, [103, 103], 'LINEAR']]);
  O.anim(O.tr(cam, 'ADBE Position'), [[0, [FOC[0] - 40, FOC[1] - 30]], [30, FOC, 'BRAND'], [DUR, [FOC[0] + 10, FOC[1] - 24], 'LINEAR']]);
  // Mở từ màn trắng: tin nhắn trắng của cảnh 1 phủ kín khung cuối, cảnh 2 tan dần từ trắng nên điểm cắt không lộ.
  // Khung đầu 90 % (không 100 %) để không trùng hệt khung trắng cuối cảnh 1.
  var wipe = O.shape(S, 'MAN TRANG (noi tu canh 1)', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'white', name: 'Trang' }]);
  O.anim(O.tr(wipe, 'ADBE Opacity'), [[0, 90], [10, 0, 'LINEAR']]);
  S.motionBlur = true; uL.motionBlur = true; pL.motionBlur = true;
  O.report.measures.push({ scene: 'S2', bullets: rects });
  return S;
};

// ----- Hộp thư: khung cố định + danh sách tin chạy (comp dòng dùng lại, mask cắt vùng danh sách) -----
OPA.buildInbox = function (ctx) {
  var O = OPA, F = ctx.F, K = O.S2, DUR = K.DUR;
  var U = O.comp('UI_HOP_THU_PANCAKE', 1920, 1080, DUR, F.art, 'blueDark');
  U.comment = 'Hop thu minh hoa (khong dung giao dien that cua Pancake). Sua cau hoi trong comp DONG_TIN_*.';
  O.shape(U, 'KHUNG hop thu', [
    { t: 'rect', size: [776, 856], round: 40, pos: [484, 540], fill: 'white', name: 'The' },
    { t: 'rect', size: [776, 4], pos: [484, 214], fill: 'blueLight', name: 'Ke ngang' },
    { t: 'rect', size: [220, 18], round: 9, pos: [330, 150], fill: 'blueLight', name: 'Tieu de 1' },
    { t: 'rect', size: [140, 14], round: 7, pos: [290, 178], fill: 'blueLight', name: 'Tieu de 2' }
  ]);
  O.icon(U, 'ICON hop thu', 'chat', [164, 163], { size: 64, bg: 'blue', fg: 'white' });
  var pill = O.shape(U, 'NHAN DEM chua doc', [{ t: 'rect', size: [108, 52], round: 26, pos: [0, 0], fill: 'alert', name: 'Nhan' }]);
  O.setT(pill, { pos: [800, 163] });
  var cnt = O.text(U, '99+', { font: O.FONT.bold, size: 30, color: 'white', just: 'C', name: 'DEM chua doc' });
  var rc = O.rect(cnt, 0);
  O.tr(cnt, 'ADBE Position').setValue([800 - rc.left - rc.width / 2, 163 - rc.top - rc.height / 2]);
  cnt.parent = pill;

  // Comp dòng: 3 câu hỏi nguyên văn kịch bản + 1 câu trả lời giống hệt nhau (sao chép).
  var qs = ['Còn size M không shop?', 'Giá bao nhiêu?', 'Check bill giúp em'];
  var qComp = [];
  for (var i = 0; i < qs.length; i++) qComp.push(O.rowQuestion(ctx, 'DONG_TIN_' + (i + 1), qs[i]));
  var rComp = O.rowReply(ctx);

  var Lc = O.comp('UI_DANH_SACH_TIN', 1920, 1080, DUR, F.art, 'white');
  Lc.comment = 'Danh sach tin chay: moi tin moi day danh sach len 1 o (106 px).';
  var list = O.nul(Lc, 'DANH SACH (cuon)');
  // [loại, câu, khung đến]; -1 = có sẵn khi vào cảnh.
  var feed = [['q', 0, -1], ['q', 1, -1], ['q', 2, -1], ['q', 0, -1], ['q', 1, -1], ['q', 2, -1], ['q', 0, -1],
    ['q', 1, 20], ['q', 2, 28], ['q', 0, 38], ['q', 1, 50], ['q', 2, 62], ['q', 0, 74], ['q', 1, 86],
    ['r', 0, 100], ['q', 1, 112], ['r', 0, 122], ['q', 2, 134], ['r', 0, 144], ['q', 0, 156], ['r', 0, 166],
    ['q', 1, 184], ['q', 2, 204], ['q', 0, 222]];
  var scroll = [], initial = 0, lastQ = null, pings = [];
  for (var n = 0; n < feed.length; n++) {
    var it = feed[n], at = it[2], y = n * K.SLOT;
    var L = O.place(Lc, it[0] === 'q' ? qComp[it[1]] : rComp, { name: (it[0] === 'q' ? 'Tin ' : 'Tra loi ') + (n + 1) });
    O.setT(L, { anchor: [0, 50], pos: [110, y] });
    L.parent = list;
    if (at < 0) { initial = n; } else {
      var dx = it[0] === 'q' ? -40 : 40;
      O.anim(O.tr(L, 'ADBE Position'), [[at, [110 + dx, y]], [at + 9, [110, y], 'BRAND']]);
      O.anim(O.tr(L, 'ADBE Opacity'), [[at, 0], [at + 7, 100, 'BRAND']]);
      O.anim(O.tr(L, 'ADBE Scale'), [[at, [96, 96]], [at + 9, [100, 100], 'BRAND']]);
      scroll.push([at, K.YB - n * K.SLOT]);
      if (it[0] === 'q') pings.push(at);
    }
    if (it[0] === 'q') {
      var dot = O.shape(Lc, 'CHAM chua doc ' + (n + 1), [{ t: 'ellipse', size: [20, 20], pos: [0, 0], fill: 'alert', name: 'Cham' }]);
      O.setT(dot, { pos: [836, y] });
      dot.parent = list;
      if (at >= 0) O.popScale(O.tr(dot, 'ADBE Scale'), at + 3);
      lastQ = dot;
    } else if (lastQ) {
      // Tin vừa được trả lời: chấm đỏ tắt.
      O.anim(O.tr(lastQ, 'ADBE Opacity'), [[at + 4, 100], [at + 10, 0, 'EXIT']]);
      lastQ = null;
    }
  }
  var keys = [[0, [0, K.YB - initial * K.SLOT]]];
  for (var s = 0; s < scroll.length; s++) {
    var prev = keys[keys.length - 1][1];
    if (scroll[s][0] > keys[keys.length - 1][0]) keys.push([scroll[s][0], prev, 'SOFT']);
    keys.push([scroll[s][0] + 9, [0, scroll[s][1]], 'BRAND']);
  }
  O.anim(O.tr(list, 'ADBE Position'), keys);
  var lL = O.place(U, Lc, { name: 'UI danh sach tin (cat theo khung)' });
  O.rectMask(lL, [100, 224, 868, 966]);
  // "99+" nảy theo từng tin mới.
  var pulse = [[0, [100, 100]]];
  for (var p = 0; p < pings.length; p++) {
    if (pings[p] > pulse[pulse.length - 1][0]) pulse.push([pings[p], [100, 100], 'SOFT']);
    pulse.push([pings[p] + 3, [114, 114], 'BRAND'], [pings[p] + 8, [100, 100], 'BRAND']);
  }
  O.anim(O.tr(pill, 'ADBE Scale'), pulse);
  O.S2.pings = pings;
  return U;
};

// Dòng câu hỏi khách: avatar + bong bóng tự giãn theo chữ (expression đo sourceRect).
OPA.rowQuestion = function (ctx, name, text) {
  var O = OPA, C = O.comp(name, 760, 100, O.S2.DUR, ctx.F.edit, 'white');
  C.comment = 'Sua cau hoi o layer TEXT; bong bong tu gian theo chu.';
  O.icon(C, 'AVATAR', 'person', [40, 50], { size: 64, bg: 'blueLight', fg: 'blue' });
  var t = O.text(C, text, { font: O.FONT.body, size: 32, color: 'black', name: 'TEXT' });
  var r = O.rect(t, 0);
  O.tr(t, 'ADBE Position').setValue([128 - r.left, 50 - r.top - r.height / 2]);
  var b = O.shape(C, 'BONG', [{ t: 'rect', size: [r.width + 56, 66], round: 24, pos: [100 + (r.width + 56) / 2, 50], fill: 'blueLight', name: 'Bong' }]);
  b.moveAfter(t);
  var mx = 'var r = thisComp.layer("TEXT").sourceRectAtTime(0, false);\n';
  O.item(b, 'Bong', 'size').expression = mx + '[r.width + 56, 66]';
  O.item(b, 'Bong', 'pos').expression = mx + '[100 + (r.width + 56) / 2, 50]';
  return C;
};
// Dòng trả lời của shop: luôn cùng một bong bóng (gõ lại / dán lại y hệt).
OPA.rowReply = function (ctx) {
  var O = OPA, C = O.comp('DONG_TRA_LOI_LAP', 760, 100, O.S2.DUR, ctx.F.art, 'white');
  O.shape(C, 'BONG tra loi', [
    { t: 'rect', size: [340, 66], round: 24, pos: [560, 50], fill: 'blue', name: 'Bong' },
    { t: 'rect', size: [190, 12], round: 6, pos: [530, 40], fill: 'white', name: 'Dong 1' },
    { t: 'rect', size: [130, 12], round: 6, pos: [500, 62], fill: 'white', name: 'Dong 2' }
  ]);
  O.icon(C, 'DA GUI', 'check', [672, 50], { size: 40, bg: 'white', fg: 'blue' });
  return C;
};

// ----- Phiếu POS gõ tay: chip số điện thoại / địa chỉ bay từ tin nhắn vào ô, vạch gõ dài ra, con trỏ bấm lưu -----
OPA.buildPosForm = function (ctx) {
  var O = OPA, F = ctx.F, DUR = O.S2.DUR;
  var P = O.comp('UI_PHIEU_POS_GO_TAY', 1920, 1080, DUR, F.art, 'blueDark');
  P.comment = 'Phieu len don POS thu cong (minh hoa). Mo f168; chip bay f184/f204; con tro bam luu f232.';
  O.shape(P, 'PHIEU', [
    { t: 'rect', size: [430, 330], round: 30, pos: [734, 800], fill: 'white', stroke: 'blue', sw: 6, name: 'The' },
    { t: 'rect', size: [430, 72], round: 30, pos: [734, 671], fill: 'blue', name: 'Dau phieu' },
    { t: 'rect', size: [430, 30], pos: [734, 692], fill: 'blue', name: 'Dau phieu vuong' },
    { t: 'rect', size: [276, 52], round: 12, pos: [776, 772], fill: 'blueLight', name: 'O so dien thoai' },
    { t: 'rect', size: [276, 52], round: 12, pos: [776, 860], fill: 'blueLight', name: 'O dia chi' },
    { t: 'rect', size: [100, 44], round: 22, pos: [866, 926], fill: 'blue', name: 'Nut luu' }
  ]);
  O.icon(P, 'ICON luu', 'check', [866, 926], { size: 36, bg: 'blue', fg: 'white', glyph: 0.8 });
  var pos = O.text(P, 'POS', { font: O.FONT.head, size: 32, color: 'white', name: 'NHAN POS' });
  O.placeTop(pos, 608, 656);
  O.icon(P, 'ICON phone', 'phone', [596, 772], { size: 56, bg: 'white', fg: 'blue', glyph: 0.85 });
  O.icon(P, 'ICON pin', 'pin', [596, 860], { size: 56, bg: 'white', fg: 'blue', glyph: 0.85 });
  // Vạch "đã gõ" neo mép trái để dài ra từ trái sang.
  var t1 = O.shape(P, 'DA GO so dien thoai', [{ t: 'rect', size: [170, 14], round: 7, pos: [652, 772], anchor: [-85, 0], fill: 'blue', name: 'Vach' }]);
  var t2 = O.shape(P, 'DA GO dia chi', [{ t: 'rect', size: [210, 14], round: 7, pos: [652, 860], anchor: [-105, 0], fill: 'blue', name: 'Vach' }]);
  O.anim(O.item(t1, 'Vach', 'scale'), [[196, [0, 100]], [208, [100, 100], 'BRAND']]);
  O.anim(O.item(t2, 'Vach', 'scale'), [[216, [0, 100]], [228, [100, 100], 'BRAND']]);
  var caret = O.shape(P, 'CON TRO GO', [{ t: 'rect', size: [4, 34], pos: [0, 0], fill: 'black', name: 'Vach' }]);
  O.anim(O.tr(caret, 'ADBE Position'), [[168, [658, 772]], [196, [658, 772], 'HOLD'], [208, [826, 772], 'BRAND'], [212, [658, 860], 'HOLD'], [216, [658, 860], 'HOLD'], [228, [866, 860], 'BRAND']]);
  O.tr(caret, 'ADBE Opacity').expression = 'Math.floor(time * 30 / 8) % 2 ? 0 : 100';
  // Chip dữ liệu: bật ở tin mới nhất trong hộp thư rồi bay vào ô (sao chép – dán bằng tay).
  var chips = [['phone', 184, [700, 772]], ['pin', 204, [700, 860]]];
  for (var i = 0; i < chips.length; i++) {
    var at = chips[i][1], dst = chips[i][2], src = [340, 846 - i * 106];
    var chip = O.shape(P, 'CHIP sao chep ' + (i + 1), [{ t: 'rect', size: [120, 50], round: 25, pos: [0, 0], fill: 'blue', stroke: 'white', sw: 4, name: 'Chip' }]);
    var gl = O.icon(P, 'CHIP icon ' + (i + 1), chips[i][0], [0, 0], { size: 40, bg: 'blue', fg: 'white', glyph: 0.9 });
    gl.parent = chip;
    O.setT(chip, { pos: src, scale: 0 });
    O.popScale(O.tr(chip, 'ADBE Scale'), at);
    O.anim(O.tr(chip, 'ADBE Position'), [[at + 4, src], [at + 14, dst, 'BRAND']]);
    O.anim(O.tr(chip, 'ADBE Opacity'), [[at + 12, 100], [at + 16, 0, 'EXIT']]);
    O.followOpacity(gl, chip);
    chip.motionBlur = true;
  }
  var cur = O.shape(P, 'CON TRO chuot', [{ t: 'path', v: [[0, 0], [0, 44], [11, 34], [19, 52], [27, 48], [19, 31], [34, 31]], fill: 'black', stroke: 'white', sw: 4, name: 'Mui ten' }]);
  O.anim(O.tr(cur, 'ADBE Position'), [[168, [930, 990]], [190, [884, 796], 'BRAND'], [206, [884, 796], 'SOFT'], [218, [884, 884], 'BRAND'], [222, [884, 884], 'SOFT'], [230, [872, 934], 'BRAND']]);
  O.anim(O.tr(cur, 'ADBE Scale'), [[230, [100, 100]], [232, [86, 86], 'BRAND'], [236, [100, 100], 'BRAND']]);
  cur.motionBlur = true;
  return P;
};
