(function(){
 var B='D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21';
 function q(s){return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n')+'"';}
 function wr(n,s){var f=new File(B+'/raw/'+n);f.encoding='UTF-8';f.open('w');f.write(s);f.close();}
 if(app.project&&(app.project.numItems||app.project.file||app.project.dirty)){wr('queue-refused.json','{"reason":"Initial project is not empty"}');return;}
 try{
 app.beginSuppressDialogs();app.open(new File('F:/video AE/save/1.aep'));
 var source=null;for(var i=1;i<=app.project.numItems;i++)if(app.project.item(i).id===167)source=app.project.item(i);
 var preview=app.project.items.addComp('AUDIT_PREVIEW_ONLY',540,960,1,8,30);var layer=preview.layers.add(source);layer.property('ADBE Transform Group').property('ADBE Scale').setValue([25,25,100]);
 var rq=app.project.renderQueue;for(var i=rq.numItems;i>=1;i--)rq.item(i).remove();var item=rq.items.add(preview);var om=item.outputModule(1);
 var names=[];for(var i=0;i<om.templates.length;i++)names.push(q(om.templates[i]));wr('output-templates.json','['+names.join(',')+']');
 om.applyTemplate('TIFF Sequence with Alpha');var out=new Folder(B+'/frames/queue-probe-tiff');out.create();om.file=new File(out.fsName+'/scene01-f079_[#####].tif');
 item.timeSpanStart=79/30;item.timeSpanDuration=1/30;
 app.endSuppressDialogs(false);wr('queue-progress.json','{"stage":"rendering"}');rq.render();wr('queue-progress.json','{"stage":"done","status":'+Number(item.status)+'}');
 app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);app.quit();
 }catch(e){wr('queue-error.json','{"error":'+q(e.toString())+',"line":'+e.line+'}');try{app.endSuppressDialogs(false);app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);app.quit();}catch(x){}}
})();
