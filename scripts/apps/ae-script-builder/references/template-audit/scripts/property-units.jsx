(function(){
 var B='D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21/raw';
 function q(v){return '"'+String(v).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n')+'"';}
 var p=app.project;if(p&&(p.numItems||p.file||p.dirty))return;
 app.beginSuppressDialogs();app.open(new File('F:/video AE/save/1.aep'));p=app.project;
 var ids={};for(var i=1;i<=p.numItems;i++)ids[p.item(i).id]=p.item(i);
 var a=[];function add(label,prop){var o='{"label":'+q(label)+',"value":'+prop.value+',"units":'+q(prop.unitsText);try{o+=',"min":'+prop.minValue+',"max":'+prop.maxValue;}catch(e){}try{o+=',"valueText":'+q(prop.valueText);}catch(e){}a.push(o+'}');}
 try{add('Drop Shadow Opacity',ids[1278].layer(3).effect('ADBE Drop Shadow').property('ADBE Drop Shadow-0002'));}catch(e){a.push('{"error":'+q(e)+'}');}
 try{add('Glow Threshold',ids[1533].layer(11).effect('ADBE Glo2').property('ADBE Glo2-0002'));}catch(e){a.push('{"error":'+q(e)+'}');}
 try{add('Fill Opacity',ids[167].layer(11).effect('ADBE Fill').property('Opacity'));}catch(e){a.push('{"error":'+q(e)+'}');}
 try{add('Shadow Controller Opacity',ids[1278].layer(1).effect('Text Shadow').property('Pseudo/SRBod3d13821P-0002'));}catch(e){a.push('{"error":'+q(e)+'}');}
 var f=new File(B+'/property-units.json');f.encoding='UTF-8';f.open('w');f.write('['+a.join(',')+']');f.close();
 app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);app.endSuppressDialogs(false);app.quit();
})();
