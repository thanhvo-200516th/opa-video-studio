(function(){
 var B='D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21';
 function q(s){return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n')+'"';}
 function js(v){if(v===null||v===undefined)return 'null';var t=typeof v;if(t==='string')return q(v);if(t==='number'||t==='boolean')return String(v);var a=[],i;if(v instanceof Array){for(i=0;i<v.length;i++)a.push(js(v[i]));return '['+a.join(',')+']';}for(var k in v)if(v.hasOwnProperty(k))a.push(q(k)+':'+js(v[k]));return '{'+a.join(',')+'}';}
 function wr(n,v){var f=new File(B+'/raw/'+n);f.encoding='UTF-8';f.open('w');f.write(js(v));f.close();}
 if(app.project&&(app.project.numItems||app.project.file||app.project.dirty)){wr('frames-refused.json',{reason:'Initial project is not empty'});return;}
 var results=[];
 try{
 app.beginSuppressDialogs();app.open(new File('F:/video AE/save/1.aep'));var src={};for(var i=1;i<=app.project.numItems;i++)src[app.project.item(i).id]=app.project.item(i);
 var shots=[],fs=[15,27,42,55,67,79,90,156,165,183,201,216];for(var k=0;k<fs.length;k++)shots.push({c:167,f:fs[k],name:'scene01-f'+('000'+fs[k]).slice(-3)});
 var others=[[443,90],[657,90],[966,100],[1278,120],[1533,100],[1896,100],[2263,100],[2579,100],[2917,120],[3165,45]];
 for(var k=0;k<others.length;k++)shots.push({c:others[k][0],f:others[k][1],name:'scene'+('0'+(k+2)).slice(-2)+'-f'+others[k][1]});
 var wrappers={};var rq=app.project.renderQueue;for(var i=rq.numItems;i>=1;i--)rq.item(i).remove();var out=new Folder(B+'/frames/tiff');out.create();
 for(var k=0;k<shots.length;k++){var s=shots[k];if(!wrappers[s.c]){var c=src[s.c];var w=app.project.items.addComp('AUDIT_ONLY_'+s.c,540,960,1,c.duration,c.frameRate);var l=w.layers.add(c);l.property('ADBE Transform Group').property('ADBE Scale').setValue([25,25,100]);wrappers[s.c]=w;}}
 app.endSuppressDialogs(false);
 for(var k=0;k<shots.length;k++){var s=shots[k];try{var item=rq.items.add(wrappers[s.c]);var om=item.outputModule(1);om.applyTemplate('TIFF Sequence with Alpha');om.file=new File(out.fsName+'/'+s.name+'_[#####].tif');item.timeSpanStart=s.f/30;item.timeSpanDuration=1/30;wr('frames-progress.json',{stage:'rendering',index:k,total:shots.length,shot:s});rq.render();results.push({shot:s,status:Number(item.status)});item.remove();}catch(e){results.push({shot:s,error:String(e),line:e.line});try{if(item)item.remove();}catch(x){}}wr('frames-progress.json',{stage:'rendered',done:k+1,total:shots.length,last:results[results.length-1]});}
 wr('frames-complete.json',results);app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);app.quit();
 }catch(e){wr('frames-error.json',{error:String(e),line:e.line});try{app.endSuppressDialogs(false);app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);app.quit();}catch(x){}}
})();
