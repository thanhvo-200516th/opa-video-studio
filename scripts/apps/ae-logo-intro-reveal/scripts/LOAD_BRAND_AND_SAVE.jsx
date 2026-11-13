(function(){
 var root='F:/video AE/OPA-Blueprint-OPA',p=app.project;
 if(!p.file||p.file.fsName.replace(/\\/g,'/').indexOf(root+'/')!==0)throw Error('Open OPA working copy first.');
 if(p.dirty)throw Error('Working copy has unsaved edits; save before applying the prepared brand file.');
 app.open(new File(root+'/Source/OPA-Blueprint-OPA-BRAND.aepx'));
 app.project.save(new File(root+'/OPA-Blueprint-OPA.aep'));
 for(var i=1;i<=app.project.numItems;i++){var c=app.project.item(i);if(c instanceof CompItem&&c.name==='OPA_10s_16x9_1920x1080'){c.time=8.4;c.openInViewer();}}
})();
