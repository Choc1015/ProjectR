import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
P = '/Game/Props/Mine/'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Mine/SM_MN_'
REIMPORT = ['Lantern', 'LanternChain', 'Workbench', 'WallShelf']   # glass turned emissive for the night version
# after this script, run 04_props and 05_wall_decor again (they put the workbench / shelves back)

FLAME = {'Lantern': -0.455, 'LanternChain': -1.692}   # flame centre below the mesh origin (m) - from the blender report
# lanterns hanging under the support frame crossbeams (same (side, t) as FRAMES in 03_shell), beam underside z=600,
# beam centre 43 cm in front of the wall line
FRAMES = [('S', -800), ('S', 400), ('N', -400), ('N', 800), ('W', -800), ('W', 800), ('E', -800), ('E', 400)]
SIDES = {'S': lambda t, d: (t, -d), 'N': lambda t, d: (-t, d), 'W': lambda t, d: (-d, -t), 'E': lambda t, d: (d, t)}
# long-chain lanterns from the ceiling beams (rows y=-300 / 700, beam underside z=765) to light the fighting floor
CEILING = [(-450, -300), (500, -300), (-100, 700)]
# small fills at the lit glass of the workbench / shelf lanterns (x, y, z)
SMALL = [(1120, -400, 130), (400, -1140, 200), (1140, 800, 190)]

LAMP = {'cd': 12.0, 'radius': 1300, 'color': {'r': 255, 'g': 160, 'b': 80, 'a': 255}, 'scatter': 3.0}
FILL = {'cd': 3.0, 'radius': 350}

def xf(x, y, z, yaw=0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}

def light(name, x, y, z, cd, radius, shadows):
    a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': name, 'xform': xf(x, y, z)})
    comp = a['refPath'] + '.LightComponent0'
    vals = {'intensityUnits': 'Candelas', 'intensity': cd, 'attenuationRadius': radius, 'lightColor': LAMP['color'],
            'sourceRadius': 4, 'castShadows': shadows, 'volumetricScatteringIntensity': LAMP['scatter']}
    try:
        call('object.ObjectTools.set_properties', {'instance': ref(comp), 'values': json.dumps(vals)})
    except Exception as e:
        vals.pop('intensityUnits')
        call('object.ObjectTools.set_properties', {'instance': ref(comp), 'values': json.dumps(vals)})
        return 'units? ' + str(e)[:80]
    return 'ok'

def lamp(mesh, name, x, y, z, yaw):
    a = call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + mesh, 'name': name, 'xform': xf(x, y, z, yaw)})
    # the opaque glass would shadow its own light: the lantern mesh casts no shadow
    call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.StaticMeshComponent0'), 'values': json.dumps({'castShadow': False})})

def run():
    out = {'rm': 0}
    for p in ('MN_Lamp_', 'MN_LampLight_', 'MN_Prop_Workbench', 'MN_Decor_WallShelf'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for a in ['SM_MN_' + n for n in REIMPORT] + ['M_MN_Glass', 'M_MN_Flame']:
        try:
            call('asset.AssetTools.delete', {'path': P + a})
        except Exception:
            pass
    for n in REIMPORT:
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Mine', 'asset_name': 'SM_MN_' + n,
             'source_file': SRC + n + '.fbx', 'import_materials': True})
    k = 0
    for side, t in FRAMES:
        x, y = SIDES[side](t, 1157)
        lamp('SM_MN_Lantern', 'MN_Lamp_%02d' % k, x, y, 600, (k * 37) % 90)
        out['l%02d' % k] = light('MN_LampLight_%02d' % k, x, y, 600 + FLAME['Lantern'] * 100, LAMP['cd'], LAMP['radius'], True); k += 1
    for x, y in CEILING:
        lamp('SM_MN_LanternChain', 'MN_Lamp_%02d' % k, x, y, 765, (k * 53) % 90)
        out['l%02d' % k] = light('MN_LampLight_%02d' % k, x, y, 765 + FLAME['LanternChain'] * 100, LAMP['cd'], LAMP['radius'], True); k += 1
    for x, y, z in SMALL:
        out['l%02d' % k] = light('MN_LampLight_%02d' % k, x, y, z, FILL['cd'], FILL['radius'], False); k += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['lamps'] = k
    return out
