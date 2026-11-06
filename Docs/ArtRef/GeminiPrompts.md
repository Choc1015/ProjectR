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
