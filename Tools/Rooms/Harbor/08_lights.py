import json
# Moonlit-night harbor (review 2026-11-07): the room had no fire at all, so warm wall lanterns are borrowed from the chapel
# (SM_CP_WallLantern - its flame material is already emissive from Chapel/09_glow) and each gets a warm point light.
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
FACE = 1190
# (side, t along the wall, z) - kept off the 05 decor; two frame the entrance (W) and one sits beside the exit (E)
LANTERNS = [('S', 650, 260), ('N', -575, 260), ('W', -380, 250), ('W', 380, 250), ('E', 380, 250)]
LIGHT = {'cd': 16.0, 'radius': 900, 'out': 30, 'color': {'r': 1.0, 'g': 0.62, 'b': 0.3, 'a': 1.0}}   # same warm as the chapel candles

def run():
    for p in ('HB_Lantern_', 'HB_Light_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a})
    for k, (side, t, z) in enumerate(LANTERNS):
        yaw, pos = SIDES[side]
        x, y = pos(t, FACE)
        lan = call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': '/Game/Props/Chapel/SM_CP_WallLantern', 'name': 'HB_Lantern_%02d' % k,
                   'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        b = call('actor.ActorTools.get_actor_bounds', {'actor': lan})
        cx, cy, cz = [(b['min'][c] + b['max'][c]) / 2 for c in ('x', 'y', 'z')]
        lx, ly = pos(t, FACE - LIGHT['out'])   # light a little in front of the lantern so the wall does not swallow it
        a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': 'HB_Light_%02d' % k,
                 'xform': {'location': {'x': lx, 'y': ly, 'z': cz}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.LightComponent0'), 'values': json.dumps(
            {'intensityUnits': 'Candelas', 'intensity': LIGHT['cd'], 'attenuationRadius': LIGHT['radius'], 'lightColor': LIGHT['color'],
             'sourceRadius': 3, 'castShadows': True, 'volumetricScatteringIntensity': 1.5})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'lanterns': len(LANTERNS)}
