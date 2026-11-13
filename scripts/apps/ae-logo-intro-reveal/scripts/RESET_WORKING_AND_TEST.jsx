(function(){
 var root='F:/video AE/OPA-Blueprint-OPA',p=app.project;
 if(!p.file||p.file.fsName.replace(/\\/g,'/').indexOf(root+'/')!==0)return;
 p.close(CloseOptions.DO_NOT_SAVE_CHANGES);
 p=app.open(new File(root+'/Source/Template-Converted-Before-OPA.aep'));
 var c;for(var i=1;i<=p.numItems;i++)if(p.item(i).name==='MAIN COMP')c=p.item(i);
 var prop=c.layer('CONTROL').property('ADBE Effect Parade').property('Logo line color').property(1),r=[];
 try{r.push('NUMKEYS '+prop.numKeys);}catch(e){r.push('NUMKEYS ERROR '+e);}
 try{r.push('TYPE '+prop.propertyValueType);}catch(e){r.push('TYPE ERROR '+e);}
 try{r.push('ORIGINAL '+prop.value);}catch(e){r.push('VALUE ERROR '+e);}
 try{if(prop.numKeys){for(var k=1;k<=prop.numKeys;k++)prop.setValueAtKey(k,[0,.407843137254902,1,1]);}else prop.setValue([0,.407843137254902,1,1]);r.push('SET_RGBA OK');}catch(e){r.push('SET_RGBA ERROR '+e);}
 var f=new File(root+'/QA/color-baseline-test.txt');f.open('w');f.write(r.join('\n'));f.close();
})();
