// Cảnh 1 · 00:00–00:05 (khung 0–150) · Hook: chủ shop quá tải tin nhắn, đồng hồ chạy vùn vụt.
// Nền đêm #003C99. Trái: nhân vật + đồng hồ + thông báo. Phải: cột chữ R1 (headline theo từ) → R2 (phụ theo dòng) → cụm nhấn.
OPA.buildS1 = function (ctx) {
  var O = OPA, F = ctx.F, DUR = 150;
  var S = O.comp('S1_MO_DAU', 1920, 1080, DUR, F.scenes, 'blueDark');
  S.comment = 'Canh 1 (0-5 s). Mau nen: blueDark. May quay: null CAM.';

  // ----- Nền + khối trang trí trôi chậm (chiều sâu kiểu V2) -----
  var bg = O.shape(S, 'BG nen dem', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'blueDark' }]);
  var deco = O.shape(S, 'DECO khoi nen', [
    { t: 'ellipse', size: [460, 460], pos: [1850, 1070], fill: 'blue', name: 'Tron lon' },
    { t: 'rect', size: [240, 240], round: 60, pos: [90, 1010], rot: 14, fill: 'blue', name: 'Vuong bo' },
    { t: 'ellipse', size: [120, 120], pos: [1800, 80], fill: 'blue', name: 'Tron nho' },
    { t: 'ellipse', size: [56, 56], pos: [930, 1020], fill: 'blue', name: 'Cham' }
  ]);
  O.anim(O.tr(deco, 'ADBE Position'), [[0, [0, 0]], [DUR, [-40, -18], 'LINEAR']]);

  var cam = O.nul(S, 'CAM');

  // ----- Nhân vật (comp riêng để dùng lại, có tư thế bận) -----
  var owner = ctx.art.ownerBusy;
  var ownL = O.place(S, owner, { name: 'NHAN VAT chu shop' });
  O.setT(ownL, { pos: [520, 660] });
  ownL.parent = cam;

  // ----- Đồng hồ treo tường -----
  var CX = 236, CY = 236, R = 106;
  var ticks = [];
  for (var h = 0; h < 12; h++) {
    var a = h * Math.PI / 6, r1 = R - 22, r2 = R - (h % 3 === 0 ? 40 : 32);
    ticks.push({ t: 'path', v: [[Math.sin(a) * r1, -Math.cos(a) * r1], [Math.sin(a) * r2, -Math.cos(a) * r2]], closed: false, stroke: 'blueDark', sw: (h % 3 === 0 ? 8 : 5), pos: [CX, CY], name: 'Vach ' + h });
  }
  var clockFace = O.shape(S, 'DONG HO mat', [
    { t: 'ellipse', size: [R * 2, R * 2], pos: [CX, CY], fill: 'white', stroke: 'blue', sw: 14, name: 'Mat' }
  ].concat(ticks));
  var hourH = O.shape(S, 'DONG HO kim gio', [{ t: 'path', v: [[0, 10], [0, -48]], closed: false, stroke: 'blueDark', sw: 12, pos: [CX, CY] }]);
  var minH = O.shape(S, 'DONG HO kim phut', [{ t: 'path', v: [[0, 14], [0, -78]], closed: false, stroke: 'blueDark', sw: 8, pos: [CX, CY] }]);
  var pin = O.shape(S, 'DONG HO chot', [{ t: 'ellipse', size: [22, 22], pos: [CX, CY], fill: 'blue' }]);
  var hands = [hourH, minH];
  for (var k = 0; k < hands.length; k++) O.setT(hands[k], { anchor: [CX, CY], pos: [CX, CY] });
  // Kim phút quay 3 vòng trong 5 s: thời gian trôi vùn vụt.
  O.anim(O.tr(minH, 'ADBE Rotate Z'), [[0, 0], [DUR, 1080, 'LINEAR']]);
  O.anim(O.tr(hourH, 'ADBE Rotate Z'), [[0, 30], [DUR, 120, 'LINEAR']]);
  // Nhịp "tích" mỗi 15 khung: mặt đồng hồ nảy nhẹ (căn với SFX tích tắc).
  var clockG = [clockFace, hourH, minH, pin];
  var clockNull = O.nul(S, 'DONG HO nhom');
  O.setT(clockNull, { anchor: [CX, CY], pos: [CX, CY] });
  for (k = 0; k < clockG.length; k++) clockG[k].parent = clockNull;
  var tick = [];
  for (var f = 0; f < DUR; f += 15) { tick.push([f, [100, 100]]); tick.push([f + 3, [105, 105], 'BRAND']); }
  tick.push([DUR - 1, [100, 100], 'SOFT']);
  O.anim(O.tr(clockNull, 'ADBE Scale'), tick);
  clockNull.parent = cam;

  // ----- Thông báo tin nhắn dồn dập (chấm đỏ ALERT = chưa trả lời) -----
  var bubbles = [[742, 520, 2], [820, 446, 12], [700, 372, 21], [826, 300, 29], [716, 228, 36], [838, 158, 42]];
  for (var b = 0; b < bubbles.length; b++) {
    var bx = bubbles[b][0], by = bubbles[b][1], at = bubbles[b][2];
    var bub = O.shape(S, 'TIN NHAN ' + (b + 1), [
      { t: 'rect', size: [236, 66], round: 24, pos: [0, 0], fill: 'white', name: 'The' },
      { t: 'ellipse', size: [38, 38], pos: [-82, 0], fill: 'blue', name: 'Avatar' },
      { t: 'rect', size: [110, 11], round: 6, pos: [8, -10], fill: 'blueLight', name: 'Dong 1' },
      { t: 'rect', size: [74, 11], round: 6, pos: [-10, 11], fill: 'blueLight', name: 'Dong 2' },
      { t: 'ellipse', size: [26, 26], pos: [110, -30], fill: 'alert', name: 'Cham chua doc' }
    ]);
    O.setT(bub, { anchor: [0, 0], pos: [bx, by] });
    O.popScale(O.tr(bub, 'ADBE Scale'), at);
    // Trôi lên rất chậm sau khi bật, như dòng thông báo đang chảy.
    O.anim(O.tr(bub, 'ADBE Position'), [[at, [bx, by + 26]], [at + 12, [bx, by], 'BRAND'], [DUR, [bx, by - 22], 'LINEAR']]);
    bub.parent = cam;
    bub.motionBlur = true;
  }

  // ----- Cột chữ: TITLE_S1 chứa 3 comp TXT (sửa chữ trong thư mục 03_EDIT_CHU) -----
  var X = 1010, TOP = 128, MAXW = 1824 - X;
  var T = O.comp('TITLE_S1', 1920, 1080, DUR, F.titles, 'blueDark');
  T.comment = 'Thiet ke cot chu canh 1. Thoi diem vao: headline f4, phu f28, nhan f52; khoi danh dau quet f78.';

  var cHead = O.comp('TXT_S1_HEADLINE', 1920, 1080, DUR, F.edit, 'blueDark');
  // Giãn dòng 1,32 em (BRAND-SPEC): chấm dưới của "Ạ" phải bám dòng trên, không lơ lửng sát chữ "BAO".
  var head = O.text(cHead, 'BẠN MẤT\rBAO NHIÊU\rTHỜI GIAN', { font: O.FONT.head, size: 126, leading: 166, color: 'white' });
  O.fitWidth(head, MAXW, 96);
  var rH = O.placeTop(head, X, TOP);
  O.textAnim(head, 'R1', { em: 126, inAt: 0, inDur: 30, outAt: 118, outDur: 28 });

  var cSub = O.comp('TXT_S1_PHU', 1920, 1080, DUR, F.edit, 'blueDark');
  var sub = O.text(cSub, 'Để trả lời khách và lên đơn\rTrên Pancake', { font: O.FONT.body, size: 56, leading: 74, color: 'white' });
  O.fitWidth(sub, MAXW, 40);
  var rS = O.placeTop(sub, X, TOP + rH.height + 46);
  O.textAnim(sub, 'R2', { em: 56, inAt: 0, inDur: 30, outAt: 92, outDur: 26 });

  var cAcc = O.comp('TXT_S1_NHAN', 1920, 1080, DUR, F.edit, 'blueDark');
  var acc = O.text(cAcc, 'Mỗi ngày?', { font: O.FONT.accent, size: 80, color: 'white' });
  // Khối đánh dấu thò trái 0,12 em: lùi chữ vào để khối không chạm lề.
  var rA = O.placeTop(acc, X + Math.round(0.12 * 80), TOP + rH.height + 46 + rS.height + 34);
  O.textAnim(acc, 'R2', { em: 80, inAt: 0, inDur: 30, outAt: 68, outDur: 26 });

  var lHead = O.place(T, cHead, { start: 4 });
  var lSub = O.place(T, cSub, { start: 28 });
  var accB = O.accentBlock(T, cAcc, { start: 52, em: 80, measureT: 1.5, markKey: 'white', inkKey: 'blue', sweepAt: 78 });
  // Khối rút về trái cùng lúc chữ nhấn rút (khung của TITLE).
  O.anim(O.tr(accB.mark, 'ADBE Scale'), [[118, [100, 100]], [124, [0, 100], 'EXIT']]);

  var tL = O.place(S, T, { name: 'TITLE_S1' });
  tL.parent = cam;

  // ----- Nối cảnh 2: một tin nhắn trắng nở về phía ống kính, phủ kín khung cuối (cảnh 2 mở từ màn trắng) -----
  var FOC = [770, 340];
  var burst = O.shape(S, 'TIN NHAN NO TRANG (noi canh 2)', [{ t: 'rect', size: [236, 66], round: 24, pos: [0, 0], fill: 'white', name: 'Bong' }], { pos: FOC, scale: 0 });
  burst.parent = cam;  // gắn khi máy quay còn ở gốc nên không bị bù toạ độ

  // ----- Máy quay: trôi chậm rồi lao vào chồng tin nhắn (nối cảnh 2) -----
  O.setT(cam, { anchor: FOC, pos: FOC });
  O.anim(O.tr(cam, 'ADBE Scale'), [[0, [100, 100]], [124, [103.5, 103.5], 'SOFT'], [DUR, [360, 360], 'PUSH']]);
  O.anim(O.tr(cam, 'ADBE Position'), [[0, FOC], [124, [FOC[0] - 8, FOC[1] + 4], 'SOFT'], [DUR, [960, 560], 'PUSH']]);
  // Tin nhắn trắng phủ vừa kín khung đúng khung cuối (dư 15 % cho nhoè chuyển động), không sớm hơn:
  // tránh hai khung trắng giống hệt nhau liền nhau. Cỡ tính theo máy quay thật ở khung cuối.
  var camS = O.tr(cam, 'ADBE Scale').valueAtTime(O.t(DUR - 1), false)[0] / 100;
  var camY = O.tr(cam, 'ADBE Position').valueAtTime(O.t(DUR - 1), false)[1];
  var bs = 100 * 1.15 * Math.max(camY, 1080 - camY) / (33 * camS);
  O.anim(O.tr(burst, 'ADBE Scale'), [[136, [0, 0]], [DUR - 1, [bs, bs], 'EXIT']]);
  S.motionBlur = true;
  ownL.motionBlur = true; tL.motionBlur = true; clockNull.motionBlur = true; burst.motionBlur = true;
  for (k = 0; k < clockG.length; k++) clockG[k].motionBlur = true;

  O.report.measures.push({ scene: 'S1', headline: rH, sub: rS, accent: rA, burstScale: bs });
  return S;
};
