import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
P = '/Game/Weapons/Staff/'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Weapons/'
MESHES = ['SM_Staff', 'SM_StaffBolt', 'SM_Fireball']
# FBX는 블렌더 발광을 안 가져와서 여기서 Emissive Color에 상수 색을 꽂는다. (r, g, b, 세기, 언릿)
GLOW = {
    'M_Staff_Amber':   (1.0, 0.55, 0.15, 0.6, False),  # 스태프 수정: 조명 위에 은은하게
    'M_Staff_Bolt':    (1.0, 0.65, 0.25, 6.0, True),   # 기본 공격 탄
    'M_Fireball':      (1.0, 0.40, 0.10, 8.0, True),   # 화염구 겉
    'M_Fireball_Core': (1.0, 0.80, 0.30, 12.0, True),  # 화염구 속
}

def run():
    out = {'import': {}, 'glow': {}}
    for n in MESHES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Weapons/Staff', 'asset_name': n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out['import'][n] = 'ok'
        except Exception as e:
            out['import'][n] = str(e)[:160]
    for m, (r, g, b, k, unlit) in GLOW.items():
        mat = ref(P + m + '.' + m)
        try:
            call('object.ObjectTools.set_properties', {'instance': mat, 'values': json.dumps(
                {'shadingModel': 'MSM_Unlit' if unlit else 'MSM_DefaultLit'})})
            src = call('material.MaterialTools.get_property_input', {'material': mat, 'material_property': 'MP_EmissiveColor'})
            node = src['expression'] if 'expression' in src else 'None'
            if not isinstance(node, dict) or 'Constant3Vector' not in node['refPath']:
                node = call('material.MaterialTools.add_expression', {'material_or_function': mat,
                            'expression_class': ref('/Script/Engine.MaterialExpressionConstant3Vector'), 'x': -400, 'y': 300})
                call('material.MaterialTools.connect_to_output', {'expression': node, 'output_name': '', 'material_property': 'MP_EmissiveColor'})
            call('object.ObjectTools.set_properties', {'instance': node, 'values': json.dumps({'constant': {'r': r * k, 'g': g * k, 'b': b * k, 'a': 1}})})
            call('material.MaterialTools.recompile', {'material_or_function': mat})
            out['glow'][m] = 'ok'
        except Exception as e:
            out['glow'][m] = str(e)[:160]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
