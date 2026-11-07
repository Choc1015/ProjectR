import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
LV = '/Game/Maps/Rooms/L_Room_Market'
# DevMap actors that don't belong in a room (training dummy, dev floor)
DROP = ('TrainingDummy', 'Floor')

def run():
    out = {}
    try:
        out['dup'] = call('asset.AssetTools.duplicate', {'path': '/Game/Maps/DevMap', 'new_path': LV})
        call('asset.AssetTools.save_assets', {'asset_paths': []})
    except Exception as e:
        out['dup'] = 'exists? ' + str(e)[:80]
    call('scene.SceneTools.load_level', {'level_path': LV})
    names = []
    for a in call('scene.SceneTools.find_actors', {'name': '', 'tag': '', 'collision_channels': []}):
        n = a['refPath'].split('.')[-1]
        if n.startswith('MK_'):
            continue
        if any(d in n for d in DROP):
            call('scene.SceneTools.remove_from_scene', {'actor': a})
            n = 'REMOVED ' + n
        names.append(n)
    # player starts on the -X side facing the exit (+X)
    ps = call('scene.SceneTools.find_actors', {'name': 'PlayerStart', 'tag': '', 'collision_channels': []})
    if ps:
        call('actor.ActorTools.set_actor_transform', {'actor': ps[0], 'xform': {'location': {'x': -900, 'y': 0, 'z': 92},
             'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['actors'] = names
    return out
