# props_lib.py 확장: 회전체, 전체 회전/이동, 상자/광차 부품. props_lib.py를 먼저 exec한 뒤 불러온다.
def _lathe(s, c, profile, mat, seg=8, caps=True, closed=False, yaw=0.0):
    rings = []
    for (r, z) in profile:
        row = []
        for i in range(seg):
            a = yaw + 2 * PI * i / seg
            row.append(s.bm.verts.new((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2] + z)))
        rings.append(row)
    k = s.mi(mat)
    fl = []
    pairs = list(range(len(rings) - 1)) + ([len(rings) - 1] if closed else [])
    for p in pairs:
        a = rings[p]; b = rings[(p + 1) % len(rings)]
        for i in range(seg):
            j = (i + 1) % seg
            fl.append(s.bm.faces.new((a[i], a[j], b[j], b[i])))
    if caps and not closed:
        fl.append(s.bm.faces.new(rings[0][::-1]))
        fl.append(s.bm.faces.new(rings[-1]))
    for f in fl:
        f.material_index = k
Obj.lathe = _lathe


def _xform(s, rotx=0.0, rotz=0.0, move=(0, 0, 0)):
    m = Matrix.Translation(move) @ Matrix.Rotation(rotz, 4, 'Z') @ Matrix.Rotation(rotx, 4, 'X')
    bmesh.ops.transform(s.bm, matrix=m, verts=s.bm.verts[:])
Obj.xform = _xform


def crate(o, c=(0, 0, 0), lid=False, skip=(), mats=None):
    wood = M('M_MN_Wood'); dk = M('M_MN_WoodDark')
    x, y, z = c
    h = 0.8 if lid else 0.84
    o.box((x, y, z + 0.03), (0.82, 0.82, 0.06), dk)
    zc = z + 0.06 + h / 2
    for sy in (-1, 1):
        o.box((x, y + sy * 0.39, zc), (0.82, 0.04, h), wood)
    for sx in (-1, 1):
        o.box((x + sx * 0.39, y, zc), (0.04, 0.74, h), wood)
    if lid:
        o.box((x, y, z + 0.88), (0.82, 0.82, 0.04), dk)
    for sy in (-1, 1):
        if ('y', sy) in skip: continue
        o.beam((x - 0.3, y + sy * 0.43, z + 0.12), (x + 0.3, y + sy * 0.43, z + 0.78), 0.04, 0.07, dk, up=(0, 1, 0))
    for sx in (-1, 1):
        if ('x', sx) in skip: continue
        o.beam((x + sx * 0.43, y - 0.3, z + 0.12), (x + sx * 0.43, y + 0.3, z + 0.78), 0.04, 0.07, dk, up=(1, 0, 0))


def cart_body(o):
    iron, wood = M('M_MN_Iron'), M('M_MN_Wood')
    o.box((0, 0, 0.35), (1.5, 0.9, 0.05), wood)
    for y in (-0.425, 0.425): o.box((0, y, 0.6), (1.5, 0.05, 0.45), wood)
    for x in (-0.725, 0.725): o.box((x, 0, 0.6), (0.05, 0.8, 0.45), wood)
    for y in (-0.425, 0.425): o.box((0, y, 0.85), (1.6, 0.1, 0.05), iron)
    for x in (-0.725, 0.725): o.box((x, 0, 0.85), (0.1, 0.75, 0.05), iron)
    for x in (-0.5, 0.5):
        o.cyl((x, 0, 0.16), 0.03, 0.54, iron, axis='Y', seg=6)
        for y in (-0.3, 0.3): o.cyl((x, y, 0.16), 0.16, 0.06, iron, axis='Y', seg=8)
        for y in (-0.2, 0.2): o.box((x, y, 0.2575), (0.1, 0.1, 0.135), iron)


def _ground(s, center_xy=False):
    zs = min(v.co.z for v in s.bm.verts)
    dx = dy = 0
    if center_xy:
        xs = [v.co.x for v in s.bm.verts]; ys = [v.co.y for v in s.bm.verts]
        dx = -(min(xs) + max(xs)) / 2; dy = -(min(ys) + max(ys)) / 2
    bmesh.ops.translate(s.bm, vec=(dx, dy, -zs), verts=s.bm.verts[:])
Obj.ground = _ground


def _maxy(s, target=0.0):
    my = max(v.co.y for v in s.bm.verts)
    bmesh.ops.translate(s.bm, vec=(0, target - my, 0), verts=s.bm.verts[:])
Obj.back0 = _maxy


def lantern(o, c, s=1.0):
    x, y, z = c
    iron, gl = M('M_MN_Iron'), M('M_MN_Glass')
    o.box((x, y, z + 0.01 * s), (0.14 * s, 0.14 * s, 0.02 * s), iron)
    o.box((x, y, z + 0.11 * s), (0.1 * s, 0.1 * s, 0.18 * s), gl)
    for dx in (-1, 1):
        for dy in (-1, 1):
            o.box((x + dx * 0.06 * s, y + dy * 0.06 * s, z + 0.11 * s), (0.02 * s, 0.02 * s, 0.18 * s), iron)
    o.box((x, y, z + 0.215 * s), (0.16 * s, 0.16 * s, 0.03 * s), iron)
    o.box((x, y, z + 0.25 * s), (0.08 * s, 0.08 * s, 0.04 * s), iron)
    o.torus((x, y, z + 0.30 * s), 0.035 * s, 0.01 * s, iron, rot=(PI / 2, 0, 0), nmaj=8, nmin=4)
