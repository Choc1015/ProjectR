import json
# Deck tone (review 2026-11-07 follow-up): the three board tones + dark gap lines read as busy stripes in Unreal.
# Pull DeckB / DeckC / DeckGap toward the main Deck colour so the floor is one calm wood surface with faint board lines.
# Shared by the three deck rooms (Harbor, Mill, Library); the blender colours in SourceArt/<Theme>_Floor.blend stay as the originals.
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
ROOMS = [('Harbor', 'HB'), ('Mill', 'ML'), ('Library', 'LB')]
PULL = {'DeckB': 0.65, 'DeckC': 0.65, 'DeckGap': 0.45}   # 0 = keep, 1 = same as Deck
# NOTE: each run pulls again (cumulative) - re-import the decks (10_floor) before running it a second time
GAP_DARK = 0.8                                           # gap ends a little darker than the boards

def color_node(mat):   # imported FBX colours are MaterialExpressionVectorParameter (defaultValue)
    src = call('material.MaterialTools.get_property_input', {'material': mat, 'material_property': 'MP_BaseColor'})
    return src['expression'] if isinstance(src, dict) and isinstance(src.get('expression'), dict) else None

def get_col(node):
    p = call('object.ObjectTools.get_properties', {'instance': node, 'properties': ['defaultValue']})
    p = json.loads(p) if isinstance(p, str) else p
    return p['defaultValue']

def run():
    out = {}
    for theme, ab in ROOMS:
        base = '/Game/Props/%s/M_%s_' % (theme, ab)
        mats = {k: ref(base + k + '.M_%s_%s' % (ab, k)) for k in ('Deck', 'DeckB', 'DeckC', 'DeckGap')}
        nodes = {k: color_node(m) for k, m in mats.items()}
        if not all(nodes.values()):
            out[theme] = 'no constant node: ' + str([k for k, n in nodes.items() if not n]); continue
        a = get_col(nodes['Deck'])
        for k, t in PULL.items():
            c = get_col(nodes[k])
            d = GAP_DARK if k == 'DeckGap' else 1.0
            nc = {ch: (c[ch] + (a[ch] * d - c[ch]) * t) for ch in ('r', 'g', 'b')}
            nc['a'] = 1
            call('object.ObjectTools.set_properties', {'instance': nodes[k], 'values': json.dumps({'defaultValue': nc})})
            call('material.MaterialTools.recompile', {'material_or_function': mats[k]})
        out[theme] = 'ok'
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
