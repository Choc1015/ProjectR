import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
LV = '/Game/Maps/Rooms/L_Room_SnowShrine.L_Room_SnowShrine:PersistentLevel.'
def setp(path, vals):
    call('object.ObjectTools.set_properties', {'instance': ref(LV + path), 'values': json.dumps(vals)})

# tunables - DAY snow: pale cool daylight through the broken roof panels, bright snow bounce from below.
# Starting point = oasis values with a neutral-cool tint; snow is bright, so exposure stays high.
SUN = {'pitch': -52, 'yaw': 25, 'lux': 35.0, 'scatter': 10.0, 'color': {'r': 245, 'g': 248, 'b': 255, 'a': 255}}
FOG = {'density': 0.05, 'scatter_dist': 0.8}
SKY = {'intensity': 2.0, 'lower': {'r': 0.5, 'g': 0.52, 'b': 0.55, 'a': 1}, 'color': {'r': 255, 'g': 250, 'b': 245, 'a': 255}}
EV = 4.4

def ppv():
    # DevMap has no post process volume: make one (unbound) the first time and use its real object path
    found = call('scene.SceneTools.find_actors', {'name': 'PostProcessVolume', 'tag': '', 'collision_channels': []})
    if not found:
        found = [call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PostProcessVolume'},
                 'name': 'PostProcessVolume', 'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})]
    return found[0]['refPath'].split('PersistentLevel.')[-1]

def run():
    pp = ppv()
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'DirectionalLight_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 1500}, 'rotation': {'pitch': SUN['pitch'], 'yaw': SUN['yaw'], 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('DirectionalLight_0.LightComponent0', {'intensity': SUN['lux'], 'lightColor': SUN['color'],
         'volumetricScatteringIntensity': SUN['scatter'], 'bCastVolumetricShadow': True, 'bEnableLightShaftBloom': True})
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'ExponentialHeightFog_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('ExponentialHeightFog_0.HeightFogComponent0', {'fogDensity': FOG['density'], 'fogHeightFalloff': 0.2, 'bEnableVolumetricFog': True,
         'volumetricFogScatteringDistribution': FOG['scatter_dist'], 'volumetricFogExtinctionScale': 1.0, 'volumetricFogDistance': 3000})
    setp('SkyLight_0.SkyLightComponent0', {'intensity': SKY['intensity'], 'volumetricScatteringIntensity': 0.2, 'lightColor': SKY.get('color', {'r': 255, 'g': 255, 'b': 255, 'a': 255}),
         'bLowerHemisphereIsBlack': False, 'lowerHemisphereColor': SKY['lower']})
    setp(pp, {'bUnbound': True, 'settings': {
        'bOverride_AutoExposureMinBrightness': True, 'autoExposureMinBrightness': EV,
        'bOverride_AutoExposureMaxBrightness': True, 'autoExposureMaxBrightness': EV,
        'bOverride_BloomIntensity': True, 'bloomIntensity': 0.9,
        'bOverride_VignetteIntensity': True, 'vignetteIntensity': 0.5}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'pp': pp, 'sky': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'SkyLight_0.SkyLightComponent0'), 'properties': ['intensity']}),
            'fog': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'ExponentialHeightFog_0.HeightFogComponent0'), 'properties': ['bEnableVolumetricFog', 'fogDensity']})}
