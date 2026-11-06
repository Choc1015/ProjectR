# 미사모 모션을 1인칭용 "팔만 움직이는" 모션으로 바꿔 FBX로 내보낸다(블렌더 MCP execute_blender_code로 실행).
# - 팔(Shoulder/Arm/Hand) 본만 남기고 나머지 본은 Anim_Idle 첫 프레임 자세로 고정
# - 아마추어 회전 적용(안 하면 언리얼에서 눕는다), FBX_SCALE_NONE → 언리얼은 uniform_scale=100으로 임포트
# - 오른손이 가장 빠른 프레임(Hit 노티파이 자리)을 같이 알려 준다
# 쓰는 법: JOBS에 (미사모 원본 파일, 내보낼 이름)을 넣고 코드 전체를 실행한다.
import bpy, re
# (원본, 이름, 끝 프레임 또는 None, 돌아오기 프레임 수 또는 None).
# 끝 프레임에서 자르고, 돌아오기 프레임 수가 있으면 그 뒤에 팔을 대기 자세(Anim_Idle 첫 프레임)로 부드럽게 되돌리는 구간을 붙인다.
# 스태프 공격은 내려치기만 쓰려고 22프레임에서 자르고(그 뒤는 옆으로 휘두르기) 12프레임에 걸쳐 돌아온다.
JOBS = [("Anim_Staff_Attack.fbx", "A_Staff_Attack_ArmsOnly", 22, 12), ("Anim_Skill_Fireball.fbx", "A_Skill_Fireball_ArmsOnly", None, None)]
SRC = r"C:\UnrealProject\ProjectR\SourceArt\Mixamo"
OUT = r"C:\UnrealProject\ProjectR\SourceArt\Export"

scn = bpy.data.scenes.get("ArmsOnlyWork") or bpy.data.scenes.new("ArmsOnlyWork")
bpy.context.window.scene = scn
for o in list(scn.objects): bpy.data.objects.remove(o)
for o in bpy.data.objects:
    if o.name == "Armature": o.name = "Armature_old"

def import_arm(fn):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=SRC + "\\" + fn)
    new = [o for o in bpy.data.objects if o not in before]
    return next(o for o in new if o.type == 'ARMATURE'), new

def all_fcurves(act):
    fcs = list(act.fcurves) if hasattr(act, "fcurves") else []
    if not fcs:
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    fcs += [(cb, fc) for fc in cb.fcurves]
        return fcs
    return [(None, fc) for fc in fcs]

idle_arm, idle_objs = import_arm("Anim_Idle.fbx")
scn.frame_set(1)
idle_pose = {b.name: (b.location.copy(), b.rotation_quaternion.copy(), b.scale.copy()) for b in idle_arm.pose.bones}
for o in idle_objs: bpy.data.objects.remove(o)

ARM_KEYS = ("Shoulder", "Arm", "Hand")
def is_arm(n): return any(k in n.split(":")[-1] for k in ARM_KEYS)

report = {}
for src, name, end, back in JOBS:
    arm, objs = import_arm(src)
    act = arm.animation_data.action
    fr = (act.frame_range[0], float(end) if end else act.frame_range[1])
    hit_range = fr
    pairs = all_fcurves(act)
    if end and back:
        # 끝 프레임 자세를 키로 박고 그 뒤 키는 지운 다음, back 프레임 뒤에 대기 자세 키를 넣는다(베지어라 감속·가속이 붙는다).
        arm_bones = [b for b in arm.pose.bones if is_arm(b.name)]
        scn.frame_set(int(end))
        held = {b.name: (b.location.copy(), b.rotation_quaternion.copy(), b.scale.copy()) for b in arm_bones}
        for _, fc in pairs:
            m = re.match(r'pose\.bones\["(.+?)"\]', fc.data_path)
            if m and is_arm(m.group(1)):
                for kp in reversed(list(fc.keyframe_points)):
                    if kp.co.x > end:
                        fc.keyframe_points.remove(kp)
        for b in arm_bones:
            b.location, b.rotation_quaternion, b.scale = held[b.name]
            for p in ("location", "rotation_quaternion", "scale"): b.keyframe_insert(p, frame=end)
            loc, rot, scl = idle_pose[b.name]
            if rot.dot(held[b.name][1]) < 0:
                rot = -rot
            b.location, b.rotation_quaternion, b.scale = loc, rot, scl
            for p in ("location", "rotation_quaternion", "scale"): b.keyframe_insert(p, frame=end + back)
        fr = (fr[0], float(end + back))
        pairs = all_fcurves(act)
    frozen = set()
    for _, fc in pairs:
        m = re.match(r'pose\.bones\["(.+?)"\]', fc.data_path)
        if m and not is_arm(m.group(1)):
            frozen.add(m.group(1))
    for cb, fc in pairs:
        m = re.match(r'pose\.bones\["(.+?)"\]', fc.data_path)
        if m and m.group(1) in frozen:
            (cb.fcurves if cb else act.fcurves).remove(fc)
    for bn in frozen:
        b = arm.pose.bones[bn]
        b.location, b.rotation_quaternion, b.scale = idle_pose[bn]
        for f in (fr[0], fr[1]):
            for p in ("location", "rotation_quaternion", "scale"): b.keyframe_insert(p, frame=f)
    for o in scn.objects: o.select_set(o == arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    # 오른손이 가장 빠른 프레임
    hand = next(b for b in arm.pose.bones if b.name.split(":")[-1] == "RightHand")
    prev, best, best_f = None, -1.0, int(fr[0])
    for f in range(int(hit_range[0]), int(hit_range[1]) + 1):
        scn.frame_set(f)
        p = arm.matrix_world @ hand.head
        if prev is not None and (p - prev).length > best:
            best, best_f = (p - prev).length, f
        prev = p.copy()
    arm.name = "Armature"
    scn.frame_start, scn.frame_end = int(fr[0]), int(fr[1])
    bpy.ops.export_scene.fbx(filepath=OUT + "\\" + name + ".fbx", use_selection=True, object_types={'ARMATURE'},
        apply_scale_options='FBX_SCALE_NONE', add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0)
    report[name] = {"frames": (fr[0], fr[1]), "frozen": len(frozen), "hit_frame": best_f,
                    "hit_sec_30fps": round((best_f - fr[0]) / 30.0, 3)}
    for o in objs: bpy.data.objects.remove(o)
print(report)
