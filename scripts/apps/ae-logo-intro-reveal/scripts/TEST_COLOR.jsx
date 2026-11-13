(function(){
 var c;for(var i=1;i<=app.project.numItems;i++)if(app.project.item(i).name==='MAIN COMP')c=app.project.item(i);
 var r=[];
 try{
 var p=c.layer('CONTROL').property('ADBE Effect Parade').property('Logo line color').property(1);
 r.push('KEYS '+p.numKeys+' VALUE '+p.value+' TYPE '+p.propertyValueType);
 for(var k=1;k<=p.numKeys;k++)r.push('KEY '+k+' '+p.keyTime(k)+' '+p.keyValue(k));
 try {if(p.numKeys)p.setValueAtTime(0,[0,0.407843137254902,1,1]);else p.setValue([0,0.407843137254902,1,1]);r.push('FOUR VALUES OK');}catch(e){r.push('FOUR ERROR '+e.toString());}
 }catch(e){r.push('ERROR '+e.toString()+' line '+e.line);}
 var f=new File('F:/video AE/OPA-Blueprint-OPA/QA/color-test.txt');f.open('w');f.write(r.join('\n'));f.close();
})();
