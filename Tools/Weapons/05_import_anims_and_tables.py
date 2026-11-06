import json
E = 'editor_toolset.toolsets.'
P = 'projectr_toolset.toolsets.animation_asset.AnimationAssetTools.'
def call(n, a): return execute_tool(n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
SKEL = ref('/Game/Characters/Player/SK_Player_Skeleton.SK_Player_Skeleton')
EXP = 'C:/UnrealProject/ProjectR/SourceArt/Export/'
DATA = 'C:/UnrealProject/ProjectR/SourceArt/Data/'
ANIM = '/Game/Characters/Player/Animations'
MONT = '/Game/Characters/Player/Montages'
# (애니 이름, 팔만 남긴 FBX, 몽타주 이름, Hit 노티파이 초 또는 None)
JOBS = [('A_Staff_Attack', 'A_Staff_Attack_ArmsOnly', 'AM_Staff_Attack', 0.633),
        ('A_Skill_Fireball', 'A_Skill_Fireball_ArmsOnly', 'AM_Skill_Fireball', None)]
# 표: (에셋 이름, CSV, 행 구조체). 바꾸면 지우고 다시 임포트 → BP 참조도 다시 넣는다.
TABLES = [('DT_Weapons', 'Weapons.csv', '/Script/ProjectR.WeaponRow'), ('DT_Skills', 'Skills.csv', '/Script/ProjectR.SkillRow')]

def delete(path):
    try:
        call(E + 'asset.AssetTools.delete', {'path': path})
    except Exception:
        pass

def run():
    out = {}
    for anim, fbx, mont, hit in JOBS:
        delete(MONT + '/' + mont)
        delete(ANIM + '/' + anim)
        a = call(P + 'import_animation', {'folder_path': ANIM, 'asset_name': anim, 'source_file': EXP + fbx + '.fbx',
                 'skeleton': SKEL, 'uniform_scale': 100.0, 'replace_existing': False})
        m = call(P + 'create_montage', {'folder_path': MONT, 'asset_name': mont, 'animation': a})
        if hit is not None:
            call(P + 'set_montage_notify', {'montage': m, 'notify_name': 'Hit', 'time': hit})
        out[mont] = m['refPath'] if isinstance(m, dict) else str(m)[:100]
    for name, csv, schema in TABLES:
        delete('/Game/Data/' + name)
        t = call(E + 'data_table.DataTableTools.import_file', {'folder_path': '/Game/Data', 'asset_name': name,
                 'source_file': DATA + csv, 'schema': ref(schema)})
        out[name] = call(E + 'data_table.DataTableTools.list_rows', {'data_table': ref('/Game/Data/' + name + '.' + name)})
    call(E + 'object.ObjectTools.set_properties', {'instance': ref('/Game/Blueprints/BP_PlayerCharacter.Default__BP_PlayerCharacter_C:Skills'),
         'values': json.dumps({'skillTable': '/Game/Data/DT_Skills.DT_Skills'})})
    out['bp'] = call(E + 'object.ObjectTools.get_properties', {'instance': ref('/Game/Blueprints/BP_PlayerCharacter.Default__BP_PlayerCharacter_C:Skills'),
         'properties': ['skillTable']})
    call(E + 'asset.AssetTools.save_assets', {'asset_paths': []})
    return out
