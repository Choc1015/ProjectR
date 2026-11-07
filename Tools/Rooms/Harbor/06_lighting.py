import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
LV = '/Game/Maps/Rooms/L_Room_Harbor.L_Room_Harbor:PersistentLevel.'
def setp(path, vals):
    call('object.ObjectTools.set_properties', {'instance': ref(LV + path), 'values': json.dumps(vals)})

# tunables - MOONLIT NIGHT (review 2026-11-07, user picked "blue moonlight + fire"): make it feel dark without being dark.
# The whole room is lit by pale blue moon + blue sky and a few shadowless blue fill lights under the roof (MOONFILL),
# exposure is raised so floor and enemies read clearly; fires / lanterns (08 lights, 09 glow) are warm pools for contrast.
SUN = {'pitch': -50, 'yaw': 30, 'lux': 4.0, 'scatter': 2.0, 'color': {'r': 0.62, 'g': 0.74, 'b': 1.0, 'a': 1.0}}
FOG = {'density': 0.03, 'scatter_dist': 0.6}
SKY = {'intensity': 0.7, 'lower': {'r': 0.1, 'g': 0.11, 'b': 0.16, 'a': 1}, 'color': {'r': 0.62, 'g': 0.74, 'b': 1.0, 'a': 1.0}}
EV = 1.6
MOONFILL = {'cd': 50.0, 'radius': 1800, 'z': 650, 'xy': [(-600, -600), (600, -600), (-600, 600), (600, 600)], 'color': {'r': 0.62, 'g': 0.74, 'b': 1.0, 'a': 1.0}}

def ppv():
    # DevMap has no post process volume: make one (unbound) the first time and use its real object path
    found = call('scene.SceneTools.find_actors', {'name': 'PostProcessVolume', 'tag': '', 'collision_channels': []})
    if not found:
        found = [call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PostProcessVolume'},
                 'name': 'PostProcessVolume', 'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})]
    return found[0]['refPath'].split('PersistentLevel.')[-1]

def run():
    call('scene.SceneTools.load_level', {'level_path': LV.split('.')[0]})   # light colours are linear 0-1 (0-255 clamps to white)
    pp = ppv()
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'DirectionalLight_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 1500}, 'rotation': {'pitch': SUN['pitch'], 'yaw': SUN['yaw'], 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('DirectionalLight_0.LightComponent0', {'intensity': SUN['lux'], 'lightColor': SUN['color'],
         'volumetricScatteringIntensity': SUN['scatter'], 'bCastVolumetricShadow': True, 'bEnableLightShaftBloom': True})
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'ExponentialHeightFog_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('ExponentialHeightFog_0.HeightFogComponent0', {'fogDensity': FOG['density'], 'fogHeightFalloff': 0.2, 'bEnableVolumetricFog': True,
         'volumetricFogScatteringDistribution': FOG['scatter_dist'], 'volumetricFogExtinctionScale': 1.0, 'volumetricFogDistance': 3000})
    setp('SkyLight_0.SkyLightComponent0', {'intensity': SKY['intensity'], 'volumetricScatteringIntensity': 0.2,
         'lightColor': SKY['color'], 'bLowerHemisphereIsBlack': False, 'lowerHemisphereColor': SKY['lower']})
    setp(pp, {'bUnbound': True, 'settings': {
        'bOverride_AutoExposureMinBrightness': True, 'autoExposureMinBrightness': EV,
        'bOverride_AutoExposureMaxBrightness': True, 'autoExposureMaxBrightness': EV,
        'bOverride_BloomIntensity': True, 'bloomIntensity': 0.9,
        'bOverride_VignetteIntensity': True, 'vignetteIntensity': 0.5}})
    for a in call('scene.SceneTools.find_actors', {'name': 'MoonFill_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for k, (x, y) in enumerate(MOONFILL['xy']):
        a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PointLight'}, 'name': 'MoonFill_%d' % k,
                 'xform': {'location': {'x': x, 'y': y, 'z': MOONFILL['z']}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        call('object.ObjectTools.set_properties', {'instance': ref(a['refPath'] + '.LightComponent0'), 'values': json.dumps(
            {'intensityUnits': 'Candelas', 'intensity': MOONFILL['cd'], 'attenuationRadius': MOONFILL['radius'], 'lightColor': MOONFILL['color'],
             'sourceRadius': 200, 'castShadows': False, 'volumetricScatteringIntensity': 0.0})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'pp': pp, 'sky': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'SkyLight_0.SkyLightComponent0'), 'properties': ['intensity']}),
            'fog': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'ExponentialHeightFog_0.HeightFogComponent0'), 'properties': ['bEnableVolumetricFog', 'fogDensity']})}
