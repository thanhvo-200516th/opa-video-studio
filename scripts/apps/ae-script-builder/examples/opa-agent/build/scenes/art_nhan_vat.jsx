// Nhân vật chủ shop 2D phẳng, chỉ dùng 5 màu OPA: da #E6F0FF, tóc #0A0A0A, áo #FFFFFF, ghế #0068FF, laptop đen.
// Comp 1000×800; mặt bàn ở y≈696. Tư thế "bận" (cảnh 1): gõ phím liên tục, mày chau, toát mồ hôi, điện thoại rung.
OPA.buildOwnerBusy = function (ctx) {
  var O = OPA, DUR = 150;
  var C = O.comp('ART_CHU_SHOP_BAN_RON', 1000, 800, DUR, ctx.F.art, 'blueDark');
  C.comment = 'Nhan vat chu shop - tu the ban ron (canh 1). Moi bo phan la shape layer, khop noi bang parent.';

  O.shape(C, 'GHE tua', [{ t: 'rect', size: [344, 372], round: 84, pos: [500, 560], fill: 'blue', name: 'Lung ghe' }]);
  O.shape(C, 'CO', [{ t: 'rect', size: [50, 70], round: 14, pos: [500, 452], fill: 'blueLight', name: 'Co' }]);
  var torso = O.shape(C, 'THAN ao', [
    { t: 'rect', size: [280, 268], round: 96, pos: [500, 612], fill: 'white', name: 'Ao' },
    { t: 'path', v: [[466, 480], [500, 526], [534, 480]], fill: 'blueLight', name: 'Co ao chu V' }
  ]);
  O.setT(torso, { anchor: [500, 744], pos: [500, 744] });
  O.tr(torso, 'ADBE Scale').expression = 'var s = 100 + Math.sin(time * 2 * Math.PI * 0.6) * 0.8; [s, s]';

  // Đầu: khớp ở cổ để nghiêng nhẹ theo nhịp gõ.
  var head = O.shape(C, 'DAU', [
    { t: 'ellipse', size: [192, 192], pos: [500, 328], fill: 'black', name: 'Toc sau' },
    { t: 'ellipse', size: [82, 82], pos: [500, 224], fill: 'black', name: 'Bui toc' },
    { t: 'ellipse', size: [28, 36], pos: [420, 358], fill: 'blueLight', name: 'Tai trai' },
    { t: 'ellipse', size: [28, 36], pos: [580, 358], fill: 'blueLight', name: 'Tai phai' },
    { t: 'ellipse', size: [160, 172], pos: [500, 356], fill: 'blueLight', name: 'Mat' },
    { t: 'path', v: [[414, 334], [432, 274], [500, 250], [572, 270], [590, 324], [548, 292], [492, 304]],
      i: [[0, 0], [-6, 22], [-40, 0], [-26, -14], [-4, -20], [16, 10], [24, -2]],
      o: [[0, 0], [8, -28], [40, 0], [20, 12], [0, 0], [-18, -8], [-34, 4]], fill: 'black', name: 'Mai toc' }
  ]);
  O.setT(head, { anchor: [500, 452], pos: [500, 464] });
  O.tr(head, 'ADBE Rotate Z').expression = 'Math.sin(time * 2 * Math.PI * 0.9) * 1.6';

  var eyes = O.shape(C, 'MAT nham', [
    { t: 'ellipse', size: [14, 19], pos: [472, 366], fill: 'black', name: 'Mat trai' },
    { t: 'ellipse', size: [14, 19], pos: [528, 366], fill: 'black', name: 'Mat phai' }
  ]);
  O.setT(eyes, { anchor: [500, 366], pos: [500, 366] });
  eyes.parent = head;
  O.anim(O.tr(eyes, 'ADBE Scale'), [[40, [100, 100]], [43, [100, 8], 'SOFT'], [47, [100, 100], 'SOFT'], [104, [100, 100], 'HOLD'], [107, [100, 8], 'SOFT'], [111, [100, 100], 'SOFT']]);
  var brows = O.shape(C, 'MAY chau', [
    { t: 'path', v: [[452, 340], [485, 328]], closed: false, stroke: 'black', sw: 6, name: 'May trai' },
    { t: 'path', v: [[548, 340], [515, 328]], closed: false, stroke: 'black', sw: 6, name: 'May phai' }
  ]);
  brows.parent = head;
  var mouth = O.shape(C, 'MIENG', [{ t: 'path', v: [[486, 408], [500, 401], [514, 408]], closed: false, stroke: 'black', sw: 5, name: 'Mieng mim' }]);
  mouth.parent = head;
  var sweat = O.shape(C, 'MO HOI', [{ t: 'path', v: [[0, -18], [10, 6], [0, 16], [-10, 6]], i: [[0, 0], [0, -10], [6, 0], [0, 6]], o: [[0, 0], [0, 6], [-6, 0], [0, -10]], fill: 'white', name: 'Giot' }]);
  O.setT(sweat, { pos: [600, 306] });
  sweat.parent = head;
  O.anim(O.tr(sweat, 'ADBE Opacity'), [[56, 0], [62, 100, 'BRAND'], [118, 100, 'HOLD'], [128, 0, 'EXIT']]);
  O.anim(O.tr(sweat, 'ADBE Position'), [[56, [600, 304]], [128, [602, 346], 'SOFT']]);

  // Tay: khớp ở vai, gõ phím 5 nhịp/giây (hai tay lệch pha).
  var armL = O.shape(C, 'TAY trai', [
    { t: 'path', v: [[402, 508], [360, 612]], closed: false, stroke: 'white', sw: 52, name: 'Tay ao' },
    { t: 'path', v: [[360, 612], [440, 668]], closed: false, stroke: 'blueLight', sw: 42, name: 'Cang tay' }
  ]);
  O.setT(armL, { anchor: [402, 508], pos: [402, 508] });
  O.tr(armL, 'ADBE Rotate Z').expression = 'Math.sin(time * 2 * Math.PI * 5) * 2.4';
  var armR = O.shape(C, 'TAY phai', [
    { t: 'path', v: [[598, 508], [640, 612]], closed: false, stroke: 'white', sw: 52, name: 'Tay ao' },
    { t: 'path', v: [[640, 612], [560, 668]], closed: false, stroke: 'blueLight', sw: 42, name: 'Cang tay' }
  ]);
  O.setT(armR, { anchor: [598, 508], pos: [598, 508] });
  O.tr(armR, 'ADBE Rotate Z').expression = 'Math.sin(time * 2 * Math.PI * 5 + Math.PI) * 2.4';

  O.shape(C, 'LAPTOP', [
    { t: 'rect', size: [366, 14], round: 7, pos: [500, 690], fill: 'blueLight', name: 'De may' },
    { t: 'rect', size: [316, 196], round: 18, pos: [500, 600], fill: 'blueDark', name: 'Mat lung' },
    { t: 'ellipse', size: [28, 28], pos: [500, 598], fill: 'white', name: 'Logo tron' }
  ]);
  O.shape(C, 'BAN', [
    { t: 'rect', size: [26, 120], pos: [96, 776], fill: 'white', name: 'Chan trai' },
    { t: 'rect', size: [26, 120], pos: [904, 776], fill: 'white', name: 'Chan phai' },
    { t: 'rect', size: [944, 32], round: 12, pos: [500, 712], fill: 'white', name: 'Mat ban' }
  ]);
  O.shape(C, 'HOP HANG', [
    { t: 'rect', size: [136, 92], round: 10, pos: [168, 650], fill: 'blueLight', name: 'Hop duoi' },
    { t: 'rect', size: [18, 92], pos: [168, 650], fill: 'blue', name: 'Bang dinh duoi' },
    { t: 'rect', size: [100, 70], round: 10, pos: [176, 569], fill: 'blueLight', name: 'Hop tren' },
    { t: 'rect', size: [16, 70], pos: [176, 569], fill: 'blue', name: 'Bang dinh tren' }
  ]);
  var phone = O.shape(C, 'DIEN THOAI rung', [
    { t: 'rect', size: [70, 122], round: 14, pos: [812, 636], fill: 'black', name: 'Vo' },
    { t: 'rect', size: [56, 100], round: 8, pos: [812, 636], fill: 'blue', name: 'Man hinh' },
    { t: 'ellipse', size: [22, 22], pos: [812, 618], fill: 'white', name: 'Thong bao' },
    { t: 'ellipse', size: [12, 12], pos: [830, 600], fill: 'alert', name: 'Cham do' }
  ]);
  O.setT(phone, { anchor: [812, 696], pos: [812, 696] });
  O.tr(phone, 'ADBE Rotate Z').expression =
    'var f = time * 30, hits = [2, 12, 21, 29, 36, 42, 56, 70, 84, 98, 112], r = 0;\n' +
    'for (var i = 0; i < hits.length; i++) { var d = f - hits[i]; if (d >= 0 && d < 8) r = Math.sin(d * 2.6) * 4 * (1 - d / 8); }\nr';
  return C;
};
