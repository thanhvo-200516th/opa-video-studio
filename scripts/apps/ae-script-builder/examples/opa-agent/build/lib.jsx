// lib.jsx — thư viện dựng After Effects cho video "OPA Agent × Pancake" (ExtendScript ES3).
// Mọi số khung tính ở 30 fps, khung đầu là 0. Toạ độ: comp 1920×1080, gốc trên-trái.
// Công thức chữ R1–R5 và easing lấy từ research/ae-text-audit-2026-10-21/MOTION-PRESETS.json;
// đại lượng pixel đổi theo cỡ chữ (em) để giữ đúng tỉ lệ chuyển động của mẫu.
var OPA = {};
(function (O) {
  O.FPS = 30;
  O.W = 1920;
  O.H = 1080;
  O.report = { texts: [], comps: [], warnings: [], errors: [], measures: [], placements: [] };

  // ---------- Màu thương hiệu (BRAND-SPEC mục 1) ----------
  O.COLORS = {
    blue: [0, 104, 255], blueDark: [0, 60, 153], blueLight: [230, 240, 255],
    black: [10, 10, 10], white: [255, 255, 255], alert: [229, 72, 77]
  };
  O.COLOR_LABEL = { blue: 'Xanh OPA #0068FF', blueDark: 'Xanh dem #003C99', blueLight: 'Xanh nhat #E6F0FF', black: 'Den #0A0A0A', white: 'Trang #FFFFFF', alert: 'Do canh bao #E5484D' };
  O.rgb = function (key) { var c = O.COLORS[key]; if (!c) throw new Error('Mau khong co trong bang thuong hieu: ' + key); return [c[0] / 255, c[1] / 255, c[2] / 255]; };
  O.t = function (frames) { return frames / O.FPS; };

  // ---------- Font ----------
  O.FONT = { head: 'BeVietnamPro-ExtraBold', semi: 'BeVietnamPro-SemiBold', bold: 'BeVietnamPro-Bold', body: 'BeVietnamPro-Medium', accent: 'FrauncesOPA-ExtraBoldItalic' };

  // ---------- Easing ----------
  // Mỗi preset mô tả một đoạn giữa 2 key: o = [hệ số tốc độ, influence %] cho key đầu, i = cho key sau.
  // Tốc độ thực = hệ số × tốc độ trung bình của đoạn. Hệ số 0 = đứng yên ở key.
  O.EASE = {
    R1_IN: { o: [0, 75.2169715011673], i: [0, 75.1205431068497] },
    R1_OUT: { o: [0, 75.1205431068497], i: [0, 75.2169715011673] },
    R2_IN: { o: [0, 75.3224538410263], i: [0, 75.6638871276932] },
    R2_OUT: { o: [0, 75.6638871276932], i: [0, 75.3224538410263] },
    R3_IN: { o: [0, 75.2169715011673], i: [0, 75.6026969993668] },
    R3_OUT: { o: [0, 100], i: [0, 20.9928701961594] },
    R4_IN: { o: [0, 70.6364499176102], i: [0, 70.5400215232925] },
    R4_OUT: { o: [0, 70.0247751319962], i: [0, 70.2989564979629] },
    R5_IN: { o: [0, 60.7521699512558], i: [0, 60.1735817039566] },
    R5_OUT: { o: [0, 60.1735817039566], i: [0, 60.7521699512558] },
    MASK: { o: [0, 15.2362571800308], i: [0, 100] },          // R10: mở khung ảnh — vào nhanh, đuôi dài
    BRAND: { o: [4, 20], i: [0, 80] },                         // EASE_IN_SCENE cubic-bezier(0.2,0.8,0.2,1)
    EXIT: { o: [0, 60], i: [4, 20] },                          // ease ra cảnh cubic-bezier(0.6,0,0.8,0.2)
    SOFT: { o: [0, 50], i: [0, 50] },                          // trôi máy quay chậm
    PUSH: { o: [0, 85], i: [2.2, 30] },                        // máy quay lao vào: tăng tốc tới điểm cắt
    LINEAR: 'LINEAR', HOLD: 'HOLD'
  };

  function dimsOf(v) { return (v instanceof Array) ? v.length : 1; }
  function isFn(x) { return typeof x === 'function'; }

  // Đặt keyframe: keys = [[frame, value], [frame, value, 'PRESET'], ...]; preset ở key k mô tả đoạn (k-1 → k).
  O.anim = function (prop, keys) {
    var i, idx = [];
    for (i = 0; i < keys.length; i++) {
      prop.setValueAtTime(O.t(keys[i][0]), keys[i][1]);
    }
    for (i = 0; i < keys.length; i++) idx.push(prop.nearestKeyIndex(O.t(keys[i][0])));
    var spatial = false;
    try { spatial = prop.isSpatial; } catch (e) { spatial = false; }
    // Số chiều ease lấy từ chính property (Scale của layer 2D vẫn có 3 chiều).
    var nd = spatial ? 1 : dimsOf(prop.value);
    var inE = [], outE = [], inT = [], outT = [];
    for (i = 0; i < keys.length; i++) { inE.push(null); outE.push(null); inT.push(KeyframeInterpolationType.BEZIER); outT.push(KeyframeInterpolationType.BEZIER); }
    for (i = 1; i < keys.length; i++) {
      var pre = keys[i][2] || 'BRAND';
      var P = O.EASE[pre];
      if (P === undefined) throw new Error('Khong co preset ease: ' + pre);
      var dt = O.t(keys[i][0] - keys[i - 1][0]);
      if (P === 'LINEAR') { outT[i - 1] = KeyframeInterpolationType.LINEAR; inT[i] = KeyframeInterpolationType.LINEAR; continue; }
      if (P === 'HOLD') { outT[i - 1] = KeyframeInterpolationType.HOLD; inT[i] = KeyframeInterpolationType.HOLD; continue; }
      var a = keys[i - 1][1], b = keys[i][1], avg = [], d;
      if (spatial) {
        var s = 0; for (d = 0; d < a.length; d++) s += (b[d] - a[d]) * (b[d] - a[d]);
        avg.push(Math.sqrt(s) / dt);
      } else if (a instanceof Array) {
        for (d = 0; d < nd; d++) avg.push((a[d] !== undefined && b[d] !== undefined) ? (b[d] - a[d]) / dt : 0);
      } else avg.push((b - a) / dt);
      var o = [], n = [];
      for (d = 0; d < nd; d++) {
        o.push(new KeyframeEase(P.o[0] * avg[d], Math.max(0.1, P.o[1])));
        n.push(new KeyframeEase(P.i[0] * avg[d], Math.max(0.1, P.i[1])));
      }
      outE[i - 1] = o; inE[i] = n;
    }
    for (i = 0; i < keys.length; i++) {
      var k = idx[i];
      var flat = []; for (var d2 = 0; d2 < nd; d2++) flat.push(new KeyframeEase(0, 33.333333));
      var ie = inE[i] || flat, oe = outE[i] || flat;
      if (inT[i] === KeyframeInterpolationType.BEZIER || outT[i] === KeyframeInterpolationType.BEZIER) {
        try { prop.setTemporalEaseAtKey(k, ie, oe); } catch (e) { O.report.warnings.push('ease ' + prop.name + ' k' + k + ': ' + e); }
      }
      // Đặt kiểu nội suy SAU ease: setTemporalEaseAtKey đổi cả phía LINEAR thành Bezier đứng yên (đo: màn trắng cảnh 2).
      prop.setInterpolationTypeAtKey(k, inT[i], outT[i]);
      if (spatial) {
        try {
          var z = (keys[i][1].length === 3) ? [0, 0, 0] : [0, 0];
          prop.setSpatialAutoBezierAtKey(k, false); prop.setSpatialContinuousAtKey(k, false);
          prop.setSpatialTangentsAtKey(k, z, z);
        } catch (e2) { }
      }
    }
    return prop;
  };

  // ---------- Project ----------
  O.folder = function (name, parent) {
    var f = app.project.items.addFolder(name);
    if (parent) f.parentFolder = parent;
    return f;
  };
  O.comp = function (name, w, h, frames, folder, bgKey) {
    var c = app.project.items.addComp(name, w, h, 1, O.t(frames), O.FPS);
    if (folder) c.parentFolder = folder;
    c.bgColor = O.rgb(bgKey || 'blueDark');
    O.report.comps.push(name);
    return c;
  };
  O.tr = function (layer, mn) { return layer.property('ADBE Transform Group').property(mn); };
  O.setT = function (layer, o) {
    if (o.anchor) O.tr(layer, 'ADBE Anchor Point').setValue(o.anchor);
    if (o.pos) O.tr(layer, 'ADBE Position').setValue(o.pos);
    if (o.scale !== undefined) O.tr(layer, 'ADBE Scale').setValue(o.scale instanceof Array ? o.scale : [o.scale, o.scale]);
    if (o.rot !== undefined) O.tr(layer, 'ADBE Rotate Z').setValue(o.rot);
    if (o.opacity !== undefined) O.tr(layer, 'ADBE Opacity').setValue(o.opacity);
    return layer;
  };
  O.nul = function (comp, name) {
    var n = comp.layers.addNull(comp.duration);
    n.name = name;
    O.setT(n, { anchor: [0, 0], pos: [0, 0] });
    return n;
  };
  // Đặt comp con vào comp cha, gốc trùng gốc (toạ độ đi qua 1:1).
  O.place = function (parent, child, o) {
    o = o || {};
    var L = parent.layers.add(child);
    L.name = o.name || child.name;
    O.setT(L, { anchor: [child.width / 2, child.height / 2], pos: [parent.width / 2, parent.height / 2] });
    if (o.start !== undefined) L.startTime = O.t(o.start);
    if (o.parent) L.parent = o.parent;
    O.report.placements.push({ parent: parent.name, child: child.name, layer: L.name, start: o.start || 0 });
    return L;
  };

  // ---------- CONTROL: bảng màu dùng chung qua expression ----------
  O.makeControl = function (folder) {
    var c = O.comp('CONTROL', 400, 200, 30, folder, 'blueDark');
    c.comment = 'Bang mau thuong hieu. Doi mau o day: moi shape lien ket bang expression se doi theo.';
    var n = c.layers.addNull(c.duration); n.name = 'BRAND';
    var keys = ['blue', 'blueDark', 'blueLight', 'black', 'white', 'alert'];
    for (var i = 0; i < keys.length; i++) {
      var fx = n.property('ADBE Effect Parade').addProperty('ADBE Color Control');
      fx.name = keys[i];
      fx.property(1).setValue(O.rgb(keys[i]));
    }
    O.CONTROL = c;
    return c;
  };
  O.colorExpr = function (key) { return 'comp("CONTROL").layer("BRAND").effect("' + key + '")(1)'; };
  O.linkColor = function (prop, key) {
    prop.setValue(O.rgb(key));
    if (O.CONTROL) prop.expression = O.colorExpr(key);
  };

  // ---------- Shape ----------
  // items: [{t:'rect'|'ellipse'|'path', size, pos, round, v,i,o,closed, fill, fillOp, stroke, sw, cap, join, name, dash:[d,g], rot, anchor, scale}]
  // AE vẽ nhóm ở ĐẦU danh sách lên trên cùng, nên thêm theo thứ tự ngược:
  // phần tử đầu của mảng nằm dưới cùng, phần tử cuối nằm trên cùng (giống thứ tự vẽ thông thường).
  // Tên nhóm phải khác nhau trong một layer vì O.item tìm theo tên.
  O.shape = function (comp, name, items, o) {
    var L = comp.layers.addShape();
    L.name = name;
    O.setT(L, { anchor: [0, 0], pos: [0, 0] });
    for (var k = items.length - 1; k >= 0; k--) O.addItem(L, items[k], k);
    if (o) O.setT(L, o);
    return L;
  };
  O.grp = function (L, key) { return L.property('ADBE Root Vectors Group').property(key); };
  O.addItem = function (L, it, k) {
    var root = L.property('ADBE Root Vectors Group');
    var g = root.addProperty('ADBE Vector Group');
    g.name = it.name || (it.t + ' ' + ((k || 0) + 1));
    var gi = L.property('ADBE Root Vectors Group').numProperties;
    var C = function () { return O.grp(L, gi).property('ADBE Vectors Group'); };
    var s;
    if (it.t === 'rect') {
      s = C().addProperty('ADBE Vector Shape - Rect');
      s.property('ADBE Vector Rect Size').setValue(it.size);
      s.property('ADBE Vector Rect Roundness').setValue(it.round || 0);
    } else if (it.t === 'ellipse') {
      s = C().addProperty('ADBE Vector Shape - Ellipse');
      s.property('ADBE Vector Ellipse Size').setValue(it.size);
    } else if (it.t === 'path') {
      s = C().addProperty('ADBE Vector Shape - Group');
      var sh = new Shape();
      sh.vertices = it.v; sh.inTangents = it.i || zeros(it.v.length); sh.outTangents = it.o || zeros(it.v.length);
      sh.closed = (it.closed !== false);
      s.property('ADBE Vector Shape').setValue(sh);
    }
    if (it.stroke) {
      C().addProperty('ADBE Vector Graphic - Stroke');
      var si = C().numProperties;
      var ST = function () { return C().property(si); };
      O.linkColor(ST().property('ADBE Vector Stroke Color'), it.stroke);
      ST().property('ADBE Vector Stroke Width').setValue(it.sw || 4);
      ST().property('ADBE Vector Stroke Line Cap').setValue(it.cap || 2);
      ST().property('ADBE Vector Stroke Line Join').setValue(it.join || 2);
      if (it.strokeOp !== undefined) ST().property('ADBE Vector Stroke Opacity').setValue(it.strokeOp);
      if (it.dash) {
        ST().property('ADBE Vector Stroke Dashes').addProperty('ADBE Vector Stroke Dash 1');
        ST().property('ADBE Vector Stroke Dashes').property('ADBE Vector Stroke Dash 1').setValue(it.dash[0]);
        ST().property('ADBE Vector Stroke Dashes').addProperty('ADBE Vector Stroke Gap 1');
        ST().property('ADBE Vector Stroke Dashes').property('ADBE Vector Stroke Gap 1').setValue(it.dash[1]);
      }
    }
    if (it.fill) {
      var fl = C().addProperty('ADBE Vector Graphic - Fill');
      O.linkColor(fl.property('ADBE Vector Fill Color'), it.fill);
      if (it.fillOp !== undefined) fl.property('ADBE Vector Fill Opacity').setValue(it.fillOp);
    }
    if (it.trim) {
      var tm = C().addProperty('ADBE Vector Filter - Trim');
      tm.property('ADBE Vector Trim Start').setValue(it.trim[0]);
      tm.property('ADBE Vector Trim End').setValue(it.trim[1]);
    }
    var gt = O.grp(L, gi).property('ADBE Vector Transform Group');
    if (it.anchor) gt.property('ADBE Vector Anchor').setValue(it.anchor);
    gt.property('ADBE Vector Position').setValue(it.pos || [0, 0]);
    if (it.rot) gt.property('ADBE Vector Rotation').setValue(it.rot);
    if (it.scale) gt.property('ADBE Vector Scale').setValue(it.scale);
    if (it.op !== undefined) gt.property('ADBE Vector Group Opacity').setValue(it.op);
    return gi;
  };
  function zeros(n) { var a = []; for (var k = 0; k < n; k++) a.push([0, 0]); return a; }
  O.zeros = zeros;
  // Lấy property của nhóm (theo tên hoặc chỉ số): 'size' | 'pos' | 'scale' | 'rot' | 'op' | 'anchor' | 'trimEnd' | 'trimStart' | 'path'
  O.item = function (L, key, what) {
    var g = O.grp(L, key);
    if (!g) throw new Error('Khong co nhom "' + key + '" trong ' + L.name);
    var C = g.property('ADBE Vectors Group'), T = g.property('ADBE Vector Transform Group');
    if (what === 'pos') return T.property('ADBE Vector Position');
    if (what === 'scale') return T.property('ADBE Vector Scale');
    if (what === 'rot') return T.property('ADBE Vector Rotation');
    if (what === 'op') return T.property('ADBE Vector Group Opacity');
    if (what === 'anchor') return T.property('ADBE Vector Anchor');
    for (var k = 1; k <= C.numProperties; k++) {
      var p = C.property(k), mn = p.matchName;
      if (what === 'size' && mn === 'ADBE Vector Shape - Rect') return p.property('ADBE Vector Rect Size');
      if (what === 'round' && mn === 'ADBE Vector Shape - Rect') return p.property('ADBE Vector Rect Roundness');
      if (what === 'size' && mn === 'ADBE Vector Shape - Ellipse') return p.property('ADBE Vector Ellipse Size');
      if (what === 'trimEnd' && mn === 'ADBE Vector Filter - Trim') return p.property('ADBE Vector Trim End');
      if (what === 'trimStart' && mn === 'ADBE Vector Filter - Trim') return p.property('ADBE Vector Trim Start');
      if (what === 'path' && mn === 'ADBE Vector Shape - Group') return p.property('ADBE Vector Shape');
    }
    throw new Error('Khong tim thay ' + what + ' trong ' + L.name + '#' + key);
  };

  // ---------- Chữ ----------
  // o: {font, size, color, leading, tracking, just:'L'|'C'|'R', name}
  O.text = function (comp, str, o) {
    var L = comp.layers.addText(str);
    L.name = o.name || 'TEXT';
    var tp = L.property('ADBE Text Properties').property('ADBE Text Document');
    var td = tp.value;
    td.resetCharStyle();
    td.resetParagraphStyle();
    td.font = o.font;
    td.fontSize = o.size;
    td.applyFill = true;
    td.fillColor = O.rgb(o.color || 'white');
    td.applyStroke = false;
    td.tracking = o.tracking || 0;
    if (o.leading) { td.autoLeading = false; td.leading = o.leading; }
    td.justification = o.just === 'C' ? ParagraphJustification.CENTER_JUSTIFY : (o.just === 'R' ? ParagraphJustification.RIGHT_JUSTIFY : ParagraphJustification.LEFT_JUSTIFY);
    tp.setValue(td);
    var back = tp.value, sub = null, ps = back.font;
    try { sub = back.fontObject.isSubstitute; ps = back.fontObject.postScriptName; } catch (e) { }
    if (back.font !== o.font || sub === true) O.report.errors.push('FONT ' + L.name + ': can ' + o.font + ', nhan ' + ps + (sub ? ' (font thay the)' : ''));
    O.setT(L, { anchor: [0, 0], pos: o.pos || [0, 0] });
    return L;
  };
  O.rect = function (L, t) { var r = L.sourceRectAtTime(O.t(t || 0), false); return { left: r.left, top: r.top, width: r.width, height: r.height }; };
  // Co chữ cho vừa bề rộng tối đa, không nhỏ hơn minSize (luật ≥ 28 px).
  O.fitWidth = function (L, maxW, minSize) {
    var r = O.rect(L, 0);
    if (r.width <= maxW) return 1;
    var tp = L.property('ADBE Text Properties').property('ADBE Text Document'), td = tp.value;
    var k = maxW / r.width, ns = Math.max(minSize || 28, Math.floor(td.fontSize * k));
    O.report.warnings.push('fitWidth ' + L.name + ': ' + td.fontSize + ' -> ' + ns + ' px');
    if (!td.autoLeading) td.leading = td.leading * ns / td.fontSize;
    td.fontSize = ns; tp.setValue(td);
    return k;
  };
  // Hộp chữ theo toạ độ comp (layer không parent, không scale): vị trí + hộp đo được.
  O.wrect = function (L, t) {
    var r = O.rect(L, t || 0), p = O.tr(L, 'ADBE Position').value;
    return { left: p[0] + r.left, top: p[1] + r.top, width: r.width, height: r.height };
  };
  // Đặt mép trên-trái của khối chữ (theo hộp chữ đo được) vào (x, top); trả hộp theo toạ độ comp.
  O.placeTop = function (L, x, top) {
    var r = O.rect(L, 0);
    O.tr(L, 'ADBE Position').setValue([x - r.left, top - r.top]);
    return O.wrect(L, 0);
  };

  // Công thức Text Animator. em = cỡ chữ; pos/blur nhân em.
  O.RECIPE = {
    R1: { name: 'R1 Headline theo tu', basedOn: 3, pos: [0, 1.0], blur: 0.4267, inE: 'R1_IN', outE: 'R1_OUT' },
    R2: { name: 'R2 Nhan phu theo dong', basedOn: 4, pos: [0, 0.6667], blur: 0.6667, inE: 'R2_IN', outE: 'R2_OUT' },
    R3: { name: 'R3 Display theo ky tu', basedOn: 1, pos: [0, 0.7111], blur: 0.3556, inE: 'R3_IN', outE: 'R3_OUT' },
    R4: { name: 'R4 Heading vao', basedOn: 4, pos: [0, -0.5], blur: 0.5, inE: 'R4_IN', outE: 'R4_OUT' },
    R5: { name: 'R5 Body theo dong tu phai', basedOn: 4, pos: [2.0, 0], blur: 1.0, inE: 'R5_IN', outE: 'R5_OUT' }
  };
  // o: {em, inAt, inDur(30), outAt (null = không rút bằng animator), outDur(30)}; khung là khung cục bộ của comp chứa chữ.
  O.textAnim = function (L, id, o) {
    var R = O.RECIPE[id];
    var animators = function () { return L.property('ADBE Text Properties').property('ADBE Text Animators'); };
    animators().addProperty('ADBE Text Animator');
    var ai = animators().numProperties;
    var A = function () { return animators().property(ai); };
    A().name = R.name;
    var em = o.em;
    A().property('ADBE Text Animator Properties').addProperty('ADBE Text Position 3D').setValue([R.pos[0] * em, R.pos[1] * em, 0]);
    A().property('ADBE Text Animator Properties').addProperty('ADBE Text Opacity').setValue(0);
    A().property('ADBE Text Animator Properties').addProperty('ADBE Text Blur').setValue([R.blur * em, R.blur * em]);
    A().property('ADBE Text Selectors').addProperty('ADBE Text Selector');
    var S = function () { return A().property('ADBE Text Selectors').property(1); };
    // EffectCraft đặt tên nhóm Advanced là advanced / basedOn / shape thay cho matchName của After Effects.
    var adv = S().property('ADBE Text Range Advanced') || S().property('advanced');
    (adv.property('ADBE Text Range Type2') || adv.property('basedOn')).setValue(R.basedOn);
    (adv.property('ADBE Text Range Shape') || adv.property('shape')).setValue(1);
    var inDur = o.inDur || 30, outDur = o.outDur || 30;
    var keys = [[o.inAt, 0], [o.inAt + inDur, 100, R.inE]];
    if (o.outAt !== undefined && o.outAt !== null) keys.push([o.outAt, 100, 'HOLD'], [o.outAt + outDur, 0, R.outE]);
    // Đoạn giữ (100 → 100) để BEZIER phẳng thay vì HOLD nhằm khớp mẫu (mẫu dùng Bézier ở mọi key).
    if (keys.length === 4) keys[2][2] = 'SOFT';
    O.anim(S().property('ADBE Text Percent Start'), keys);
    O.report.texts.push({ layer: L.containingComp.name + '/' + L.name, recipe: id, em: em, inAt: o.inAt, full: o.inAt + inDur, outAt: (o.outAt === undefined ? null : o.outAt), outEnd: (o.outAt === undefined || o.outAt === null) ? null : o.outAt + outDur });
    return A();
  };

  // ---------- Effects ----------
  O.fxColor = function (fx, key) {
    for (var k = 1; k <= fx.numProperties; k++) {
      var p = fx.property(k);
      try { if (p.propertyValueType === PropertyValueType.COLOR) { p.setValue(O.rgb(key)); if (O.CONTROL) p.expression = O.colorExpr(key); return p; } } catch (e) { }
    }
    throw new Error('Effect khong co tham so mau: ' + fx.matchName);
  };

  // Đổi màu effect tại một thời điểm (giây): trước t là màu a, từ t là màu b; cả hai lấy từ CONTROL.
  O.fxColorSwitch = function (fx, a, b, t) {
    for (var k = 1; k <= fx.numProperties; k++) {
      var p = fx.property(k);
      try {
        if (p.propertyValueType === PropertyValueType.COLOR) {
          p.expression = 'var a = ' + O.colorExpr(a) + ', b = ' + O.colorExpr(b) + ';\ntime < ' + t + ' ? a : b';
          return p;
        }
      } catch (e) { }
    }
    throw new Error('Effect khong co tham so mau: ' + fx.matchName);
  };
  // Opacity của layer đi theo layer khác (parent trong AE không truyền opacity).
  O.followOpacity = function (L, src) { O.tr(L, 'ADBE Opacity').expression = 'thisComp.layer("' + src.name + '").transform.opacity'; };
  // Mask chữ nhật trên layer (toạ độ của layer): r = [x0, y0, x1, y1].
  O.rectMask = function (L, r) {
    L.property('ADBE Mask Parade').addProperty('ADBE Mask Atom');
    var m = L.property('ADBE Mask Parade').property(L.property('ADBE Mask Parade').numProperties);
    var s = new Shape();
    s.vertices = [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]];
    s.closed = true;
    m.property('ADBE Mask Shape').setValue(s);
    return m;
  };

  // ---------- Cụm nhấn: font Fraunces + khối "đánh dấu" quét từ trái (luật Minh 09/10, V2 accentMark) ----------
  // title: comp TITLE chứa; txtComp: comp TXT có layer "TEXT" (Fraunces); markKey: màu khối; inkKey: màu chữ trên khối;
  // sweepAt: khung bắt đầu quét (theo khung của title); measureT: giây đo hộp chữ khi chữ đứng yên.
  O.MARK = { sweepF: 8, padL: 0.12, padR: 0.22, top: 0.98, height: 1.26 };
  O.accentBlock = function (title, txtComp, o) {
    var base = O.place(title, txtComp, { name: txtComp.name + ' (nen)', start: o.start || 0 });
    var mark = O.shape(title, 'MARK ' + txtComp.name, [{ t: 'rect', size: [100, 100], pos: [50, 50], fill: o.markKey, name: 'Khoi danh dau' }]);
    var em = o.em, T = o.measureT;
    var ref = 'comp("' + txtComp.name + '").layer("TEXT")';
    var rectExpr = 'var L = ' + ref + '; var r = L.sourceRectAtTime(' + T + ', false); var em = ' + em + ';\n';
    O.item(mark, 1, 'size').expression = rectExpr + '[r.width + ' + (O.MARK.padL + O.MARK.padR) + ' * em, ' + O.MARK.height + ' * em]';
    O.item(mark, 1, 'pos').expression = rectExpr + 'var w = r.width + ' + (O.MARK.padL + O.MARK.padR) + ' * em; [w / 2, ' + O.MARK.height + ' * em / 2]';
    O.tr(mark, 'ADBE Position').expression = rectExpr + 'var p = L.toComp([r.left, 0]); [p[0] - ' + O.MARK.padL + ' * em, p[1] - ' + O.MARK.top + ' * em]';
    var sc = O.tr(mark, 'ADBE Scale');
    O.anim(sc, [[o.sweepAt, [0, 100]], [o.sweepAt + O.MARK.sweepF, [100, 100], 'BRAND']]);
    mark.moveBefore(base);
    var ink = O.place(title, txtComp, { name: txtComp.name + ' (chu tren khoi)', start: o.start || 0 });
    var fill = ink.property('ADBE Effect Parade').addProperty('ADBE Fill');
    O.fxColor(fill, o.inkKey);
    ink.moveBefore(mark);
    ink.setTrackMatte(mark, TrackMatteType.ALPHA);
    mark.enabled = true;  // khối vừa là matte vừa phải hiện
    return { base: base, mark: mark, ink: ink };
  };

  // ---------- Lò xo bật (SPRING_POP: damping 12, stiffness 100, mass 1 → vọt ~9,5 %, đỉnh 0,39 s) ----------
  // Trả về key scale % (đỉnh, đáy, ổn định) tính từ nghiệm lò xo thật.
  O.springKeys = function (at, from, to) {
    var z = 0.6, w0 = 10, wd = 8, keys = [[at, from]];
    var ts = [0.3927, 0.7854, 1.1781], vals = [];
    for (var k = 0; k < ts.length; k++) {
      var t = ts[k], env = Math.exp(-z * w0 * t), y = 1 - env * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
      vals.push(from + (to - from) * y);
    }
    keys.push([at + Math.round(ts[0] * O.FPS), vals[0], 'BRAND']);
    keys.push([at + Math.round(ts[1] * O.FPS), vals[1], 'SOFT']);
    keys.push([at + Math.round(ts[2] * O.FPS) + 4, to, 'SOFT']);
    return keys;
  };
  O.popScale = function (prop, at, peakScale) {
    var k = O.springKeys(at, 0, 100), out = [];
    for (var i = 0; i < k.length; i++) out.push([k[i][0], [k[i][1], k[i][1]], k[i][2]]);
    return O.anim(prop, out);
  };

  // ---------- JSON gọn cho báo cáo ----------
  O.json = function (v) {
    if (v === null || v === undefined) return 'null';
    var t = typeof v;
    if (t === 'string') return '"' + v.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\r/g, '\\r').replace(/\n/g, '\\n') + '"';
    if (t === 'number') return isFinite(v) ? String(Math.round(v * 1000) / 1000) : 'null';
    if (t === 'boolean') return String(v);
    var a = [], k;
    if (v instanceof Array) { for (k = 0; k < v.length; k++) a.push(O.json(v[k])); return '[' + a.join(',') + ']'; }
    for (k in v) if (v.hasOwnProperty(k)) a.push('"' + k + '":' + O.json(v[k]));
    return '{' + a.join(',') + '}';
  };
  O.writeFile = function (path, s) { var f = new File(path); f.encoding = 'UTF-8'; f.open('w'); f.write(s); f.close(); };
})(OPA);
