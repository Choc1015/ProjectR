import json
N = 'NiagaraToolsets.NiagaraToolset_System.'
def ref(p): return {'refPath': p}
SYS = ref('/Game/Props/ForestTemple/NS_FT_LightDust.NS_FT_LightDust')
def nt(f, a): return execute_tool(N + f, json.dumps(a))['returnValue']
# (module, input, struct, value)
SETS = [
    ('SpawnRate', 'SpawnRate', 'NiagaraFloat', {'value': 14}),
    ('InitializeParticle', 'Color', 'LinearColor', {'r': 3.0, 'g': 2.3, 'b': 1.2, 'a': 1}),
    ('InitializeParticle', 'Uniform Sprite Size Min', 'NiagaraFloat', {'value': 1.5}),
    ('InitializeParticle', 'Uniform Sprite Size Max', 'NiagaraFloat', {'value': 3.0}),
    ('ShapeLocation', 'Box Size', 'Vector3f', {'x': 320, 'y': 320, 'z': 650}),
    ('WindForce', 'Wind Speed Scale', 'NiagaraFloat', {'value': 0.25}),
]
def run():
    out = {}
    topo = nt('GetEmitterTopology', {'EmitterRef': {'system': SYS, 'emitterName': 'Dust'}})
    where = {}
    for key, sc in topo.items():
        if isinstance(sc, dict) and 'scriptName' in sc:
            for m in (sc['modules'] if 'modules' in sc else []):
                nm = m['moduleName'] if isinstance(m, dict) and 'moduleName' in m else None
                if nm: where[nm] = sc['scriptName']
    out['where'] = where
    for mod, inp, st, val in SETS:
        r = {'system': SYS, 'emitterName': 'Dust', 'scriptName': where[mod] if mod in where else '', 'moduleName': mod, 'inputNameStack': [inp]}
        cur = nt('GetStackInputData', {'StackInputRef': r})
        data = {'struct': cur['struct'], 'value': val}
        try:
            nt('SetStackInputData', {'StackInputRef': r, 'InputData': data})
            out[inp] = 'ok'
        except Exception as e:
            out[inp] = str(e)[:160]
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets', json.dumps({'asset_paths': []}))
    return out
