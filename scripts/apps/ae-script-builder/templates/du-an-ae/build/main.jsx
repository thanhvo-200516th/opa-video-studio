// main.jsx — dựng project mẫu (16:9, 1920×1080, 30 fps, 5 s). Chạy trong phiên AE headless riêng do tools/ae.py mở.
// OPA_ARGS = {target, report, sfx}. Project đích là bản sao của seed trống (phiên headless chỉ lưu được đè lên file đã mở).
// Thêm cảnh: viết OPA.buildSx trong build/scenes/*.jsx rồi thêm một dòng vào plan (khung bắt đầu trên master).
(function () {
  var O = OPA, A = OPA_ARGS, rep = O.report, t0 = new Date().getTime();
  rep.args = A;
  try {
    if (app.project && (app.project.file || app.project.numItems)) throw new Error('GUARD: phien AE nay dang mo project khac, dung lai.');
    app.beginSuppressDialogs();
    var p = app.open(new File(A.target));
    if (!p || p.numItems !== 0) throw new Error('Project dich phai la ban sao trong cua seed.');
    p.bitsPerChannel = 8;
    try { p.expressionEngine = 'javascript-1.0'; } catch (e0) { rep.warnings.push('expressionEngine: ' + e0); }

    var F = {
      master: O.folder('00_MASTER'), scenes: O.folder('01_CANH (scene)'), titles: O.folder('02_TITLE (thiet ke chu)'),
      edit: O.folder('03_EDIT_CHU (sua chu o day)'), art: O.folder('04_HINH'), control: O.folder('05_CONTROL (mau)'),
      audio: O.folder('06_AM_THANH')
    };
    O.makeControl(F.control);
    var ctx = { F: F };

    var M = O.comp('MASTER_16x9', 1920, 1080, 150, F.master, 'blueDark');
    M.comment = 'Master mau 5 s. Them canh: viet OPA.buildSx trong build/scenes roi them vao plan trong main.jsx.';
    var plan = [['S1', 0, O.buildS1]];
    var placed = [];
    for (var i = 0; i < plan.length; i++) {
      var sc = plan[i][2](ctx);
      var L = M.layers.add(sc);
      L.startTime = O.t(plan[i][1]);
      rep.placements.push({ parent: M.name, child: sc.name, layer: L.name, start: plan[i][1] });
      placed.push(L);
    }
    // Cảnh sau nằm trên cảnh trước để chuyển cảnh phủ lên.
    for (i = 1; i < placed.length; i++) placed[i].moveBefore(placed[i - 1]);
    M.motionBlur = true;

    // QA: buộc tính mọi expression rồi gom lỗi; xuất mọi layer chữ (nội dung, font, cỡ) cho tools/qa_chu.py.
    rep.expressionErrors = scanExpressions();
    rep.textDump = dumpTexts();
    p.save();
    rep.saved = p.file ? p.file.fsName : null;
  } catch (e) {
    rep.errors.push('BUILD: ' + e.toString() + ' (dong ' + e.line + ')');
  }
  try { app.endSuppressDialogs(false); } catch (e2) { }
  rep.seconds = (new Date().getTime() - t0) / 1000;
  O.writeFile(A.report, O.json(rep));

  function dumpTexts() {
    var out = [];
    for (var c = 1; c <= app.project.numItems; c++) {
      var it = app.project.item(c);
      if (!(it instanceof CompItem)) continue;
      for (var l = 1; l <= it.numLayers; l++) {
        var Ly = it.layer(l);
        if (!(Ly instanceof TextLayer)) continue;
        var td = Ly.property('ADBE Text Properties').property('ADBE Text Document').value, sub = null;
        try { sub = td.fontObject.isSubstitute; } catch (e) { }
        out.push({ comp: it.name, layer: Ly.name, text: td.text, font: td.font, size: td.fontSize, substitute: sub });
      }
    }
    return out;
  }

  function scanExpressions() {
    var errs = [], n = 0;
    function walk(prop, path, comp) {
      for (var k = 1; k <= prop.numProperties; k++) {
        var q = prop.property(k);
        if (q.propertyType === PropertyType.PROPERTY) {
          if (q.canSetExpression && q.expression !== '') {
            n++;
            try { q.valueAtTime(comp.duration / 2, false); } catch (e) { }
            if (q.expressionError) errs.push(comp.name + ' > ' + path + '/' + q.name + ': ' + q.expressionError);
          }
        } else walk(q, path + '/' + q.name, comp);
      }
    }
    for (var c = 1; c <= app.project.numItems; c++) {
      var it = app.project.item(c);
      if (!(it instanceof CompItem)) continue;
      for (var l = 1; l <= it.numLayers; l++) walk(it.layer(l), it.layer(l).name, it);
    }
    rep.expressionCount = n;
    return errs;
  }
})();
