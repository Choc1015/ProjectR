import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
# Warm candle lights on the flames (positions from the blender report + 04 PLACE / 05 DECOR). (x, y, z, candela, radius)
LIGHTS = [
    (-350, 1050, 45, 3.0, 500),       # candle cluster beside the altar
    (0, 1060, 110, 4.0, 700),         # altar candles (flames at local x +-0.5, z 0.93)
    (-1000, 780, 35, 2.5, 450),       # candles at the angel
    (1000, -1050, 45, 3.0, 500),      # candle cluster SE
    (-650, 650, 30, 2.0, 350),        # small candles at the edge of the floor
    (-200, -1167, 300, 4.0, 700),     # wall candelabras: flames 25 cm off the wall, 60 cm above the decor origin
    (-600, 1167, 300, 4.0, 700),
    (1167, -1000, 295, 3.5, 650),
    (586, 1184, 245, 1.5, 300),       # candle in the saint niche
]
COLOR = {'r': 1.0, 'g': 0.62, 'b': 0.3, 'a': 1.0}   # linear 0-1

# moonlit night (06 EV 1.6, was 0.6): warm lights x4 / radius x1.5 so they still pop against the blue
GAIN = 4.0
RGAIN = 1.5   # wider warm pools

def run():
    for a in call('scene.SceneTools.find_actors', {'name': 'CP_Light_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for k, (x, y, z, cd, r) in enumerate(LIGHTS):
        a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': 'CP_Light_%02d' % k,
                 'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.LightComponent0'), 'values': json.dumps(
            {'intensityUnits': 'Candelas', 'intensity': cd * GAIN, 'attenuationRadius': r * RGAIN, 'lightColor': COLOR,
             'sourceRadius': 3, 'castShadows': True, 'volumetricScatteringIntensity': 1.5})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'lights': len(LIGHTS)}
