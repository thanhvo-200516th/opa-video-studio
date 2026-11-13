/* Adapt the supplied PixelTruck Blueprint Logo Reveal to OPA.
   Run only in the separate OPA-Blueprint-OPA.aep working copy.
   Original template is never opened, overwritten or closed by this script. */
(function(){
 var ROOT='F:/video AE/OPA-Blueprint-OPA',P=app.project,DATA=__OPA_PATH_DATA__,FPS=30;
 var B=[0,104/255,1],WHITE=[1,1,1],PAPER=[247/255,249/255,252/255],INK=[.07,.11,.18],MUTED=[.36,.43,.54];
 var report=[],exports=[],masterFolder,assetFolder;
 function trim(s){return String(s).replace(/^\s+|\s+$/g,'');}
 function find(n){for(var i=1;i<=P.numItems;i++)if(trim(P.item(i).name)===n&&P.item(i) instanceof CompItem)return P.item(i);throw Error('Missing composition: '+n);}
 function layer(c,n){for(var i=1;i<=c.numLayers;i++)if(trim(c.layer(i).name)===n)return c.layer(i);throw Error('Missing layer '+n+' in '+c.name);}
 function fx(l,n){var g=l.property('ADBE Effect Parade');for(var i=1;i<=g.numProperties;i++)if(trim(g.property(i).name)===n)return g.property(i);throw Error('Missing effect '+n+' in '+l.name);}
 function assign(p,v){try{if(p.numKeys){for(var k=1;k<=p.numKeys;k++)p.setValueAtKey(k,v);}else p.setValue(v);}catch(e){if(v instanceof Array&&v.length===4&&p.canSetExpression){p.expression='['+v.join(',')+']';report.push('Color expression compatibility fallback: '+p.name);}else throw e;}return p;}
 function value(l,n,v){if(/color|position/i.test(n)){report.push('Preserve legacy multi-value control until XML stage / '+l.name+' / '+n);return null;}var p=assign(fx(l,n).property(1),v);report.push(l.name+' / '+n+' = '+v);return p;}
 function tr(l,n){return l.property('ADBE Transform Group').property(n);}
 function set(l,n,v){tr(l,n).setValue(v);return l;}
 function ease(p){for(var i=1;i<=p.numKeys;i++){try{var d=p.isSpatial?1:(p.value instanceof Array?p.value.length:1),a=[];for(var j=0;j<d;j++)a.push(new KeyframeEase(0,65));p.setTemporalEaseAtKey(i,a,a);}catch(e){}}}
 function keys(p,t,v){for(var i=0;i<t.length;i++)p.setValueAtTime(t[i],v[i]);ease(p);}
 function op(l,t,v){keys(tr(l,'ADBE Opacity'),t,v);}
 function folder(n){return P.items.addFolder(n);}
 function comp(n,w,h,d,f){var c=P.items.addComp(n,w,h,1,d,FPS);c.parentFolder=f;c.motionBlur=true;c.shutterAngle=180;return c;}
 function shape(c,n,x,y){var l=c.layers.addShape();l.name=n;l.label=10;l.motionBlur=true;set(l,'ADBE Position',[x,y]);return l;}
 function path(g,n,pts,closed){var p=g.addProperty('ADBE Vector Shape - Group');p.name=n;var s=new Shape();s.vertices=pts;s.closed=closed;s.inTangents=[];s.outTangents=[];for(var i=0;i<pts.length;i++){s.inTangents.push([0,0]);s.outTangents.push([0,0]);}p.property('ADBE Vector Shape').setValue(s);return p;}
 function line(c,n,pts,col,sw,t0,t1){var l=shape(c,n,0,0),g=l.property('ADBE Root Vectors Group');path(g,'Editable path',pts,false);var st=g.addProperty('ADBE Vector Graphic - Stroke');st.property('ADBE Vector Stroke Color').setValue(col);st.property('ADBE Vector Stroke Width').setValue(sw);st.property('ADBE Vector Stroke Line Cap').setValue(2);if(t0!==undefined){var tm=g.addProperty('ADBE Vector Filter - Trim');keys(tm.property('ADBE Vector Trim End'),[t0,t1],[0,100]);}return l;}
 function rect(c,n,x,y,w,h,col,rad){var l=shape(c,n,x,y),g=l.property('ADBE Root Vectors Group'),r=g.addProperty('ADBE Vector Shape - Rect');r.property('ADBE Vector Rect Size').setValue([w,h]);r.property('ADBE Vector Rect Roundness').setValue(rad||0);var f=g.addProperty('ADBE Vector Graphic - Fill');f.property('ADBE Vector Fill Color').setValue(col);return l;}
 function circle(c,n,x,y,size,col){var l=shape(c,n,x,y),g=l.property('ADBE Root Vectors Group'),r=g.addProperty('ADBE Vector Shape - Ellipse');r.property('ADBE Vector Ellipse Size').setValue([size,size]);var f=g.addProperty('ADBE Vector Graphic - Fill');f.property('ADBE Vector Fill Color').setValue(col);return l;}
 function text(c,n,s,x,y,size,col){var l=c.layers.addText(s);l.name=n;l.label=2;var p=l.property('ADBE Text Properties').property('ADBE Text Document'),d=p.value;d.font='ArialMT';d.fontSize=size;d.tracking=0;d.justification=ParagraphJustification.CENTER_JUSTIFY;d.applyFill=true;d.fillColor=col;d.applyStroke=false;p.setValue(d);var b=l.sourceRectAtTime(0,false);set(l,'ADBE Anchor Point',[b.left+b.width/2,b.top+b.height/2]);set(l,'ADBE Position',[x,y]);return l;}
 function glyph(c,i,n,x,y,width,col){var l=shape(c,n,x,y),g=l.property('ADBE Root Vectors Group'),paths=DATA.letters[i].paths;for(var j=0;j<paths.length;j++){var pts=[];for(var k=0;k<paths[j].length;k++)pts.push([paths[j][k][0]-DATA.width/2,paths[j][k][1]-DATA.height/2]);path(g,'OPA '+DATA.letters[i].name+' path '+j,pts,true);}var f=g.addProperty('ADBE Vector Graphic - Fill');f.property('ADBE Vector Fill Color').setValue(col);f.property('ADBE Vector Fill Rule').setValue(2);set(l,'ADBE Scale',[width/DATA.width*100,width/DATA.width*100]);return l;}
 function addLogo(c,n,x,y,w,col){var a=[];for(var i=0;i<3;i++)a.push(glyph(c,i,n+'_'+DATA.letters[i].name,x,y,w,col));return a;}
 function marker(c,t,s,d){var m=new MarkerValue(s);if(d)m.duration=d;c.markerProperty.setValueAtTime(t,m);}
 function imported(path,name){var it=P.importFile(new ImportOptions(new File(ROOT+'/Assets/'+path)));it.name=name||path;it.parentFolder=assetFolder;return it;}
 function queue(c,name){var q=P.renderQueue.items.add(c);q.applyTemplate('Best Settings');var om=q.outputModule(1);om.applyTemplate('H.264 - Match Render Settings - 15 Mbps');om.file=new File(ROOT+'/Exports/'+name+'.mp4');q.render=false;}
 function write(n,s){var f=new File(ROOT+'/QA/'+n);f.encoding='UTF-8';if(f.open('w')){f.write(s);f.close();}}
 function inspect(c){report.push('COMP '+c.name+' | '+c.width+'x'+c.height+' | '+c.duration+'s');for(var i=1;i<=c.numLayers;i++){var l=c.layer(i);report.push(' LAYER '+l.name+' | '+(l.source?l.source.name:'')+' | in '+l.inPoint+' | out '+l.outPoint);}}
 try{
  if(!P||!P.file||P.file.fsName.replace(/\\/g,'/').indexOf(ROOT+'/')!==0)throw Error('Safety stop: open the separate OPA working copy, not the original template.');
  var main=find('MAIN COMP'),logo=find('YOUR LOGO'),tx=find('YOUR TEXT'),rulers=find('ALL RULERS');
  if(P.items.length&&masterFolder)throw Error('Already built.');
  P.save(new File(ROOT+'/Source/Before-OPA-Adaptation.aep'));
  // Remove only our temporary inspector report folders from this working copy.
  for(var z=P.numItems;z>=1;z--){var it=P.item(z);if(it instanceof FolderItem&&it.name==='99_OPA_INSPECTION')it.remove();}
  masterFolder=folder('00_OPA_EXPORTS');assetFolder=folder('01_OPA_BRAND_ASSETS');
  for(var fi=1;fi<=P.numItems;fi++){var it=P.item(fi);if(it instanceof FootageItem&&it.name==='PT_Blac.png'){it.replace(new File(ROOT+'/Assets/PT_Blac.png'));report.push('Relinked original placeholder image.');}}
  // The vector trace is editable, measured against the alpha of the supplied OPA image.
  for(var li=1;li<=logo.numLayers;li++)logo.layer(li).enabled=false;
  addLogo(logo,'OPA_VECTOR',750,750,1360,B);
  logo.comment='OPA wordmark traced from supplied Logoweb.png. Editable native paths. Width 1360 inside 1500x1500. Source art 732x221; compare Assets/OPA-logo-blue.png before major redesign.';
  var png=imported('OPA-logo-blue.png','OPA_ORIGINAL_WORDMARK');var reference=logo.layers.add(png);reference.name='OPA_PNG_REFERENCE / Disabled';reference.enabled=false;set(reference,'ADBE Anchor Point',[1541,875.5]);set(reference,'ADBE Position',[750,750]);set(reference,'ADBE Scale',[1360/732*100,1360/732*100]);
  var tl=tx.layer(1),tdp=tl.property('ADBE Text Properties').property('ADBE Text Document'),td=tdp.value;td.text='Marketing × Công nghệ × AI';td.font='ArialMT';td.fontSize=74;td.tracking=15;td.applyFill=true;td.fillColor=INK;td.applyStroke=false;td.justification=ParagraphJustification.CENTER_JUSTIFY;tdp.setValue(td);var tb=tl.sourceRectAtTime(0,false);set(tl,'ADBE Anchor Point',[tb.left+tb.width/2,tb.top+tb.height/2]);set(tl,'ADBE Position',[1500,400]);tl.name='OPA_TAGLINE / Edit this text';
  var ctl=layer(main,'CONTROL');value(ctl,'RGB split',0);value(ctl,'Camera lens blur',10);value(ctl,'Logo line width',3);value(ctl,'Logo line color',B.concat([1]));value(ctl,'Logo line_echo intensity',26);value(ctl,'Logo line_echo quantity',2);
  var ri=value(ctl,'Rulers intensity',65);keys(ri,[0,4.8,6.3,7.2],[65,65,15,0]);value(ctl,'Rulers color',B.concat([1]));var ai=value(ctl,'Auxiliary lines intensity',28);keys(ai,[0,4.6,6.5],[28,28,0]);value(ctl,'Auxiliary lines color',[.42,.59,.85,1]);value(ctl,'Shadows intensity',6);value(ctl,'Shadows color',[.12,.24,.43,1]);
  var gi=value(ctl,'Grid intensity',55);keys(gi,[0,4.6,6.4,7.2],[55,55,15,0]);value(ctl,'Grid color',[.78,.84,.93,1]);value(ctl,'Text intensity',100);value(ctl,'Text color',INK.concat([1]));value(ctl,'Text position',[1500,830]);
  var ag=layer(main,'AUXILIARY GEOMETRY');value(ag,'AG Color',B.concat([1]));value(ag,'AG opacity_1',20);value(ag,'AG direction_1',0);value(ag,'AG opacity_2',18);value(ag,'AG direction_2',90);value(ag,'AG opacity_3',0);
  var cc=layer(main,'CC');try{fx(cc,'Noise').property(1).setValue(.6);}catch(ignore){}
  // Original angular/radius dimensions belong to the demo logo; hide them.
  for(var r=1;r<=rulers.numLayers;r++)if(/^RULER/.test(trim(rulers.layer(r).name)))rulers.layer(r).enabled=false;
  // Custom native construction rules match the OPA wordmark bounding box.
  var x0=1240,x1=2600,y0=1080-221*1360/732/2,y1=1080+221*1360/732/2;
  var rules=[[[x0,y0-80],[x1,y0-80]],[[x0,y0-95],[x0,y0-20]],[[x1,y0-95],[x1,y0-20]],[[x0-80,y0],[x0-80,y1]],[[x0-95,y0],[x0-20,y0]],[[x0-95,y1],[x0-20,y1]]];
  for(var rr=0;rr<rules.length;rr++){var rl=line(rulers,'OPA_RULER_'+(rr+1),rules[rr],B,2,.12+rr*.05,.9+rr*.05);op(rl,[0,.4,3.5,4.5],[0,72,72,0]);rl.outPoint=4.5;}
  var wlabel=text(rulers,'OPA_LABEL_W','W',1920,y0-111,30,B);op(wlabel,[.3,.8,3.5,4.5],[0,90,90,0]);wlabel.outPoint=4.5;
  var hlabel=text(rulers,'OPA_LABEL_H','H',x0-112,1080,30,B);op(hlabel,[.3,.8,3.5,4.5],[0,90,90,0]);hlabel.outPoint=4.5;
  main.comment='PixelTruck supplied template, adapted for OPA. Keep MAIN COMP name: original expressions use it. Controllers use native effects. Original demonstration rulers disabled; OPA_RULER_* layers added in ALL RULERS.';
  // HD wrapper preserves the original 4K engine and all editable template controls.
  var hd=comp('OPA_10s_16x9_1920x1080',1920,1080,10,masterFolder),ml=hd.layers.add(main);ml.name='BLUEPRINT_TEMPLATE / Edit MAIN COMP';set(ml,'ADBE Scale',[50,50]);set(ml,'ADBE Position',[960,540]);
  var snd10=imported('OPA-SFX-10s-original.wav','OPA_SFX_10s_ORIGINAL'),snd16=imported('OPA-SFX-16s-original.wav','OPA_SFX_16s_ORIGINAL');var aud=hd.layers.add(snd10);aud.name='SFX / Original guide audio';aud.audio.audioLevels.setValue([0,0]);
  marker(hd,0,'01 / Blueprint wire + camera',3);marker(hd,3,'02 / OPA construction',2.2);marker(hd,5.2,'03 / Fill + settle',2);marker(hd,7.2,'04 / Clean OPA lockup',2.8);
  hd.time=8.4;exports.push(hd);queue(hd,'OPA-Intro-10s-16x9');
  // Brand-film extension adapts the reference palette / icon / final lockup rhythm.
  var film=comp('OPA_16s_BRAND_FILM_1920x1080',1920,1080,16,masterFolder);rect(film,'BG_PAPER',960,540,1920,1080,PAPER,0);var intro=film.layers.add(hd);intro.name='01_BLUEPRINT_10s / Shared source';intro.outPoint=10;intro.audioEnabled=false;
  var pb=rect(film,'BG_PALETTE',960,540,1920,1080,PAPER,0);pb.inPoint=10;pb.outPoint=12.3;
  var cols=[B,WHITE,INK],names=['OPA Blue','OPA White','OPA Ink'];
  for(var ci=0;ci<3;ci++){var xx=960+(ci-1)*310;var card=rect(film,'CARD_'+names[ci],xx,520,280,430,cols[ci],9);card.inPoint=10;card.outPoint=12.3;keys(tr(card,'ADBE Position'),[10+ci*.09,10.6+ci*.09,11.9,12.3],[[xx,650],[xx,520],[xx,520],[xx,450]]);op(card,[10,10.4+ci*.09,11.9,12.3],[0,100,100,0]);var cap=text(film,'LABEL_'+names[ci],names[ci],xx,795,25,MUTED);cap.inPoint=10.3+ci*.09;cap.outPoint=12.3;op(cap,[cap.inPoint,cap.inPoint+.3,11.9,12.3],[0,100,100,0]);}
  var badgeBg=rect(film,'BG_BADGE',960,540,1920,1080,PAPER,0);badgeBg.inPoint=12.3;badgeBg.outPoint=13.7;var badge=circle(film,'O_ICON_BADGE',960,540,360,B);badge.inPoint=12.3;badge.outPoint=13.7;keys(tr(badge,'ADBE Scale'),[12.3,12.8,13.4,13.7],[[70,70],[100,100],[100,100],[380,380]]);op(badge,[12.3,12.6,13.5,13.7],[0,100,100,0]);
  var oi=glyph(film,0,'OPA_O_ICON',960+(366-111.5)*.84,540,732*.84,WHITE);oi.inPoint=12.4;oi.outPoint=13.65;op(oi,[12.4,12.8,13.4,13.65],[0,100,100,0]);
  var fb=rect(film,'BG_FINAL_BLUE',960,540,1920,1080,B,0);fb.inPoint=13.5;op(fb,[13.5,13.9],[0,100]);var last=addLogo(film,'FINAL_OPA',960,465,860,WHITE);for(var f=0;f<last.length;f++){last[f].inPoint=13.65;op(last[f],[13.65,14.1],[0,100]);}
  var caption=text(film,'TXT_FINAL_TAGLINE','Marketing × Công nghệ × AI',960,675,29,WHITE);caption.property('ADBE Text Properties').property('ADBE Text Document').expression='comp("YOUR TEXT ").layer(1).text.sourceText.toString()';caption.inPoint=13.9;op(caption,[13.9,14.35],[0,100]);
  var a16=film.layers.add(snd16);a16.name='SFX / Original 16-second guide';marker(film,0,'01 / Blueprint intro',10);marker(film,10,'02 / Brand palette',2.3);marker(film,12.3,'03 / O icon badge',1.2);marker(film,13.5,'04 / Blue OPA lockup',2.5);film.time=14.8;exports.push(film);queue(film,'OPA-Brand-Film-16s-16x9');
  var read=comp('00_OPA_START_HERE',1920,1080,10,masterFolder);rect(read,'BG',960,540,1920,1080,PAPER,0);text(read,'TITLE','OPA / Blueprint Logo Reveal',960,180,66,B);text(read,'HELP_1','10 seconds: OPA_10s_16x9_1920x1080',960,350,36,INK);text(read,'HELP_2','16 seconds: OPA_16s_BRAND_FILM_1920x1080',960,450,34,INK);text(read,'HELP_3','Logo: YOUR LOGO / OPA_VECTOR_O, P, A',960,570,32,INK);text(read,'HELP_4','Text: YOUR TEXT  / OPA_TAGLINE',960,670,32,INK);text(read,'HELP_5','Colors and motion: MAIN COMP > CONTROL > F3',960,770,30,INK);text(read,'HELP_6','Read Docs/HUONG-DAN-DUNG-OPA-TU-TEMPLATE.md',960,870,27,MUTED);
  for(var ei=0;ei<exports.length;ei++)inspect(exports[ei]);inspect(logo);inspect(tx);inspect(main);inspect(rulers);write('adaptation-log.txt',report.join('\n'));
  P.save(new File(ROOT+'/OPA-Blueprint-OPA.aep'));P.save(new File(ROOT+'/Source/OPA-Blueprint-OPA.aepx'));P.save(new File(ROOT+'/OPA-Blueprint-OPA.aep'));
  hd.openInViewer();app.exitCode=0;
 }catch(e){try{write('adaptation-error.txt',e.toString()+'\nLine '+e.line+'\n'+report.join('\n'));}catch(ignore){}app.exitCode=90;}
})();
