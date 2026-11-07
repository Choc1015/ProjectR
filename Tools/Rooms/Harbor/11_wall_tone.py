import json
# Harbor walls (review 2026-11-07: "walls messy"): the wall boards alternate M_HB_PlankLight / M_HB_Plank / M_HB_PlankDark,
# which reads as loud horizontal stripes. Pull Light and Dark toward the middle plank colour (props using them calm down too).
# NOTE: cumulative - each run pulls again. The blender colours in SourceArt/Harbor_Props.blend stay as the originals.
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
BASE = 'Plank'
PULL = {'PlankLight': 0.6, 'PlankDark': 0.6}

def node(mat):   # imported FBX colours are MaterialExpressionVectorParameter (defaultValue)
    src = call('material.MaterialTools.get_property_input', {'material': mat, 'material_property': 'MP_BaseColor'})
    return src['expression']

def col(n):
    p = call('object.ObjectTools.get_properties', {'instance': n, 'properties': ['defaultValue']})
    p = json.loads(p) if isinstance(p, str) else p
    return p['defaultValue']

def run():
    m = lambda k: ref('/Game/Props/Harbor/M_HB_%s.M_HB_%s' % (k, k))
    a = col(node(m(BASE)))
    out = {}
    for k, t in PULL.items():
        n = node(m(k)); c = col(n)
        nc = {ch: c[ch] + (a[ch] - c[ch]) * t for ch in ('r', 'g', 'b')}; nc['a'] = 1
        call('object.ObjectTools.set_properties', {'instance': n, 'values': json.dumps({'defaultValue': nc})})
        call('material.MaterialTools.recompile', {'material_or_function': m(k)})
        out[k] = [round(c[ch], 3) for ch in ('r', 'g', 'b')]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['base'] = [round(a[ch], 3) for ch in ('r', 'g', 'b')]
    return out
