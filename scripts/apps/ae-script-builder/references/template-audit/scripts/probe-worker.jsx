(function(){
 var p=app.project;var d=new Folder('D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21/raw');d.create();
 var f=new File(d.fsName+'/worker-probe.json');f.encoding='UTF-8';f.open('w');f.write('{"numItems":'+(p?p.numItems:0)+',"hasFile":'+(p&&p.file?'true':'false')+'}');f.close();
 if(p && p.numItems===0 && !p.file && !p.dirty){app.quit();}
})();
