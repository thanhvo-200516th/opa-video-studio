// Cảnh 4 · 00:22–00:30 (khung 660–900, cục bộ 0–240) · Giải phóng sức lao động. Nền trắng, khung xanh OPA bên trái.
// Trái: chủ shop ngả lưng thư thả (tham chiếu SMIT 23–29 s), tích xanh bay lên từ laptop. Phải: 3 dòng "Không cần…" R5 + icon tích.
OPA.buildOwnerRelax = function (ctx) {
  var O = OPA, DUR = 240;
  var C = O.comp('ART_CHU_SHOP_THU_THA', 1000, 800, DUR, ctx.F.art, 'blue');
  C.comment = 'Nhan vat chu shop - tu the nga lung thu tha (canh 4). Dat tren nen xanh OPA.';
  var lean = O.nul(C, 'NGA LUNG (khop hong)');
  O.setT(lean, { anchor: [500, 744], pos: [500, 744] });
  O.anim(O.tr(lean, 'ADBE Rotate Z'), [[0, 0], [24, -7, 'BRAND']]);
  var parts = [];
  parts.push(O.shape(C, 'GHE tua', [{ t: 'rect', size: [344, 372], round: 84, pos: [500, 560], fill: 'blueDark', name: 'Lung ghe' }]));
  // Tay vòng sau gáy: vẽ trước đầu để đầu che bàn tay.
  parts.push(O.shape(C, 'TAY trai sau gay', [
    { t: 'path', v: [[402, 508], [318, 392]], closed: false, stroke: 'white', sw: 52, name: 'Tay ao' },
    { t: 'path', v: [[318, 392], [440, 300]], closed: false, stroke: 'blueLight', sw: 42, name: 'Cang tay' }
  ]));
  parts.push(O.shape(C, 'TAY phai sau gay', [
    { t: 'path', v: [[598, 508], [682, 392]], closed: false, stroke: 'white', sw: 52, name: 'Tay ao' },
    { t: 'path', v: [[682, 392], [560, 300]], closed: false, stroke: 'blueLight', sw: 42, name: 'Cang tay' }
  ]));
  parts.push(O.shape(C, 'CO', [{ t: 'rect', size: [50, 70], round: 14, pos: [500, 452], fill: 'blueLight', name: 'Co' }]));
  var torso = O.shape(C, 'THAN ao', [
    { t: 'rect', size: [280, 268], round: 96, pos: [500, 612], fill: 'white', name: 'Ao' },
    { t: 'path', v: [[466, 480], [500, 526], [534, 480]], fill: 'blueLight', name: 'Co ao chu V' }
  ]);
  parts.push(torso);
  var head = O.shape(C, 'DAU', [
    { t: 'ellipse', size: [192, 192], pos: [500, 328], fill: 'black', name: 'Toc sau' },
    { t: 'ellipse', size: [82, 82], pos: [500, 224], fill: 'black', name: 'Bui toc' },
    { t: 'ellipse', size: [28, 36], pos: [420, 358], fill: 'blueLight', name: 'Tai trai' },
    { t: 'ellipse', size: [28, 36], pos: [580, 358], fill: 'blueLight', name: 'Tai phai' },
    { t: 'ellipse', size: [160, 172], pos: [500, 356], fill: 'blueLight', name: 'Mat' },
    { t: 'path', v: [[414, 334], [432, 274], [500, 250], [572, 270], [590, 324], [548, 292], [492, 304]],
      i: [[0, 0], [-6, 22], [-40, 0], [-26, -14], [-4, -20], [16, 10], [24, -2]],
      o: [[0, 0], [8, -28], [40, 0], [20, 12], [0, 0], [-18, -8], [-34, 4]], fill: 'black', name: 'Mai toc' },
    { t: 'path', v: [[458, 368], [472, 360], [486, 368]], i: [[0, 0], [-7, 0], [0, 0]], o: [[0, 0], [7, 0], [0, 0]], closed: false, stroke: 'black', sw: 6, name: 'Mat nham trai' },
    { t: 'path', v: [[514, 368], [528, 360], [542, 368]], i: [[0, 0], [-7, 0], [0, 0]], o: [[0, 0], [7, 0], [0, 0]], closed: false, stroke: 'black', sw: 6, name: 'Mat nham phai' },
    { t: 'path', v: [[480, 402], [500, 416], [520, 402]], i: [[0, 0], [-10, 0], [0, 0]], o: [[0, 0], [10, 0], [0, 0]], closed: false, stroke: 'black', sw: 6, name: 'Mieng cuoi' }
  ]);
  O.setT(head, { anchor: [500, 452], pos: [500, 464] });
  O.tr(head, 'ADBE Rotate Z').expression = 'Math.sin(time * 2 * Math.PI * 0.35) * 2.2';
  parts.push(head);
  for (var k = 0; k < parts.length; k++) parts[k].parent = lean;

  O.shape(C, 'LAPTOP', [
    { t: 'rect', size: [366, 14], round: 7, pos: [500, 690], fill: 'blueLight', name: 'De may' },
    { t: 'rect', size: [316, 196], round: 18, pos: [500, 600], fill: 'blueDark', name: 'Mat lung' },
    { t: 'ellipse', size: [28, 28], pos: [500, 598], fill: 'white', name: 'Logo tron' }
  ]);
  // Không vẽ chân bàn: mặt bàn chạy tràn mép khung xanh (matte cắt gọn), tránh chân bàn bị cắt ở góc bo.
  O.shape(C, 'BAN', [{ t: 'rect', size: [944, 32], round: 12, pos: [500, 712], fill: 'white', name: 'Mat ban' }]);
  O.shape(C, 'COC CA PHE', [
    { t: 'ellipse', size: [34, 40], pos: [812, 652], stroke: 'white', sw: 10, name: 'Quai' },
    { t: 'rect', size: [66, 80], round: 12, pos: [784, 656], fill: 'white', name: 'Coc' },
    { t: 'rect', size: [66, 14], round: 6, pos: [784, 626], fill: 'blueLight', name: 'Mieng coc' }
  ]);
  var steam = O.shape(C, 'HOI CA PHE', [
    { t: 'path', v: [[770, 600], [778, 570], [770, 540]], i: [[0, 0], [0, 8], [0, 0]], o: [[0, 0], [0, -8], [0, 0]], closed: false, stroke: 'white', sw: 6, trim: [0, 100], name: 'Hoi 1' },
    { t: 'path', v: [[796, 600], [804, 566], [796, 532]], i: [[0, 0], [0, 8], [0, 0]], o: [[0, 0], [0, -8], [0, 0]], closed: false, stroke: 'white', sw: 6, trim: [0, 100], name: 'Hoi 2' }
  ]);
  // Hơi bốc: một đoạn nét trắng đặc chạy dọc đường hơi (trim), không làm mờ (độ mờ pha ra màu ngoài bảng OPA).
  var rise = function (off) { return 'var p = ((time * 0.8 + ' + off + ') % 1) * 150 - 50;\n'; };
  var wisps = [['Hoi 1', 0], ['Hoi 2', 0.5]];
  for (var w = 0; w < wisps.length; w++) {
    O.item(steam, wisps[w][0], 'trimStart').expression = rise(wisps[w][1]) + 'Math.max(0, p)';
    O.item(steam, wisps[w][0], 'trimEnd').expression = rise(wisps[w][1]) + 'Math.min(100, Math.max(0, p + 50))';
  }
  O.tr(steam, 'ADBE Position').expression = '[0, -Math.abs(Math.sin(time * 2 * Math.PI * 0.4)) * 10]';
  return C;
};

OPA.buildS4 = function (ctx) {
  var O = OPA, F = ctx.F, DUR = 240, P4 = O.S3.PANEL4;
  var S = O.comp('S4_GIAI_PHONG', 1920, 1080, DUR, F.scenes, 'white');
  S.comment = 'Canh 4 (22-30 s). Khung xanh noi tu canh 3; nhan vat troi len f0-26; dong 1 f12, dong 2 f60, dong 3 f106 (R5), rut f196; khung no tran f214-239 sang canh 5.';
  O.shape(S, 'BG nen trang', [{ t: 'rect', size: [1920, 1080], pos: [960, 540], fill: 'white', name: 'Nen' }]);
  var cam = O.nul(S, 'CAM');
  // Khung xanh đúng toạ độ cảnh 3 để lại; vừa là nền vừa là matte của nhân vật.
  var panel = O.shape(S, 'KHUNG xanh', [{ t: 'rect', size: P4.size, round: P4.round, pos: [0, 0], fill: 'blue', name: 'Khung' }]);
  O.setT(panel, { pos: P4.pos });
  var deco = O.shape(S, 'DECO trong khung', [
    { t: 'ellipse', size: [300, 300], pos: [210, 250], fill: 'blueDark', name: 'Tron' },
    { t: 'ellipse', size: [120, 120], pos: [780, 210], fill: 'blueDark', name: 'Tron nho' }
  ]);
  O.anim(O.tr(deco, 'ADBE Opacity'), [[0, 0], [20, 100, 'BRAND'], [198, 100, 'HOLD'], [214, 0, 'EXIT']]);
  var own = O.place(S, ctx.art.ownerRelax, { name: 'NHAN VAT thu tha' });
  O.setT(own, { pos: [492, 596], scale: 94 });
  own.setTrackMatte(panel, TrackMatteType.ALPHA);
  deco.setTrackMatte(panel, TrackMatteType.ALPHA);
  panel.enabled = true;
  // Khung xanh đứng theo toạ độ khung hình (khớp cảnh 3 và lúc nở tràn); phần bên trong trôi theo máy quay.
  var kids = [deco, own];
  for (var k = 0; k < kids.length; k++) kids[k].parent = cam;
  // Nhân vật trồi lên trong khung rồi ngả lưng; cuối cảnh trượt xuống nhường khung xanh nở ra.
  // Khung 0 chỉ ló búi tóc ở mép dưới khung xanh: không hiện nguyên người ngay điểm cắt từ cảnh 3.
  O.anim(O.tr(own, 'ADBE Position'), [[0, [492, 1140]], [26, [492, 596], 'BRAND'], [200, [492, 596], 'SOFT'], [222, [492, 1500], 'EXIT']]);
  own.motionBlur = true;
  // Tích xanh bay lên từ laptop: việc trả lời đang tự chạy.
  var floats = [[300, 24], [690, 50], [250, 76], [740, 102], [330, 128], [660, 154]];
  for (var i = 0; i < floats.length; i++) {
    var fx = floats[i][0], at = floats[i][1];
    var ic = O.icon(S, 'TICH bay ' + (i + 1), 'check', [fx, 600], { size: 58, bg: 'white', fg: 'blue' });
    ic.parent = cam;
    O.anim(O.tr(ic, 'ADBE Position'), [[at, [fx, 600]], [at + 70, [fx + (i % 2 ? 24 : -24), 250], 'SOFT']]);
    O.anim(O.tr(ic, 'ADBE Opacity'), [[at, 0], [at + 8, 100, 'BRAND'], [at + 52, 100, 'HOLD'], [at + 70, 0, 'EXIT']]);
    O.popScale(O.tr(ic, 'ADBE Scale'), at);
  }

  var T = O.comp('TITLE_S4', 1920, 1080, DUR, F.titles, 'white');
  T.comment = 'Ba muc song song, xu ly nhu nhau: icon tich xanh OPA bat lo xo + chu R5 tu phai.';
  var items = [
    'Không cần tạo App\rFacebook phức tạp',
    'Không cần gõ lại một câu hỏi\rHàng trăm lần',
    'Không cần copy-paste từng\rSố điện thoại, địa chỉ vào POS'
  ];
  var ins = [12, 60, 106], X = 1074, tops = [210, 444, 678], rr = [];
  for (var j = 0; j < items.length; j++) {
    var c = O.comp('TXT_S4_Y' + (j + 1), 1920, 1080, DUR, F.edit, 'white');
    var L = O.text(c, items[j], { font: O.FONT.body, size: 48, leading: 64, color: 'black' });
    O.fitWidth(L, 1824 - X, 36);
    rr.push(O.placeTop(L, X, tops[j]));
    O.textAnim(L, 'R5', { em: 48, inAt: 0, inDur: 30, outAt: 196 - ins[j], outDur: 26 });
    O.place(T, c, { start: ins[j] });
    var ic2 = O.icon(T, 'ICON tich ' + (j + 1), 'check', [1012, tops[j] + 30], { size: 70, bg: 'blue', fg: 'white' });
    O.popScale(O.tr(ic2, 'ADBE Scale'), ins[j] + 2);
    O.anim(O.tr(ic2, 'ADBE Opacity'), [[196, 100], [210, 0, 'EXIT']]);
  }
  var tL4 = O.place(S, T, { name: 'TITLE_S4' });
  tL4.parent = cam;

  // Máy quay bắt đầu 100 % để khớp khung xanh cảnh 3, trôi chậm tới 103 %.
  var FOC = [492, 540];
  O.setT(cam, { anchor: FOC, pos: FOC });
  // Trôi sang trái-lên: dòng dài nhất bên phải luôn cách lề (rà chéo: trôi phải đẩy chữ chạm x 1860).
  O.anim(O.tr(cam, 'ADBE Scale'), [[0, [100, 100]], [DUR, [102.5, 102.5], 'LINEAR']]);
  O.anim(O.tr(cam, 'ADBE Position'), [[0, FOC], [DUR, [FOC[0] - 44, FOC[1] - 20], 'LINEAR']]);
  // Khung xanh nở tràn khung hình, tăng tốc tới đúng khung cuối (không để nền xanh đứng yên trước khi sang cảnh 5).
  O.anim(O.item(panel, 'Khung', 'size'), [[214, P4.size], [239, [1940, 1100], 'EXIT']]);
  O.anim(O.item(panel, 'Khung', 'round'), [[214, P4.round], [237, 0, 'EXIT']]);
  O.anim(O.tr(panel, 'ADBE Position'), [[214, P4.pos], [239, [960, 540], 'EXIT']]);
  S.motionBlur = true;
  O.report.measures.push({ scene: 'S4', items: rr });
  return S;
};
