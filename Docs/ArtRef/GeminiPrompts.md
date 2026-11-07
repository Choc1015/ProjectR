# ProjectR 제미나이 레퍼런스 프롬프트

스타일: 스타일라이즈드 로우폴리. 세 장 모두 같은 **공통 스타일 문구**를 붙여서 디자인을 통일한다.
뽑은 이미지는 `Docs/ArtRef/`에 `character.png`, `dummy.png`, `sword.png`로 저장한다.

## 공통 스타일 문구 (모든 프롬프트 끝에 붙인다)

```
Stylized low-poly 3D game asset, flat-shaded faceted surfaces, simple solid colors with subtle gradients, no fine texture detail, clean readable silhouette. Medieval fantasy RPG. Muted warm palette: leather brown, iron grey, faded cloth blue, straw yellow. Orthographic reference sheet on a plain light-grey background, even soft lighting, no shadows on the ground, no text, no labels.
```

## 1. 플레이어 캐릭터

미사모 오토리거가 인식하려면 **T포즈, 정면/측면/후면**이 필요하다.

```
Character turnaround reference sheet of a young human swordsman adventurer, full body, standing in a T-pose with arms straight out horizontally and legs slightly apart. Three views side by side: front, side, back. Simple layered outfit: padded cloth tunic, leather vest, belt, fitted trousers, leather boots, fingerless gloves. Short hair, no helmet, no cape, no loose hanging cloth. Realistic adult proportions (about 7 heads tall), hands open with fingers spread.
```
+ 공통 스타일 문구

## 2. 허수아비 (훈련용 타격 더미)

```
Reference sheet of a wooden training dummy for sword practice, front view and side view side by side. A thick vertical wooden post set in a round wooden base, a horizontal wooden crossbar for arms, torso made of a burlap sack stuffed with straw tied with rope, round burlap sack head with a simple painted target mark, a few straw tufts sticking out. About human height.
```
+ 공통 스타일 문구

## 3. 검

```
Reference sheet of a simple one-handed longsword, shown horizontally in front view and edge-on side view. Straight double-edged iron blade with a central fuller, simple straight crossguard, leather-wrapped grip, round iron pommel. Plain and practical, no gems, no engravings.
```
+ 공통 스타일 문구

## 팁
- 세 장을 **같은 대화창**에서 연달아 뽑으면 톤이 더 잘 맞는다. 두 번째부터는 "앞 이미지와 같은 스타일로"를 덧붙인다.
- 캐릭터가 T포즈가 아니거나 뷰가 겹쳐 나오면 다시 뽑는다. 모델링 정확도에 바로 영향을 준다.

## UI 공통 스타일 문구 (모든 UI·아이콘 프롬프트 끝에 붙인다)

```
Vintage parchment game UI style matching an old illuminated manuscript or treasure map. Clean tidy sepia brown ink lines of even width, aged gold leaf for highlights, small dark red wax seal accents. Muted warm palette: parchment beige, sepia brown, aged gold, deep red. Flat front view, crisp edges, no text. Isolated on a pure flat solid white background (#FFFFFF), no paper texture behind, no shadow.
```
- 바탕(종이) 자체를 뽑을 때만 마지막 문장(흰 배경)을 빼고 쓴다.
- 스킬 아이콘처럼 노드 안에 들어갈 그림도 이 문구를 붙여 잉크 + 금박 느낌으로 맞춘다.

## 스킬트리 UI (캐릭터 스타일 기준)
- 배경: Vintage aged parchment paper texture for a game UI background, 16:9. Plain empty sheet, warm parchment beige with subtle stains, soft worn edges, light vignette, faint paper grain. Muted warm palette: parchment beige, leather brown edges. No drawings, no lines, no icons, no text, completely empty.
- 연결선: Two straight horizontal skill tree connector lines, isolated on a pure flat solid white background (#FFFFFF), no paper, no texture, no shadow. Top: inactive, thin faded sepia brown dashed ink line. Bottom: active, solid aged gold leaf bar with a thin deep brown ink outline. Even width, long and straight, centered, lots of empty space around, no text.
- 노드: Skill tree node frames for a vintage parchment UI, drawn like an old illuminated manuscript or treasure map. Square slots with slightly rounded corners, thin double-line sepia ink border, inside filled with a slightly lighter parchment tone and left completely blank (a skill icon will be placed inside). States side by side: locked (faded pale ink, dim), available (deep brown ink border), unlocked (aged gold leaf border with warm subtle shine), selected (gold border plus a small dark red wax seal accent at the corner). Isolated on a pure flat solid white background (#FFFFFF), no paper texture behind the frames, no shadow, clean and tidy, consistent size, no symbols inside, no text.

## 스킬 아이콘 시트 (16개씩)
- 한 장에 4x4 = 16개. 같은 대화창에서 이어 뽑아야 그림체가 맞는다. 두 번째부터는 앞에 `Generate a new image in exactly the same style, size and layout as the previous icon sheets:`를 붙인다.
- 틀: `A 4x4 grid sprite sheet of 16 game skill icons, square 1:1 image. Each icon is one simple bold emblem centered in its own equal square cell, no frames, no borders, no boxes around icons, wide empty white gaps between cells, all icons the same size. Order left to right, top to bottom: 1. ..., 16. ...` + UI 공통 스타일 문구 (+ `no numbers`)
- 순서는 스킬 표 줄 순서. 받은 시트는 `SourceArt/UI/SkillIcons/Sheets/SheetN.png`, 자르기는 `Tools/SliceIconSheet.ps1 -Names <표 순서 ID들>`.

## HUD 조각 (체력·마나 바 틀, 아이템 칸)
- 설명창과 같은 대화창(https://gemini.google.com/app/273b03221003647f)에서 뽑았다. 그냥 요청하면 **앞 그림을 고쳐 버리므로** 앞에 `Draw a brand-new separate image from scratch (do not reuse or edit the previous card). Only the bar, cropped tightly:`를 붙인다. 새 대화창은 이미지 생성을 거부한 적이 있다.
- 바 틀: `a single long horizontal health bar frame, very wide and thin (about 10 times wider than tall), the only object in the picture. Thin tidy rectangular border of sepia brown ink with small ornate aged gold leaf caps on the left and right ends. Inside filled with flat solid dark sepia brown (#3a2614), empty bar with no fill. No parchment card, no paper sheet, no panel around it.` + UI 공통 스타일 문구
- 아이템 칸: `a single square hotbar item slot frame for a game HUD. Thin tidy square border of sepia brown ink with small ornate aged gold leaf corners matching the bar caps. Inside filled with flat solid dark sepia brown (#3a2614) slightly lighter toward the center, an empty slot with no icon.` + UI 공통 스타일 문구 (+ `no numbers`)
- 원본 `SourceArt/UI/Sheets/HudBar_Source.png`, `HudSlot_Source.png` → 흰색 지우고 줄여서 `SourceArt/UI/T_HudBar.png`(640x103), `T_HudSlot.png`(96x96)
- 바탕 판(바와 칸을 감쌈): `a wide horizontal backing plaque panel for a game HUD that will hold the health bar, mana bar and item slots, about 5 times wider than tall, the only object in the picture. Aged parchment beige panel with a thin tidy double border of sepia brown ink, small ornate aged gold leaf flourishes only at the four corners matching the bar caps, the large center area left plain and empty parchment. Slightly rounded rectangle, no wax seal, no text, no bars or slots drawn inside.` + UI 공통 스타일 문구 → `SourceArt/UI/T_HudPanel.png`(1072x204)

## 방(맵) 콘셉트
- 3D 공통 스타일 문구의 마지막 문장(orthographic reference sheet)은 방 그림과 안 맞아서, 방 콘셉트는 아래처럼 "isometric cutaway diorama"로 바꿔 쓴다. 스타일 부분은 같다.
- 테마 비교(2x2): `A 2x2 grid of four different concept art views of a single square room for a first-person sword action roguelike, each room shown as an isometric cutaway diorama from above at 45 degrees, with walls cut low so the floor is visible. Every room has an entrance door on one side and an exit door on the opposite side, an open clear floor in the middle for fighting, and props placed along the walls. Top left: ... Top right: ... Bottom left: ... Bottom right: ... Stylized low-poly 3D game environment, flat-shaded faceted surfaces, simple solid colors with subtle gradients, no fine texture detail, clean readable shapes. Medieval fantasy RPG, bright and cozy, not dark. Muted warm palette: leather brown, iron grey, faded cloth blue, straw yellow. Plain light-grey background around each room, even soft lighting, no text, no labels.`
- 결과 `Docs/ArtRef/Rooms/room_themes.png` (성 무기고 훈련장 / 숲속 신전 폐허 / 마을 지하 창고 / 수도원 도서관)
- 두 번째 테마 비교(같은 템플릿에 "each room is a small piece of an outdoor world fitted into a square room and fully enclosed by walls and a ceiling"를 넣음): 버려진 광산 동굴 / 바닷가 어촌 창고 / 수확철 농가 헛간 / 눈 덮인 산 망루 폐허 → `Docs/ArtRef/Rooms/room_themes_2.png`
- 버려진 광산 동굴(약자 MN): 내부 `One large detailed concept art of a single square combat arena that is a small piece of an old abandoned mountain mine fitted into a square room, fully enclosed: four rough faceted rock walls about 8 m tall, reinforced with sturdy wooden mine support frames ... a low rough rock ceiling held up by wooden beams, with one or two jagged cracks ... A wooden mine tunnel frame as entrance ... exit ...` + 방 콘셉트 스타일 문구 → `mine_interior.png` / 소품 4x4(지지대 틀·갱도 입구·레일 직선·곡선·광차·뒤집힌 광차·광석 상자·상자 더미·통·곡괭이와 삽·부서진 사다리·돌무더기·큰 수정·작은 수정·도르래와 양동이·작업대) → `mine_props.png` / 벽 장식 3x3(수정 덩이·수정 맥·판자 덧댄 구멍·밧줄과 곡괭이 고리·선반·푸른 천·경고 팻말·쇠사슬·광석 벽감) → `mine_wall_decor.png`
- 세 번째 테마 비교(같은 템플릿, 앞에 "this is not a staff or UI"를 덧붙임 — 같은 대화창에 다른 세션의 지팡이·UI 그림이 쌓여 있음): 드워프 대장간 / 사막 오아시스 폐허 / 늪지 어촌 / 가을 사냥꾼 오두막 → `room_themes_3.png`
- 사막 오아시스 폐허(약자 OA, 낮): 내부 `... a small piece of a sunny desert oasis ruin fitted into a square room, fully enclosed: four sandstone block walls about 8 m tall ... a ceiling made of heavy wooden beams in a grid with faded cloth canopies stretched between them (blue, straw yellow, terracotta red), some canopy panels missing or torn so warm sunlight falls in ...` → `oasis_interior.png` / 소품 4x4(기둥·부러진 기둥·쓰러진 기둥·사암 블록·야자수·연못·항아리 묶음·암포라·바구니·말린 양탄자·시장 노점·천 덮은 상자·덤불과 선인장·모래 더미·석상 머리·돌무더기) → `oasis_props.png` / 벽 장식(깃발·부조·벽감·야자잎 깔개와 바구니·갈라진 틈과 덤불·선반·모래 더미·걸린 양탄자·나무 격자 창) → `oasis_wall_decor.png`
- 네 번째 테마 비교: 밤 드워프 대장간 / 눈 덮인 산길 사당 / 해질녘 잠긴 항구 창고 / 거대 고목 속 버섯 숲 → `room_themes_4.png`
- 눈 덮인 산길 사당(약자 SN, 낮): 내부 `... a small piece of a snowy mountain pass fitted into a square room, fully enclosed: four grey stone block walls about 8 m tall with heavy wooden posts and beams, snow on the ledges and icicles ... a ceiling of thick wooden rafters with snow-covered plank roof panels, a few panels broken open so pale daylight and a little falling snow come in ...` → `snow_interior.png` / 소품 4x4(전나무·어린 전나무·작은 돌 사당·기도 깃발 기둥·짐 썰매·기운 썰매·모닥불 자리·장작더미·얼음 바위·낮은 돌담·눈 더미·이정표·눈 덮인 통·상자 더미·등 기둥·스키와 설피) → `snow_props.png` / 벽 장식 3x3(고드름 선반·기도 깃발 줄·눈 더미·설피와 밧줄 걸이·사슴 가죽·영석 선반·창과 방패·서리 틈·덧창) → `snow_wall_decor.png`
- 제미나이 이미지 생성에는 한도가 있다. 하룻밤(2026-11-07 01:20경, 다른 세션 그림 포함 약 28장)에 걸렸고 약 1시간 뒤 풀렸다. 응답이 "I can create more images as soon as your limit resets"면 한도.
- 다섯 번째 테마 비교: 고목 속 버섯 숲(밤) / 잠긴 항구 창고(노을) / 왕실 온실 폐허 / 밤 드워프 대장간 → `room_themes_5.png`
- 여섯 번째 테마 비교: 왕실 온실 폐허 / 가을 사냥꾼 오두막 / 해질녘 마을 예배당 묘지 / 마법사 탑 서재 → `room_themes_6.png`
- 왕실 온실 폐허(약자 GH, 낮): 내부 `... a small piece of a royal garden fitted into a square room, fully enclosed as an old greenhouse ruin: four walls made of a low stone base about 1.2 m tall topped with a dark green-grey iron frame holding tall glass panes up to about 8 m, and a ceiling of iron arched ribs holding glass panels, several panes cracked or missing so sunlight streams in ...` → `greenhouse_interior.png` / 소품 4x4(긴 화단·네모 화분·마른 분수·낮은 화분·화분 나무·둥근 관목·화분 묶음·작업대·외바퀴 수레·물뿌리개와 갈퀴·벤치·새 석상·깨진 유리·들꽃·흙 포대·장미 아치) → `greenhouse_props.png` / 벽 장식(담쟁이·꽃바구니·연장 걸이 둘·창가 화분·깨진 유리·천 차양·선반·장미 격자·둥지 걸이) → `greenhouse_wall_decor.png`
- 일곱 번째 테마 비교: 노을 잠긴 항구 창고 / 밤 고목 버섯 숲 / 마법사 탑 서재 / 해질녘 예배당 묘지 → `room_themes_7.png`
- 해 질 녘 잠긴 항구 창고(약자 HB): 내부 `... a small piece of a fishing harbor at sunset fitted into a square room, fully enclosed as an old half-flooded harbor warehouse: four weathered wooden plank walls about 8 m tall on thick timber posts with a few gaps between boards where low orange sunset light shines in as warm stripes ... One corner of the floor is broken away into shallow sea water with a small wooden jetty ...` → `harbor_interior.png` / 소품 4x4(상자 더미·엎어진 배·뜬 배·부두·계류 기둥·그물 더미·통·통 묶음·밧줄 타래·통발·닻·노·생선 바구니·기중기·천 덮은 상자·판자 더미) → `harbor_props.png` / 벽 장식 3x3(그물·구명 튜브·선반·밧줄 갈고리·돛천·게시판·노와 닻 명판·말린 생선·빛 새는 틈) → `harbor_wall_decor.png`
- 여덟 번째 테마 비교: 밤 고목 버섯 숲 / 마법사 탑 서재 / 포도원 지하 저장고 입구 / 강가 물레방앗간 → `room_themes_8.png`
- 밤의 거대 고목 속 버섯 숲(약자 MU): 내부 `... a small piece of an enchanted forest at night fitted into a square room, fully enclosed inside a giant hollow tree: four walls of thick vertical bark ridges about 8 m tall with moss patches and shelf fungus, and a ceiling of the tree's inner wood ... with a few small knot holes showing the night sky ... no huge roots breaking through the walls` → `mushroom_interior.png` / 소품 4x4(호박·분홍·청록 버섯 무리·작은 버섯·통나무·납작 바위·이끼 바위·고사리·벤치·탁자·그루터기·낙엽·씨앗 꼬투리 줄·이끼 언덕·팻말·버섯 바구니) → `mushroom_props.png` / 벽 장식 3x3(선반 버섯·빛나는 틈 버섯·이끼 자락·옹이 둥지·꽃 담쟁이·정령 탈·씨앗 꼬투리 줄·물약 선반·꽃 이끼) → `mushroom_wall_decor.png`
- 아홉 번째 테마 비교: 성 무기고 훈련장 / 해질녘 예배당 묘지 / 가을 사냥꾼 오두막 / 달빛 수정 동굴 호수 → `room_themes_9.png`
- 해 질 녘 마을 예배당 묘지(약자 CP): 내부 `... a small piece of a quiet village chapel graveyard at dusk fitted into a square room, fully enclosed: four walls of old grey stone with a plastered upper half and dark timber trims ... small arched chapel windows glowing warm, and a ceiling of dark wooden roof trusses with plank roof boards, a few boards missing so the violet dusk sky shows ...` → `chapel_interior.png` / 소품 4x4(둥근 비석·십자 비석·무덤 판·천사상·무너진 담·돌관·초 무리·제단·등 기둥·들풀·벤치·외바퀴 수레·우물·죽은 나무·돌 더미·나무 십자) → `chapel_props.png` / 벽 장식 3x3(빛나는 창·벽 촛대·기념 명판·꽃 담쟁이·별 깃발·성인 벽감·벽등·말린 꽃·초 선반) → `chapel_wall_decor.png`
- 열 번째 테마 비교(바닥은 "one calm low-contrast surface ... never a checkerboard of tiles" 문장 추가): 성 무기고 훈련장 / 가을 사냥꾼 오두막 / 달빛 수정 동굴 호수 / 새벽 마을 장터 → `room_themes_10.png`
- 새벽 마을 장터(약자 MK): 내부 `... a cozy medieval village market square at dawn fitted into a square room, fully enclosed: the four walls are rows of timber-framed house fronts about 8 m tall ... the ceiling is a grid of heavy wooden beams with faded cloth awnings ... The floor is one calm surface of packed earth with a wide band of large pale flagstones ...` → `market_interior.png` / 소품(노점 2·우물·사과·양배추 상자·상자 더미·통·통 묶음·포대·꽃 수레·건초 수레·벤치·항아리 탁자·등 기둥·장작·빵 바구니) → `market_props.png` / 벽 장식 3x3(빵 간판·창 화분·벽 랜턴·양파 마늘 줄·문 차양·항아리 선반·말발굽 간판·담쟁이·게시판) → `market_wall_decor.png`(원본 다운로드가 안 돼 화면 캡처)
- 직전 2x2(`room_themes_8.png`)에서 서재·포도원·방앗간을 상세 레퍼런스 없이 만들었다(제미나이 한도 06:00~07:27).
- 제미나이 입력창 클릭은 좌표 말고 `find`로 찾은 ref로 한다(창 크기에 따라 좌표가 바뀌어 프롬프트가 안 들어간 적 있음).
- 주의: 벽 장식 시트는 "wall decorations"만 쓰면 앞의 신전 벽돌 시트를 고쳐 그린다. `(do not reuse or edit any previous image, no stone bricks, no temple)`와 `in front of a small chunk of rough faceted cave rock (natural rock, not bricks)`처럼 바탕을 분명히 적는다.
- 고른 테마 상세(세상 한 조각을 방에 담기): `One large detailed concept art of a single combat arena that is a small piece of an outdoor world fitted into a square room: no indoor walls, instead the square is bounded naturally by dense forest trees, a rocky cliff edge, and crumbling ruined temple wall sections. ... A ruined stone archway entrance on the near side and ... exit on the far side. A wide open ... plaza in the center for fighting monsters, with only a few low pieces of cover ... Around the edges, filled densely but tidily with props: ...` + 방 콘셉트 스타일 문구 → `forest_temple_arena.png`
- 소품 시트: `A modeling reference sheet of the individual props and building pieces from that arena, each shown alone, evenly spaced in a 4x4 grid with empty space between them, all at a consistent 3/4 view: 1. ... 16. ...` + 3D 공통 스타일 문구(배경 문장은 `Plain light-grey background, even soft lighting, no shadows on the ground, no text, no labels, no numbers.`) → `forest_temple_props.png`
- 신전 내부로 막은 버전(사방 벽 + 일부 무너진 천장): `The same overgrown temple ruin arena, but now fully enclosed inside an old stone temple hall: four thick cut-stone walls about 8 m tall with simple pilasters, a heavy stone ceiling with large partly collapsed holes ... a wide arched doorway in the middle of the left wall as entrance and another in the right wall as exit. Inside: worn stone floor of large plain slabs with only a few big soft organic moss patches (not square, not repeated) ... Shown as a cutaway view from above at 45 degrees with the near two walls and part of the ceiling cut away` + 방 콘셉트 스타일 문구 → `forest_temple_interior.png`
- 벽 장식 시트(3x3, 배경 벽은 모델링하지 않음): `A modeling reference sheet of wall decorations for the inner walls of that overgrown stone temple, each piece shown alone flat against a short plain stone wall backdrop, evenly spaced in a 3x3 grid ... 1. ivy climbing up ... 2. moss drape hanging down from the top cornice ... 3. carved stone relief panel ... 4. shallow arched wall niche ... 5. broken iron wall sconce bracket with a lantern ... 6. large diagonal crack ... fern ... 7. faded cloth banner ... 8. tree roots breaking through the wall ... 9. small mushrooms and moss growing on a ledge. Natural, irregular, organic placement, nothing symmetrical or repeated.` + 3D 공통 스타일 문구 → `forest_temple_wall_decor.png`

## 방 지도 화면
- 비교 6안: `A 2x2 grid of four different full-screen game UI concepts for a dungeon route map screen ... small round room node icons connected by dashed ink paths that branch and merge upward from a start node at the bottom ...` + UI 공통 스타일 문구 → `Docs/ArtRef/RoomMap_concepts.png`(사용자 선택: 6번 찢어진 가죽 일지 느낌)
- 배경: `A single empty game map backdrop page in the style of concept 6 of the previous image: one wide torn aged parchment journal page, 16:9, with ragged torn edges ..., a few faint small sepia ink sketches only in the four corners ... The large center area is completely empty plain parchment: no paths, no nodes, no icons, no legend, no scroll, no wax seal.` + UI 공통 스타일 문구 → `SourceArt/UI/Map/T_MapBackdrop.png`
- 칸 조각(2x2): 칼 두 자루 칸 / 돌 아치 시작 칸 / 붉은 X 표시 / 금 테두리 + 밀랍 봉인(지금 칸) + UI 공통 스타일 문구(+ `no numbers`) → `Tools/SliceIconSheet.ps1 -Cols 2 -Rows 2 -Size 192 -Prefix T_Map`
- 제미나이 원본 다운로드 버튼이 안 먹을 때: 페이지에서 마지막 큰 `img`를 캔버스에 그려 `toDataURL`로 내려받는다.

## 무기: 스태프
- 비교 4안: `Reference sheet of four different simple wooden magic staffs for a first-person action roguelike, each shown standing upright in front view, evenly spaced side by side in one row ... 1: a gnarled oak staff with a glowing amber crystal held in twisted roots at the top. 2: ... pale blue orb. 3: ... hanging small brass lantern. 4: ... iron ring holding a floating straw-yellow rune stone ... about chest height of a human, plain and practical.` + 3D 공통 스타일 문구 → `Docs/ArtRef/staff_concepts.png`(사용자 선택: 1번 뿌리+호박 수정)

## 무기: 전투 도끼·번개 지팡이
- 레퍼런스: `Reference sheet of two weapons for a first-person action roguelike, each shown alone, side by side ..., each in front view and edge-on side view. Left: a two-handed battle axe about 90 cm long, straight ash wood haft with a leather-wrapped grip near the bottom end and a small iron butt cap, one single-bladed crescent iron axe head with a short back spike, held to the haft by iron bands and rivets. Right: a short one-handed magic wand about 45 cm long, dark wood rod with a leather-wrapped grip at the bottom, the top tip wrapped in coiled copper wire holding a small pointed straw-yellow crystal that faintly glows like a lightning spark. Plain and practical, no engravings.` + 3D 공통 스타일 문구 → `Docs/ArtRef/axe_wand.png`
- 아이템 아이콘(같은 대화창): `two game inventory item icons side by side in one wide 2:1 image, each icon one simple bold drawing centered in its own equal half, ... drawn diagonally from bottom-left to top-right. 1. the battle axe from the previous image ... 2. the short magic wand from the previous image ... No frames, no borders, no slots, no numbers.` + UI 공통 스타일 문구 → `SourceArt/UI/Inventory/WeaponIcons2_sheet.png` → `Tools/SliceIconSheet.ps1 -Cols 2 -Rows 1 -Size 192 -Prefix T_Item_`

## 인벤토리 창
- 비교 4안: `A 2x2 grid of four different game UI concepts for an inventory window ... on the left an equipment area with one large weapon slot and three smaller gem skill slots in a row, on the right a bag grid of 5 columns by 4 rows ... icons: a red health potion bottle, a blue mana potion bottle, two small faceted gems, a sword, and a wooden staff with an amber crystal. Concept 1: torn parchment journal page. 2: open leather-bound book. 3: wooden-framed parchment board with brass corner caps. 4: rolled-out scroll with gold leaf borders and a red wax seal.` + UI 공통 스타일 문구 → `Docs/ArtRef/Inventory_concepts.png`
- 배경(사용자 선택: 1안 + 검은 바탕): `A single empty inventory window backdrop in the style of concept 1 ...: one wide torn aged parchment journal spread (two facing pages) with ragged torn edges, a thin gold leaf inner border line, and a faint vertical center fold ... Both pages are completely empty ...` + UI 공통 스타일 문구(마지막 문장 대신 `The page lies on a pure flat solid black background (#000000), no shadow.`) → `SourceArt/UI/Inventory/T_InventoryBackdrop.png`(오른쪽 아래 제미나이 표시는 칠해서 지움)
- 칸·아이템 3x3: 1 가방 칸 2 무기 칸(금박 모서리) 3 젬 칸 4 금박 선택 테두리 5 체력 포션 6 마나 포션 7 검 8 스태프 9 밀랍 + UI 공통 스타일 문구(+ `no numbers`) → `Tools/SliceIconSheet.ps1 -Cols 3 -Rows 3 -Size 192 -Prefix T_` (선택 테두리 안쪽 흰색은 따로 지움)
- 젬 2x2: `one faceted cut gemstone ... 1. muted red gem with engraved swirling circular arrow 2. muted amber gem with downward hammer 3. muted sage green gem with leaf and breath wisp 4. plain muted blue gem` + UI 공통 스타일 문구 → `T_Item_Gem_<스킬ID>`
