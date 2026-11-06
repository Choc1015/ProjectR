import json
E = 'editor_toolset.toolsets.'
P = 'projectr_toolset.toolsets.animation_asset.AnimationAssetTools.'
def call(n, a): return execute_tool(n, json.dumps(a))['returnValue']
# 스태프 기본 공격 모션만 다시 임포트한다(arms_only.py로 다시 내보낸 뒤). 몽타주 경로는 무기 표가 쓰는 그대로.
ANIM, MONT = '/Game/Characters/Player/Animations', '/Game/Characters/Player/Montages'
HIT = 0.6    # arms_only.py가 알려 준 hit_sec_30fps
RATE = 0.5   # 몽타주 재생 배율(1 = 원래 속도). 공격 속도 스탯과 곱해진다

def delete(path):
    try:
        call(E + 'asset.AssetTools.delete', {'path': path})
    except Exception:
        pass

def run():
    delete(MONT + '/AM_Staff_Attack')
    delete(ANIM + '/A_Staff_Attack')
    a = call(P + 'import_animation', {'folder_path': ANIM, 'asset_name': 'A_Staff_Attack',
             'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Export/A_Staff_Attack_ArmsOnly.fbx',
             'skeleton': {'refPath': '/Game/Characters/Player/SK_Player_Skeleton.SK_Player_Skeleton'},
             'uniform_scale': 100.0, 'replace_existing': False})
    m = call(P + 'create_montage', {'folder_path': MONT, 'asset_name': 'AM_Staff_Attack', 'animation': a})
    call(P + 'set_montage_notify', {'montage': m, 'notify_name': 'Hit', 'time': HIT})
    call(E + 'object.ObjectTools.set_properties', {'instance': m, 'values': json.dumps({'rateScale': RATE})})
    rate = call(E + 'object.ObjectTools.get_properties', {'instance': m, 'properties': ['rateScale']})
    length = call(E + 'object.ObjectTools.get_properties', {'instance': {'refPath': '/Game/Characters/Player/Animations/A_Staff_Attack.A_Staff_Attack'}, 'properties': ['sequenceLength']})
    call(E + 'asset.AssetTools.save_assets', {'asset_paths': []})
    return {'length': str(length)[:80], 'rate': str(rate)[:80]}
