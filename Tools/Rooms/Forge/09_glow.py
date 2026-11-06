import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
P = '/Game/Props/Forge/'
# The FBX import does not carry blender emission, so the glow is wired here: a constant colour into Emissive Color.
# Values are emissive brightness against the night exposure (EV 0.6 in 06_lighting). The glass must out-shine the lamp-lit wall behind it (capture pixel check: wall ~ 217,201,186).
# All glow parts are unlit (lit, their base colour catches the nearby point light and washes out to white - mine lesson).
# (r, g, b, strength, unlit)
GLOW = {
    'M_FG_Molten':  (1.0, 0.45, 0.08, 2.0, True),    # molten metal in the floor channels
    'M_FG_Fire':    (1.0, 0.55, 0.15, 3.0, True),    # furnace mouth fire
    'M_FG_Coal':    (1.0, 0.30, 0.05, 1.2, True),    # glowing coals in braziers
    'M_FG_Glow':    (1.0, 0.40, 0.10, 0.8, True),    # warm glow behind the wall vent grates
}

def run():
    out = {}
    for m, (r, g, b, k, unlit) in GLOW.items():
        mat = ref(P + m + '.' + m)
        call('object.ObjectTools.set_properties', {'instance': mat, 'values': json.dumps(
            {'shadingModel': 'MSM_Unlit' if unlit else 'MSM_DefaultLit', 'twoSided': unlit})})
        src = call('material.MaterialTools.get_property_input', {'material': mat, 'material_property': 'MP_EmissiveColor'})
        node = src.get('expression')  # dict with refPath, or the string 'None' when unwired
        if not isinstance(node, dict) or 'Constant3Vector' not in node['refPath']:
            node = call('material.MaterialTools.add_expression', {'material_or_function': mat,
                        'expression_class': ref('/Script/Engine.MaterialExpressionConstant3Vector'), 'x': -400, 'y': 300})
            call('material.MaterialTools.connect_to_output', {'expression': node, 'output_name': '', 'material_property': 'MP_EmissiveColor'})
        call('object.ObjectTools.set_properties', {'instance': node, 'values': json.dumps({'constant': {'r': r * k, 'g': g * k, 'b': b * k, 'a': 1}})})
        call('material.MaterialTools.recompile', {'material_or_function': mat})
        out[m] = node['refPath'].split('.')[-1]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
