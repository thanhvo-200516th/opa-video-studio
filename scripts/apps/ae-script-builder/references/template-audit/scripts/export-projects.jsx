(function () {
 var BASE='D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21/raw';
 var dir=new Folder(BASE);dir.create();
 function quote(s){return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n').replace(/\t/g,'\\t').replace(/[\x00-\x1f]/g,function(c){return '\\u'+('0000'+c.charCodeAt(0).toString(16)).slice(-4);})+'"';}
 function json(v){if(v===null||v===undefined)return 'null';var t=typeof v;if(t==='string')return quote(v);if(t==='number')return isFinite(v)?String(v):'null';if(t==='boolean')return String(v);var a=[],i;if(v instanceof Array){for(i=0;i<v.length;i++)a.push(json(v[i]));return '['+a.join(',')+']';}for(var k in v)if(v.hasOwnProperty(k)&&typeof v[k]!=='function')a.push(quote(k)+':'+json(v[k]));return '{'+a.join(',')+'}';}
 function write(name,v){var f=new File(BASE+'/'+name);f.encoding='UTF-8';if(!f.open('w'))throw Error('Cannot write '+f.fsName);f.write(json(v));f.close();}
 function read(o,k,d){try{var v=o[k];return v===undefined?d:v;}catch(e){return d;}}
 function en(v){try{return String(v);}catch(e){return null;}}
 function value(v){
  if(v===null||v===undefined)return null;var t=typeof v;if(t==='string'||t==='boolean'||t==='number')return v;
  if(v instanceof Array){var a=[];for(var i=0;i<v.length;i++)a.push(value(v[i]));return a;}
  if(typeof TextDocument!=='undefined'&&v instanceof TextDocument){var td={kind:'TextDocument'};var names=['text','font','fontFamily','fontStyle','fontSize','applyFill','fillColor','applyStroke','strokeColor','strokeWidth','strokeOverFill','tracking','leading','autoLeading','baselineShift','horizontalScale','verticalScale','fauxBold','fauxItalic','allCaps','smallCaps','justification','boxText','boxTextSize','boxTextPos','firstBaseline','tsume'];for(var j=0;j<names.length;j++){var n=names[j];var tv=read(v,n,null);td[n]=(typeof tv==='object'?value(tv):typeof tv==='number'||typeof tv==='boolean'||typeof tv==='string'?tv:en(tv));}return td;}
  if(typeof Shape!=='undefined'&&v instanceof Shape)return {kind:'Shape',vertices:v.vertices,inTangents:v.inTangents,outTangents:v.outTangents,closed:v.closed};
  if(typeof MarkerValue!=='undefined'&&v instanceof MarkerValue)return {kind:'MarkerValue',comment:v.comment,duration:v.duration,chapter:v.chapter};
  return en(v);
 }
 function ease(a){var x=[];for(var i=0;i<a.length;i++)x.push({speed:a[i].speed,influence:a[i].influence});return x;}
 function prop(p,depth){
  var d={name:read(p,'name',''),matchName:read(p,'matchName',''),index:read(p,'propertyIndex',0),type:en(read(p,'propertyType',null))};
  if(depth>15)return d;
  if(p.propertyType!==PropertyType.PROPERTY){d.enabled=read(p,'enabled',null);d.children=[];for(var i=1;i<=p.numProperties;i++){try{d.children.push(prop(p.property(i),depth+1));}catch(e){d.children.push({index:i,error:String(e)});}}return d;}
  d.valueType=en(p.propertyValueType);d.units=read(p,'unitsText',null);d.spatial=read(p,'isSpatial',false);d.dimensionsSeparated=read(p,'dimensionsSeparated',false);d.separationFollower=read(p,'isSeparationFollower',false);
  try{d.value=value(p.value);}catch(e){d.valueError=String(e);}
  if(read(p,'canSetExpression',false)){d.expression=read(p,'expression','');d.expressionEnabled=read(p,'expressionEnabled',false);d.expressionError=read(p,'expressionError','');}
  var n=read(p,'numKeys',0);d.numKeys=n;
  if(n){d.keys=[];for(var k=1;k<=n;k++){var a={index:k,time:p.keyTime(k),value:value(p.keyValue(k))};
   try{a.inType=en(p.keyInInterpolationType(k));a.outType=en(p.keyOutInterpolationType(k));}catch(e){}
   try{a.inEase=ease(p.keyInTemporalEase(k));a.outEase=ease(p.keyOutTemporalEase(k));a.temporalAutoBezier=p.keyTemporalAutoBezier(k);a.temporalContinuous=p.keyTemporalContinuous(k);}catch(e){}
   if(d.spatial){try{a.inSpatial=p.keyInSpatialTangent(k);a.outSpatial=p.keyOutSpatialTangent(k);a.spatialAutoBezier=p.keySpatialAutoBezier(k);a.spatialContinuous=p.keySpatialContinuous(k);a.roving=p.keyRoving(k);}catch(e){}}
   d.keys.push(a);
  }}
  return d;
 }
 function layer(l,c){
  var d={index:l.index,id:read(l,'id',null),name:l.name,matchName:read(l,'matchName',null),enabled:l.enabled,solo:l.solo,shy:l.shy,locked:l.locked,label:l.label,parentIndex:l.parent?l.parent.index:null,startTime:l.startTime,inPoint:l.inPoint,outPoint:l.outPoint,stretch:l.stretch};
  var fields=['threeDLayer','threeDPerChar','motionBlur','adjustmentLayer','guideLayer','nullLayer','collapseTransformation','blendingMode','trackMatteType','hasTrackMatte','isTrackMatte','preserveTransparency','timeRemapEnabled','quality','samplingQuality','autoOrient','audioEnabled','hasAudio','hasVideo'];for(var i=0;i<fields.length;i++){var v=read(l,fields[i],null);d[fields[i]]=(typeof v==='number'||typeof v==='boolean')?v:en(v);}
  try{d.trackMatteLayerIndex=l.trackMatteLayer?l.trackMatteLayer.index:null;}catch(e){}
  try{if(l.source){d.sourceId=l.source.id;d.sourceName=l.source.name;d.sourceType=l.source instanceof CompItem?'CompItem':'FootageItem';}}catch(e){}
  d.properties=[];for(var p=1;p<=l.numProperties;p++){try{d.properties.push(prop(l.property(p),0));}catch(e){d.properties.push({index:p,error:String(e)});}}
  if(l instanceof TextLayer){d.textBounds=[];var times=[Math.max(0,l.inPoint),Math.min(c.duration-1/c.frameRate,Math.max(0,l.inPoint)+1)];for(var t=0;t<times.length;t++)try{d.textBounds.push({time:times[t],rect:l.sourceRectAtTime(times[t],false)});}catch(e){}}
  return d;
 }
 function exportProject(slug,path){
  write('progress.json',{slug:slug,stage:'opening',path:path});
  if(app.project)app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
  app.open(new File(path));
  var p=app.project;var d={slug:slug,source:path,version:app.version,numItems:p.numItems,bitsPerChannel:p.bitsPerChannel,workingSpace:read(p,'workingSpace',null),linearizeWorkingSpace:read(p,'linearizeWorkingSpace',null),items:[],errors:[]};
  for(var i=1;i<=p.numItems;i++){var item=p.item(i);var it={id:item.id,name:item.name,parentFolderId:item.parentFolder?item.parentFolder.id:null};
   if(item instanceof CompItem){it.kind='CompItem';it.width=item.width;it.height=item.height;it.pixelAspect=item.pixelAspect;it.duration=item.duration;it.frameRate=item.frameRate;it.displayStartTime=item.displayStartTime;it.bgColor=item.bgColor;it.motionBlur=item.motionBlur;it.shutterAngle=item.shutterAngle;it.shutterPhase=item.shutterPhase;it.renderer=read(item,'renderer',null);it.workAreaStart=item.workAreaStart;it.workAreaDuration=item.workAreaDuration;it.layers=[];for(var j=1;j<=item.numLayers;j++){try{it.layers.push(layer(item.layer(j),item));}catch(e){it.layers.push({index:j,error:String(e)});}}}
   else if(item instanceof FootageItem){it.kind='FootageItem';it.width=item.width;it.height=item.height;it.duration=item.duration;it.frameRate=item.frameRate;it.file=item.file?item.file.fsName:null;it.missing=read(item,'footageMissing',null);it.sourceKind=item.mainSource instanceof SolidSource?'SolidSource':item.mainSource instanceof PlaceholderSource?'PlaceholderSource':'FileSource';it.color=read(item.mainSource,'color',null);it.missingFootagePath=read(item.mainSource,'missingFootagePath',null);}
   else it.kind='FolderItem';
   d.items.push(it);if(i%25===0)write('progress.json',{slug:slug,stage:'exporting',item:i,total:p.numItems});
  }
  write(slug+'.json',d);write('progress.json',{slug:slug,stage:'done',items:p.numItems});
 }
 var p=app.project;
 if(p&&(p.numItems>0||p.file||p.dirty)){write('worker-refused.json',{reason:'Initial project is not empty. No project opened or closed.',items:p.numItems,file:p.file?p.file.fsName:null});return;}
 var tasks=[
 ['working-1','F:/video AE/save/1.aep'],
 ['template-current','F:/video AE/video/vertical-corporate-opener-2026-09-24-08-52-22-utc/Corporate Opener Mobile.aep'],
 ['template-23','F:/video AE/video/vertical-corporate-opener-2026-09-24-08-52-22-utc/Corporate Opener Mobile copy 23.x.aep'],
 ['working-untitled','F:/video AE/save/Untitled Project.aep'],
 ['autosave-1','F:/video AE/save/Adobe After Effects Auto-Save/Untitled Project auto-save 1.aep'],
 ['autosave-2','F:/video AE/save/Adobe After Effects Auto-Save/Untitled Project auto-save 2.aep']
 ];
 app.beginSuppressDialogs();
 var results=[];
 for(var t=0;t<tasks.length;t++){try{exportProject(tasks[t][0],tasks[t][1]);results.push({slug:tasks[t][0],ok:true});}catch(e){results.push({slug:tasks[t][0],ok:false,error:String(e),line:read(e,'line',null)});write(tasks[t][0]+'-error.json',results[results.length-1]);}}
 if(app.project)app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
 app.endSuppressDialogs(false);write('export-complete.json',results);app.quit();
})();
