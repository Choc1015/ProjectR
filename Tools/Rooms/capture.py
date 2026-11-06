import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
SHOTS = {'vp1': ({'x': -2000, 'y': -2000, 'z': 2200}, -38, 45), 'vp2': ({'x': 2000, 'y': 2000, 'z': 2200}, -38, 225)}
def run():
    out = {}
    for name, (loc, pitch, yaw) in SHOTS.items():
        r = execute_tool('EditorToolset.EditorAppToolset.CaptureViewport', json.dumps({
            'captureTransform': {'location': loc, 'rotation': {'pitch': pitch, 'yaw': yaw, 'roll': 0}},
            'annotations': {'count': 0, 'classFilter': None}}))
        rv = r['returnValue'] if 'returnValue' in r else r
        if isinstance(rv, str):
            rv = json.loads(rv)
        data = rv['image']['data'] if 'image' in rv else None
        out[name] = list(rv.keys()) if data is None else len(data)
        if data:
            call('asset.AssetTools.write_file', {'file_path': 'C:/UnrealProject/ProjectR/Saved/' + name + '.txt', 'content': data})
    return out
