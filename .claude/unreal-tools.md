# 확인된 언리얼 MCP 도구

unreal-worker가 `describe_toolset`으로 확인한 도구를 한 줄씩 추가한다. 여기 있는 도구는 다시 조회하지 않고 바로 `call_tool`로 쓴다.
형식: `- <toolset_name> / <tool_name>(<핵심 인자>) — 용도`

## 자주 쓰는 툴셋 (이름 확인됨)
- `editor_toolset.toolsets.scene.SceneTools` — 레벨 로드, 액터 배치·삭제, 카메라, 아웃라이너
- `editor_toolset.toolsets.actor.ActorTools` — 액터 트랜스폼·라벨·부모·컴포넌트
- `editor_toolset.toolsets.asset.AssetTools` — 에셋 조회·임포트·저장
- `editor_toolset.toolsets.blueprint.BlueprintTools` — 블루프린트 생성·편집
- `editor_toolset.toolsets.object.ObjectTools` — 프로퍼티 조회·수정, 클래스 탐색
- `editor_toolset.toolsets.material.MaterialTools` / `material_instance.MaterialInstanceTools`
- `editor_toolset.toolsets.static_mesh.StaticMeshTools` / `skeletal_mesh.SkeletalMeshTools`
- `editor_toolset.toolsets.programmatic.ProgrammaticToolset` — 여러 도구 호출을 파이썬 스크립트 하나로 묶어 실행
- `EditorToolset.EditorAppToolset` — 콘솔 변수, 선택, 뷰포트 카메라, PIE 제어
- `EditorToolset.LogsToolset` — 출력 로그 읽기
- `aimodule_toolset.toolsets.behavior_tree.BehaviorTreeTools` / `state_tree_toolset.toolsets.state_tree.StateTreeTools`
- `ToolsetRegistry.AgentSkillToolset` — 프로젝트 스킬 목록·읽기

## 도구 상세
공통: 액터/오브젝트 인자는 `{"refPath": "..."}`, 트랜스폼은 `{location:{x,y,z}, rotation:{pitch,yaw,roll}, scale:{x,y,z}}`(미지정 필드=변경 없음/항등).
(요청의 "SceneTools 또는 LevelTools" 중 실제 존재하는 `SceneTools`를 사용. LevelTools는 없음.)

### editor_toolset.toolsets.scene.SceneTools (20개)
- scene.SceneTools / load_level(level_path) — 레벨 로드
- scene.SceneTools / get_current_level() — 현재 레벨 경로
- scene.SceneTools / find_actors(name, tag, actor_type?, root?, bounds?, collision_channels) — 조건 검색(name/tag/collision_channels는 필수 키, 빈 값 가능)
- scene.SceneTools / get_collision_channels() — find_actors용 충돌 채널 목록
- scene.SceneTools / add_to_scene_from_asset(asset_path, name, xform, parent?, snap_to_ground?) — 에셋으로 액터 배치
- scene.SceneTools / add_to_scene_from_class(actor_type, name, xform, parent?, snap_to_ground?) — 클래스로 액터 배치
- scene.SceneTools / remove_from_scene(actor) — 액터 삭제
- scene.SceneTools / save_actor(actor) — 액터 저장
- scene.SceneTools / is_checked_out(actor) — 소스컨트롤 체크아웃 여부
- scene.SceneTools / can_edit(actor) — 편집 가능 여부
- scene.SceneTools / merge_actors(actors, output_path, name, destroy_source_actors?) — 스태틱메시 액터 병합
- scene.SceneTools / trace_world(start, end) — 라인 트레이스 거리
- scene.SceneTools / create_level_instance(level_path, name, xform, parent?) — 레벨 인스턴스 생성
- scene.SceneTools / edit_level_instance(level_instance) — 레벨 인스턴스 편집 진입
- scene.SceneTools / commit_level_instance(level_instance, discard?) — 편집 저장/취소 후 종료
- scene.SceneTools / get_folders() — 아웃라이너 폴더 목록
- scene.SceneTools / get_actors_in_folder(folder_path, recursive?) — 폴더 내 액터
- scene.SceneTools / set_actor_folder(actor, folder_path) — 액터를 폴더로 이동(빈 문자열=루트)
- scene.SceneTools / rename_folder(old_path, new_path) — 폴더 이름 변경
- scene.SceneTools / delete_folder(folder_path) — 폴더 삭제(액터는 부모 폴더로)

### editor_toolset.toolsets.actor.ActorTools (17개)
- actor.ActorTools / get_label(actor) / set_label(actor, label) — 액터 라벨 조회·변경
- actor.ActorTools / get_actor_transform(actor) — 월드 트랜스폼 조회
- actor.ActorTools / set_actor_transform(actor, xform, worldspace?=true) — 트랜스폼 설정
- actor.ActorTools / look_at(actor, target) — 월드 좌표를 바라보게 회전
- actor.ActorTools / get_actor_bounds(actor) — 월드 바운딩 박스
- actor.ActorTools / get_tags(actor) / add_tag(actor, tag) / remove_tag(actor, tag) / has_tag(actor, tag) — 태그 조회·추가·제거·확인
- actor.ActorTools / get_components(actor, component_type?) — 컴포넌트 목록
- actor.ActorTools / add_component(owner, component_type, name) — 컴포넌트 추가(액터/BP/씬컴포넌트)
- actor.ActorTools / remove_component(component) — 컴포넌트 제거
- actor.ActorTools / get_root_component(actor) — 루트 컴포넌트
- actor.ActorTools / get_parent_component(component) / set_parent_component(component, parent?) — 부모 컴포넌트 조회·변경
- actor.ActorTools / get_component_actor(component) — 컴포넌트 소유 액터

### editor_toolset.toolsets.asset.AssetTools (21개)
- asset.AssetTools / find_assets(folder_path, name, asset_type?, recursive?, tags?) — 에셋 검색(빈 folder_path=전체)
- asset.AssetTools / load_asset(asset_path) — 에셋 로드
- asset.AssetTools / save_assets(asset_paths) — 저장(빈 리스트=더티 전체)
- asset.AssetTools / exists(path) — 에셋/폴더 존재 여부
- asset.AssetTools / list_folders(root_path, recursive?) — 하위 폴더 목록
- asset.AssetTools / create_folder(path) — 폴더 생성
- asset.AssetTools / move(path, new_path) / duplicate(path, new_path) / delete(path) — 이동·복제·삭제(삭제는 되돌리기 어려움, 주의)
- asset.AssetTools / get_asset_class(asset_path) — 에셋 클래스명
- asset.AssetTools / get_asset_tags(asset_path) — 레지스트리 태그
- asset.AssetTools / get_metadata_tags(asset_path) / update_metadata_tags(asset_path, set_tags?, remove_tags?) — 메타데이터 조회·수정
- asset.AssetTools / get_dependencies(asset_path) / get_referencers(asset_path) — 의존/참조 에셋
- asset.AssetTools / is_dirty(asset_path) — 미저장 변경 여부
- asset.AssetTools / is_checked_out(asset_path) / can_edit_asset(asset_path) — 소스컨트롤 상태
- asset.AssetTools / read_file(file_path) / write_file(file_path, content) — /Game, 플러그인 Content, Saved 하위 텍스트 파일 읽기·쓰기
- asset.AssetTools / get_plugin_content_paths(include_engine?) — 플러그인 콘텐츠 루트

### editor_toolset.toolsets.programmatic.ProgrammaticToolset (2개)
- programmatic.ProgrammaticToolset / get_execution_environment() — 스크립트 환경·지침 조회(execute 전에 1회 필수 호출)
- programmatic.ProgrammaticToolset / execute_tool_script(script) — `run()`이 dict를 반환하는 파이썬 스크립트로 여러 도구 호출 일괄 실행
