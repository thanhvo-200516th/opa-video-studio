// ec_build.js — runs inside EffectCraft through `script.run` (After Effects-style JavaScript).
// ec_build.py prepends `var MODE = "probe" | "build" | "dump"; var ARGS = {...};` and reads back the JSON
// string this script evaluates to. All decisions (timing, keys, effect parameters, fonts) are made in
// Python; this file only executes the plan and reads the project back.
(function () {
  var TR = { anchor: "ADBE Anchor Point", position: "ADBE Position", scale: "ADBE Scale",
             rotation: "ADBE Rotate Z", opacity: "ADBE Opacity" };
  var KIT = KeyframeInterpolationType;
  var SIDE = { linear: KIT.LINEAR, ease: KIT.BEZIER, hold: KIT.HOLD };
  var EASE_INFLUENCE = 33.333;   // After Effects "Easy Ease"
  var BLEND = { normal: BlendingMode.NORMAL, screen: BlendingMode.SCREEN, multiply: BlendingMode.MULTIPLY,
                add: BlendingMode.ADD, overlay: BlendingMode.OVERLAY };
  var JUST = { left: ParagraphJustification.LEFT_JUSTIFY, center: ParagraphJustification.CENTER_JUSTIFY,
               right: ParagraphJustification.RIGHT_JUSTIFY };
  var notes = [];

  function allItems() {
    var a = [];
    for (var i = 1; i <= app.project.numItems; i++) a.push(app.project.item(i));
    return a;
  }
  function itemById(id) {
    var hit = allItems().filter(function (it) { return it.id === id; })[0];
    if (!hit) throw new Error("no project item with id " + id);
    return hit;
  }

  // ---------- probe: import every source once, report what the app sees ----------
  function probe() {
    var out = {};
    ARGS.media.forEach(function (path) {
      var it = app.project.importFile(new ImportOptions(new File(path)));
      out[path] = { id: it.id, duration: it.duration, width: it.width, height: it.height,
                    hasVideo: !!it.hasVideo, hasAudio: !!it.hasAudio,
                    still: !!(it.mainSource && it.mainSource.isStill) };
    });
    return out;
  }

  // ---------- build ----------
  function easeArray(dims, side) {
    var a = [];
    for (var d = 0; d < dims; d++) a.push(new KeyframeEase(0, side === "ease" ? EASE_INFLUENCE : 16.667));
    return a;
  }
  function setKeys(prop, keys) {
    keys.forEach(function (k) { prop.setValueAtTime(k.t, k.v); });
    var dims = prop.isSpatial ? 1 : (prop.value instanceof Array ? prop.value.length : 1);
    keys.forEach(function (k) {
      var i = prop.nearestKeyIndex(k.t);
      if (k["in"] === "ease" || k.out === "ease") prop.setTemporalEaseAtKey(i, easeArray(dims, k["in"]), easeArray(dims, k.out));
      // the type goes last: setting an ease turns a linear side into Bezier
      prop.setInterpolationTypeAtKey(i, SIDE[k["in"]], SIDE[k.out]);
    });
  }
  function setProp(prop, p) {
    if (p.keys) setKeys(prop, p.keys); else prop.setValue(p.value);
  }
  function layerProp(layer, path) {
    if (path === "levels") return layer.property("ADBE Audio Group").property("ADBE Audio Levels");
    return layer.property("ADBE Transform Group").property(TR[path]);
  }
  function leaves(group, acc) {
    for (var k = 1; k <= group.numProperties; k++) {
      var p = group.property(k);
      if (p.propertyType === PropertyType.PROPERTY) acc.push(p); else leaves(p, acc);
    }
    return acc;
  }
  function addEffect(layer, fx) {
    var e = layer.property("ADBE Effect Parade").addProperty(fx.ec);
    var params = leaves(e, []);
    fx.params.forEach(function (p) {
      var prop = params[p.index - 1];
      if (!prop || prop.name !== p.name) {
        throw new Error(fx.ec + " parameter #" + p.index + " is " + (prop ? prop.name : "missing") + ", expected " + p.name);
      }
      setProp(prop, p);
    });
  }
  function addMask(layer, m) {
    var atom = layer.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    var s = new Shape();
    s.vertices = m.vertices; s.inTangents = m.inTangents; s.outTangents = m.outTangents; s.closed = true;
    atom.property("ADBE Mask Shape").setValue(s);
    atom.name = m.name;
  }
  function makeText(comp, t) {
    var layer = comp.layers.addText(t.str);
    var tp = layer.property("ADBE Text Properties").property("ADBE Text Document");
    var td = tp.value;
    td.font = t.font; td.fontStyle = t.style; td.fontSize = t.size;
    td.applyFill = true; td.fillColor = t.fill;
    td.applyStroke = !!t.stroke;
    if (t.stroke) { td.strokeColor = t.stroke.color; td.strokeWidth = t.stroke.width; td.strokeOverFill = false; }
    td.justification = JUST[t.align];
    td.tracking = t.tracking;
    if (t.leading) { td.autoLeading = false; td.leading = t.leading; }
    tp.setValue(td);
    if (t.maxWidth) fitWidth(layer, tp, t);
    return layer;
  }
  function fitWidth(layer, tp, t) {
    var w = layer.sourceRectAtTime(0, false).width;
    if (w <= t.maxWidth) return;
    var td = tp.value;
    td.fontSize = Math.max(Math.floor(t.size * t.maxWidth / w), Math.round(t.size / 2));
    tp.setValue(td);
    notes.push(t.str.replace(/\r/g, " ") + ": caption " + Math.round(w) + " px wide, font size " + t.size + " -> " + td.fontSize);
  }
  function buildLayer(comp, L) {
    var layer = L.kind === "text" ? makeText(comp, L.text) : comp.layers.add(itemById(L.item));
    layer.name = L.name;
    layer.comment = L.comment;
    layer.label = L.label;
    if (L.stretch !== 100) layer.stretch = L.stretch;
    layer.startTime = L.start;
    layer.inPoint = L["in"];
    layer.outPoint = L.out;
    if (L.video === false) layer.enabled = false;
    if (L.audio === false && layer.hasAudio) layer.audioEnabled = false;
    if (L.blend) layer.blendingMode = BLEND[L.blend];
    L.masks.forEach(function (m) { addMask(layer, m); });
    L.props.forEach(function (p) { setProp(layerProp(layer, p.path), p); });
    L.effects.forEach(function (fx) { addEffect(layer, fx); });
  }
  function build() {
    var C = ARGS.comp;
    var comp = app.project.items.addComp(C.name, C.width, C.height, 1, C.duration, C.fps);
    ARGS.layers.forEach(function (L) {
      try { buildLayer(comp, L); } catch (e) { throw new Error("layer '" + L.name + "': " + e.message); }
    });
    ARGS.markers.forEach(function (m) { comp.markerProperty.setValueAtTime(m.time, new MarkerValue(m.comment)); });
    comp.openInViewer();
    return { comp: comp.id, layers: comp.numLayers, notes: notes };
  }

  // ---------- dump: read the (re-opened) project back, in the shape ec_build.py compares (times in frames) ----------
  function dumpLayer(L, fps) {
    var fr = function (t) { return Math.floor(t * fps + 0.5); };
    var frames = function (p) { var a = []; for (var k = 1; k <= p.numKeys; k++) a.push(fr(p.keyTime(k))); return a; };
    var isText = L instanceof TextLayer, keys = {}, effects = [], effectKeys = [], gain = null;
    for (var path in TR) if (layerProp(L, path).numKeys) keys[path] = frames(layerProp(L, path));
    var sound = !isText && L.hasAudio && L.audioEnabled;
    if (!isText && L.hasAudio) {
      var lv = layerProp(L, "levels");
      if (lv.numKeys) keys.levels = frames(lv); else if (sound) gain = Math.round(lv.value[0] * 100) / 100;
    }
    var fxs = L.property("ADBE Effect Parade");
    for (var i = 1; i <= fxs.numProperties; i++) {
      var n = 0;
      leaves(fxs.property(i), []).forEach(function (p) { n += p.numKeys; });
      effects.push(fxs.property(i).name);
      effectKeys.push(n);
    }
    var masks = L.property("ADBE Mask Parade");
    var td = isText ? L.property("ADBE Text Properties").property("ADBE Text Document").value : null;
    return { index: L.index, name: L.name, caption: L.comment.indexOf("captions ") === 0,
             kind: isText ? "text" : (L.source.hasVideo && L.enabled ? "footage" : "audio"),
             "in": fr(L.inPoint), out: fr(L.outPoint), start: fr(L.startTime), keys: keys, effect_keys: effectKeys,
             effects: effects, masks: masks ? masks.numProperties : 0, sound: !!sound, gain: gain,
             src: !isText && L.source.file ? L.source.file.fsName : null,
             text: td ? [td.text, td.font, td.fontStyle] : null };
  }
  function dump() {
    var comps = allItems().filter(function (it) { return it instanceof CompItem; });
    var comp = comps.filter(function (c) { return c.name === ARGS.comp; })[0];
    if (!comp) throw new Error("no composition named '" + ARGS.comp + "' in the project");
    var res = { comps: comps.length, layers: [], markers: [],
                comp: { name: comp.name, width: comp.width, height: comp.height, fps: comp.frameRate,
                        duration: comp.duration } };
    for (var i = 1; i <= comp.numLayers; i++) res.layers.push(dumpLayer(comp.layer(i), comp.frameRate));
    var mk = comp.markerProperty;
    for (var k = 1; k <= mk.numKeys; k++) res.markers.push({ time: mk.keyTime(k), comment: mk.keyValue(k).comment });
    return res;
  }

  var run = { probe: probe, build: build, dump: dump }[MODE];
  if (!run) throw new Error("unknown MODE " + MODE);
  return JSON.stringify(run());
})();
