// main.jsx — dựng project "OPA Agent × Pancake" (16:9, 1920×1080, 30 fps, 36 s).
// Chạy trong phiên AE headless riêng do tools/ae.py mở; OPA_ARGS = {target, report, scenes}.
// Project đích là bản sao của project trống (tools/seed) vì phiên headless chỉ lưu được đè lên file đã mở.
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
      edit: O.folder('03_EDIT_CHU (sua chu o day)'), art: O.folder('04_HINH (nhan vat, giao dien, mascot)'),
      control: O.folder('05_CONTROL (mau)'), audio: O.folder('06_AM_THANH')
    };
    O.makeControl(F.control);
    var ctx = { F: F, art: {} };
    ctx.art.ownerBusy = O.buildOwnerBusy(ctx);
    ctx.art.ownerRelax = O.buildOwnerRelax(ctx);
    ctx.art.mascot = O.buildMascot(ctx);

    var M = O.comp('OPA_AGENT_MASTER_16x9', 1920, 1080, 1080, F.master, 'blueDark');
    M.comment = 'Master 36 s. Moc canh: S1 0-5 s, S2 5-13,5 s, S3 13,5-22 s, S4 22-30 s, S5 30-36 s (Minh chot doi moc 2->3 sang 13,5 s).';
    var plan = [['S1', 0, O.buildS1]];
    if (O.buildS2) plan.push(['S2', 150, O.buildS2]);
    if (O.buildS3) plan.push(['S3', 405, O.buildS3]);
    if (O.buildS4) plan.push(['S4', 660, O.buildS4]);
    if (O.buildS5) plan.push(['S5', 900, O.buildS5]);
    var placed = [];
    for (var i = 0; i < plan.length; i++) {
      var sc = plan[i][2](ctx);
      var L = M.layers.add(sc);
      L.startTime = O.t(plan[i][1]);
      O.report.placements.push({ parent: M.name, child: sc.name, layer: L.name, start: plan[i][1] });
      placed.push(L);
    }
    // Lớp xếp sau cùng nằm dưới: cảnh sau nằm trên cảnh trước để chuyển cảnh phủ lên.
    for (i = 1; i < placed.length; i++) placed[i].moveBefore(placed[i - 1]);
    M.motionBlur = true;
    if (O.buildAudio && A.sfx) {
      var au = M.layers.add(O.buildAudio(ctx, A.sfx));
      au.name = 'AM THANH: SFX + nhac nen';
    }
    // Giọng đọc của Minh (VOICE/1023.MP3, chép WAV 48 kHz): đặt từ 0 s, gain để giọng ở −16,3 LUFS khi phát.
    if (O.VOICE && A.sfx) {
      var vf = new File(A.sfx + '/../voice/' + O.VOICE.file);
      if (!vf.exists) throw new Error('Thieu file giong doc ' + vf.fsName);
      var vi = app.project.importFile(new ImportOptions(vf));
      vi.parentFolder = F.audio;
      var vl = M.layers.add(vi);
      vl.name = 'GIONG DOC (1023.MP3 cua ban)';
      vl.startTime = 0;
      vl.property('ADBE Audio Group').property('ADBE Audio Levels').setValue([O.VOICE.gain, O.VOICE.gain]);
      rep.voice = { file: O.VOICE.file, gain: O.VOICE.gain };
    }

    // Marker câu thoại: mốc bắt đầu đo trên giọng đọc 1023.MP3 (năng lượng sau khoảng nghỉ), lời theo kịch bản khóa.
    var vo = [
      [0.10, 'Cau 1: Ban mat bao nhieu thoi gian moi ngay de tra loi tin nhan va len don cho khach tren Pancake?'],
      [4.38, 'Cau 2: Hay thu tuong tuong ban quan ly nhieu trang ban hang... thi se met moi nhu the nao?'],
      [14.09, 'Cau 3: Gio day, chi voi mot lan ket noi... voi OPA Agent!'],
      [22.62, 'Cau 4: Ban khong can phai tao App Facebook... de tao don thu cong nua.'],
      [30.33, 'Cau 5: OPA Agent - OPA lo phan tra loi, shop lo phan ban! Trai nghiem mien phi ngay tai Oping (giong doc).']
    ];
    var guide = M.layers.addNull(M.duration);
    guide.name = 'MARKER CAU THOAI (moc do tren giong doc)';
    guide.guideLayer = true;
    guide.enabled = false;
    for (i = 0; i < vo.length; i++) guide.property('ADBE Marker').setValueAtTime(vo[i][0], new MarkerValue(vo[i][1]));

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
        var L = it.layer(l);
        if (!(L instanceof TextLayer)) continue;
        var td = L.property('ADBE Text Properties').property('ADBE Text Document').value, sub = null;
        try { sub = td.fontObject.isSubstitute; } catch (e) { }
        out.push({ comp: it.name, layer: L.name, text: td.text, font: td.font, size: td.fontSize, substitute: sub });
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
