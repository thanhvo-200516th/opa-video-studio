// Cảnh mẫu · 0–5 s (khung 0–150): nền phẳng, headline R1 theo từ, nhãn phụ R2 vào trễ, nút bật lò xo, máy quay trôi đều.
// Sửa chữ: comp TXT_S1_* trong 03_EDIT_CHU. Công thức chữ, ease, lò xo: sổ tay mục 5–6.
OPA.buildS1 = function (ctx) {
  var O = OPA, F = ctx.F, DUR = 150;
  var S = O.comp('S1_MAU', 1920, 1080, DUR, F.scenes, 'blueDark');
  S.comment = 'Canh mau 5 s. Headline f6 (R1), nhan phu f34 (R2), nut bat lo xo f60, may quay troi 100 -> 104 %.';
  O.shape(S, 'BG nen', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'blueDark', name: 'Nen' }]);
  var cam = O.nul(S, 'CAM');

  // Chữ: mỗi comp TXT có một layer "TEXT" mang Text Animator; comp TITLE giữ vị trí và offset thời gian.
  var T = O.comp('TITLE_S1', 1920, 1080, DUR, F.titles, 'blueDark');
  var c1 = O.comp('TXT_S1_HEADLINE', 1920, 1080, DUR, F.edit, 'blueDark');
  var h = O.text(c1, 'Bán hàng nhẹ tênh', { font: O.FONT.head, size: 120, color: 'white' });
  var r1 = O.placeTop(h, 160, 360);
  O.textAnim(h, 'R1', { em: 120, inAt: 0, inDur: 30, outAt: 112, outDur: 28 });
  var c2 = O.comp('TXT_S1_PHU', 1920, 1080, DUR, F.edit, 'blueDark');
  var s = O.text(c2, 'Để AI trả lời khách thay bạn', { font: O.FONT.body, size: 52, color: 'white' });
  O.placeTop(s, 164, r1.top + r1.height + 36);
  O.textAnim(s, 'R2', { em: 52, inAt: 0, inDur: 30, outAt: 84, outDur: 28 });
  O.place(T, c1, { start: 6 });
  O.place(T, c2, { start: 34 });
  var tL = O.place(S, T, { name: 'TITLE_S1' });
  tL.parent = cam;

  // Nút bật lò xo (damping 12, stiffness 100: vọt 9,5 %, đỉnh 0,39 s) ở khung 60.
  var btn = O.shape(S, 'NUT CTA', [{ t: 'rect', size: [420, 108], round: 54, pos: [0, 0], fill: 'blue', name: 'Nut' }], { pos: [370, 800] });
  O.popScale(O.tr(btn, 'ADBE Scale'), 60);
  btn.parent = cam;
  btn.motionBlur = true;

  // Máy quay trôi một đường chậm, đều suốt cảnh.
  O.setT(cam, { anchor: [960, 540], pos: [960, 540] });
  O.anim(O.tr(cam, 'ADBE Scale'), [[0, [100, 100]], [DUR, [104, 104], 'LINEAR']]);
  S.motionBlur = true;
  return S;
};
