import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
# Warm candle lights sitting on the flames (positions from the blender report + 04 PLACE / 05 DECOR).
# (x, y, z, candela, radius)
LIGHTS = [
    (1050, -1050, 162, 6.0, 900),     # tall candle stand, SE corner (flames at local z 1.46-1.56)
    (615, -1032, 118, 3.0, 500),      # desk candle (desk at 560,-1020; flame local 0.55,0.12,1.12 -> UE y flipped)
    (-980, -560, 30, 2.0, 350),       # floor candles, west
    (650, -700, 30, 2.0, 350),        # floor candles, edge of the rug
    (500, -1164, 275, 4.0, 700),      # wall sconces (05 DECOR): flame 24 cm off the wall, 45 cm above the decor origin
    (100, 1164, 275, 4.0, 700),
    (-1164, 250, 275, 4.0, 700),
    (1164, 250, 275, 4.0, 700),
]
COLOR = {'r': 1.0, 'g': 0.62, 'b': 0.3, 'a': 1.0}   # linear 0-1

def run():
    for a in call('scene.SceneTools.find_actors', {'name': 'LB_Light_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for k, (x, y, z, cd, r) in enumerate(LIGHTS):
        a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': 'LB_Light_%02d' % k,
                 'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.LightComponent0'), 'values': json.dumps(
            {'intensityUnits': 'Candelas', 'intensity': cd, 'attenuationRadius': r, 'lightColor': COLOR,
             'sourceRadius': 3, 'castShadows': True, 'volumetricScatteringIntensity': 1.5})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'lights': len(LIGHTS)}
