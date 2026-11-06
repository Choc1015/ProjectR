import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
# Warm point lights sitting on the glowing models (same idea as the mine lanterns: the light is where the glow is).
# (x, y, z, candela, radius) - furnace mouth, the three floor braziers, the three wall braziers, the two channel runs
FURNACE = [(-200, 1000, 90, 20.0, 1500)]   # fire face is 1.6-1.78 m in front of the wall (blender report), light 20 cm in front of it
BRAZIERS = [(1000, 1000, 110, 8.0, 900), (1050, -1050, 110, 8.0, 900), (-780, -1050, 110, 8.0, 900)]
WALL_BRAZIERS = [(-1000, 1158, 330, 6.0, 800), (-1158, 600, 330, 6.0, 800), (1158, 300, 330, 6.0, 800)]   # from 05 DECOR: bowl 30 cm out, rim at decor z+60, light just above the rim
CHANNELS = [(-950, -800, 30, 4.0, 500), (600, -950, 30, 4.0, 500)]
COLOR = {'r': 1.0, 'g': 0.5, 'b': 0.2, 'a': 1.0}   # linear 0-1: 0-255 values get clamped to white

def light(name, x, y, z, cd, radius, shadows):
    a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': name,
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.LightComponent0'), 'values': json.dumps(
        {'intensityUnits': 'Candelas', 'intensity': cd, 'attenuationRadius': radius, 'lightColor': COLOR,
         'sourceRadius': 10, 'castShadows': shadows, 'volumetricScatteringIntensity': 2.0})})

def run():
    n = 0
    for a in call('scene.SceneTools.find_actors', {'name': 'FG_Light_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    k = 0
    for group, shadows in ((FURNACE, True), (BRAZIERS, True), (WALL_BRAZIERS, True), (CHANNELS, False)):
        for x, y, z, cd, r in group:
            light('FG_Light_%02d' % k, x, y, z, cd, r, shadows); k += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'lights': k}
