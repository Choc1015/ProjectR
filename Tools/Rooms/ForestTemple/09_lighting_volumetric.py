import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
LV = '/Game/Maps/Rooms/L_Room_ForestTemple.L_Room_ForestTemple:PersistentLevel.'
def setp(path, vals):
    call('object.ObjectTools.set_properties', {'instance': ref(LV + path), 'values': json.dumps(vals)})
def run():
    n = 0
    for a in call('scene.SceneTools.find_actors', {'name': 'FT_LightShaft_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); n += 1
    # real light only: strong sun scattering in volumetric fog, dark interior
    setp('DirectionalLight_0.LightComponent0', {'intensity': 40.0, 'volumetricScatteringIntensity': 20.0, 'bCastVolumetricShadow': True,
         'bEnableLightShaftBloom': True})
    setp('ExponentialHeightFog_0.HeightFogComponent0', {'fogDensity': 0.08, 'fogHeightFalloff': 0.2, 'bEnableVolumetricFog': True,
         'volumetricFogScatteringDistribution': 0.9, 'volumetricFogExtinctionScale': 1.0, 'volumetricFogDistance': 3000})
    setp('SkyLight_0.SkyLightComponent0', {'intensity': 0.25, 'volumetricScatteringIntensity': 0.2})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'removed': n}
