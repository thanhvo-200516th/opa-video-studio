/**
 * ============================================================================
 * FUTURISTIC HI-TECH LOGO REVEAL (A7XZTEC / VideoHive 22388914 Style)
 * Automated After Effects Template Generator (ExtendScript .jsx)
 * 100% Native After Effects - No Third-Party Plugins Required
 * ============================================================================
 * Cách chạy thủ công trong After Effects:
 *   Vào menu File -> Scripts -> Run Script File... -> Chọn file .jsx này.
 * ============================================================================
 */

(function createFuturisticHiTechTemplate() {
    if (!app.project) {
        app.newProject();
    }

    app.beginUndoGroup("Create Futuristic Hi-Tech Logo Reveal (A7XZTEC)");

    try {
        var proj = app.project;
        var W = 1920;
        var H = 1080;
        var FPS = 30;
        var DUR = 12.0; // Chuẩn 12 giây theo template A7XZTEC gốc

        // --------------------------------------------------------------------
        // HELPER FUNCTIONS (Chống lỗi "Object is invalid" của AE Shape Layer)
        // --------------------------------------------------------------------
        function setClassic3D(comp) {
            try {
                comp.renderer = "ADBE Classic 3d";
            } catch (e) {}
        }

        function applyEaseInOut(prop, speedIn, influenceIn, speedOut, influenceOut) {
            try {
                var easeIn = new KeyframeEase(speedIn || 0, influenceIn || 75);
                var easeOut = new KeyframeEase(speedOut || 0, influenceOut || 75);
                var dim = 1;
                if (prop.propertyValueType === PropertyValueType.TwoD_SPATIAL ||
                    prop.propertyValueType === PropertyValueType.ThreeD_SPATIAL) {
                    dim = 1;
                } else if (prop.propertyValueType === PropertyValueType.TwoD) {
                    dim = 2;
                } else if (prop.propertyValueType === PropertyValueType.ThreeD) {
                    dim = 3;
                }
                var inArr = [];
                var outArr = [];
                for (var d = 0; d < dim; d++) {
                    inArr.push(easeIn);
                    outArr.push(easeOut);
                }
                for (var k = 1; k <= prop.numKeys; k++) {
                    prop.setTemporalEaseAtKey(k, inArr, outArr);
                }
            } catch (e) {}
        }

        function addGlow(layer, radius, intensity, threshold) {
            try {
                var fx = layer.property("ADBE Effect Parade").addProperty("ADBE Glow2");
                if (fx) {
                    try { fx.property(2).setValue(threshold !== undefined ? threshold : 50); } catch (e) {}
                    try { fx.property(3).setValue(radius !== undefined ? radius : 35); } catch (e) {}
                    try { fx.property(4).setValue(intensity !== undefined ? intensity : 1.4); } catch (e) {}
                }
                return fx;
            } catch (e) {
                return null;
            }
        }

        function getRootVecs(shapeLayer) {
            return shapeLayer.property("ADBE Root Vectors Group");
        }

        function getGrpVecs(shapeLayer, grpIndex) {
            return shapeLayer.property("ADBE Root Vectors Group").property(grpIndex).property("ADBE Vectors Group");
        }

        function addPolygonGroup(shapeLayer, name, points, outerRadius, rotation, strokeColor, strokeWidth, strokeOpacity, dashVal, gapVal) {
            var root = getRootVecs(shapeLayer);
            var grpIdx = root.numProperties + 1;
            var grp = root.addProperty("ADBE Vector Group");
            grp.name = name;

            var star = getGrpVecs(shapeLayer, grpIdx).addProperty("ADBE Vector Shape - Star");
            try { star.property("ADBE Vector Star Type").setValue(2); } catch (e) {} // 2 = Polygon
            try { star.property("ADBE Vector Star Points").setValue(points); } catch (e) {}
            try { star.property("ADBE Vector Star Outer Radius").setValue(outerRadius); } catch (e) {}
            try { star.property("ADBE Vector Star Outer Roundness").setValue(0); } catch (e) {}
            try { star.property("ADBE Vector Star Rotation").setValue(rotation || 0); } catch (e) {}

            var stroke = getGrpVecs(shapeLayer, grpIdx).addProperty("ADBE Vector Graphic - Stroke");
            try { stroke.property("ADBE Vector Stroke Color").setValue(strokeColor); } catch (e) {}
            try { stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth); } catch (e) {}
            try { stroke.property("ADBE Vector Stroke Opacity").setValue(strokeOpacity !== undefined ? strokeOpacity : 100); } catch (e) {}
            try { stroke.property("ADBE Vector Stroke Line Cap").setValue(2); } catch (e) {} // Round Cap

            if (dashVal && dashVal > 0) {
                try {
                    var d1 = getGrpVecs(shapeLayer, grpIdx)
                        .property("ADBE Vector Graphic - Stroke")
                        .property("ADBE Vector Stroke Dashes")
                        .addProperty("ADBE Vector Stroke Dash 1");
                    d1.setValue(dashVal);
                    if (gapVal && gapVal > 0) {
                        var g1 = getGrpVecs(shapeLayer, grpIdx)
                            .property("ADBE Vector Graphic - Stroke")
                            .property("ADBE Vector Stroke Dashes")
                            .addProperty("ADBE Vector Stroke Gap 1");
                        g1.setValue(gapVal);
                    }
                } catch (e) {}
            }
            return grpIdx;
        }

        function addCircleGroup(shapeLayer, name, diameter, strokeColor, strokeWidth, strokeOpacity, dashVal, gapVal) {
            var root = getRootVecs(shapeLayer);
            var grpIdx = root.numProperties + 1;
            var grp = root.addProperty("ADBE Vector Group");
            grp.name = name;

            var ell = getGrpVecs(shapeLayer, grpIdx).addProperty("ADBE Vector Shape - Ellipse");
            try { ell.property("ADBE Vector Ellipse Size").setValue([diameter, diameter]); } catch (e) {}

            var stroke = getGrpVecs(shapeLayer, grpIdx).addProperty("ADBE Vector Graphic - Stroke");
            try { stroke.property("ADBE Vector Stroke Color").setValue(strokeColor); } catch (e) {}
            try { stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth); } catch (e) {}
            try { stroke.property("ADBE Vector Stroke Opacity").setValue(strokeOpacity !== undefined ? strokeOpacity : 100); } catch (e) {}
            try { stroke.property("ADBE Vector Stroke Line Cap").setValue(1); } catch (e) {} // Butt Cap

            if (dashVal && dashVal > 0) {
                try {
                    var d1 = getGrpVecs(shapeLayer, grpIdx)
                        .property("ADBE Vector Graphic - Stroke")
                        .property("ADBE Vector Stroke Dashes")
                        .addProperty("ADBE Vector Stroke Dash 1");
                    d1.setValue(dashVal);
                    if (gapVal && gapVal > 0) {
                        var g1 = getGrpVecs(shapeLayer, grpIdx)
                            .property("ADBE Vector Graphic - Stroke")
                            .property("ADBE Vector Stroke Dashes")
                            .addProperty("ADBE Vector Stroke Gap 1");
                        g1.setValue(gapVal);
                    }
                } catch (e) {}
            }
            return grpIdx;
        }

        function configureTrim(trimProp, startT0, startV0, startT1, startV1, endT0, endV0, endT1, endV1, offsetDeg) {
            try {
                var sProp = trimProp.property("ADBE Vector Trim Start");
                var eProp = trimProp.property("ADBE Vector Trim End");
                var oProp = trimProp.property("ADBE Vector Trim Offset");
                if (startT1 !== null && startT1 !== undefined) {
                    sProp.setValueAtTime(startT0, startV0);
                    sProp.setValueAtTime(startT1, startV1);
                    applyEaseInOut(sProp, 0, 75, 0, 75);
                } else {
                    sProp.setValue(startV0);
                }
                if (endT1 !== null && endT1 !== undefined) {
                    eProp.setValueAtTime(endT0, endV0);
                    eProp.setValueAtTime(endT1, endV1);
                    applyEaseInOut(eProp, 0, 75, 0, 75);
                } else {
                    eProp.setValue(endV0);
                }
                if (offsetDeg !== undefined && offsetDeg !== null) {
                    oProp.setValue(offsetDeg);
                }
            } catch (e) {}
        }

        function addRootTrimPaths(shapeLayer, startT0, startV0, startT1, startV1, endT0, endV0, endT1, endV1, offsetDeg) {
            var trim = getRootVecs(shapeLayer).addProperty("ADBE Vector Filter - Trim");
            configureTrim(trim, startT0, startV0, startT1, startV1, endT0, endV0, endT1, endV1, offsetDeg);
        }

        function addGroupTrimPaths(shapeLayer, grpIdx, startT0, startV0, startT1, startV1, endT0, endV0, endT1, endV1, offsetDeg) {
            var trim = getGrpVecs(shapeLayer, grpIdx).addProperty("ADBE Vector Filter - Trim");
            configureTrim(trim, startT0, startV0, startT1, startV1, endT0, endV0, endT1, endV1, offsetDeg);
        }

        // --------------------------------------------------------------------
        // 1. TẠO CẤU TRÚC THƯ MỤC CHUẨN VIDEOHIVE / ENVATO
        // --------------------------------------------------------------------
        var rootFolder = proj.items.addFolder("A7XZTEC - Futuristic Hi-Tech Logo Reveal");
        var editFolder = proj.items.addFolder("01. EDIT HERE (Thay Logo & Text)");
        var precompFolder = proj.items.addFolder("02. PRECOMPS (System)");
        var renderFolder = proj.items.addFolder("03. FINAL RENDER");
        var assetsFolder = proj.items.addFolder("04. ASSETS & SOLIDS");

        editFolder.parentFolder = rootFolder;
        precompFolder.parentFolder = rootFolder;
        renderFolder.parentFolder = rootFolder;
        assetsFolder.parentFolder = rootFolder;

        // Màu sắc chủ đạo chuẩn template A7XZTEC
        var CYAN_BRIGHT = [0.15, 0.85, 1.0];    // #26D9FF
        var CYAN_DEEP   = [0.02, 0.48, 0.85];   // #057AD9
        var CYAN_PALE   = [0.65, 0.95, 1.0];    // #A6F2FF
        var HOLO_GREEN  = [0.55, 0.88, 0.18];   // #8CE02E (Màu hologram xanh lục-cyan giống video gốc)

        // --------------------------------------------------------------------
        // 2. COMP 01: LOGO PLACEHOLDER (1000x1000)
        // --------------------------------------------------------------------
        var logoComp = proj.items.addComp("01. LOGO PLACEHOLDER (Drop Logo Here)", 1000, 1000, 1.0, DUR, FPS);
        logoComp.parentFolder = editFolder;

        // Tự động tìm & import Logoweb.png nếu có sẵn trong thư mục của bạn
        var importedLogoItem = null;
        var candidatePaths = [
            "f:/TH\u00C0NH V/intro logo/Logoweb.png",
            "f:/TH\u00C0NH V/intro logo/OPA-intro-assets/Logoweb.png",
            // EffectCraft trên Linux: ổ F là USB "Over Powers"
            "/media/vmiz/Over Powers/TH\u00C0NH V/intro logo/Logoweb.png",
            "/media/vmiz/Over Powers/TH\u00C0NH V/intro logo/OPA-intro-assets/Logoweb.png"
        ];
        for (var p = 0; p < candidatePaths.length; p++) {
            var lf = new File(candidatePaths[p]);
            if (lf.exists) {
                try {
                    var io = new ImportOptions(lf);
                    importedLogoItem = proj.importFile(io);
                    importedLogoItem.parentFolder = assetsFolder;
                    break;
                } catch (e) {}
            }
        }

        if (importedLogoItem) {
            var logoLayer = logoComp.layers.add(importedLogoItem);
            var lw = importedLogoItem.width || 1000;
            var lh = importedLogoItem.height || 1000;
            var targetSize = 560;
            var scaleFactor = (targetSize / Math.max(lw, lh)) * 100;
            scaleFactor = Math.min(scaleFactor * 1.45, 100);
            logoLayer.property("ADBE Transform Group").property("ADBE Scale").setValue([scaleFactor, scaleFactor, 100]);
        } else {
            // Tạo Logo Vector mặc định nếu không tìm thấy file ảnh
            var defaultLogoShape = logoComp.layers.addShape();
            defaultLogoShape.name = "Default Emblem Logo (Hide when adding your logo)";
            addPolygonGroup(defaultLogoShape, "Outer Shield", 6, 180, 0, HOLO_GREEN, 16, 100, 0, 0);
            var defaultTxt = logoComp.layers.addText("OPA");
            var td = defaultTxt.property("ADBE Text Properties").property("ADBE Text Document").value;
            td.fontSize = 140;
            td.fillColor = HOLO_GREEN;
            td.justification = ParagraphJustification.CENTER_JUSTIFY;
            defaultTxt.property("ADBE Text Properties").property("ADBE Text Document").setValue(td);
            defaultTxt.property("ADBE Transform Group").property("ADBE Position").setValue([500, 545]);
        }

        // --------------------------------------------------------------------
        // 3. COMP 02: TAGLINE / WEBSITE PLACEHOLDER (1920x300)
        // --------------------------------------------------------------------
        var textComp = proj.items.addComp("02. TAGLINE PLACEHOLDER (Edit Text)", W, 300, 1.0, DUR, FPS);
        textComp.parentFolder = editFolder;

        var taglineLayer = textComp.layers.addText("w w w . y o u r b r a n d . c o m");
        taglineLayer.name = "Tagline / Website URL";
        try {
            var tDocProp = taglineLayer.property("ADBE Text Properties").property("ADBE Text Document");
            var tDoc = tDocProp.value;
            tDoc.fontSize = 26;
            tDoc.fillColor = [0.88, 0.94, 1.0];
            tDoc.tracking = 240;
            try { tDoc.font = "ArialMT"; } catch (e) {}
            tDoc.justification = ParagraphJustification.CENTER_JUSTIFY;
            tDocProp.setValue(tDoc);
        } catch (e) {}
        taglineLayer.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, 160]);

        // --------------------------------------------------------------------
        // 4. PRECOMP 01: DIGITAL MATRIX FLOOR (2200x2200)
        // --------------------------------------------------------------------
        var matrixComp = proj.items.addComp("Precomp_01_Digital_Matrix_Floor", 2200, 2200, 1.0, DUR, FPS);
        matrixComp.parentFolder = precompFolder;

        // 4a. Lưới vi mạch cơ sở (Grid)
        var gridSolid = matrixComp.layers.addSolid([0.05, 0.35, 0.55], "Cyber_Grid_Lines", 2200, 2200, 1.0, DUR);
        gridSolid.source.parentFolder = assetsFolder;
        try {
            var gridFx = gridSolid.property("ADBE Effect Parade").addProperty("ADBE Grid");
            gridFx.property("ADBE Grid-0001").setValue([0, 0]);
            gridFx.property("ADBE Grid-0002").setValue(2); // Width & Height Sliders
            gridFx.property("ADBE Grid-0003").setValue(110);
            gridFx.property("ADBE Grid-0004").setValue(110);
            gridFx.property("ADBE Grid-0005").setValue(1.0); // Border
            gridFx.property("ADBE Grid-0007").setValue(CYAN_DEEP);
            gridFx.property("ADBE Grid-0008").setValue(18);  // Opacity
        } catch (e) {}
        gridSolid.property("ADBE Transform Group").property("ADBE Opacity").setValue(28);

        // 4b. Các cụm điểm dữ liệu (Dot-Matrix Clusters & Circuit Traces)
        var matrixShapes = matrixComp.layers.addShape();
        matrixShapes.name = "Data_Clusters_And_Circuits";

        addCircleGroup(matrixShapes, "Floor_Dot_Ring_Outer", 1650, CYAN_DEEP, 14, 35, 2, 12);
        addCircleGroup(matrixShapes, "Floor_Dot_Ring_Mid",   1350, CYAN_BRIGHT, 6, 40, 3, 18);
        addCircleGroup(matrixShapes, "Floor_Dot_Ring_Inner",  960, CYAN_DEEP, 22, 25, 2, 10);

        // Đường mạch điện (Circuit Lines) chạy dọc ngang trên sàn
        for (var c = 0; c < 8; c++) {
            var angle = (c * 45) * Math.PI / 180;
            var r1 = 520;
            var r2 = 1020;
            var cIdx = getRootVecs(matrixShapes).numProperties + 1;
            var cGrp = getRootVecs(matrixShapes).addProperty("ADBE Vector Group");
            cGrp.name = "Circuit_Ray_" + (c + 1);

            var pGrp = getGrpVecs(matrixShapes, cIdx).addProperty("ADBE Vector Shape - Group");
            var sh = new Shape();
            sh.vertices = [
                [Math.cos(angle) * r1, Math.sin(angle) * r1],
                [Math.cos(angle) * r2, Math.sin(angle) * r2]
            ];
            sh.closed = false;
            pGrp.property("ADBE Vector Shape").setValue(sh);

            var cSt = getGrpVecs(matrixShapes, cIdx).addProperty("ADBE Vector Graphic - Stroke");
            cSt.property("ADBE Vector Stroke Color").setValue(CYAN_BRIGHT);
            cSt.property("ADBE Vector Stroke Width").setValue(2);
            cSt.property("ADBE Vector Stroke Opacity").setValue(45);
            try {
                getGrpVecs(matrixShapes, cIdx)
                    .property("ADBE Vector Graphic - Stroke")
                    .property("ADBE Vector Stroke Dashes")
                    .addProperty("ADBE Vector Stroke Dash 1").setValue(4);
                getGrpVecs(matrixShapes, cIdx)
                    .property("ADBE Vector Graphic - Stroke")
                    .property("ADBE Vector Stroke Dashes")
                    .addProperty("ADBE Vector Stroke Gap 1").setValue(14);
            } catch (e) {}
            addGroupTrimPaths(matrixShapes, cIdx, 0, 0, null, null, 0.0, 0, 2.5, 100, c * 15);
        }

        var mOp = matrixShapes.property("ADBE Transform Group").property("ADBE Opacity");
        mOp.setValueAtTime(0.0, 0);
        mOp.setValueAtTime(1.0, 75);
        mOp.setValueAtTime(5.2, 75);
        mOp.setValueAtTime(6.6, 0);

        // 4c. Các chữ số kỹ thuật nhỏ (HUD Telemetry Readouts: 010 / SYS_INIT)
        var coords = [
            [-620, -420, "010 // SYS.HEX"],
            [ 620, -420, "88.42 // SYNC"],
            [-640,  420, "010110 // MATRIX"],
            [ 640,  420, "CORE // ACTIVE"]
        ];
        for (var idx = 0; idx < coords.length; idx++) {
            var hudTxt = matrixComp.layers.addText(coords[idx][2]);
            hudTxt.name = "HUD_Data_Label_" + (idx + 1);
            try {
                var hDocP = hudTxt.property("ADBE Text Properties").property("ADBE Text Document");
                var hDoc = hDocP.value;
                hDoc.fontSize = 18;
                hDoc.fillColor = CYAN_BRIGHT;
                hDoc.tracking = 120;
                hDocP.setValue(hDoc);
            } catch (e) {}
            hudTxt.property("ADBE Transform Group").property("ADBE Position").setValue([1100 + coords[idx][0], 1100 + coords[idx][1]]);
            var hOp = hudTxt.property("ADBE Transform Group").property("ADBE Opacity");
            hOp.setValueAtTime(0.4, 0);
            hOp.setValueAtTime(1.2, 45);
            hOp.setValueAtTime(5.2, 45);
            hOp.setValueAtTime(6.4, 0);
        }

        // --------------------------------------------------------------------
        // 5. PRECOMP 02: LOGO HOLOGRAM WIREFRAME (Auto-Trace từ Logo Placeholder)
        // --------------------------------------------------------------------
        var wireComp = proj.items.addComp("Precomp_02_Logo_Hologram_Wireframe", 1000, 1000, 1.0, DUR, FPS);
        wireComp.parentFolder = precompFolder;

        var wireLogoLayer = wireComp.layers.add(logoComp);
        wireLogoLayer.name = "Auto_Traced_Logo_Edges";

        // Dùng hiệu ứng Vegas có sẵn của AE để tự động vẽ viền tia laser quanh Alpha của BẤT KỲ Logo nào!
        try {
            var vegas = wireLogoLayer.property("ADBE Effect Parade").addProperty("ADBE Vegas");
            if (vegas) {
                try { vegas.property("ADBE Vegas-0001").setValue(2); } catch (e) {} // Stroke: Image Contours
                try { vegas.property("ADBE Vegas-0004").setValue(4); } catch (e) {} // Channel: Alpha
                try { vegas.property("ADBE Vegas-0010").setValue(2); } catch (e) {} // Segments: 2
                try {
                    var vLen = vegas.property("ADBE Vegas-0011");
                    vLen.setValueAtTime(1.0, 0.0);
                    vLen.setValueAtTime(2.6, 0.95);
                    vLen.setValueAtTime(3.6, 1.0);
                    applyEaseInOut(vLen, 0, 75, 0, 75);
                } catch (e) {}
                try {
                    var vRot = vegas.property("ADBE Vegas-0013");
                    vRot.setValueAtTime(1.0, 0);
                    vRot.setValueAtTime(4.0, 360);
                } catch (e) {}
                try { vegas.property("ADBE Vegas-0016").setValue(1); } catch (e) {} // Blend Mode: Transparent
                try { vegas.property("ADBE Vegas-0017").setValue(HOLO_GREEN); } catch (e) {} // Color
                try { vegas.property("ADBE Vegas-0018").setValue(4.5); } catch (e) {} // Width
                try { vegas.property("ADBE Vegas-0019").setValue(0.8); } catch (e) {} // Hardness
                try { vegas.property("ADBE Vegas-0020").setValue(1.0); } catch (e) {} // Start Opacity
                try { vegas.property("ADBE Vegas-0022").setValue(1.0); } catch (e) {} // End Opacity
            }
        } catch (e) {}

        // Thêm lớp quét ngang Hologram Scanlines (Venetian Blinds)
        var scanLogoLayer = wireComp.layers.add(logoComp);
        scanLogoLayer.name = "Hologram_Scanline_Fill";
        scanLogoLayer.blendingMode = BlendingMode.ADD;
        try {
            var fillFx = scanLogoLayer.property("ADBE Effect Parade").addProperty("ADBE Fill");
            if (fillFx) {
                fillFx.property("ADBE Fill-0002").setValue(HOLO_GREEN);
            }
            var blindsFx = scanLogoLayer.property("ADBE Effect Parade").addProperty("ADBE Venetian Blinds");
            if (blindsFx) {
                blindsFx.property("ADBE Venetian Blinds-0001").setValue(68);
                blindsFx.property("ADBE Venetian Blinds-0002").setValue(90);
                blindsFx.property("ADBE Venetian Blinds-0003").setValue(8);
            }
        } catch (e) {}
        var scanOp = scanLogoLayer.property("ADBE Transform Group").property("ADBE Opacity");
        scanOp.setValueAtTime(1.4, 0);
        scanOp.setValueAtTime(2.8, 38);
        scanOp.setValueAtTime(3.8, 0);

        addGlow(wireLogoLayer, 25, 1.6, 40);

        // --------------------------------------------------------------------
        // 6. PRECOMP 03: HUD RINGS SYSTEM (1600x1600)
        // --------------------------------------------------------------------
        var hudComp = proj.items.addComp("Precomp_03_HUD_Rings_System", 1600, 1600, 1.0, DUR, FPS);
        hudComp.parentFolder = precompFolder;

        // 6a. Vòng vạch chia độ mảnh ngoài cùng (Outer Fine Ticks Ring)
        var ringTicksLayer = hudComp.layers.addShape();
        ringTicksLayer.name = "HUD_Outer_Fine_Ticks_Ring";
        addCircleGroup(ringTicksLayer, "Fine_Ticks_Circle", 930, CYAN_BRIGHT, 14, 70, 2, 9);
        addCircleGroup(ringTicksLayer, "Thin_Guide_Circle", 965, CYAN_DEEP, 1.5, 55, 0, 0);
        addRootTrimPaths(ringTicksLayer, 0, 0, null, null, 0.0, 0, 1.6, 100, -90);
        var rtRot = ringTicksLayer.property("ADBE Transform Group").property("ADBE Rotate Z");
        rtRot.setValueAtTime(0.0, -25);
        rtRot.setValueAtTime(6.5, 15);
        addGlow(ringTicksLayer, 20, 1.2, 50);

        // 6b. Thanh vạch năng lượng dày ở Đỉnh & Đáy (Top & Bottom Heavy Telemetry Bars ••••••)
        var meterBarsLayer = hudComp.layers.addShape();
        meterBarsLayer.name = "HUD_Top_Bottom_Telemetry_Bars";

        var topBarIdx = addCircleGroup(meterBarsLayer, "Bottom_Heavy_Ticks", 885, CYAN_BRIGHT, 16, 100, 6, 8);
        addGroupTrimPaths(meterBarsLayer, topBarIdx, 0.4, 50, 2.0, 41, 0.4, 50, 2.0, 59, 0);

        var botBarIdx = addCircleGroup(meterBarsLayer, "Top_Heavy_Ticks", 885, CYAN_BRIGHT, 16, 100, 6, 8);
        addGroupTrimPaths(meterBarsLayer, botBarIdx, 0.4, 50, 2.0, 42, 0.4, 50, 2.0, 58, 180);

        addGlow(meterBarsLayer, 30, 1.8, 35);

        // 6c. Vòng cung sáng chạy quanh (Outer Glowing Arcs)
        var arcsLayer = hudComp.layers.addShape();
        arcsLayer.name = "HUD_Rotating_Laser_Arcs";
        addCircleGroup(arcsLayer, "Laser_Arcs", 840, CYAN_PALE, 3.5, 95, 95, 160);
        addRootTrimPaths(arcsLayer, 0, 0, null, null, 0.2, 0, 1.8, 100, 45);
        var arRot = arcsLayer.property("ADBE Transform Group").property("ADBE Rotate Z");
        arRot.setValueAtTime(0.0, 40);
        arRot.setValueAtTime(6.5, -20);
        addGlow(arcsLayer, 25, 1.5, 40);

        // 6d. Hai tia laser trục ngang (Horizontal Axis Guide Lines trái & phải)
        var axisLayer = hudComp.layers.addShape();
        axisLayer.name = "HUD_Horizontal_Axis_Lines";
        var axIdx = getRootVecs(axisLayer).numProperties + 1;
        var axGrp = getRootVecs(axisLayer).addProperty("ADBE Vector Group");
        axGrp.name = "Horizontal_Laser_Beams";

        var leftLine = getGrpVecs(axisLayer, axIdx).addProperty("ADBE Vector Shape - Group");
        var lShape = new Shape();
        lShape.vertices = [[-310, 0], [-760, 0]];
        lShape.closed = false;
        leftLine.property("ADBE Vector Shape").setValue(lShape);

        var rightLine = getGrpVecs(axisLayer, axIdx).addProperty("ADBE Vector Shape - Group");
        var rShape = new Shape();
        rShape.vertices = [[310, 0], [760, 0]];
        rShape.closed = false;
        rightLine.property("ADBE Vector Shape").setValue(rShape);

        var axStroke = getGrpVecs(axisLayer, axIdx).addProperty("ADBE Vector Graphic - Stroke");
        axStroke.property("ADBE Vector Stroke Color").setValue(CYAN_BRIGHT);
        axStroke.property("ADBE Vector Stroke Width").setValue(2.5);
        axStroke.property("ADBE Vector Stroke Opacity").setValue(85);
        addGroupTrimPaths(axisLayer, axIdx, 0, 0, null, null, 0.8, 0, 2.2, 100, 0);
        addGlow(axisLayer, 20, 1.4, 45);

        // --------------------------------------------------------------------
        // 7. MAIN COMP: FINAL_Futuristic_HiTech_Logo_Reveal (1920x1080, 12s)
        // --------------------------------------------------------------------
        var mainComp = proj.items.addComp("FINAL_Futuristic_HiTech_Logo_Reveal", W, H, 1.0, DUR, FPS);
        mainComp.parentFolder = renderFolder;
        setClassic3D(mainComp);

        // 7.1. BACKGROUND (Chuyển mượt từ nền xanh đen công nghệ sang đen tuyền ở 6.0s -> 7.0s)
        var bgBlack = mainComp.layers.addSolid([0, 0, 0], "BG_Pure_Black", W, H, 1.0, DUR);
        bgBlack.source.parentFolder = assetsFolder;

        var bgCyber = mainComp.layers.addSolid([0.04, 0.14, 0.22], "BG_Cyber_Atmosphere_Glow", W, H, 1.0, DUR);
        bgCyber.source.parentFolder = assetsFolder;
        try {
            var ramp = bgCyber.property("ADBE Effect Parade").addProperty("ADBE Ramp");
            if (ramp) {
                ramp.property("ADBE Ramp-0001").setValue([W / 2, H / 2]);
                ramp.property("ADBE Ramp-0002").setValue([0.05, 0.18, 0.28]);
                ramp.property("ADBE Ramp-0003").setValue([W / 2, H + 200]);
                ramp.property("ADBE Ramp-0004").setValue([0.0, 0.01, 0.02]);
                ramp.property("ADBE Ramp-0005").setValue(2); // Radial Ramp
            }
        } catch (e) {}
        var bgOp = bgCyber.property("ADBE Transform Group").property("ADBE Opacity");
        bgOp.setValueAtTime(0.0, 35);
        bgOp.setValueAtTime(2.5, 90);
        bgOp.setValueAtTime(5.2, 85);
        bgOp.setValueAtTime(6.8, 0);
        applyEaseInOut(bgOp, 0, 75, 0, 75);

        // 7.2. 3D DIGITAL MATRIX FLOOR
        var floor3D = mainComp.layers.add(matrixComp);
        floor3D.name = "3D_Digital_Matrix_Floor";
        floor3D.threeDLayer = true;
        floor3D.blendingMode = BlendingMode.ADD;
        floor3D.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, 45]);
        var flOp = floor3D.property("ADBE Transform Group").property("ADBE Opacity");
        flOp.setValueAtTime(0.0, 15);
        flOp.setValueAtTime(1.5, 85);
        flOp.setValueAtTime(5.2, 80);
        flOp.setValueAtTime(6.6, 0);

        // 7.3. 3D HUD OUTER RINGS SYSTEM
        var hud3D = mainComp.layers.add(hudComp);
        hud3D.name = "3D_HUD_Rings_System";
        hud3D.threeDLayer = true;
        hud3D.blendingMode = BlendingMode.ADD;
        hud3D.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, 12]);
        var hudOp = hud3D.property("ADBE Transform Group").property("ADBE Opacity");
        hudOp.setValueAtTime(0.0, 0);
        hudOp.setValueAtTime(0.6, 95);
        hudOp.setValueAtTime(5.4, 95);
        hudOp.setValueAtTime(6.6, 0);
        applyEaseInOut(hudOp, 0, 75, 0, 75);

        // 7.4. 3D MULTI-LAYERED HEXAGON CAGE (Khung Lục Giác 3D nhiều lớp chiều sâu Z)
        var hexZOffsets = [36, 24, 12, 0, -14, -28];
        for (var h = 0; h < hexZOffsets.length; h++) {
            var zVal = hexZOffsets[h];
            var isMainLayer = (zVal === 0);
            var hexLayer = mainComp.layers.addShape();
            hexLayer.name = isMainLayer ? "3D_Hexagon_Core_Frame (Z=0)" : ("3D_Hexagon_Depth_Slice_" + (h + 1) + " (Z=" + zVal + ")");
            hexLayer.threeDLayer = true;
            hexLayer.blendingMode = BlendingMode.ADD;
            hexLayer.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, zVal]);

            if (isMainLayer) {
                addPolygonGroup(hexLayer, "Hex_Outer_Double_Line", 6, 365, 0, CYAN_PALE, 3.5, 100, 0, 0);
                addPolygonGroup(hexLayer, "Hex_Mid_Line",          6, 348, 0, CYAN_BRIGHT, 2.5, 90, 0, 0);
                addPolygonGroup(hexLayer, "Hex_Inner_Dotted_Line", 6, 330, 0, CYAN_PALE, 5.0, 95, 2, 11);
                addRootTrimPaths(hexLayer, 0, 0, null, null, 0.1, 0, 2.1, 100, -30);
                addGlow(hexLayer, 28, 1.6, 40);
            } else {
                var sliceColor = (zVal < 0) ? CYAN_PALE : CYAN_DEEP;
                var sliceWidth = (Math.abs(zVal) <= 15) ? 2.2 : 1.5;
                addPolygonGroup(hexLayer, "Hex_3D_Extrude_Outer", 6, 365, 0, sliceColor, sliceWidth, 65, 0, 0);
                addPolygonGroup(hexLayer, "Hex_3D_Extrude_Inner", 6, 340, 0, CYAN_BRIGHT, 1.5, 50, 4, 10);
                addRootTrimPaths(hexLayer, 0, 0, null, null, 0.3 + h * 0.08, 0, 2.3 + h * 0.08, 100, 0);
                addGlow(hexLayer, 20, 1.1, 50);
            }

            var hxOp = hexLayer.property("ADBE Transform Group").property("ADBE Opacity");
            var maxHexOp = isMainLayer ? 100 : 42;
            hxOp.setValueAtTime(0.1, 0);
            hxOp.setValueAtTime(0.8, maxHexOp);
            hxOp.setValueAtTime(3.6, maxHexOp);
            hxOp.setValueAtTime(4.5, isMainLayer ? 100 : 15);
            hxOp.setValueAtTime(5.6, isMainLayer ? 90 : 0);
            hxOp.setValueAtTime(6.9, 0);
            applyEaseInOut(hxOp, 0, 75, 0, 75);
        }

        // 7.5. 3D HOLOGRAM LOGO EXTRUDER (Tạo hiệu ứng Logo Hologram 3D nổi khối ở 00:01.5 -> 00:04.2)
        var logoZExtrude = [25, 15, 5, 0, -8, -18, -28];
        for (var lz = 0; lz < logoZExtrude.length; lz++) {
            var lzVal = logoZExtrude[lz];
            var holoSlice = mainComp.layers.add(wireComp);
            holoSlice.name = "3D_Logo_Hologram_Extrude_" + (lz + 1) + " (Z=" + lzVal + ")";
            holoSlice.threeDLayer = true;
            holoSlice.blendingMode = BlendingMode.ADD;
            holoSlice.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, lzVal]);

            var hsOp = holoSlice.property("ADBE Transform Group").property("ADBE Opacity");
            var peakOp = (lzVal === 0) ? 100 : 52;
            hsOp.setValueAtTime(1.0, 0);
            hsOp.setValueAtTime(2.0, peakOp);
            hsOp.setValueAtTime(3.4, peakOp);
            hsOp.setValueAtTime(4.2, 0);
            applyEaseInOut(hsOp, 0, 75, 0, 75);
        }

        // 7.6. SOLID LOGO REVEAL (Logo chính thức xuất hiện ở 00:03.4 -> 00:12.0)
        var mainLogoLayer = mainComp.layers.add(logoComp);
        mainLogoLayer.name = "MAIN_SOLID_LOGO_REVEAL";
        mainLogoLayer.threeDLayer = true;
        mainLogoLayer.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, 0]);

        var mlOp = mainLogoLayer.property("ADBE Transform Group").property("ADBE Opacity");
        mlOp.setValueAtTime(3.3, 0);
        mlOp.setValueAtTime(4.1, 100);
        applyEaseInOut(mlOp, 0, 75, 0, 75);

        try {
            var sweep = mainLogoLayer.property("ADBE Effect Parade").addProperty("CC Light Sweep");
            if (sweep) {
                var swCenter = sweep.property("CC Light Sweep-0001");
                swCenter.setValueAtTime(3.5, [250, 500]);
                swCenter.setValueAtTime(5.2, [750, 500]);
                try { sweep.property("CC Light Sweep-0002").setValue(35); } catch (e) {}
                try { sweep.property("CC Light Sweep-0004").setValue(65); } catch (e) {}
                try { sweep.property("CC Light Sweep-0005").setValue(0.8); } catch (e) {}
            }
        } catch (e) {}

        // 7.7. ENERGY FLASH BURST (Chớp sáng nhẹ tại 3.7s khi Hologram kết tinh thành Logo thật)
        var flashShape = mainComp.layers.addShape();
        flashShape.name = "Hologram_To_Solid_Flash";
        flashShape.threeDLayer = true;
        flashShape.blendingMode = BlendingMode.ADD;
        flashShape.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, -5]);
        addPolygonGroup(flashShape, "Hex_Flash_Pulse", 6, 355, 0, CYAN_PALE, 12, 100, 0, 0);
        addGlow(flashShape, 65, 2.2, 20);
        var flshOp = flashShape.property("ADBE Transform Group").property("ADBE Opacity");
        flshOp.setValueAtTime(3.3, 0);
        flshOp.setValueAtTime(3.75, 85);
        flshOp.setValueAtTime(4.4, 0);
        applyEaseInOut(flshOp, 0, 75, 0, 75);

        // 7.8. TAGLINE / WEBSITE TEXT REVEAL (Hiện ra ở 00:07.3 -> 00:12.0 trên nền đen sạch)
        var taglineInMain = mainComp.layers.add(textComp);
        taglineInMain.name = "TAGLINE_TEXT_REVEAL (07.3s - 12.0s)";
        taglineInMain.threeDLayer = true;
        taglineInMain.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2 + 275, 0]);

        var tgOp = taglineInMain.property("ADBE Transform Group").property("ADBE Opacity");
        tgOp.setValueAtTime(7.2, 0);
        tgOp.setValueAtTime(8.3, 100);
        applyEaseInOut(tgOp, 0, 75, 0, 75);

        var tgScale = taglineInMain.property("ADBE Transform Group").property("ADBE Scale");
        tgScale.setValueAtTime(7.2, [92, 92, 100]);
        tgScale.setValueAtTime(9.5, [100, 100, 100]);
        applyEaseInOut(tgScale, 0, 75, 0, 75);

        // --------------------------------------------------------------------
        // 8. 3D CAMERA & ORBIT RIG (Chuẩn chuyển động Camera của A7XZTEC)
        // --------------------------------------------------------------------
        var camNull = mainComp.layers.addNull(DUR);
        camNull.name = "CAMERA_3D_ORBIT_CONTROLLER";
        camNull.threeDLayer = true;

        var cnPos = camNull.property("ADBE Transform Group").property("ADBE Position");
        var cnRotX = camNull.property("ADBE Transform Group").property("ADBE Rotate X");
        var cnRotY = camNull.property("ADBE Transform Group").property("ADBE Rotate Y");
        var cnRotZ = camNull.property("ADBE Transform Group").property("ADBE Rotate Z");

        cnPos.setValueAtTime(0.0, [W / 2, H / 2, -260]);
        cnPos.setValueAtTime(4.0, [W / 2, H / 2, 0]);
        cnPos.setValueAtTime(7.0, [W / 2, H / 2, 35]);
        cnPos.setValueAtTime(12.0, [W / 2, H / 2, 35]);

        cnRotX.setValueAtTime(0.0, 62);
        cnRotX.setValueAtTime(4.1, 0);

        cnRotY.setValueAtTime(0.0, 12);
        cnRotY.setValueAtTime(4.1, 0);

        cnRotZ.setValueAtTime(0.0, -38);
        cnRotZ.setValueAtTime(4.1, 0);

        applyEaseInOut(cnPos, 0, 80, 0, 80);
        applyEaseInOut(cnRotX, 0, 80, 0, 80);
        applyEaseInOut(cnRotY, 0, 80, 0, 80);
        applyEaseInOut(cnRotZ, 0, 80, 0, 80);

        var cam = mainComp.layers.addCamera("MASTER_3D_CAMERA", [W / 2, H / 2]);
        cam.property("ADBE Transform Group").property("ADBE Position").setValue([W / 2, H / 2, -1860]);
        try {
            cam.property("ADBE Transform Group").property("ADBE Anchor Point").setValue([W / 2, H / 2, 0]);
        } catch (e) {}
        cam.parent = camNull;

        // --------------------------------------------------------------------
        // 9. CONTROL PANEL (Bảng điều khiển màu sắc nhanh trên cùng)
        // --------------------------------------------------------------------
        var ctrlNull = mainComp.layers.addNull(DUR);
        ctrlNull.name = "=== CONTROL PANEL (Info & Settings) ===";
        ctrlNull.guideLayer = true;
        ctrlNull.label = 14;
        try {
            var c1 = ctrlNull.property("ADBE Effect Parade").addProperty("ADBE Color Control");
            c1.name = "HUD Primary Cyan";
            c1.property(1).setValue(CYAN_BRIGHT);

            var c2 = ctrlNull.property("ADBE Effect Parade").addProperty("ADBE Color Control");
            c2.name = "Logo Hologram Neon";
            c2.property(1).setValue(HOLO_GREEN);
        } catch (e) {}

        // Đặt con trỏ Timeline ở 00:03.00 (Lúc hiệu ứng 3D Hologram + Hexagon rực rỡ nhất)
        mainComp.time = 3.0;

        // Mở trực tiếp Main Comp trên màn hình After Effects
        try {
            mainComp.openInViewer();
        } catch (e) {}

        // Lưu thêm 1 bản .aep vào thư mục intro logo nếu project hiện tại chưa lưu
        try {
            // After Effects (Windows) lưu .aep vào ổ F; EffectCraft (Linux) lưu .ecproj vào USB.
            var savePath = new Folder("f:/TH\u00C0NH V/intro logo").exists
                ? new File("f:/TH\u00C0NH V/intro logo/Futuristic_HiTech_Logo_Reveal_A7XZTEC.aep")
                : new File("/media/vmiz/Over Powers/TH\u00C0NH V/intro logo/Futuristic_HiTech_Logo_Reveal_A7XZTEC.ecproj");
            if (!proj.file && savePath.parent.exists) {
                proj.save(savePath);
            }
        } catch (e) {}

    } catch (err) {
        $.writeln("Error creating A7XZTEC template: " + err.toString() + " (Line " + err.line + ")");
    } finally {
        app.endUndoGroup();
    }
})();
