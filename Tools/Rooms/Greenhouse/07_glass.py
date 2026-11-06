import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
# Roof glass becomes translucent so the sun comes through and the iron ribs throw shadows (wall glass stays opaque frosted).
MAT = '/Game/Props/Greenhouse/M_GH_GlassRoof.M_GH_GlassRoof'
OPACITY = 0.25

def run():
    mat = ref(MAT)
    call('object.ObjectTools.set_properties', {'instance': mat, 'values': json.dumps({'blendMode': 'BLEND_Translucent', 'twoSided': True})})
    src = call('material.MaterialTools.get_property_input', {'material': mat, 'material_property': 'MP_Opacity'})
    node = src['expression']
    if not isinstance(node, dict) or 'MaterialExpressionConstant' not in node['refPath']:
        node = call('material.MaterialTools.add_expression', {'material_or_function': mat,
                    'expression_class': ref('/Script/Engine.MaterialExpressionConstant'), 'x': -400, 'y': 400})
        call('material.MaterialTools.connect_to_output', {'expression': node, 'output_name': '', 'material_property': 'MP_Opacity'})
    call('object.ObjectTools.set_properties', {'instance': node, 'values': json.dumps({'r': OPACITY})})
    call('material.MaterialTools.recompile', {'material_or_function': mat})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'opacity_node': node['refPath'].split('.')[-1],
            'mat': call('object.ObjectTools.get_properties', {'instance': mat, 'properties': ['blendMode', 'twoSided']})}
