(function () {
  function q(s) { return '"' + String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\r/g,'\\r').replace(/\n/g,'\\n') + '"'; }
  var p = app.project;
  var s = '{"version":'+q(app.version)+',"file":'+(p&&p.file?q(p.file.fsName):'null')+',"dirty":'+(p?String(p.dirty):'null')+',"numItems":'+(p?p.numItems:0)+',"activeItem":'+(p&&p.activeItem?q(p.activeItem.name):'null')+',"scriptSecurity":'+app.preferences.getPrefAsLong('Main Pref Section','Pref_SCRIPTING_FILE_NETWORK_SECURITY')+'}';
  var d = new Folder('D:/Vibe Coding/Motion Claude/research/ae-text-audit-2026-10-21/raw'); d.create();
  var f = new File(d.fsName+'/live-status.json'); f.encoding='UTF-8'; if(f.open('w')){f.write(s);f.close();}
})();
