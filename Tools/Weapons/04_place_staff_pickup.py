import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
LV = '/Game/Maps/Rooms/L_Room_ForestTemple'
# 시작 지점(-950,0) 바로 앞 바닥에 스태프를 놓는다. 다시 돌리면 지우고 새로 놓는다.
def run():
    call('scene.SceneTools.load_level', {'level_path': LV})
    for a in call('scene.SceneTools.find_actors', {'name': 'WeaponPickup', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/ProjectR.WeaponPickup'}, 'name': 'WeaponPickup_Staff',
        'xform': {'location': {'x': -650, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    call('object.ObjectTools.set_properties', {'instance': a, 'values': json.dumps({'weaponId': 'Staff'})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'placed': a['refPath'].split('.')[-1]}
