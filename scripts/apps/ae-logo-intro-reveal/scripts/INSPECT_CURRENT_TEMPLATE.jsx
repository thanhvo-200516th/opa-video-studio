(function(){
 var p=app.project,root='F:/video AE/OPA-Blueprint-OPA';
 if(!p||!p.numItems){alert('No template project is open.');return;}
 function clean(v){return String(v).replace(/[\t\r\n]+/g,' ');}
 var lines=['OPA_BLUEPRINT_TEMPLATE_REPORT','AE '+app.version,'Items '+p.numItems];
 function dump(prop,prefix,depth){
  if(depth>2)return;
  var val='';try{val=prop.value;if(val instanceof TextDocument)val=val.text;else if(val instanceof Array)val='['+val.join(',')+']';}catch(e){}
  var expr='';try{if(prop.canSetExpression&&prop.expression)expr=prop.expression;}catch(e){}
  lines.push(prefix+clean(prop.name)+' | '+clean(prop.matchName)+' | '+clean(val)+' | EXPR '+clean(expr));
  if(prop.numProperties)for(var x=1;x<=prop.numProperties;x++)dump(prop.property(x),prefix+'  ',depth+1);
 }
 for(var i=1;i<=p.numItems;i++){
  var item=p.item(i);
  if(item instanceof CompItem){
   lines.push('COMP\t'+item.name+'\t'+item.width+'x'+item.height+'\t'+item.duration+'\t'+item.frameRate+'\t'+item.numLayers);
   for(var j=1;j<=item.numLayers;j++){
    var l=item.layer(j);lines.push('LAYER\t'+l.index+'\t'+l.name+'\tSOURCE '+(l.source?l.source.name:'')+'\tENABLED '+l.enabled+'\tIN '+l.inPoint+'\tOUT '+l.outPoint);
    if(l instanceof TextLayer)lines.push('TEXT '+l.property('ADBE Text Properties').property('ADBE Text Document').value.text);
    if(/MAIN COMP|YOUR LOGO|YOUR TEXT|ALL RULERS|RULER/.test(item.name)){
     if(l.property('ADBE Effect Parade'))dump(l.property('ADBE Effect Parade'),' FX ',0);
     dump(l.property('ADBE Transform Group'),' TR ',0);
    }
   }
  }else if(item instanceof FootageItem)lines.push('FOOTAGE\t'+item.name+'\t'+(item.file?item.file.fsName:'SOLID')+'\tMISSING '+item.footageMissing);
 }
 var out=new File(root+'/QA/template-inspection.txt');out.encoding='UTF-8';
 try{if(out.open('w')){out.write(lines.join('\n'));out.close();}}catch(e){}
 var report=p.items.addFolder('99_OPA_INSPECTION');
 var encoded=encodeURIComponent(lines.join('\n'));
 for(var at=0,part=0;at<encoded.length;at+=12000,part++){
  var chunk=p.items.addFolder('REPORT_PART_'+('000'+part).slice(-3));chunk.parentFolder=report;chunk.comment=encoded.substr(at,12000);
 }
 p.save(new File(root+'/Source/Blueprint-Template-INSPECTED.aepx'));
 p.save(new File(root+'/OPA-Blueprint-OPA.aep'));
 alert('OPA template inspection saved.');
})();
