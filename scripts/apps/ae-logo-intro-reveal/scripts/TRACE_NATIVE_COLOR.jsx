(function(){
 var f=new File('F:/video AE/OPA-Blueprint-OPA/QA/native-color-trace.txt');f.open('w');
 function out(s){f.writeln(s);}
 try{
  out('START '+app.project.file.fsName);
  var c;for(var i=1;i<=app.project.numItems;i++){var it=app.project.item(i);if(it instanceof CompItem&&it.name==='MAIN COMP')c=it;}
  out('COMP '+c.name);var l=c.layer('CONTROL');out('LAYER '+l.name);var effects=l.property('ADBE Effect Parade');out('FX COUNT '+effects.numProperties);
  for(var i=1;i<=effects.numProperties;i++)out('EFFECT '+i+' '+effects.property(i).name+' '+effects.property(i).matchName);
  var col=effects.property(6);out('GROUP '+col.name+' '+col.numProperties);
  var p=col.property(1);out('PROPERTY '+p.name+' '+p.matchName);out('KEYS '+p.numKeys);
  try{out('VALUE '+p.value);}catch(e){out('VALUE ERROR '+e);}
  try{p.setValue([0,.407843137254902,1,1]);out('SET4 OK');}catch(e){out('SET4 ERROR '+e);}
  try{p.setValue([0,.407843137254902,1]);out('SET3 OK');}catch(e){out('SET3 ERROR '+e);}
 }catch(e){out('ERROR '+e+' LINE '+e.line);}
 f.close();
})();
