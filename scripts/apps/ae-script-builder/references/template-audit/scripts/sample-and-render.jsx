(function(){
 var BASE='D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21';
 function q(s){return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n').replace(/\t/g,'\\t')+'"';}
 function js(v){if(v===null||v===undefined)return 'null';var t=typeof v;if(t==='string')return q(v);if(t==='number')return isFinite(v)?String(v):'null';if(t==='boolean')return String(v);var a=[],i;if(v instanceof Array){for(i=0;i<v.length;i++)a.push(js(v[i]));return '['+a.join(',')+']';}for(var k in v)if(v.hasOwnProperty(k)&&typeof v[k]!=='function')a.push(q(k)+':'+js(v[k]));return '{'+a.join(',')+'}';}
 function write(n,v){var f=new File(BASE+'/raw/'+n);f.encoding='UTF-8';f.open('w');f.write(js(v));f.close();}
 function get(o,k){try{return o[k];}catch(e){return null;}}
 function font(f){var d={};var ns=['postScriptName','familyName','styleName','isSubstitute','location','fontID'];for(var i=0;i<ns.length;i++)d[ns[i]]=get(f,ns[i]);return d;}
 if(app.project&&(app.project.numItems||app.project.file||app.project.dirty)){write('render-refused.json',{reason:'Initial project is not empty'});return;}
 app.beginSuppressDialogs();app.open(new File('F:/video AE/save/1.aep'));
 var items={};for(var i=1;i<=app.project.numItems;i++)items[app.project.item(i).id]=app.project.item(i);
 var meta={version:app.version,interpolation:{LINEAR:Number(KeyframeInterpolationType.LINEAR),BEZIER:Number(KeyframeInterpolationType.BEZIER),HOLD:Number(KeyframeInterpolationType.HOLD)},missingFonts:[],textFonts:[],modifiedTextProperties:[],errors:[]};
 try{var fs=app.fonts.missingOrSubstitutedFonts;for(var i=0;i<fs.length;i++)meta.missingFonts.push(font(fs[i]));}catch(e){meta.errors.push(String(e));}
 function scan(p,path,a){for(var k=1;k<=p.numProperties;k++){var n=p.property(k);var h=path+'/'+n.matchName;if(n.propertyType===PropertyType.PROPERTY){if(get(n,'isModified'))a.push({path:h,name:n.name,value:(function(){try{var v=n.value;return v instanceof Array?v:typeof v==='number'||typeof v==='string'?v:String(v);}catch(e){return null;}})(),active:get(n,'active'),enabled:get(n,'enabled')});}else scan(n,h,a);}}
 for(var id in items){var c=items[id];if(!(c instanceof CompItem))continue;for(var j=1;j<=c.numLayers;j++){var l=c.layer(j);if(l instanceof TextLayer){try{var td=l.property('ADBE Text Properties').property('ADBE Text Document').value;meta.textFonts.push({compId:c.id,comp:c.name,layer:l.index,font:font(td.fontObject),text:td.text});if(c.id<3190){var mp=[];scan(l.property('ADBE Text Properties').property('ADBE Text Animators'),'',mp);meta.modifiedTextProperties.push({compId:c.id,comp:c.name,layer:l.index,properties:mp});}}catch(e){meta.errors.push(String(e));}}}}
 write('native-metadata.json',meta);
 var specs=[
 {id:'headline-start',c:141,l:1,path:['ADBE Text Properties','ADBE Text Animators','ADBE Text Animator','ADBE Text Selectors','ADBE Text Selector','ADBE Text Percent Start'],from:0,to:30,step:0.25},
 {id:'subtitle-start',c:154,l:1,path:['ADBE Text Properties','ADBE Text Animators','ADBE Text Animator','ADBE Text Selectors','ADBE Text Selector','ADBE Text Percent Start'],from:0,to:30,step:0.25},
 {id:'glass-opacity',c:167,l:8,path:['ADBE Transform Group','ADBE Opacity'],from:55,to:85,step:0.25},
 {id:'image-mask-size',c:167,l:6,path:['ADBE Root Vectors Group','ADBE Vector Group','ADBE Vectors Group','ADBE Vector Shape - Rect','ADBE Vector Rect Size'],from:60,to:90,step:0.25},
 {id:'scene2-title-position',c:443,l:11,path:['ADBE Transform Group','ADBE Position'],from:60,to:90,step:0.25}
 ];
 var sampled=[];for(var i=0;i<specs.length;i++){var s=specs[i];try{var p=items[s.c].layer(s.l);for(var j=0;j<s.path.length;j++)p=p.property(s.path[j]);var vals=[];for(var f=s.from;f<=s.to+0.001;f+=s.step)vals.push({frame:f,value:p.valueAtTime(f/30,false)});sampled.push({spec:s,values:vals});}catch(e){sampled.push({spec:s,error:String(e)});}}
 write('native-samples.json',sampled);
 var shots=[];var scene1=[15,30,45,55,60,67,75,79,85,90,120,150,165,180,195,210,225];
 for(var k=0;k<scene1.length;k++)shots.push({c:167,f:scene1[k],name:'scene01-f'+('000'+scene1[k]).slice(-3)});
 var others=[[443,90],[657,90],[966,100],[1278,120],[1533,100],[1896,100],[2263,100],[2579,100],[2917,120],[3165,45]];
 for(var k=0;k<others.length;k++)shots.push({c:others[k][0],f:others[k][1],name:'scene'+('0'+(k+2)).slice(-2)+'-f'+others[k][1]});
 var fd=new Folder(BASE+'/frames');fd.create();var rendered=[];
 for(var i=0;i<shots.length;i++){var s=shots[i];try{var c=items[s.c];c.resolutionFactor=[4,4];var file=new File(fd.fsName+'/'+s.name+'.png');c.saveFrameToPng(s.f/c.frameRate,file);rendered.push({compId:s.c,frame:s.f,path:file.fsName,exists:file.exists});}catch(e){rendered.push({compId:s.c,frame:s.f,error:String(e)});}write('render-progress.json',{done:i+1,total:shots.length,last:rendered[rendered.length-1]});}
 write('render-complete.json',rendered);app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);app.endSuppressDialogs(false);app.quit();
})();
