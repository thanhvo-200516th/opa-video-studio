(function(){
 var ROOT='F:/video AE/OPA-Blueprint-OPA',P=app.project,D=__OPA_PATH_DATA__,r=[];
 function find(n){for(var i=1;i<=P.numItems;i++)if(P.item(i).name.replace(/^\s+|\s+$/g,'')===n)return P.item(i);var names=[];for(var j=1;j<=P.numItems;j++)names.push(P.item(j).name);throw Error(n+' missing | items='+P.numItems+' | '+names.join(' / '));}
 function prop(l,n){return l.property('ADBE Transform Group').property(n);}
 function key(p,ts,vs){for(var i=0;i<ts.length;i++)p.setValueAtTime(ts[i],vs[i]);}
 if(!P.file||P.file.fsName.replace(/\\/g,'/').indexOf(ROOT+'/')!==0)return;
 try{
  var main=find('MAIN COMP'),logo=find('YOUR LOGO');
  main.layer('MOTION BLUR').enabled=false;
  main.layer('MOTION BLUR').comment='Pixel Motion Blur optical-flow pass disabled for clear linework and faster rendering. Original effect remains here and can be enabled manually.';
  var cam=main.layer('CONTROL').property('ADBE Effect Parade').property('Camera lens blur').property(1);
  key(cam,[0,3.4,5.7,6.7],[10,10,4,0]);
 }catch(ignore){}
 try{
  var main=find('MAIN COMP'),logo=find('YOUR LOGO');
  for(var ri=logo.numLayers;ri>=1;ri--)if(/^OPA_LIGHT_PASS_/.test(logo.layer(ri).name))logo.layer(ri).remove();
  for(var gi=0;gi<D.letters.length;gi++){
   var l=logo.layers.addShape();l.name='OPA_LIGHT_PASS_'+D.letters[gi].name;l.label=9;prop(l,'ADBE Position').setValue([750,750]);prop(l,'ADBE Scale').setValue([1360/732*100,1360/732*100]);l.inPoint=6;l.outPoint=7.3;
   var vg=l.property('ADBE Root Vectors Group');
   for(var pi=0;pi<D.letters[gi].paths.length;pi++){
    var pg=vg.addProperty('ADBE Vector Shape - Group'),s=new Shape(),pts=D.letters[gi].paths[pi],vv=[],ins=[],outs=[];s.closed=true;
    for(var k=0;k<pts.length;k++){vv.push([pts[k][0]-366,pts[k][1]-110.5]);ins.push([0,0]);outs.push([0,0]);}s.vertices=vv;s.inTangents=ins;s.outTangents=outs;pg.property('ADBE Vector Shape').setValue(s);
   }
   var fill=vg.addProperty('ADBE Vector Graphic - Fill');fill.property('ADBE Vector Fill Color').setValue([1,1,1]);fill.property('ADBE Vector Fill Rule').setValue(2);
   var mask=l.property('ADBE Mask Parade').addProperty('ADBE Mask Atom');mask.name='LIGHT_SWEEP / Editable path';var a=new Shape(),b=new Shape();a.vertices=[[-610,-300],[-470,-300],[-280,300],[-420,300]];b.vertices=[[430,-300],[570,-300],[760,300],[620,300]];a.closed=b.closed=true;a.inTangents=a.outTangents=b.inTangents=b.outTangents=[[0,0],[0,0],[0,0],[0,0]];key(mask.property('ADBE Mask Shape'),[6.05,7.2],[a,b]);mask.property('ADBE Mask Feather').setValue([22,22]);key(prop(l,'ADBE Opacity'),[6,6.2,7.05,7.3],[0,52,52,0]);
  }
  while(P.renderQueue.numItems)P.renderQueue.item(1).remove();
  r.push('AE '+app.version);r.push('PROJECT '+P.file.fsName);r.push('ITEM_COUNT '+P.numItems);
  var comps=0,shapes=0,texts=0,exprs=0,errs=0;
  function scan(p){if(p.numProperties){for(var x=1;x<=p.numProperties;x++)scan(p.property(x));}else if(p.canSetExpression&&p.expression){exprs++;try{if(p.expressionError){errs++;r.push('EXPRESSION_ERROR '+p.expressionError);}}catch(e){r.push('EXPRESSION_READ '+e);}}}
  for(var ii=1;ii<=P.numItems;ii++){
   var it=P.item(ii);if(it instanceof FootageItem&&it.file)r.push('FOOTAGE '+it.name+' | '+it.file.fsName+' | MISSING '+it.footageMissing);
   if(it instanceof CompItem){comps++;r.push('COMP '+it.name+' | '+it.width+'x'+it.height+' | '+it.duration+'s | '+it.numLayers+' layers');for(var jj=1;jj<=it.numLayers;jj++){var ly=it.layer(jj);if(ly instanceof ShapeLayer)shapes++;if(ly instanceof TextLayer)texts++;scan(ly);}}
  }
  r.push('TOTAL comps='+comps+' shapes='+shapes+' text='+texts+' expressions='+exprs+' expression_errors='+errs);
  var f=new File(ROOT+'/QA/final-project-audit.txt');f.open('w');f.write(r.join('\n'));f.close();
  P.save(new File(ROOT+'/OPA-Blueprint-OPA.aep'));P.save(new File(ROOT+'/Source/OPA-Blueprint-OPA-FINAL.aepx'));P.save(new File(ROOT+'/OPA-Blueprint-OPA.aep'));
 }catch(e){var f=new File(ROOT+'/QA/final-polish-error.txt');f.open('w');f.write(e.toString()+'\nLine '+e.line);f.close();}
})();
