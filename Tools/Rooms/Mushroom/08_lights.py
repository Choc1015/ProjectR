import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
# Coloured point lights inside the glowing mushroom clusters (same idea as the mine lanterns / forge braziers).
# (x, y, z, candela, radius, colour linear 0-1) - positions match 04_props PLACE; z is under the big caps
LIGHTS = [
    (-950, 900, 150, 8.0, 1000, (1.0, 0.6, 0.25)),     # amber cluster NW
    (-1000, -950, 130, 6.0, 900, (1.0, 0.6, 0.25)),    # amber cluster SW (scale 0.85)
    (1000, 950, 130, 7.0, 1000, (1.0, 0.5, 0.6)),      # pink cluster NE
    (980, -1000, 150, 7.0, 1000, (0.35, 0.9, 0.8)),    # teal cluster SE
    (750, 1000, 180, 3.0, 500, (1.0, 0.75, 0.35)),     # seed pod string
]

def run():
    for a in call('scene.SceneTools.find_actors', {'name': 'MU_Light_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for k, (x, y, z, cd, r, (cr, cg, cb)) in enumerate(LIGHTS):
        a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': 'MU_Light_%02d' % k,
                 'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.LightComponent0'), 'values': json.dumps(
            {'intensityUnits': 'Candelas', 'intensity': cd, 'attenuationRadius': r, 'lightColor': {'r': cr, 'g': cg, 'b': cb, 'a': 1.0},
             'sourceRadius': 20, 'castShadows': True, 'volumetricScatteringIntensity': 2.0})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'lights': len(LIGHTS)}
