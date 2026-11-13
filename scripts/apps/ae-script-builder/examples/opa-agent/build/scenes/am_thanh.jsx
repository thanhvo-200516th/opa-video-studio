// Âm thanh: SFX theo từng chuyển động + nhạc nền tự tổng hợp. Bảng cue và mức sinh bởi tools/am_thanh_cues.py
// (build/data/am_thanh_cues.jsxinc): OPA.SFX_CUES = [[file, khung master của ĐỈNH âm, gain dB, tên layer], ...],
// OPA.SFX_PEAK = {file: giây từ đầu file tới đỉnh}, OPA.MUSIC = {file, gain}. Bảng đọc được: audio/BANG-CUE-AM-THANH.md.
// Kho SFX: D:\Vibe Coding\Motion Claude\sfx (CC0/MIT, không theSOUNDS), chép WAV vào assets/sfx; logo âm thanh của bộ OPA.
// Giọng đọc chưa có: nhạc nền −31 LUFS (15 LU dưới giọng −16 LUFS), mọi SFX dưới giọng ≥ 8 LU.
OPA.buildAudio = function (ctx, sfxDir) {
  var O = OPA, F = ctx.F;
  var A = O.comp('AM_THANH_SFX_NHAC', 1920, 1080, 1080, F.audio, 'blueDark');
  A.comment = 'SFX theo chuyen dong + nhac nen tu tong hop (chua co giong doc). Moi layer SFX dat theo dinh am trung khoanh khac hinh. Sua cue: tools/am_thanh_cues.py roi dung lai.';
  var cache = {}, list = [];
  var load = function (path) {
    if (!cache[path]) {
      var file = new File(path);
      if (!file.exists) { O.report.errors.push('Thieu file am ' + file.fsName); return null; }
      var it = app.project.importFile(new ImportOptions(file));
      it.parentFolder = F.audio;
      cache[path] = it;
    }
    return cache[path];
  };
  var level = function (L, db) { L.property('ADBE Audio Group').property('ADBE Audio Levels').setValue([db, db]); };
  // Nhạc nền thêm trước nên nằm dưới cùng.
  var mus = load(sfxDir + '/../music/' + O.MUSIC.file);
  if (mus) {
    var M = A.layers.add(mus);
    M.name = 'NHAC NEN (tu tong hop, 120 BPM, giong La)';
    M.startTime = 0;
    level(M, O.MUSIC.gain);
    O.report.music = { file: O.MUSIC.file, gain: O.MUSIC.gain };
  }
  for (var i = 0; i < O.SFX_CUES.length; i++) {
    var c = O.SFX_CUES[i], it = load(sfxDir + '/' + c[0]);
    if (!it) continue;
    var L = A.layers.add(it);
    L.name = c[3];
    L.startTime = O.t(c[1]) - O.SFX_PEAK[c[0]];
    level(L, c[2]);
    list.push([c[3], c[1], c[2]]);
  }
  O.report.sfx = list;
  return A;
};
