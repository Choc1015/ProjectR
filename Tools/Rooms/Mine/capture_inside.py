import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
SHOTS = {'vp1': ({'x': -1050, 'y': -1050, 'z': 520}, -14, 45), 'vp2': ({'x': 1050, 'y': 1050, 'z': 520}, -14, 225)}  # inside: the ceiling hides views from above
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
