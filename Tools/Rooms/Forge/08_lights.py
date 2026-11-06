import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
# Warm point lights sitting on the glowing models (same idea as the mine lanterns: the light is where the glow is).
# (x, y, z, candela, radius) - furnace mouth, the three floor braziers, the three wall braziers, the two channel runs
FURNACE = [(-200, 1060, 120, 20.0, 1500)]
BRAZIERS = [(1000, 1000, 110, 8.0, 900), (1050, -1050, 110, 8.0, 900), (-780, -1050, 110, 8.0, 900)]
WALL_BRAZIERS = [(-1000, 1150, 290, 6.0, 800), (-1150, 600, 290, 6.0, 800), (1150, 300, 290, 6.0, 800)]   # from 05 DECOR
CHANNELS = [(-950, -800, 30, 4.0, 500), (600, -950, 30, 4.0, 500)]
COLOR = {'r': 255, 'g': 140, 'b': 60, 'a': 255}

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
