---
name: imagen-design-hub
description: 사용자가 imagegen 또는 로컬 source art로 MiriCanvas/DesignHub 산출물을 준비할 때 사용한다. JPG 배경, 사진 JPG, 투명 PNG 요소, SVG 요소, GIF 요소, 크로마키 컷아웃, Photopea 마무리, DesignHub CSV 수정, 키워드 정리, 업로드 안전 파일명, 공식 요소 가이드 라우팅을 다룬다.
---

# Imagen Design Hub

[English version](SKILL.md)

이 스킬은 `image_gen`, 로컬 source art, 벡터/애니메이션 도구로 준비하는 MiriCanvas / DesignHub 시각 산출물을 다룬다. raster imagegen 경로와 공식 SVG/GIF 요소 가이드 라우팅을 한곳에서 관리한다.

핵심 분기:

- 배경 요소가 목표이면 `image_gen -> source PNG 보존 -> JPG 변환/검증 -> Background CSV`.
- 투명 PNG 요소가 목표이면 `image_gen -> chroma-key source 보존 -> helper alpha -> Photopea -> PNG element CSV`.
- SVG 요소가 목표이면 `vector source -> SVG cleanup -> SVG validation -> SVG element CSV`를 사용하되, 이 경로는 아직 초기 alpha라 수동 검수를 강화한다.
- GIF 요소가 목표이면 `frame/animation source -> GIF encode -> animation/size validation -> GIF CSV`를 사용하되, 이 경로는 아직 초기 alpha라 수동 검수를 강화한다.
- HTML/canvas보다 자연스러운 수면, 물결, 빛반사, 사진풍 질감, 실사 배경이 더 중요하면 imagegen 배경 경로를 우선한다.
- 공식 요소 가이드 전체 링크맵이 필요하면 [references/designhub-element-guide-map.ko.md](references/designhub-element-guide-map.ko.md)를 읽는다.

## 의존성

- 생성 필수: built-in `image_gen` 도구.
- 로컬 이미지 처리 필수: `scripts/chroma_key.py` 사용 시 Python 3.10 이상과 Pillow. NumPy는 legacy fallback인 `scripts/remove_chroma_key.py`를 사용할 때만 필요하다.
- 업로드용 PNG 요소 필수: Chromium 계열 브라우저의 Photopea와 Photopea runner. 프로젝트 전용 runner가 있으면 우선 사용하고, 없으면 `scripts/write_photopea_runner.py`를 사용한다.
- SVG 요소 필수: 실제 벡터 source/editor/export 경로와 XML/SVG 검증. raster 이미지만 embed한 SVG는 제출하지 않는다.
- GIF 요소 필수: frame 또는 animation source와 loop/playback, 투명도, 크기, 용량을 확인할 GIF encoder/player.
- 재사용 Python 코드는 `src/imagegen_chroma_cutout/`에 있다. 기존 스크립트 호환성을 위해 예전 패키지명을 유지한다.
- 사용자가 명시적으로 승인하지 않은 외부 업로드나 제출 작업은 하지 않는다.

필요할 때만 helper 의존성을 설치한다.

```bash
python -m pip install -r requirements.txt
```

Windows에서는 스킬 디렉터리에서 PowerShell로 실행하고, `python3`나 POSIX shell expansion에 기대지 말고 `py -3` 또는 `python`을 사용한다.

```powershell
py -3 -m pip install -r requirements.txt
```

## 경로 선택

이미지를 생성하기 전에 산출물 종류를 먼저 분류한다.

### `background-jpg`

DesignHub 배경 요소, JPG 배경, 넓은 질감, 수면, 수영장 바닥, 패턴, 종이/그라데이션 배경, 문서 전체를 채우는 이미지에 사용한다.

- built-in `image_gen`을 사용한다.
- 투명 배경, 크로마키, 체크보드, 컷아웃, Photopea alpha 처리를 요청하지 않는다.
- 뚜렷한 피사체가 없는 full-bleed 직사각형 또는 정사각형 배경으로 프롬프트를 작성한다.
- Codex generated image directory의 source PNG를 작업 폴더에 보존한다. POSIX shell에서는 `$CODEX_HOME/generated_images/...`, Windows PowerShell에서는 환경 변수가 있을 때 `$env:CODEX_HOME\generated_images\...` 형식을 사용한다.
- 최종 파일은 JPG로 변환한다.
- DesignHub CSV의 `contentType` 값은 `Background`를 사용한다.
- CSV `fileName`에서 `.jpg`를 제거한다.
- `uniqueId`는 파일 업로드 후 DesignHub에서 내려받은 메타데이터 CSV의 값이 아니면 비워 둔다.

권장 폴더:

```text
outputs/<run-id>/assets/source-imagegen-batch/
outputs/<run-id>/assets/background-jpg-imagegen/
outputs/<run-id>/metadata/
outputs/<run-id>/review/
outputs/<run-id>/logs/
```

### `png-element`

투명 스티커, 일러스트, 오브젝트, 컷아웃, PNG 요소, 배경 제거, alpha가 필요한 산출물에 사용한다.

- 제거 가능한 단색 크로마키 배경으로 생성한다.
- 독립 PNG 요소를 여러 개 만들 때는 요소마다 source 이미지를 따로 생성한다. 여러 요소를 한 장에 몰아 만든 뒤 잘라 쓰지 않는다. 분리 후 확대하면 계단현상과 약한 anti-aliasing이 드러날 수 있다.
- source 이미지는 `assets/source-imagegen/`에 보존한다.
- 복사된 `scripts/chroma_key.py` helper를 실행해 `assets/raw/`로 출력한다. DesignHub PNG 요소 작업에서는 built-in `.system/imagegen`의 `remove_chroma_key.py` helper를 사용하지 않는다.
- DesignHub/MiriCanvas 업로드용 PNG 요소라면 Photopea 또는 프로젝트 Photopea runner를 실행해 `assets/processed/`를 만든다.
- DesignHub CSV의 `contentType` 값은 `PNG element`를 사용한다.
- 실제 DesignHub 등록 전에 업로드 안전 고유 basename을 준비한다.

### `photo-jpg`

배경 요소가 아닌 실제 사진에 사용한다. JPG라는 이유만으로 실제 사진을 배경으로 잘못 분류하지 않는다.

### `svg-element`

명확한 피사체와 완전히 제거된 배경을 가진 단순하고 색상 변경 가능한 벡터 일러스트에 사용한다.

- 이 스킬의 SVG 지원은 아직 초기 alpha다. vector 생성 품질, path 모양, crop/viewBox, 색상 수, DesignHub 승인 가능성에 한계가 있을 수 있다.
- 손으로 작성한 SVG, 벡터 에디터 export, trace/rebuild 벡터 art처럼 실제 벡터 workflow를 사용한다.
- 형태는 단순하게 유지하고 색상은 5개 이하로 정리한다.
- 같은 flat 디자인이 MiriCanvas에서 색상 변경 가능해야 한다면 PNG보다 SVG를 우선한다.
- 3D, 그라데이션, 사진 같은 질감, 복잡한 raster art, embed bitmap 출력에는 SVG를 쓰지 않는다. 이런 경우 `png-element`로 보낸다.
- DesignHub CSV의 `contentType` 값은 `SVG element`를 사용한다.
- CSV `fileName`에서 `.svg`를 제거한다.
- 확장형 요소는 먼저 SVG로 업로드한 뒤 메타데이터 입력 단계에서 크기조정 타입을 설정한다.

### `gif-element`

명확한 피사체와 완전히 제거된 배경을 가진 움직이는 일러스트/아트 요소에 사용한다.

- 이 스킬의 GIF 지원은 아직 초기 alpha다. 투명도 한계, dithering, edge halo, frame flicker, 큰 파일 크기, loop/playback 문제를 수동으로 보정해야 할 수 있다.
- frame 또는 animation source 파일을 사용하고 `.gif`로 encode한다.
- 최종 산출물은 눈에 보이게 움직여야 한다. 정지 이미지를 GIF로 저장한 것만으로는 부족하다.
- animation format과 source가 허용하는 범위에서 배경을 제거/투명하게 유지한다.
- 촬영 영상/footage를 GIF 요소로 취급하지 않는다. 영상은 권한이 필요한 `video-element` 경로다.
- DesignHub CSV의 `contentType` 값은 `GIF`를 사용한다.
- CSV `fileName`에서 `.gif`를 제거한다.

### 권한형 또는 에디터 전용 경로

- `video-element`: MP4 동영상 제출은 DesignHub 포트폴리오 심사와 업로드 권한이 필요하다. 사용자가 이미 권한을 보유한 경우가 아니면 upload-ready MP4 제출을 약속하지 않는다.
- `combination-element`: 미리캔버스 에디터에서 만들고 디자인 문서 URL로 등록한다. 이 스킬이 만드는 로컬 파일 배치가 아니다.

## Imagegen 배경 워크플로

사용자가 imagegen이 더 낫다고 말하거나, 배경 JPG를 요청하거나, 자연스러운 질감/배경이 중요한 산출물일 때 이 경로를 사용한다.

1. `miricanvas-design` 체크아웃 안에서 작업할 때는 먼저 프로젝트 지침을 읽고, 현재 repo root 기준 상대경로를 사용한다.
2. 사용자가 reference 이미지를 주면 먼저 검사하고, 사용자가 해당 이미지를 직접 수정하라고 한 경우가 아니면 edit target이 아니라 reference로 표시한다.
3. 요청된 variant마다 built-in `image_gen`을 한 번씩 호출한다. 서로 다른 배경에는 서로 다른 프롬프트를 사용한다.
4. 생성 후 Codex generated image directory 아래의 새 파일을 찾아 작업 폴더로 복사한다. 원래 생성 파일은 그대로 둔다.
5. 선택한 source를 JPG로 변환한다.
   - RGB, alpha 없음
   - DesignHub 배경 기준 한 변 최소 2500 px
   - 최대 9800 px
   - 최소 120 DPI, 프로젝트 별도 기준이 없으면 로컬 일관성을 위해 300 DPI
   - 50 MB 미만
6. 다음 헤더로 매칭 CSV를 작성한다.
   ```text
   fileName,uniqueId,elementName,keywords,tier,contentType
   ```
7. 배경 JPG 행은 다음 규칙을 따른다.
   - `fileName`: basename만 사용하고 `.jpg` 제거
   - `uniqueId`: filename-only 등록용이면 빈칸
   - `tier`: `Premium`
   - `contentType`: `Background`
8. contact sheet를 만들고 눈으로 확인한다. 배경 요소에는 사람, 오브젝트, 텍스트, 로고, 워터마크, 프레임, 단일 지배 피사체가 없어야 한다.
9. 준비 완료를 보고하기 전에 수치 검증과 눈검수를 모두 수행한다.

### 배경 프롬프트 템플릿

```text
Use case: photorealistic-natural
Asset type: MiriCanvas DesignHub background JPG source
Primary request: <background topic>
Scene/backdrop: <surface/environment>
Style/medium: photorealistic high-resolution background texture
Composition/framing: full-bleed square or rectangular background, no focal subject, no border
Lighting/mood: <lighting and mood>
Color palette: <colors>
Materials/textures: <tile, water, paper, caustic light, etc.>
Constraints: no text, no logo, no watermark, no people, no objects, no transparent background, no checkerboard, no dominant subject
```

## 투명 PNG 컷아웃 워크플로

사용자가 투명 PNG, PNG 요소, 컷아웃, 배경 제거, Photopea, 업로드용 alpha 산출물을 요청할 때 이 경로를 사용한다.

1. 크로마키 색을 선택한다.
   - 기본값 `#00ff00`
   - 초록 피사체에는 `#ff00ff`
   - 파란 피사체에는 `#0000ff`를 피한다
   - 기존 프로젝트 key color는 피사체와 충돌하지 않을 때만 사용한다
   - 피사체 색이 key color와 가깝다면 생성 전에 다른 key color를 고른다. 충돌하는 key color를 helper가 해결해 줄 것이라고 기대하지 않는다.
2. built-in `image_gen`으로 완전히 평평한 key-color 배경에 생성한다.
3. 생성 source를 작업 폴더로 복사한다.
4. 복사된 `scripts/chroma_key.py` helper를 실행한다.
5. alpha, 투명 모서리, 피사체 범위, key-color fringe, 피사체 내부 디테일 보존, anti-aliased edge를 체크보드/흰색/어두운 배경 preview에서 검증한다.
6. DesignHub/MiriCanvas 업로드용 PNG 요소라면 Photopea finishing을 실행하고 `assets/processed/`를 검증한다.
7. 업로드 안전 고유 파일명과 매칭 CSV를 준비한다.

### 크로마 프롬프트 템플릿

```text
Use case: background-extraction
Asset type: transparent PNG cutout / PNG element
Primary request: <user request>
Subject: <single clear subject or element set>
Style/medium: <photo, illustration, 3D, flat 2D, etc.>
Composition/framing: centered subject, fully visible, generous padding, no cropping
Scene/backdrop: perfectly flat solid <KEY_COLOR> chroma-key background
Constraints:
- The background must be one uniform <KEY_COLOR> color with no shadows, gradients, texture, reflections, floor plane, lighting variation, or checkerboard.
- Keep the subject fully separated from the background with crisp readable edges.
- Do not use <KEY_COLOR> anywhere inside the subject.
- No cast shadow, contact shadow, reflection, watermark, logo, signature, UI capture, QR code, or text unless explicitly requested.
- Preserve all subject details; do not cut off any part of the subject.
```

## Helper 명령

복사된 `scripts/chroma_key.py` helper를 먼저 사용한다. 이 파일은 첨부/프로젝트의 `scripts/chroma_key.py` helper를 스킬 번들에 복사해 둔 것이다. DesignHub PNG 요소 작업에서는 built-in `.system/imagegen`의 `remove_chroma_key.py` helper를 사용하지 않는다. 사용자가 비교나 fallback을 명시적으로 요청한 경우가 아니면 legacy `scripts/remove_chroma_key.py`도 기본 helper로 쓰지 않는다.

복사된 helper가 없거나 오래되었으면 실행 전에 첨부/프로젝트 helper를 스킬로 복사한다.

```bash
cp "<repo>/scripts/chroma_key.py" "scripts/chroma_key.py"
chmod +x "scripts/chroma_key.py"
```

명시적인 key color와 edge-connected cleanup으로 실행한다.

```bash
python scripts/chroma_key.py \
  --input "<source.png>" \
  --output "<final-alpha.png>" \
  --background "<KEY_COLOR>" \
  --tolerance 48 \
  --scope edge \
  --dpi 350
```

PowerShell 예시:

```powershell
py -3 ./scripts/chroma_key.py `
  --input "./source.png" `
  --output "./final-alpha.png" `
  --background "<KEY_COLOR>" `
  --tolerance 48 `
  --scope edge `
  --dpi 350
```

기본 edge mode는 이미지 border와 연결된 픽셀을 지우고, 내부의 정확/근접 key-color 섬도 `min(tolerance, 24)` 기준으로 제거한다. 피사체에 key color와 가까운 색이 있다면 먼저 더 안전한 key color로 다시 생성한다. 내부 near-key 피사체 색을 보존하는 비교용 run이 필요할 때만 다음 옵션을 쓴다.

```bash
python scripts/chroma_key.py \
  --input "<source.png>" \
  --output "<final-alpha-preserve0.png>" \
  --background "<KEY_COLOR>" \
  --tolerance 48 \
  --scope edge \
  --enclosed-tolerance 0 \
  --dpi 350
```

tolerance를 높이는 것은 key color가 피사체와 겹치지 않는다고 확인한 뒤에만 한다. key color가 피사체와 충돌하면 tolerance를 넓히지 말고 프롬프트/배경색을 바꾼다.

contact sheet는 검토용 산출물일 뿐이다. 여러 오브젝트가 들어간 sheet에서 최종 업로드 PNG를 잘라 만들지 않는다. 독립 요소가 분리 후 jagged하게 보이면 원래 per-element source로 돌아가거나 요소별로 다시 생성한다.

## Photopea 처리

Photopea는 배경 제거의 대체 수단이 아니다. alpha PNG 요소의 마무리 단계다.

DesignHub/MiriCanvas PNG 요소 작업:

1. imagegen source는 `assets/source-imagegen/`에 둔다.
2. helper alpha 출력은 `assets/raw/`에 둔다.
3. 프로젝트 runner가 있으면 먼저 실행한다.
   ```bash
   node src/cli.mjs photopea-runner --run outputs/<run-id>
   ```
4. 없으면 번들 runner를 만든다.
   ```bash
   python scripts/write_photopea_runner.py \
     --raw-dir "outputs/<run-id>/assets/raw" \
     --processed-dir "outputs/<run-id>/assets/processed" \
     --out "outputs/<run-id>/photopea/runner.html"
   ```
   Windows PowerShell:
   ```powershell
   py -3 ./scripts/write_photopea_runner.py `
     --raw-dir "outputs/<run-id>/assets/raw" `
     --processed-dir "outputs/<run-id>/assets/processed" `
     --out "outputs/<run-id>/photopea/runner.html"
   ```
5. `miricanvas-design` repo에서는 PNG 요소를 350 DPI, 한 변 최소 2500 px, tight alpha bbox, alpha 보존 기준에 맞춘다.

사용자가 수동 이미지 편집을 명시적으로 요청하지 않으면 JPG 배경에는 Photopea를 건너뛴다.

## SVG 요소 워크플로

사용자가 SVG 요소, vector 요소, 색상 변경 가능한 icon, 단순 sticker, 확장형 요소, 말풍선, label, flag, memo note, 깨끗하게 resize되어야 하는 shape를 요청할 때 이 경로를 사용한다.

이 경로는 아직 초기 alpha다. DesignHub 승인을 보장하는 경로가 아니라 후보와 검증 근거를 만드는 경로로 취급한다. 시각 품질이 중요하면 vector editor 또는 Claude 생성 후보와 비교해 더 나은 source를 선택한다.

1. vector source에서 시작한다. imagegen을 아이디어용으로 썼다면 최종 export 전에 실제 vector shape로 다시 만들거나 trace한다.
2. 사각형 이미지처럼 동작하는 배경과 artboard를 제거한다.
3. 명확한 단일 피사체 또는 재사용 가능한 요소를 유지한다. template처럼 완성된 layout은 피한다.
4. 보이는 fill/stroke 색상을 5개 이하로 줄이고 정리한다.
5. embedded raster image, external link, script, `foreignObject`, 숨은 watermark, 알 수 없는 font text, artboard 밖 stray object를 피한다.
6. tight-crop `viewBox`가 있는 깨끗한 `.svg`로 export한다.
7. 파일 규격을 검증한다.
   - SVG 확장자
   - export 도구가 DPI를 제공한다면 최소 72 DPI
   - 최대 dimension 6000 px
   - 150 MB 미만
8. SVG를 체크보드, 흰색, 어두운 배경 preview에서 렌더링하고 사각형 artboard/backdrop, 잘린 피사체, 과한 여백, path 품질 문제가 없는지 확인한다.
9. CSV 행은 확장자 없는 `fileName`, 빈칸 또는 DesignHub 제공 `uniqueId`, `tier=Premium`, `contentType=SVG element`로 작성한다.

확장형 SVG 요소도 파일 workflow는 동일하다. 확장형/기본형 차이는 파일 확장자가 아니라 메타데이터의 크기조정 타입에서 선택한다.

## GIF 요소 워크플로

사용자가 GIF 요소, animated sticker, looping illustration, motion badge, 움직이는 icon형 art를 요청할 때 이 경로를 사용한다.

이 경로는 아직 초기 alpha다. DesignHub 승인을 보장하는 경로가 아니라 후보와 검증 근거를 만드는 경로로 취급한다. GIF 투명도와 frame 최적화는 수동 검수가 자주 필요하다.

1. frame/animation source 파일을 만들거나 모은다. source 폴더에 보존한다.
2. 모든 frame에서 피사체가 명확하고, 잘리지 않고, 배경과 분리되어 있어야 한다.
3. 사용자가 DesignHub와 무관한 실험을 명시하지 않는 한 촬영 footage를 GIF 요소로 변환하지 않는다. DesignHub 영상은 권한이 필요한 별도 MP4 경로다.
4. `.gif`로 encode하고 playback, loop timing, edge residue, frame jitter를 확인한다.
5. 파일 규격을 검증한다.
   - GIF 확장자
   - 정지 GIF가 아니라 눈에 보이게 움직임
   - 가능한 경우 최소 72 DPI
   - 최소 700 px
   - 최대 1920 px
   - 25 MB 미만
6. GIF를 체크보드, 흰색, 어두운 배경 preview에서 렌더링하고 투명/제거된 배경이 frame 사이에서 flicker되지 않는지 확인한다.
7. CSV 행은 확장자 없는 `fileName`, 빈칸 또는 DesignHub 제공 `uniqueId`, `tier=Premium`, `contentType=GIF`로 작성한다.

요청된 움직임이 촬영 영상에 가깝다면 `video-element`로 보내고, MP4 제출 배치를 준비하기 전에 사용자가 DesignHub 영상 권한을 보유했는지 확인한다.

## 메타데이터 규칙

DesignHub/MiriCanvas 메타데이터는 제작 과정이 아니라 구매자가 검색할 단어를 설명해야 한다.

- 쉼표로 구분한 키워드 20~25개를 사용한다.
- 중복을 제거한다.
- 공식 주제어와 구체적인 시각 용어를 앞쪽에 둔다.
- `keywords`와 `elementName`에서 제작/프로세스/파일/관리 용어를 제거한다.
- `Photopea`, `API`, `후처리`, `프롬프트`, `imagegen`, `배경제거`, `PNG`, `JPG`, `SVG`, `GIF`, `MP4`, `2D`, `350DPI`, `투명배경`, run ID, 날짜, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스`, `배경소스`, `꾸밈요소` 같은 용어를 피한다.
- 사용자가 특정 키워드를 유지하거나 제거하라고 명시하면 CSV와 문서 전체에 적용한다.

CSV content type 값:

```text
Photo
Photo(Cut-out)
SVG element
PNG element
GIF
Background
```

DesignHub CSV에는 `JPG background`라고 쓰지 않는다. `Background`를 사용한다.

## DesignHub CSV 왕복

실제 파일 업로드 후에는 DesignHub에서 내려받은 CSV가 `fileName`과 `uniqueId`의 기준이다. 파일 등록 후 로컬 preupload CSV를 그대로 올리지 않는다.

1. 사용자 확인 후 승인된 UI 경로로 파일을 업로드한다.
2. 현재 DesignHub CSV를 다운로드한다.
3. 다운로드한 전체 CSV에 준비한 메타데이터를 병합하되 기존 모든 행과 모든 `uniqueId`를 보존한다.
4. 병합한 전체 CSV를 UI로 업로드한다.
5. DesignHub 완료 메시지나 배너를 확인하고 처리된 행 수를 기록한다.
6. 파일 업로드, CSV 업로드, 최종 심사 제출 여부를 각각 따로 말한다. 사용자가 별도 단계로 요청하지 않으면 최종 심사 제출은 누르지 않는다.

## 업로드 안전 파일명

PNG 요소는 DesignHub에서 이전 시도에 사용한 이름 때문에 거절될 수 있다. 업로드 전에 별도 고유 이름 폴더와 매칭 CSV를 만든다.

권장 basename:

```text
<short-topic-slug>-<YYYYMMDD>-<HHmm>-<NN>
```

번들 helper:

```bash
python scripts/prepare_designhub_unique_upload.py \
  --csv "outputs/<run-id>/metadata/preupload.csv" \
  --images-dir "outputs/<run-id>/assets/processed" \
  --out-dir "outputs/<run-id>/assets/processed-designhub-unique-<YYYYMMDD-HHmm>" \
  --out-csv "outputs/<run-id>/metadata/designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" \
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

PowerShell 예시:

```powershell
py -3 ./scripts/prepare_designhub_unique_upload.py `
  --csv "outputs/<run-id>/metadata/preupload.csv" `
  --images-dir "outputs/<run-id>/assets/processed" `
  --out-dir "outputs/<run-id>/assets/processed-designhub-unique-<YYYYMMDD-HHmm>" `
  --out-csv "outputs/<run-id>/metadata/designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" `
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

JPG 배경, SVG 요소, GIF 요소도 generic name은 피한다. topic slug와 timestamp/index를 사용하고, CSV `fileName`에는 확장자를 넣지 않는다.

## 검증

경로에 맞는 검증을 실행한다.

### 배경 JPG 검사

- source PNG가 Codex generated image directory에만 있지 않고 작업 폴더에도 존재한다.
- 최종 파일이 JPEG/JPG다.
- alpha 채널이 없다.
- 너비와 높이가 DesignHub 배경 제한을 만족한다.
- DPI가 최소 120이다.
- 파일 크기가 50 MB 미만이다.
- CSV 행 수가 최종 JPG 수와 같다.
- CSV `fileName`에 확장자가 없고 `<fileName>.jpg`와 매칭된다.
- CSV `uniqueId`가 비어 있거나 DesignHub에서 제공한 값이다.
- CSV `contentType`이 `Background`다.
- 키워드가 20~25개의 고유한 구매자 검색어다.
- contact sheet에서 금지 콘텐츠 없이 사용할 수 있는 배경임이 확인된다.

### PNG 요소 검사

- 최종 파일이 alpha가 있는 PNG다.
- 모서리가 투명하고 피사체 범위가 그럴듯하다.
- 눈에 띄는 key-color fringe가 없다.
- key color와 비슷하다는 이유로 피사체 내부 디테일이 지워지지 않았다.
- 확대 검수에서 edge가 계단형이 아니라 anti-aliased 상태다.
- 최종 업로드 파일을 결합된 contact sheet에서 잘라 만들지 않았다.
- 체크보드, 흰색, 어두운 배경 preview가 통과한다.
- 업로드용 PNG 요소를 요청받았다면 Photopea processed 출력이 존재한다.
- PNG 요소 크기/DPI가 로컬 프로젝트 규칙과 맞는다.
- CSV basename과 processed/upload PNG basename이 일치한다.
- 키워드가 20~25개의 고유한 구매자 검색어다.

### SVG 요소 검사

- 최종 파일이 SVG이며 raster image를 `.svg`로 이름만 바꾼 것이 아니다.
- XML이 정상 parsing된다.
- embedded raster `<image>` payload, script, external link, `foreignObject`가 없다.
- `viewBox`와 dimension이 있고 최대 6000 px 제한 안에 있다.
- 보이는 색상이 5개 이하이다.
- 배경이 제거되어 있으며, 요소 자체가 재사용 가능한 memo/sticker shape인 경우가 아니라면 사각형 backdrop을 포함하지 않는다.
- crack, stray shape, 숨은 off-artboard object, watermark, logo, text artifact가 없다.
- 이 경로는 초기 alpha이므로 upload-ready라고 부르기 전에 path 품질, crop, DesignHub 적합성을 눈으로 확인한다.
- CSV `contentType`이 `SVG element`이고 CSV basename이 최종 SVG basename과 확장자 없이 일치한다.

### GIF 요소 검사

- 최종 파일이 GIF이고 눈에 보이게 움직인다.
- 크기가 최소 700 px, 최대 1920 px 범위다.
- 파일 크기가 25 MB 미만이다.
- 적절한 경우 배경이 제거/투명하고 frame 사이에서 flicker가 없다.
- loop 전체에서 피사체가 명확하고 잘리지 않으며 안정적이다.
- GIF로 잘못 분류한 video element가 아니라 움직이는 일러스트/아트다.
- 이 경로는 초기 alpha이므로 upload-ready라고 부르기 전에 투명도 품질, edge halo, playback 안정성을 눈으로 확인한다.
- CSV `contentType`이 `GIF`이고 CSV basename이 최종 GIF basename과 확장자 없이 일치한다.

프로젝트가 적용 가능한 검증 명령을 제공하면 실행한다.

```bash
node src/cli.mjs validate --run outputs/<run-id>
```

## 복잡한 투명도 경계

머리카락, 털, 깃털, 연기, 안개, 물보라, 유리, 액체, 투명 오브젝트, 반사, 부드러운 그림자, 실용적인 key color와 색이 충돌하는 피사체에는 크로마키 제거가 실패하거나 피사체를 손상할 수 있다.

진짜 native transparency가 필요해 보이면 CLI/API fallback으로 조용히 바꾸지 말고 먼저 사용자에게 물어본다. built-in `image_gen` 경로에서 무단으로 전환하지 않는다.

## 최종 보고

구체적인 경로와 산출물을 보고한다.

- built-in `image_gen` 또는 CLI fallback
- 산출물 종류: `background-jpg`, `png-element`, `photo-jpg`, `svg-element`, `gif-element`, `video-element`, `combination-element`
- source 이미지 폴더
- 최종 이미지 폴더
- metadata CSV 경로
- review/contact sheet 경로
- batch를 생성했다면 prompt log 경로
- 키워드 개수와 제거한 제작 용어
- 검증 요약
- SVG/GIF 경로를 사용했다면 초기 alpha 한계와 남은 수동 검수 리스크
- Photopea 사용 여부 또는 의도적으로 건너뛴 이유
- 남은 업로드 리스크

사용자가 명시적으로 승인하지 않았다면 외부 업로드/제출을 하지 않았다고 분명히 말한다.

## 테스트 프롬프트

라우팅 sanity check에는 `evals/evals.json`을 사용한다. 전체 eval/viewer 루프는 선택 사항이며, 사용자가 더 깊은 스킬 benchmark를 원할 때 실행한다.
