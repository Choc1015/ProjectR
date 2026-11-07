import json
# Blowing sand: a low, wide sheet of sand grains drifting across the floor (review 2026-11-07).
# Same recipe as ForestTemple 11-13 (MinimalLightweight system + HangingParticulates emitter), tuned for sand.
E = 'editor_toolset.toolsets.'
N = 'NiagaraToolsets.NiagaraToolset_System.'
def ref(p): return {'refPath': p}
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def nt(f, a): return execute_tool(N + f, json.dumps(a))
DIR, NAME = '/Game/Props/Oasis', 'NS_OA_SandDrift'
SYS = ref(DIR + '/' + NAME + '.' + NAME)
# (module, input, struct, value)
SETS = [
    ('SpawnRate', 'SpawnRate', 'NiagaraFloat', {'value': 260}),
    ('InitializeParticle', 'Color', 'LinearColor', {'r': 1.1, 'g': 0.82, 'b': 0.5, 'a': 0.8}),
    ('InitializeParticle', 'Uniform Sprite Size Min', 'NiagaraFloat', {'value': 1.0}),
    ('InitializeParticle', 'Uniform Sprite Size Max', 'NiagaraFloat', {'value': 2.5}),
    ('ShapeLocation', 'Box Size', 'Vector3f', {'x': 2200, 'y': 2200, 'z': 220}),
    ('WindForce', 'Wind Speed', 'Vector3f', {'x': 1, 'y': 0.4, 'z': 0.03}),   # direction (sun side -> exit)
    ('WindForce', 'Wind Speed Scale', 'NiagaraFloat', {'value': 300}),        # cm/s
]
PLACE = [(0, 0, 110)]   # one sheet covering the room, centre a bit above the floor

def run():
    out = {}
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_Oasis'})
    try:
        nt('CreateNiagaraSystem', {'AssetName': NAME, 'AssetPath': DIR,
           'TemplateSystem': ref('/Niagara/DefaultAssets/Templates/Systems/MinimalLightweight.MinimalLightweight')})
        nt('AddEmitter', {'System': SYS, 'TemplateEmitter': ref('/Niagara/DefaultAssets/Templates/Emitters/HangingParticulates.HangingParticulates'), 'EmitterName': 'Sand'})
        nt('RemoveEmitter', {'EmitterToRemove': {'system': SYS, 'emitterName': 'Minimal'}})
        out['create'] = 'new'
    except Exception as e:
        out['create'] = 'kept: ' + str(e)[:120]
    topo = nt('GetEmitterTopology', {'EmitterRef': {'system': SYS, 'emitterName': 'Sand'}})['returnValue']
    where = {}
    for key, sc in topo.items():
        if isinstance(sc, dict) and 'scriptName' in sc:
            for m in (sc['modules'] if 'modules' in sc else []):
                nm = m['moduleName'] if isinstance(m, dict) and 'moduleName' in m else None
                if nm: where[nm] = sc['scriptName']
    for mod, inp, st, val in SETS:
        r = {'system': SYS, 'emitterName': 'Sand', 'scriptName': where[mod] if mod in where else '', 'moduleName': mod, 'inputNameStack': [inp]}
        try:
            cur = nt('GetStackInputData', {'StackInputRef': r})['returnValue']
            nt('SetStackInputData', {'StackInputRef': r, 'InputData': {'struct': cur['struct'], 'value': val}})
            out[inp] = 'ok'
        except Exception as e:
            out[inp] = str(e)[:120]
    for a in call('scene.SceneTools.find_actors', {'name': 'OA_Sand_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for n, (x, y, z) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': DIR + '/' + NAME, 'name': 'OA_Sand_%02d' % n,
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
