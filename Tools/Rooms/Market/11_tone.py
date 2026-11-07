import json
# Colour tweaks after the first capture: the packed earth #A4865E read as orange under the warm dawn light -> calmer tan.
# Values are linear (imported FBX colours are MaterialExpressionVectorParameter.defaultValue). Not cumulative - safe to re-run.
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
TONE = {
    'Ground': {'r': 0.40, 'g': 0.34, 'b': 0.24, 'a': 1},     # ~ #A99E86
}
def run():
    out = {}
    for m, c in TONE.items():
        mat = {'refPath': '/Game/Props/Market/M_MK_%s.M_MK_%s' % (m, m)}
        src = call('material.MaterialTools.get_property_input', {'material': mat, 'material_property': 'MP_BaseColor'})
        call('object.ObjectTools.set_properties', {'instance': src['expression'], 'values': json.dumps({'defaultValue': c})})
        call('material.MaterialTools.recompile', {'material_or_function': mat})
        out[m] = 'ok'
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
