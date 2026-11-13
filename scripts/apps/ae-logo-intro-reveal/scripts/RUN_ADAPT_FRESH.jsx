(function(){
 var root='F:/video AE/OPA-Blueprint-OPA';
 if(!app.project.file||app.project.file.fsName.replace(/\\/g,'/').indexOf(root+'/')!==0)return;
 app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
 app.open(new File(root+'/Source/Template-Converted-Before-OPA.aep'));
 $.evalFile(new File(root+'/Source/ADAPT_BLUEPRINT_OPA.jsx'));
})();
