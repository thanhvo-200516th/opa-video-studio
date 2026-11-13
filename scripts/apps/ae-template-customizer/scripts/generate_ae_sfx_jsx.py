import json
import os
import sys

DEFAULT_JSON = r"/media/vmiz/Over Powers/video AE/template intro/video edit teamplate/OPA_T5_Assets/SFX_Pro/resolved_sfx_cues.json"
DEFAULT_JSX = r"/media/vmiz/Over Powers/add_sfx_t5.jsx"

json_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JSON
jsx_out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_JSX

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

files_map = data["files"]
cues = data["cues"]


def js_str(s):
    return json.dumps(s, ensure_ascii=True)


jsx_lines = []
jsx_lines.append("""// Auto-generated ExtendScript: Frame-Accurate High-Tech SFX Injection (-6 dB to -9.5 dB)
(function() {
    app.beginSuppressDialogs();
    var logLines = [];
    function log(msg) { logLines.push(msg); }

    try {
        var projPath = "F:/video AE/template intro/video edit teamplate/template 5.aep";
        var copyPath = "F:/video AE/template intro/template gi\\u1ea3i n\\u00e9n/template 5/OPA_Agent_Promo_2026.aep";
        var projFile = new File(projPath);

        if (!app.project || !app.project.file || app.project.file.fsName.toLowerCase().indexOf("template 5.aep") === -1) {
            if (projFile.exists) {
                app.open(projFile);
                log("Opened project: " + projFile.fsName);
            } else {
                throw new Error("Project file not found: " + projPath);
            }
        } else {
            log("Using already-open project: " + app.project.file.fsName);
        }

        var proj = app.project;

        function findComp(name) {
            for (var i = 1; i <= proj.numItems; i++) {
                var it = proj.item(i);
                if (it instanceof CompItem && it.name === name) return it;
            }
            return null;
        }

        function findFolder(name) {
            for (var i = 1; i <= proj.numItems; i++) {
                var it = proj.item(i);
                if (it instanceof FolderItem && it.name === name) return it;
            }
            return null;
        }

        // 1. Clean up previous SFX Master Comp and Folder if re-running
        var oldMaster = findComp("00_OPA_SFX_Master");
        if (oldMaster) {
            oldMaster.remove();
            log("Removed old 00_OPA_SFX_Master comp");
        }
        var oldFolder = findFolder("OPA_SFX_48kHz");
        if (oldFolder) {
            oldFolder.remove();
            log("Removed old OPA_SFX_48kHz folder");
        }

        // Remove any old [SFX ...] layers inside 01_Scene .. 13_Scene
        for (var sIdx = 1; sIdx <= 13; sIdx++) {
            var sName = (sIdx < 10 ? "0" + sIdx : "" + sIdx) + "_Scene";
            var sComp = findComp(sName);
            if (sComp) {
                for (var l = sComp.numLayers; l >= 1; l--) {
                    var lyr = sComp.layer(l);
                    if (lyr.name.indexOf("[SFX") === 0) {
                        lyr.remove();
                    }
                }
            }
        }

        // 2. Create OPA_SFX_48kHz folder and import all WAV files
        var sfxFolder = proj.items.addFolder("OPA_SFX_48kHz");
        var footageMap = {};
        var wavList = [
""")

for rel_path, info in sorted(files_map.items()):
    jsx_lines.append(f'            {{ key: {js_str(rel_path)}, name: {js_str(info["wav_name"])}, path: {js_str(info["wav_path"])} }},')

jsx_lines.append("""        ];

        for (var w = 0; w < wavList.length; w++) {
            var wf = new File(wavList[w].path);
            if (!wf.exists) {
                throw new Error("Missing WAV file: " + wavList[w].path);
            }
            var io = new ImportOptions(wf);
            var ftg = proj.importFile(io);
            ftg.name = wavList[w].name;
            ftg.parentFolder = sfxFolder;
            footageMap[wavList[w].key] = ftg;
        }
        log("Imported " + wavList.length + " WAV files (48kHz 24-bit) into OPA_SFX_48kHz");

        // 3. Cue definitions
        var cues = [
""")

for c in cues:
    jsx_lines.append(
        f'            {{ idx: {c["idx"]}, scene: {js_str(c["scene"])}, cueSec: {c["cue_sec"]}, frame: {c["frame"]}, '
        f'startSec: {c["start_sec"]}, localCueSec: {c["local_cue_sec"]}, localStartSec: {c["local_start_sec"]}, '
        f'cat: {js_str(c["cat"])}, label: {c["label_color"]}, name: {js_str(c["name"])}, key: {js_str(c["rel_path"])}, '
        f'gainDb: {c["gain_db"]}, rationale: {js_str(c["rationale"])} }},'
    )

jsx_lines.append("""        ];

        function pad3(n) {
            if (n < 10) return "00" + n;
            if (n < 100) return "0" + n;
            return "" + n;
        }

        function setAudioGain(layer, dbVal) {
            try {
                var audGrp = layer.property("ADBE Audio Group");
                if (audGrp) {
                    var lvl = audGrp.property("ADBE Audio Levels");
                    if (lvl) lvl.setValue([dbVal, dbVal]);
                }
            } catch (e) {}
        }

        // 4. Create 00_OPA_SFX_Master comp (3840x2160, 30fps, 55.50s)
        var masterComp = proj.items.addComp("00_OPA_SFX_Master", 3840, 2160, 1.0, 55.50, 30);
        for (var i = cues.length - 1; i >= 0; i--) {
            var c = cues[i];
            var ftg = footageMap[c.key];
            if (!ftg) continue;
            var lyr = masterComp.layers.add(ftg);
            lyr.audioEnabled = true;
            lyr.startTime = c.startSec;
            var secStr = c.cueSec.toFixed(2);
            if (c.cueSec < 10) secStr = "0" + secStr;
            lyr.name = "[#" + pad3(c.idx) + " " + c.scene.substring(0, 3) + " " + secStr + "s] " + c.name;
            lyr.label = c.label;
            lyr.comment = c.rationale + " | Gain: " + c.gainDb + " dB";
            setAudioGain(lyr, c.gainDb);

            try {
                var mk = new MarkerValue(c.name);
                lyr.property("ADBE Marker").setValueAtTime(c.cueSec, mk);
            } catch (eMk) {}
        }
        log("Created 00_OPA_SFX_Master with " + masterComp.numLayers + " peak-aligned SFX layers");

        // 5. Add scene-local SFX layers inside each 01_Scene .. 13_Scene comp
        var sceneCounts = {};
        for (var j = 0; j < cues.length; j++) {
            var sc = cues[j];
            var sComp = findComp(sc.scene);
            if (!sComp) continue;
            var ftg2 = footageMap[sc.key];
            if (!ftg2) continue;
            var sLyr = sComp.layers.add(ftg2);
            sLyr.moveToEnd();
            sLyr.audioEnabled = true;
            sLyr.startTime = sc.localStartSec;
            var lSecStr = sc.localCueSec.toFixed(2);
            if (sc.localCueSec < 10) lSecStr = "0" + lSecStr;
            sLyr.name = "[SFX " + lSecStr + "s] " + sc.name;
            sLyr.label = sc.label;
            sLyr.comment = sc.rationale + " | Global: " + sc.cueSec.toFixed(2) + "s (f" + sc.frame + ") | Gain: " + sc.gainDb + " dB";
            setAudioGain(sLyr, sc.gainDb);
            sceneCounts[sc.scene] = (sceneCounts[sc.scene] || 0) + 1;
        }
        for (var k in sceneCounts) {
            log("Scene " + k + ": added " + sceneCounts[k] + " local SFX layers");
        }

        // 6. Adjust BGM in Music_Holder to -8.0 dB so music leads and high-tech SFX blend smoothly underneath
        var musicComp = findComp("Music_Holder");
        if (musicComp && musicComp.numLayers >= 1) {
            for (var m = 1; m <= musicComp.numLayers; m++) {
                var mLyr = musicComp.layer(m);
                if (mLyr.hasAudio) {
                    setAudioGain(mLyr, -8.0);
                    log("Balanced BGM layer '" + mLyr.name + "' in Music_Holder to -8.0 dB");
                }
            }
        }

        // 7. Wire 00_OPA_SFX_Master into Final_4k (3840 x 2160) and Full_HD (1920 x 1080)
        var targetFinals = ["Final_4k (3840 x 2160)", "Full_HD (1920 x 1080)"];
        var sceneMarkers = [
            { t: 0.03,  txt: "S01: Hook & Color Flash" },
            { t: 3.03,  txt: "S02: Multi-Channel Hub Burst" },
            { t: 6.43,  txt: "S03: Pain 1 - 5m Delay" },
            { t: 9.13,  txt: "S04: Inbox Overload Counter" },
            { t: 12.13, txt: "S05: OPA Agent Hero Reveal" },
            { t: 15.20, txt: "S06A: Live Chat - Stock Check" },
            { t: 21.65, txt: "S06B: Auto Bill & Order #PK8921" },
            { t: 26.90, txt: "S07: 24/7 Multi-Chat Wall" },
            { t: 31.37, txt: "S08: 5-Minute Pancake Setup" },
            { t: 34.13, txt: "S09: Smart Mode Click & Glow" },
            { t: 38.47, txt: "S10: Shop Tone Click & Glow" },
            { t: 42.70, txt: "S11: 3x POS Slot-Machine Sync" },
            { t: 47.47, txt: "S12: AI Network & Sparkle Stars" },
            { t: 50.70, txt: "S13: Finale & OPA Sonic Logo" }
        ];

        for (var fIdx = 0; fIdx < targetFinals.length; fIdx++) {
            var fComp = findComp(targetFinals[fIdx]);
            if (!fComp) continue;

            for (var fl = fComp.numLayers; fl >= 1; fl--) {
                if (fComp.layer(fl).name === "00_OPA_SFX_Master") {
                    fComp.layer(fl).remove();
                }
            }

            // Mute audio on 01_Scene .. 13_Scene instances inside Final comp so they don't double-play with 00_OPA_SFX_Master
            for (var sl = 1; sl <= fComp.numLayers; sl++) {
                var subLyr = fComp.layer(sl);
                if (subLyr.name.indexOf("_Scene") !== -1) {
                    try { subLyr.audioEnabled = false; } catch (eAud) {}
                }
                if (subLyr.name === "Music_Holder") {
                    try { subLyr.audioEnabled = true; } catch (eMus) {}
                }
            }

            var masterLyr = fComp.layers.add(masterComp);
            masterLyr.moveToBeginning();
            masterLyr.audioEnabled = true;
            masterLyr.label = 14; // Cyan
            masterLyr.comment = "Master Peak-Aligned High-Tech SFX Track (-6.0 to -9.5 dB)";

            var mkProp = masterLyr.property("ADBE Marker");
            if (mkProp) {
                for (var sm = 0; sm < sceneMarkers.length; sm++) {
                    var mv = new MarkerValue(sceneMarkers[sm].txt);
                    mkProp.setValueAtTime(sceneMarkers[sm].t, mv);
                }
            }
            log("Wired 00_OPA_SFX_Master + 14 timeline markers into " + fComp.name);
        }

        var final4k = findComp("Final_4k (3840 x 2160)");
        if (final4k) {
            final4k.openInViewer();
        }

        // 8. Save project to both primary and extracted template locations
        proj.save(projFile);
        log("Saved primary project: " + projFile.fsName);

        var copyFile = new File(copyPath);
        if (copyFile.parent && copyFile.parent.exists) {
            proj.save(copyFile);
            log("Saved backup copy: " + copyFile.fsName);
            proj.save(projFile);
        }

        log("SUCCESS: All " + cues.length + " high-tech SFX cues injected and saved!");
    } catch (err) {
        log("ERROR: " + err.toString() + " (line " + err.line + ")");
    }

    app.endSuppressDialogs(false);

    var repFile = new File("C:/Users/Public/OPA-AE-20261021/SFX_INJECT_REPORT.txt");
    repFile.encoding = "UTF-8";
    repFile.open("w");
    for (var r = 0; r < logLines.length; r++) {
        repFile.writeln(logLines[r]);
    }
    repFile.close();
})();
""")

with open(jsx_out_path, "w", encoding="utf-8-sig") as f:
    f.write("\n".join(jsx_lines))

print(f"Generated {jsx_out_path} with ASCII-safe Unicode escapes and UTF-8 BOM")
