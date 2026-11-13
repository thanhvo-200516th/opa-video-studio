// Cảnh 5 · 00:30–00:36 (khung 900–1080, cục bộ 0–180) · Outro & CTA. Nền xanh OPA, Bò trắng (BRAND-SPEC: bản trắng chỉ trên nền xanh/tối).
// Bò hiện (mõm bật lên, sừng mọc từ gốc) → "OPA Agent" R3 → câu định vị R2 → nhãn CTA R2 → nút bật lò xo → con trỏ bấm.
OPA.buildS5 = function (ctx) {
  var O = OPA, F = ctx.F, DUR = 180;
  var S = O.comp('S5_CTA', 1920, 1080, DUR, F.scenes, 'blue');
  S.comment = 'Canh 5 (30-36 s). Bo f0-34; ten f12 (R3); dinh vi f34 (R2); nhan CTA f56 (R2); nut f66; con tro bam f124. Link that: sua TXT_S5_URL.';
  O.shape(S, 'BG nen xanh', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'blue', name: 'Nen' }]);
  var deco = O.shape(S, 'DECO khoi nen', [
    { t: 'ellipse', size: [560, 560], pos: [130, 1080], fill: 'blueDark', name: 'Tron lon' },
    { t: 'rect', size: [220, 220], round: 56, pos: [1830, 90], rot: 16, fill: 'blueDark', name: 'Vuong bo' }
  ]);
  O.anim(O.tr(deco, 'ADBE Position'), [[0, [0, 0]], [DUR, [70, -44], 'LINEAR']]);
  O.anim(O.tr(deco, 'ADBE Opacity'), [[0, 0], [24, 100, 'BRAND']]);
  var cam = O.nul(S, 'CAM');

  // Bò trắng hiện kiểu V2 (comp riêng ART_MASCOT_BO_OPA_HIEN): mõm bật lên, sừng mọc từ gốc, rồi thở.
  var M = O.place(S, O.buildMascotReveal(ctx, 0), { name: 'MASCOT trang (hien)' });
  O.setT(M, { anchor: [1000, 1000], pos: [548, 520], scale: 31 });
  O.fxColor(M.property('ADBE Effect Parade').addProperty('ADBE Fill'), 'white');
  M.parent = cam;
  M.motionBlur = true;
  // Hai vòng tỏa từ Bò lúc hiện, khớp sonic logo (nét phẳng, không glow).
  var waves = [4, 16];
  for (var w = 0; w < waves.length; w++) {
    var wv = O.shape(S, 'VONG TOA ' + (w + 1), [{ t: 'ellipse', size: [460, 460], pos: [0, 0], stroke: 'white', sw: 6, name: 'Vong' }], { pos: [548, 520] });
    wv.parent = cam;
    wv.moveAfter(M);
    O.anim(O.tr(wv, 'ADBE Scale'), [[waves[w], [60, 60]], [waves[w] + 40, [330, 330], 'BRAND']]);
    O.anim(O.tr(wv, 'ADBE Opacity'), [[waves[w], 0], [waves[w] + 3, 40, 'LINEAR'], [waves[w] + 40, 0, 'BRAND']]);
  }

  var X = 900, T = O.comp('TITLE_S5', 1920, 1080, DUR, F.titles, 'blue');
  var c1 = O.comp('TXT_S5_TEN', 1920, 1080, DUR, F.edit, 'blue');
  var nm = O.text(c1, 'OPA Agent', { font: O.FONT.head, size: 128, color: 'white' });
  var r1 = O.placeTop(nm, X, 286);
  O.textAnim(nm, 'R3', { em: 128, inAt: 0, inDur: 30 });
  var c2 = O.comp('TXT_S5_DINH_VI', 1920, 1080, DUR, F.edit, 'blue');
  var tg = O.text(c2, 'AI bán hàng cho shop dùng Pancake', { font: O.FONT.body, size: 46, color: 'white' });
  O.fitWidth(tg, 1824 - X, 36);
  var r2 = O.placeTop(tg, X + 4, r1.top + r1.height + 26);
  O.textAnim(tg, 'R2', { em: 46, inAt: 0, inDur: 30 });
  var c3 = O.comp('TXT_S5_NHAN_CTA', 1920, 1080, DUR, F.edit, 'blue');
  var lb = O.text(c3, 'Thử miễn phí ngay tại:', { font: O.FONT.semi, size: 40, color: 'white' });
  var r3 = O.placeTop(lb, X + 64, r2.top + r2.height + 70);
  O.textAnim(lb, 'R2', { em: 40, inAt: 0, inDur: 30 });
  O.place(T, c1, { start: 12 });
  O.place(T, c2, { start: 34 });
  O.place(T, c3, { start: 56 });
  var arrow = O.icon(T, 'ICON mui ten (thay emoji tro tay)', 'arrow', [X + 24, r3.top + r3.height / 2], { size: 48, bg: 'white', fg: 'blue', glyph: 0.66 });
  O.popScale(O.tr(arrow, 'ADBE Scale'), 56);

  // Nút CTA: URL thật (Minh gửi 23/10), bỏ "https://" và "/" cuối cho gọn; nút rộng theo chữ (đổi URL thì dựng lại).
  var c4 = O.comp('TXT_S5_URL', 1920, 1080, DUR, F.edit, 'blue');
  var url = O.text(c4, 'chat.overpowers.agency', { font: O.FONT.head, size: 48, color: 'blue', just: 'C' });
  var ru = O.rect(url, 0);
  var BY = r3.top + r3.height + 92, BH = 108, BW = Math.max(560, Math.ceil(ru.width) + 2 * 64);
  var btn = O.shape(T, 'NUT CTA', [{ t: 'rect', size: [BW, BH], round: BH / 2, pos: [0, 0], fill: 'white', name: 'Nut' }]);
  O.setT(btn, { anchor: [0, 0], pos: [X + BW / 2, BY] });
  O.popScale(O.tr(btn, 'ADBE Scale'), 66);
  O.tr(url, 'ADBE Position').setValue([X + BW / 2 - ru.left - ru.width / 2, BY - ru.top - ru.height / 2]);
  O.textAnim(url, 'R3', { em: 48, inAt: 0, inDur: 24 });
  var lu = O.place(T, c4, { start: 72 });
  lu.moveBefore(btn);
  // Bấm: nút lún 96 % rồi bật lại; vòng gợn lan ra.
  O.anim(O.tr(btn, 'ADBE Scale'), [[124, [100, 100]], [128, [94, 94], 'BRAND'], [136, [100, 100], 'BRAND']]);
  var ring = O.shape(T, 'GON BAM', [{ t: 'rect', size: [BW, BH], round: BH / 2, pos: [0, 0], stroke: 'white', sw: 6, name: 'Vong' }]);
  O.setT(ring, { anchor: [0, 0], pos: [X + BW / 2, BY] });
  O.anim(O.tr(ring, 'ADBE Scale'), [[126, [100, 100]], [150, [118, 150], 'BRAND']]);
  O.anim(O.tr(ring, 'ADBE Opacity'), [[124, 0], [126, 90, 'LINEAR'], [150, 0, 'EXIT']]);
  ring.moveAfter(btn);
  var ring2 = O.shape(T, 'GON NHAC LAI', [{ t: 'rect', size: [BW, BH], round: BH / 2, pos: [0, 0], stroke: 'white', sw: 6, name: 'Vong' }]);
  O.setT(ring2, { anchor: [0, 0], pos: [X + BW / 2, BY] });
  O.anim(O.tr(ring2, 'ADBE Scale'), [[152, [100, 100]], [179, [118, 150], 'BRAND']]);
  O.anim(O.tr(ring2, 'ADBE Opacity'), [[150, 0], [152, 70, 'LINEAR'], [179, 0, 'EXIT']]);
  ring2.moveAfter(btn);
  O.tr(btn, 'ADBE Scale').expression = 'var t = time - 140 / 30; var k = t > 0 ? 2.5 * Math.sin(t * 2 * Math.PI / 1.2) : 0; [value[0] + k, value[1] + k]';
  var cur = O.shape(T, 'CON TRO bam', [{ t: 'path', v: [[0, 0], [0, 56], [14, 43], [24, 66], [34, 61], [24, 39], [43, 39]], fill: 'black', stroke: 'white', sw: 5, name: 'Mui ten' }]);
  // Con trỏ bấm vào đầu bo phải của nút, sau chữ URL (không đè chữ).
  var CX = X + BW / 2 + ru.width / 2 + 14;
  O.anim(O.tr(cur, 'ADBE Position'), [[92, [1880, 1040]], [122, [CX, BY + 8], 'BRAND'], [128, [CX - 4, BY + 12], 'SOFT'], [136, [CX, BY + 8], 'SOFT']]);
  O.anim(O.tr(cur, 'ADBE Opacity'), [[92, 0], [96, 100, 'LINEAR']]);
  cur.motionBlur = true;
  var tL5 = O.place(S, T, { name: 'TITLE_S5' });
  tL5.parent = cam;
  var FOC = [960, 540];
  O.setT(cam, { anchor: FOC, pos: FOC });
  O.anim(O.tr(cam, 'ADBE Scale'), [[0, [100, 100]], [DUR, [106, 106], 'LINEAR']]);
  O.anim(O.tr(cam, 'ADBE Position'), [[0, FOC], [DUR, [FOC[0] - 60, FOC[1] - 30], 'LINEAR']]);
  S.motionBlur = true;
  O.report.measures.push({ scene: 'S5', name: r1, tagline: r2, ctaLabel: r3, button: [X, BY - BH / 2, BW, BH] });
  return S;
};
