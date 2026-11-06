import json
N = 'NiagaraToolsets.NiagaraToolset_System.'
SYS = {'refPath': '/Game/Weapons/Staff/NS_FireballExplosion.NS_FireballExplosion'}
def nt(f, a): return execute_tool(N + f, json.dumps(a))['returnValue']
# 짧고 밝은 주황 불꽃이 사방으로 튀는 폭발 (module, input, value)
SETS = [
    ('SpawnBurst_Instantaneous', 'Spawn Count', {'value': 70}),
    ('InitializeParticle', 'Color', {'r': 8.0, 'g': 3.0, 'b': 0.6, 'a': 1}),
    ('InitializeParticle', 'Lifetime Min', {'value': 0.35}),
    ('InitializeParticle', 'Lifetime Max', {'value': 0.8}),
    ('InitializeParticle', 'Uniform Sprite Size Min', {'value': 14}),
    ('InitializeParticle', 'Uniform Sprite Size Max', {'value': 34}),
    ('ShapeLocation', 'Sphere Radius', {'value': 45}),
    ('GravityForce', 'Gravity', {'x': 0, 'y': 0, 'z': 150}),
]
def run():
    out = {}
    topo = nt('GetEmitterTopology', {'EmitterRef': {'system': SYS, 'emitterName': 'Burst'}})
    where = {}
    for key, sc in topo.items():
        if isinstance(sc, dict) and 'scriptName' in sc:
            for m in (sc['modules'] if 'modules' in sc else []):
                nm = m['moduleName'] if isinstance(m, dict) and 'moduleName' in m else None
                if nm: where[nm] = sc['scriptName']
    for mod, inp, val in SETS:
        r = {'system': SYS, 'emitterName': 'Burst', 'scriptName': where[mod] if mod in where else '', 'moduleName': mod, 'inputNameStack': [inp]}
        try:
            cur = nt('GetStackInputData', {'StackInputRef': r})
            nt('SetStackInputData', {'StackInputRef': r, 'InputData': {'struct': cur['struct'], 'value': val}})
            out[inp] = 'ok'
        except Exception as e:
            out[inp] = str(e)[:120]
    execute_tool('editor_toolset.toolsets.asset.AssetTools.save_assets', json.dumps({'asset_paths': []}))
    return out
