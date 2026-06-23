---
name: imagen-design-hub
description: 사용자가 imagegen으로 MiriCanvas 또는 DesignHub용 비트맵 산출물을 준비할 때 이 스킬을 사용한다. JPG 배경 요소, AI 생성 수영장/물빛/패턴/질감 배경, 투명 PNG 컷아웃, PNG 요소, 크로마키 배경 제거, Photopea crop/DPI 마무리, DesignHub 메타데이터 CSV 수정, 키워드 정리, 업로드 안전 파일명 배치를 다룬다. 자연스럽거나 실사풍 DesignHub 배경에는 built-in image_gen을 우선하고, source PNG를 작업 폴더에 보존한 뒤 최종 배경을 검증된 JPG로 변환한다. 투명 PNG 요소에만 크로마키 제거를 사용하고, 준비 완료를 보고하기 전에 파일 형식, 크기, DPI, alpha/no-alpha, CSV fileName/uniqueId/contentType, 키워드, 리뷰 시트를 반드시 검증한다.
---

# Imagen Design Hub

[English version](SKILL.md)

이 스킬은 MiriCanvas / DesignHub에 올릴 `imagegen` 기반 비트맵 산출물을 다룬다. 기존 투명 PNG 중심 흐름을 포함하되, 이제 투명 PNG 요소뿐 아니라 DesignHub 배경 JPG까지 같은 판단 체계 안에서 처리한다.

핵심 분기:

- 배경 요소가 목표이면 `image_gen -> source PNG 보존 -> JPG 변환/검증 -> Background CSV`.
- 투명 PNG 요소가 목표이면 `image_gen -> chroma-key source 보존 -> helper alpha -> Photopea -> PNG element CSV`.
- HTML/canvas보다 자연스러운 수면, 물결, 빛반사, 사진풍 질감, 실사 배경이 더 중요하면 imagegen 배경 경로를 우선한다.

## 의존성

- 생성 필수: built-in `image_gen` 도구.
- 로컬 이미지 처리 필수: Python 3.10 이상, Pillow, 그리고 `scripts/remove_chroma_key.py` 사용 시 NumPy.
- 업로드용 PNG 요소 필수: Chromium 계열 브라우저의 Photopea와 Photopea runner. 프로젝트 전용 runner가 있으면 우선 사용하고, 없으면 `scripts/write_photopea_runner.py`를 사용한다.
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
- source 이미지는 `assets/source-imagegen/`에 보존한다.
- `scripts/remove_chroma_key.py`를 실행해 `assets/raw/`로 출력한다.
- DesignHub/MiriCanvas 업로드용 PNG 요소라면 Photopea 또는 프로젝트 Photopea runner를 실행해 `assets/processed/`를 만든다.
- DesignHub CSV의 `contentType` 값은 `PNG element`를 사용한다.
- 실제 DesignHub 등록 전에 업로드 안전 고유 basename을 준비한다.

### `photo-jpg`

배경 요소가 아닌 실제 사진에 사용한다. JPG라는 이유만으로 실제 사진을 배경으로 잘못 분류하지 않는다.

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
2. built-in `image_gen`으로 완전히 평평한 key-color 배경에 생성한다.
3. 생성 source를 작업 폴더로 복사한다.
4. 번들 helper를 실행한다.
5. alpha, 투명 모서리, 피사체 범위, key-color fringe를 검증한다.
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

번들 helper를 먼저 사용한다. Windows 호환성을 위해 Bash 전용 환경변수 fallback 문법에 기대지 말고, 스킬 디렉터리에서 상대 script 경로로 실행하는 방식을 우선한다.

```bash
python scripts/remove_chroma_key.py \
  --input "<source.png>" \
  --out "<final-alpha.png>" \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

PowerShell 예시:

```powershell
py -3 .\scripts\remove_chroma_key.py `
  --input ".\source.png" `
  --out ".\final-alpha.png" `
  --auto-key border `
  --soft-matte `
  --transparent-threshold 12 `
  --opaque-threshold 220 `
  --despill
```

얇은 key-color fringe가 남으면 한 번만 다시 시도한다.

```bash
python scripts/remove_chroma_key.py \
  --input "<source.png>" \
  --out "<final-alpha-v2.png>" \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --edge-contract 1 \
  --despill
```

`--edge-feather 0.25`는 stair-stepping이 보이고 피사체가 유리, 물, 연기, 안개, 반사처럼 반투명 재질이 아닐 때만 사용한다.

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
   py -3 .\scripts\write_photopea_runner.py `
     --raw-dir "outputs\<run-id>\assets\raw" `
     --processed-dir "outputs\<run-id>\assets\processed" `
     --out "outputs\<run-id>\photopea\runner.html"
   ```
5. `miricanvas-design` repo에서는 PNG 요소를 350 DPI, 한 변 최소 2500 px, tight alpha bbox, alpha 보존 기준에 맞춘다.

사용자가 수동 이미지 편집을 명시적으로 요청하지 않으면 JPG 배경에는 Photopea를 건너뛴다.

## 메타데이터 규칙

DesignHub/MiriCanvas 메타데이터는 제작 과정이 아니라 구매자가 검색할 단어를 설명해야 한다.

- 쉼표로 구분한 키워드 20~25개를 사용한다.
- 중복을 제거한다.
- 공식 주제어와 구체적인 시각 용어를 앞쪽에 둔다.
- `keywords`와 `elementName`에서 제작/프로세스/파일/관리 용어를 제거한다.
- `Photopea`, `API`, `후처리`, `프롬프트`, `imagegen`, `배경제거`, `PNG`, `JPG`, `2D`, `350DPI`, `투명배경`, run ID, 날짜, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스`, `배경소스`, `꾸밈요소` 같은 용어를 피한다.
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
py -3 .\scripts\prepare_designhub_unique_upload.py `
  --csv "outputs\<run-id>\metadata\preupload.csv" `
  --images-dir "outputs\<run-id>\assets\processed" `
  --out-dir "outputs\<run-id>\assets\processed-designhub-unique-<YYYYMMDD-HHmm>" `
  --out-csv "outputs\<run-id>\metadata\designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" `
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

JPG 배경도 generic name은 피한다. topic slug와 timestamp/index를 사용하고, CSV `fileName`에는 확장자를 넣지 않는다.

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
- 체크보드, 흰색, 어두운 배경 preview가 통과한다.
- 업로드용 PNG 요소를 요청받았다면 Photopea processed 출력이 존재한다.
- PNG 요소 크기/DPI가 로컬 프로젝트 규칙과 맞는다.
- CSV basename과 processed/upload PNG basename이 일치한다.
- 키워드가 20~25개의 고유한 구매자 검색어다.

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
- 산출물 종류: `background-jpg`, `png-element`, `photo-jpg`
- source 이미지 폴더
- 최종 이미지 폴더
- metadata CSV 경로
- review/contact sheet 경로
- batch를 생성했다면 prompt log 경로
- 키워드 개수와 제거한 제작 용어
- 검증 요약
- Photopea 사용 여부 또는 의도적으로 건너뛴 이유
- 남은 업로드 리스크

사용자가 명시적으로 승인하지 않았다면 외부 업로드/제출을 하지 않았다고 분명히 말한다.

## 테스트 프롬프트

라우팅 sanity check에는 `evals/evals.json`을 사용한다. 전체 eval/viewer 루프는 선택 사항이며, 사용자가 더 깊은 스킬 benchmark를 원할 때 실행한다.
