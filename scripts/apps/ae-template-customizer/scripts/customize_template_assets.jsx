// Reusable ExtendScript: Customize .aep Template (2D/3D Characters, Portraits, Logos, Colors, Vietnamese Text & Range Selectors)
(function () {
    app.beginSuppressDialogs();
    try {
        // 1. Ensure Template 5 project is open
        var projFile = new File("F:/video AE/template intro/video edit teamplate/template 5.aep");
        var hasFinal4k = false;
        for (var i = 1; i <= app.project.numItems; i++) {
            if (app.project.item(i) instanceof CompItem && app.project.item(i).name === "Final_4k (3840 x 2160)") {
                hasFinal4k = true;
                break;
            }
        }
        if (!hasFinal4k && projFile.exists) {
            app.open(projFile);
        }

        function findComp(name) {
            for (var i = 1; i <= app.project.numItems; i++) {
                var it = app.project.item(i);
                if (it instanceof CompItem && it.name === name) return it;
            }
            return null;
        }

        function findOrCreateFolder(name) {
            for (var i = 1; i <= app.project.numItems; i++) {
                var it = app.project.item(i);
                if (it instanceof FolderItem && it.name === name) return it;
            }
            return app.project.items.addFolder(name);
        }

        var opaFolder = findOrCreateFolder("00. OPA Assets & Footage (Minh Hoa)");

        function importAsset(pathStr, loopCount) {
            var f = new File(pathStr);
            if (!f.exists) return null;
            for (var i = 1; i <= app.project.numItems; i++) {
                var it = app.project.item(i);
                if (it instanceof FootageItem && it.file && it.file.fsName === f.fsName) {
                    if (loopCount && loopCount > 1 && it.mainSource) {
                        try { it.mainSource.loop = loopCount; } catch (e) {}
                    }
                    return it;
                }
            }
            var io = new ImportOptions(f);
            var imported = app.project.importFile(io);
            imported.parentFolder = opaFolder;
            if (loopCount && loopCount > 1 && imported.mainSource) {
                try { imported.mainSource.loop = loopCount; } catch (e) {}
            }
            return imported;
        }

        var assetDir = "F:/video AE/template intro/video edit teamplate/OPA_T5_Assets/";
        var ftLogoPng = importAsset(assetDir + "OPA_Logo_Hub_1000.png", 1);
        var ftLogoMp4 = importAsset(assetDir + "OPA_Logo_Hub_Anim.mp4", 5);
        var ftAv01 = importAsset(assetDir + "Avatar01_Customer.png", 1);
        var ftAv02 = importAsset(assetDir + "Avatar02_OPA_AI.png", 1);
        var ftCardPOS = importAsset(assetDir + "OPA_UI_Card_PancakePOS.png", 1);
        var ftCardBill = importAsset(assetDir + "OPA_UI_Card_CheckBill.png", 1);
        var ftDashMp4 = importAsset(assetDir + "OPA_Pancake_POS_Sync.mp4", 5);
        var ftWordmarkWhite = importAsset("F:/video AE/OPA-Guide-3-Templates/Assets/OPA-white-1500x500.png", 1);
        var ftBgm = importAsset("F:/THÀNH V/atlasaudio-upbeat-corporate-617614.mp3", 2);

        var ftPersons = [];
        for (var p = 1; p <= 8; p++) {
            var pName = "Person_0" + p + ".png";
            ftPersons.push(importAsset(assetDir + pName, 1));
        }

        // 2. Populate Logo_Holder (3D Mascot / Brand Hub)
        var logoHolder = findComp("Logo_Holder");
        if (logoHolder) {
            logoHolder.duration = 10.0;
            while (logoHolder.numLayers > 0) {
                logoHolder.layer(1).remove();
            }
            if (ftLogoPng) {
                var lPng = logoHolder.layers.add(ftLogoPng);
                lPng.property("Position").setValue([500, 500]);
                lPng.property("Scale").setValue([100, 100]);
                lPng.outPoint = 10.0;
            }
            if (ftLogoMp4) {
                var lMp4 = logoHolder.layers.add(ftLogoMp4);
                lMp4.property("Position").setValue([500, 500]);
                lMp4.property("Scale").setValue([100, 100]);
                lMp4.outPoint = 10.0;
            }
        }

        // 3. Populate 01_Person_Holder .. 08_Person_Holder (3D Character Portraits)
        for (var idx = 1; idx <= 8; idx++) {
            var hName = "0" + idx + "_Person_Holder";
            var hComp = findComp(hName);
            var ftP = ftPersons[idx - 1];
            if (hComp && ftP) {
                hComp.duration = 10.0;
                while (hComp.numLayers > 0) {
                    hComp.layer(1).remove();
                }
                var lp = hComp.layers.add(ftP);
                lp.property("Position").setValue([500, 500]);
                lp.property("Scale").setValue([100, 100]);
                lp.outPoint = 10.0;
            }
            var pCompName = "0" + idx + "_Person";
            var pComp = findComp(pCompName);
            if (pComp) {
                pComp.duration = 10.0;
                for (var li = 1; li <= pComp.numLayers; li++) {
                    pComp.layer(li).outPoint = 10.0;
                }
            }
        }

        // 4. Populate 06_Scene_Avatar01 & 06_Scene_Avatar02
        function populateScene06Avatar(compName, footageItem) {
            var c = findComp(compName);
            if (!c || !footageItem) return;
            c.duration = 10.0;
            for (var i = c.numLayers; i >= 1; i--) {
                if (c.layer(i).name !== "Background") {
                    c.layer(i).remove();
                } else {
                    c.layer(i).outPoint = 10.0;
                }
            }
            var avL = c.layers.add(footageItem);
            avL.moveToBeginning();
            avL.property("Position").setValue([500, 500]);
            avL.property("Scale").setValue([100, 100]);
            avL.outPoint = 10.0;
        }
        populateScene06Avatar("06_Scene_Avatar01", ftAv01);
        populateScene06Avatar("06_Scene_Avatar02", ftAv02);

        // 5. Populate Music_Holder & enable in Final_4k
        var musicHolder = findComp("Music_Holder");
        if (musicHolder && ftBgm) {
            while (musicHolder.numLayers > 0) {
                musicHolder.layer(1).remove();
            }
            var mLayer = musicHolder.layers.add(ftBgm);
            mLayer.audioEnabled = true;
            mLayer.outPoint = musicHolder.duration;
        }

        // 6. Update Master Color Controllers in Final_4k (3840 x 2160)
        var finalComp = findComp("Final_4k (3840 x 2160)");
        if (finalComp) {
            var tcLayer = finalComp.layer("Text Colors");
            if (tcLayer) {
                tcLayer.effect("Titles_Color")("Color").setValue([1.0, 1.0, 1.0, 1.0]);
                tcLayer.effect("Sub-Titles_Color_01")("Color").setValue([0.0, 0.88, 1.0, 1.0]);
                tcLayer.effect("Sub-Titles_Color_02")("Color").setValue([0.05, 0.52, 1.0, 1.0]);
            }
            var bgcLayer = finalComp.layer("Background Colors");
            if (bgcLayer) {
                bgcLayer.effect("BG_Color_01")("Color").setValue([0.02, 0.07, 0.18, 1.0]);
                bgcLayer.effect("BG_Color_02")("Color").setValue([0.015, 0.05, 0.14, 1.0]);
                bgcLayer.effect("BG_Color_03")("Color").setValue([0.0, 0.24, 0.55, 1.0]);
                bgcLayer.effect("BG_Color_04")("Color").setValue([0.01, 0.03, 0.09, 1.0]);
            }
            var uicLayer = finalComp.layer("Icons, Buttons & UI Colors");
            if (uicLayer) {
                uicLayer.effect("Icons_Color")("Color").setValue([0.0, 0.88, 1.0, 1.0]);
                uicLayer.effect("BG_Icons_Color")("Color").setValue([0.03, 0.16, 0.38, 1.0]);
                uicLayer.effect("BG_Avatars_Color")("Color").setValue([0.04, 0.15, 0.35, 1.0]);
                uicLayer.effect("Buttons_Color")("Color").setValue([0.02, 0.16, 0.42, 1.0]);
                uicLayer.effect("Edge_Color_01")("Color").setValue([0.0, 0.90, 1.0, 1.0]);
                uicLayer.effect("Edge_Color_02")("Color").setValue([0.0, 0.41, 1.0, 1.0]);
                uicLayer.effect("Buttons_Glow_Color_01")("Color").setValue([0.0, 0.83, 1.0, 1.0]);
                uicLayer.effect("Buttons_Glow_Color_02")("Color").setValue([0.0, 0.35, 0.95, 1.0]);
                uicLayer.effect("Passive_Buttons_Color")("Color").setValue([0.05, 0.12, 0.26, 1.0]);
            }
            var mhLayer = finalComp.layer("Music_Holder");
            if (mhLayer) {
                mhLayer.enabled = true;
                mhLayer.audioEnabled = true;
            }
        }

        // 7. Helper to update Text Layer safely while preserving layer.name (so expressions never break)
        function setLayerText(compName, layerIndex, newText, fontName, fontSize, trackingVal) {
            var c = findComp(compName);
            if (!c || layerIndex > c.numLayers) return;
            var l = c.layer(layerIndex);
            var origName = l.name;
            var prop = l.property("ADBE Text Properties") ? l.property("ADBE Text Properties").property("ADBE Text Document") : l.property("Source Text");
            if (!prop) return;
            var td = prop.value;
            td.text = newText;
            if (fontName) {
                try { td.font = fontName; } catch (e) {}
            }
            if (fontSize) {
                try { td.fontSize = fontSize; } catch (e) {}
            }
            if (trackingVal !== undefined && trackingVal !== null) {
                try { td.tracking = trackingVal; } catch (e) {}
            }
            prop.setValue(td);
            l.name = origName;
        }

        // Helper to speed up per-word Text Animator so multi-word Vietnamese phrases illuminate 100% cleanly
        function fixTextAnimator(compName, startSec, endSec) {
            var c = findComp(compName);
            if (!c || c.numLayers < 1) return;
            var l = c.layer(1);
            var tp = l.property("ADBE Text Properties");
            if (!tp) return;
            var anims = tp.property("ADBE Text Animators");
            if (!anims) return;
            for (var a = 1; a <= anims.numProperties; a++) {
                var anim = anims.property(a);
                var sels = anim.property("ADBE Text Selectors");
                if (!sels) continue;
                for (var s = 1; s <= sels.numProperties; s++) {
                    var sel = sels.property(s);
                    var adv = sel.property("ADBE Text Range Advanced");
                    if (adv) {
                        var maxEase = adv.property("ADBE Text Levels Max Ease");
                        if (maxEase) {
                            try { maxEase.setValue(0); } catch (e) {}
                        }
                    }
                    var pStart = sel.property("ADBE Text Percent Start");
                    if (pStart) {
                        try {
                            while (pStart.numKeys > 0) {
                                pStart.removeKey(1);
                            }
                            pStart.setValueAtTime(startSec, 0);
                            pStart.setValueAtTime(endSec, 100);
                        } catch (e) {}
                    }
                }
            }
        }

        var fBold = "BeVietnamPro-Bold";
        var fExtra = "BeVietnamPro-ExtraBold";
        var fBlack = "BeVietnamPro-Black";
        var fSemi = "BeVietnamPro-SemiBold";
        var fMed = "BeVietnamPro-Medium";

        setLayerText("01_Scene_Text01", 1, "Hàng trăm khách nhắn tin mỗi ngày", fBold, 130, 0);
        setLayerText("01_Scene_Text02", 1, "là mỏ vàng doanh thu", fExtra, 150, 0);
        fixTextAnimator("01_Scene_Text02", 0.20, 1.05);

        setLayerText("03_Scene_Text01", 1, "Nhưng trả lời chậm chỉ 5 phút", fBold, 134, 0);
        setLayerText("03_Scene_Text02", 1, "là mất đơn vào tay đối thủ", fExtra, 138, 0);
        fixTextAnimator("03_Scene_Text02", 0.20, 1.05);

        setLayerText("04_Scene_Text", 1, "Inbox quá tải — Bỏ lỡ khách mua", fBold, 132, 0);

        setLayerText("05_Scene_Text01", 1, "Giải pháp đột phá từ", fBold, 140, 0);
        setLayerText("05_Scene_Text02", 1, "OPA AGENT", fBlack, 265, 20);
        setLayerText("05_Scene_Text03", 1, "AI Bán Hàng Cho Shop Dùng Pancake", fSemi, 58, 0);

        setLayerText("06_Scene_Title01", 1, "Tự trả lời khách theo tồn kho", fBold, 132, 0);
        setLayerText("06_Scene_Title02", 1, "Chốt đơn & Xác minh bill tự động", fBold, 126, 0);
        setLayerText("06_Scene_Text05", 1, "Nhắn tin cho OPA Agent — Đồng bộ Pancake POS...", fMed, 56, 0);

        setLayerText("07_Scene_Title", 1, "Chăm sóc hàng ngàn khách 24/7", fBold, 128, 0);

        setLayerText("08_Scene_Text01", 1, "Thiết lập chỉ trong 5 phút", fBold, 140, 0);
        setLayerText("08_Scene_Text02", 1, "Kết nối thẳng qua Pancake", fExtra, 138, 0);
        fixTextAnimator("08_Scene_Text02", 0.20, 1.05);

        setLayerText("09_Scene_Text01", 1, "Chế độ phản hồi thông minh", fBold, 138, 0);
        setLayerText("09_Scene_Text02", 1, "AI tự tư vấn & lên đơn POS", fSemi, 60, 0);
        setLayerText("09_Scene_Text03", 1, "Nhân viên tiếp quản tức thì", fSemi, 60, 0);

        setLayerText("10_Scene_Text01", 1, "Tùy chỉnh giọng điệu của shop", fBold, 134, 0);
        setLayerText("10_Scene_Text02", 1, "Chuyên nghiệp", fSemi, 66, 0);
        setLayerText("10_Scene_Text03", 1, "Thân thiện", fBold, 72, 0);
        setLayerText("10_Scene_Text04", 1, "Ngắn gọn", fSemi, 72, 0);

        setLayerText("11_Scene_Text01", 1, "Đồng bộ trực tiếp với", fBold, 142, 0);
        setLayerText("11_Scene_Text02", 1, "tồn kho Pancake POS", fExtra, 140, 0);
        setLayerText("11_Scene_Text03", 1, "bảng giá & chính sách shop", fExtra, 130, 0);
        setLayerText("11_Scene_Text04", 1, "xác minh bill chuyển khoản", fExtra, 130, 0);
        fixTextAnimator("11_Scene_Text02", 0.0, 0.45);
        fixTextAnimator("11_Scene_Text03", 0.0, 0.45);
        fixTextAnimator("11_Scene_Text04", 0.0, 0.45);

        setLayerText("13_Scene_Text01", 1, "Bứt phá doanh số tự động cùng", fBold, 130, 0);
        setLayerText("13_Scene_Text02", 1, "OPA AGENT", fBlack, 265, 20);
        setLayerText("13_Scene_Text03", 1, "chat.overpowers.agency", fBold, 102, 5);

        app.project.save(projFile);
    } catch (err) {
    } finally {
        app.endSuppressDialogs(false);
    }
})();
