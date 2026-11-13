from pathlib import Path
import xml.etree.ElementTree as ET
import struct, json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Source/OPA-Blueprint-OPA.aepx'
OUTPUT=ROOT/'Source/OPA-Blueprint-OPA-BRAND.aepx'
NS='http://www.adobe.com/products/aftereffects'
ET.register_namespace('',NS)
N={'a':NS}
tree=ET.parse(SOURCE)
palette={
 'Logo line color':[0,104/255,1],
 'Rulers color':[0,104/255,1],
 'Auxiliary lines color':[.42,.59,.85],
 'Shadows color':[.12,.24,.43],
 'Grid color':[.78,.84,.93],
 'Text color':[.07,.11,.18],
 'AG Color':[0,104/255,1],
}
patches=[]
for group in tree.getroot().iter(f'{{{NS}}}tdgp'):
    name_node=group.find('a:tdsn/a:string',N)
    name=(name_node.text or '').strip() if name_node is not None else ''
    if name not in palette and name!='Background color':continue
    for prop in group.findall('a:tdbs',N):
        p_name_node=prop.find('a:tdsn/a:string',N)
        p_name=(p_name_node.text or '').strip() if p_name_node is not None else ''
        col=None
        if name in palette and p_name=='Color':col=palette[name]
        elif name=='Background color' and p_name=='Map Black To':col=[.945,.963,.99]
        elif name=='Background color' and p_name=='Map White To':col=[.985,.99,1]
        if col is None:continue
        data=prop.find('a:cdat',N)
        if data is None:raise RuntimeError(f'No color data for {name}/{p_name}')
        blob=bytes.fromhex(data.attrib['bdata'])
        before=struct.unpack('>4d',blob[:32])
        if abs(before[0]-255)>1e-6:raise RuntimeError(f'Unexpected native color scale: {before}')
        after=[255]+[x*255 for x in col]
        data.set('bdata',(struct.pack('>4d',*after)+blob[32:]).hex())
        patches.append({'effect':name,'parameter':p_name,'before_argb_255':before,'after_argb_255':after})
if len(patches)<9:raise RuntimeError(f'Too few color patches: {len(patches)}')
tree.write(OUTPUT,encoding='utf-8',xml_declaration=True)
(ROOT/'QA/brand-color-changes.json').write_text(json.dumps(patches,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUTPUT),'color_parameters_updated':len(patches)}))
