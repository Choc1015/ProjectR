# 광산 소품 공용 헬퍼. 블렌더에서 exec(open(...).read())로 불러 쓴다.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

EXPORT_DIR = 'C:/UnrealProject/ProjectR/SourceArt/Export/Mine/'
PI = math.pi


def mk_mat(name, color, rough=0.9, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = emit_strength
    else:
        p.inputs['Emission Strength'].default_value = 0.0
    m.diffuse_color = (*color, 1)
    return m


class Obj:
    def __init__(s, name):
        s.name = name
        s.bm = bmesh.new()
        s.mats = []

    def mi(s, mat):
        if mat not in s.mats:
            s.mats.append(mat)
        return s.mats.index(mat)

    def _tag(s, verts, mat):
        i = s.mi(mat)
        fs = set()
        for v in verts:
            for f in v.link_faces:
                fs.add(f)
        for f in fs:
            f.material_index = i

    def box(s, c, size, mat, rot=(0, 0, 0)):
        m = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((size[0], size[1], size[2], 1))
        r = bmesh.ops.create_cube(s.bm, size=1.0, matrix=m)
        s._tag(r['verts'], mat)

    def cyl(s, c, r, h, mat, axis='Z', seg=8, r2=None, rot=None):
        if rot is None:
            rot = {'Z': (0, 0, 0), 'X': (0, PI / 2, 0), 'Y': (-PI / 2, 0, 0)}[axis]
        m = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4()
        r = bmesh.ops.create_cone(s.bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r,
                                  radius2=(r if r2 is None else r2), depth=h, matrix=m)
        s._tag(r['verts'], mat)

    def beam(s, p0, p1, w, t, mat, up=(0, 0, 1)):
        p0 = Vector(p0); p1 = Vector(p1)
        d = p1 - p0
        L = d.length
        q = d.to_track_quat('X', 'Z') if abs(d.normalized().z) < 0.999 else d.to_track_quat('X', 'Y')
        m = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((L, w, t, 1))
        r = bmesh.ops.create_cube(s.bm, size=1.0, matrix=m)
        s._tag(r['verts'], mat)

    def rock(s, c, r, mat, seed=0, squash=0.75, sub=1, stretch=(1, 1)):
        rnd = random.Random(seed)
        m = Matrix.Translation(c) @ Matrix.Diagonal((r * stretch[0], r * stretch[1], r * squash, 1))
        res = bmesh.ops.create_icosphere(s.bm, subdivisions=sub, radius=1.0, matrix=m)
        vs = res['verts']
        for v in vs:
            k = rnd.uniform(0.78, 1.1)
            v.co = Vector(c) + (v.co - Vector(c)) * k
        s._tag(vs, mat)

    def crystal(s, c, r, h, mat, rot=(0, 0, 0), top=0.55, yaw=0.0, body=0.72):
        bv = []
        ring0 = []
        ring1 = []
        for i in range(6):
            a = yaw + i * PI / 3
            ring0.append((r * math.cos(a), r * math.sin(a), 0))
            ring1.append((r * top * math.cos(a), r * top * math.sin(a), h * body))
        m = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4()
        v0 = [s.bm.verts.new(m @ Vector(p)) for p in ring0]
        v1 = [s.bm.verts.new(m @ Vector(p)) for p in ring1]
        ap = s.bm.verts.new(m @ Vector((0, 0, h)))
        i = s.mi(mat)
        fl = [s.bm.faces.new(v0[::-1])]
        for k in range(6):
            n = (k + 1) % 6
            fl.append(s.bm.faces.new((v0[k], v0[n], v1[n], v1[k])))
            fl.append(s.bm.faces.new((v1[k], v1[n], ap)))
        for f in fl:
            f.material_index = i

    def torus(s, c, R, r, mat, rot=(0, 0, 0), nmaj=8, nmin=4, stretch=1.0):
        m = Matrix.Translation(c) @ Euler(rot).to_matrix().to_4x4()
        vs = []
        for i in range(nmaj):
            a = 2 * PI * i / nmaj
            row = []
            for j in range(nmin):
                b = 2 * PI * j / nmin + PI / nmin
                rr = R + r * math.cos(b)
                row.append(s.bm.verts.new(m @ Vector((rr * math.cos(a) * stretch, rr * math.sin(a), r * math.sin(b)))))
            vs.append(row)
        k = s.mi(mat)
        for i in range(nmaj):
            for j in range(nmin):
                f = s.bm.faces.new((vs[i][j], vs[(i + 1) % nmaj][j], vs[(i + 1) % nmaj][(j + 1) % nmin], vs[i][(j + 1) % nmin]))
                f.material_index = k

    def poly(s, pts, mat, thick=0.02, normal_dir=-1):
        """2D polygon (x,z) on wall plane, extruded in y by thick toward -Y (y from 0 to -thick shifted by caller via pts y)."""
        pass

    def prism_xz(s, pts, y0, y1, mat):
        """x,z 점 목록(반시계)을 y0..y1로 압출한 판 (y0 > y1, 뒤쪽이 y0)."""
        a = [s.bm.verts.new((x, y0, z)) for x, z in pts]
        b = [s.bm.verts.new((x, y1, z)) for x, z in pts]
        k = s.mi(mat)
        n = len(pts)
        fl = [s.bm.faces.new(a), s.bm.faces.new(b[::-1])]
        for i in range(n):
            j = (i + 1) % n
            fl.append(s.bm.faces.new((a[i], a[j], b[j], b[i])))
        for f in fl:
            f.material_index = k
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces[:])

    def finish(s, display=None):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces[:])
        me = bpy.data.meshes.new(s.name)
        s.bm.to_mesh(me)
        s.bm.free()
        for p in me.polygons:
            p.use_smooth = False
        for mt in s.mats:
            me.materials.append(mt)
        ob = bpy.data.objects.get(s.name)
        if ob:
            bpy.data.objects.remove(ob)
        ob = bpy.data.objects.new(s.name, me)
        bpy.context.scene.collection.objects.link(ob)
        # export
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        ob.location = (0, 0, 0)
        bpy.ops.export_scene.fbx(filepath=EXPORT_DIR + s.name + '.fbx', use_selection=True, object_types={'MESH'},
                                 apply_scale_options='FBX_SCALE_NONE', mesh_smooth_type='FACE')
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        mn = [min(v[i] for v in bb) for i in range(3)]
        mx = [max(v[i] for v in bb) for i in range(3)]
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        if display:
            ob.location = display
        print(s.name, 'min', [round(x, 2) for x in mn], 'max', [round(x, 2) for x in mx], 'tris', tris)
        return ob


def M(n):
    return bpy.data.materials[n]
