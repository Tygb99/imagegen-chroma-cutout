---
name: imagegen-chroma-cutout
description: Use this skill whenever the user wants AI-generated transparent PNG cutouts, DesignHub or MiriCanvas PNG elements, "imagegen으로 만들고 배경제거", chroma-key background removal, Photopea crop/DPI finishing, DesignHub metadata keywords, DesignHub CSV filename de-duplication, or batch-style raster element assets that should end as validated alpha PNG/WebP files. Generate with the built-in image_gen tool on a flat removable chroma-key background, preserve the source image, run the bundled scripts/remove_chroma_key.py helper locally, route the alpha result through Photopea processing when preparing uploadable PNG elements, make buyer-facing keywords plus upload-safe unique file names and matching CSV rows, validate alpha/corners/fringes/size/DPI/metadata, and save final assets into the workspace. Use it even if the user only says "투명 PNG", "배경 제거", "헬퍼로 제거", "포토피아", "요소 만들기", "키워드", "파일명 중복", or "DesignHub 업로드용 이미지".
---

# Imagegen Chroma Cutout

이 스킬은 `imagegen`으로 비트맵 이미지를 만들고, 번들 헬퍼로 단색 배경을 제거한 뒤, 필요하면 Photopea 단계로 crop/resize/DPI 처리를 거쳐 업로드 가능한 투명 PNG/WebP 산출물까지 만드는 절차를 고정한다. 목적은 모델 생성과 후처리를 섞어 말하다가 원본을 잃거나, `$CODEX_HOME` 아래 생성물을 프로젝트에 복사하지 않거나, 배경 제거 및 Photopea 처리 실패를 놓치는 일을 줄이는 것이다.

## Dependencies

- Required: built-in `image_gen` tool, Python 3.10+, Pillow, and NumPy for `scripts/remove_chroma_key.py`.
- `scripts/prepare_designhub_unique_upload.py` uses only the Python standard library.
- Reusable Python code lives in `src/imagegen_chroma_cutout/`; `scripts/` files are thin CLI wrappers kept for copy-paste friendly commands.
- Install helper dependency in the active environment if needed:
  ```bash
  python3 -m pip install -r requirements.txt
  ```
- Optional for upload-ready PNG elements: Photopea or a project-specific Photopea runner.
- Optional for MiriCanvas/DesignHub repos: local project commands such as `node src/cli.mjs photopea-runner --run <run>` and `node src/cli.mjs validate --run <run>`.
- Do not assume any external helper exists. Prefer this skill's bundled `scripts/remove_chroma_key.py`.

## 기본 원칙

- 기본 경로는 built-in `image_gen` 도구다. `OPENAI_API_KEY`가 필요 없는 경로를 먼저 사용한다.
- 투명 배경을 바로 요구받아도 먼저 flat chroma-key 배경으로 생성한 뒤 로컬 헬퍼로 제거한다.
- true/native transparency가 필요할 정도로 복잡한 대상이면 바로 CLI로 넘어가지 말고 사용자에게 확인한다.
- 생성 원본과 배경 제거 결과를 둘 다 보존한다. 원본은 `assets/source-imagegen/` 또는 `tmp/imagegen/source/`, 최종 alpha 결과는 `assets/raw/`, `assets/processed/`, 또는 사용자가 지정한 위치에 둔다.
- DesignHub/MiriCanvas용 PNG 요소는 helper 결과를 `assets/raw/`에 둔 뒤 Photopea 처리 결과를 `assets/processed/`에 저장하는 흐름을 기본으로 삼는다.
- DesignHub/MiriCanvas용 metadata 키워드는 20~25개, 중복 없음, 구매자 검색어 중심으로 만든다.
- DesignHub에 올릴 최종 PNG와 CSV는 업로드 직전에 전역 충돌 가능성이 낮은 고유 basename으로 별도 복사본을 만든다. `job-001-01`처럼 배치마다 반복될 수 있는 이름은 DesignHub 등록용 `fileName`으로 쓰지 않는다.
- 프로젝트에서 쓰일 이미지는 `$CODEX_HOME/generated_images/...`에만 남기지 않는다. 반드시 workspace로 복사하거나 이동한다.
- 기존 파일을 덮어쓰지 않는다. 교체 요청이 없으면 `-v2`, timestamp, job id 같은 새 이름을 쓴다.
- 외부 업로드, 제출, 전송은 사용자가 명시적으로 확인하기 전에는 하지 않는다.

## Workflow

1. 사용자의 의도를 분류한다.
   - 새 이미지 생성이면 `generate`.
   - 기존 이미지 일부를 바꾸면 `edit`.
   - 투명 PNG, cutout, PNG element, DesignHub/MiriCanvas 요소, 배경 제거가 포함되면 이 스킬을 계속 적용한다.
2. 산출 위치를 정한다.
   - 현재 repo 작업이면 해당 run 폴더나 `tmp/imagegen/` 아래에 둔다.
   - MiriCanvas/DesignHub run이면 가능하면 다음 구조를 따른다:
     - `outputs/<run-id>/assets/source-imagegen/`
     - `outputs/<run-id>/assets/raw/`
     - `outputs/<run-id>/assets/processed/`
     - `outputs/<run-id>/metadata/`
     - `outputs/<run-id>/review/`
3. chroma-key 색을 고른다.
   - 기본값은 `#00ff00`.
   - 피사체에 초록이 있으면 `#ff00ff`.
   - 피사체가 보라/자주 계열이면 `#00ff00` 또는 밝은 cyan 계열을 쓴다.
   - 피사체가 파란색이면 `#0000ff`를 피한다.
   - MiriCanvas 기존 파이프라인에서 `#8000ff`를 쓰는 run이면 피사체와 충돌하지 않을 때만 그대로 쓴다.
4. built-in `image_gen` 프롬프트를 chroma-key 친화적으로 만든다.
5. 생성 결과를 확인하고 선택한 source를 workspace로 복사한다.
6. 로컬 헬퍼를 실행한다.
7. helper 결과의 alpha와 배경 잔여물을 먼저 검증한다.
8. DesignHub/MiriCanvas 업로드용이면 Photopea 단계로 `assets/raw/` 입력을 `assets/processed/` 출력으로 만든다.
9. metadata CSV를 만들거나 갱신할 때 키워드를 20~25개로 정리하고, production/process terms를 제거한다.
10. DesignHub/MiriCanvas 업로드용이면 `assets/processed/`를 직접 업로드 후보로 쓰기 전에 고유 이름의 업로드용 복사본과 매칭 CSV를 만든다.
11. processed/upload PNG의 alpha, 크기, DPI, bbox, preview, CSV basename 매칭, 키워드 개수를 검증한다.
12. 필요하면 한 번만 보수적으로 재시도한다.
13. 최종 파일 경로, source 보존 경로, raw alpha 경로, processed 경로, 업로드용 unique 폴더/CSV, 키워드 검증 결과, 프롬프트, 헬퍼 옵션, Photopea 처리 여부, 검증 결과를 보고한다.

## Prompt Template

사용자 프롬프트를 유지하되, 투명 PNG 목적일 때는 다음 제약을 넣어라.

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

## Helper Command

항상 이 스킬에 번들된 헬퍼를 우선 사용한다. 공개 GitHub 배포본에서도 동작하도록 `${SKILL_DIR:-.}/scripts/remove_chroma_key.py` 형태로 호출한다. 현재 작업 환경에 `SKILL_DIR`가 없으면 스킬 폴더 절대 경로나 repo checkout 경로를 직접 넣는다.

```bash
python3 "${SKILL_DIR:-.}/scripts/remove_chroma_key.py" \
  --input "<source.png>" \
  --out "<final-alpha.png>" \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

잔여 key-color fringe가 얇게 남으면 한 번만 더 시도한다.

```bash
python3 "${SKILL_DIR:-.}/scripts/remove_chroma_key.py" \
  --input "<source.png>" \
  --out "<final-alpha-v2.png>" \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --edge-contract 1 \
  --despill
```

`--edge-feather 0.25`는 계단 현상이 보일 때만 쓰고, 유리/물/광택/반투명 질감에서는 과도하게 쓰지 않는다. 그런 소재는 가장자리 자체가 피사체일 수 있다.

## Photopea Processing

Photopea는 배경 제거 헬퍼를 대체하는 단계가 아니다. 헬퍼가 만든 alpha PNG를 업로드 가능한 크기/DPI/tight crop 산출물로 정리하는 단계다.

DesignHub/MiriCanvas run에서는 다음 순서를 따른다.

1. built-in `image_gen` 결과를 `assets/source-imagegen/`에 보존한다.
2. `remove_chroma_key.py` 결과를 `assets/raw/<job-id>.png`에 저장한다.
3. Photopea runner를 만든다.
   ```bash
   node src/cli.mjs photopea-runner --run outputs/<run-id>
   ```
4. 생성된 `photopea/runner.html` 또는 runner 안내를 Chrome 계열 브라우저에서 열고, `assets/raw/*.png`를 입력으로 선택한다.
5. 출력은 가능하면 `assets/processed/`에 같은 basename으로 저장한다.
6. Photopea 단계에서는 resize와 DPI 처리를 먼저 하고, 최종 trim/crop 액션을 마지막에 실행한다.
7. 이 repo의 기본 DesignHub 기준은 350 DPI, 가로/세로 2500px 이상, 9000px 이하, tight alpha bbox다. 사용자가 바꾸지 않으면 300 DPI로 낮추지 않는다.
8. Photopea export가 alpha를 잃거나 흰 matte를 만들면 성공으로 처리하지 않는다. 원본 source와 raw alpha를 기준으로 재시도하고 원인을 기록한다.
9. Photopea가 브라우저 저장 제한 때문에 다운로드 폴더로 저장하면, 사용자가 확인한 파일만 `assets/processed/`로 옮긴 뒤 검증한다.

Photopea가 없는 repo나 일반 작업에서는 이 단계를 생략할 수 있다. 하지만 사용자가 `포토피아`, `Photopea`, `DesignHub`, `MiriCanvas`, `350 DPI`, `processed`, `업로드용`을 언급하면 Photopea 단계를 포함한다.

## Keyword Generation Rules

DesignHub/MiriCanvas metadata를 만들 때 키워드는 이미지 생성 과정 설명이 아니라 구매자가 검색할 말이어야 한다.

기본 규칙:

- 키워드는 20개 이상 25개 이하로 만든다. 기본 목표는 25개다.
- 중복을 제거한다. 띄어쓰기/대소문자 차이만 있는 중복도 하나로 본다.
- 앞쪽 8~12개는 핵심 소재, 질감, 대상명을 둔다.
- 뒤쪽은 사용 장면, 분위기, 계절, 스타일, 관련 오브젝트로 확장한다.
- 한국어 검색어를 기본으로 하되, 실제로 통용되는 외래어는 함께 쓴다. 예: `글래스모피즘`, `오로라`, `크리스탈`.
- 너무 넓은 일반어만 채우지 않는다. `일러스트`, `장식`, `아이콘`, `요소` 같은 단어는 부족한 수를 메울 때만 뒤쪽에 둔다.

우선순위:

1. 사용자나 챌린지 원문에서 나온 공식 주제어
2. 피사체의 구체적인 명사
3. 시각적 질감/재질/색감
4. 구매자가 사용할 장면과 카테고리
5. 계절/이벤트/분위기

반드시 제거할 말:

- 제작 과정: `Photopea`, `API`, `후처리`, `프롬프트`, `imagegen`, `배경제거`
- 파일/기술 형식: `PNG`, `2D`, `350DPI`, `투명배경`
- 날짜/관리값: `2026년`, `7월`, `job-001`, run id
- 심사/업로드 내부어: `DesignHub`, `MiriCanvas`, `CSV`, `Premium`
- 과도하게 일반적인 채움말: `클립아트`, `디자인소스`

위 항목은 우선순위 뒤로 보내지 말고 최종 metadata keyword와 `elementName`에서 반드시 제거한다.

예시:

```text
글래스모피즘,유리질감,비눗방울,물방울,유리구슬,유리버튼,오로라,빛반사,하이라이트,광택,블러,홀로그램,크리스탈,젤리,아크릴,반짝임,그라데이션,파스텔,여름,바다,모바일꾸미기,배너장식,유리장식,물방울스티커,감성꾸미기
```

검증:

- CSV `keywords` 필드를 쉼표로 나눴을 때 20~25개인지 확인한다.
- 중복 제거 후에도 20개 미만이면 실패로 보고 다시 보강한다.
- `elementName`에는 production terms를 넣지 않고 사람이 읽는 짧은 제목만 둔다.
- 같은 배치에서 모든 asset이 같은 주제라면 같은 키워드 세트를 써도 되지만, asset별 소재가 다르면 앞쪽 5~8개는 asset별로 조정한다.

## DesignHub Unique Upload Names

DesignHub는 CSV 안에서 중복이 없어도 과거 업로드/등록 시도에 남아 있는 파일명과 충돌할 수 있다. 그래서 업로드 직전에는 실제 업로드할 PNG basename과 CSV `fileName`을 새 배치 고유 이름으로 맞춘 별도 폴더를 만든다.

권장 basename 패턴:

```text
<short-topic-slug>-<YYYYMMDD>-<HHmm>-<NN>
```

예:

```text
glassmorphism-bubble-20260622-2048-01
glassmorphism-bubble-20260622-2048-02
```

번들 helper를 사용할 수 있으면 다음처럼 실행한다.

```bash
python3 "${SKILL_DIR:-.}/scripts/prepare_designhub_unique_upload.py" \
  --csv "outputs/<run-id>/metadata/preupload.csv" \
  --images-dir "outputs/<run-id>/assets/processed" \
  --out-dir "outputs/<run-id>/assets/processed-designhub-unique-<YYYYMMDD-HHmm>" \
  --out-csv "outputs/<run-id>/metadata/designhub-preupload-unique-<YYYYMMDD-HHmm>.csv" \
  --prefix "<short-topic-slug>-<YYYYMMDD>-<HHmm>"
```

규칙:

- 원본 `assets/processed/`는 보존하고, 업로드용 고유 이름 폴더를 새로 만든다.
- CSV `fileName`에는 확장자를 넣지 않고, 업로드할 PNG basename과 정확히 같게 쓴다.
- `fileName`은 CSV 내부 중복만 보는 것이 아니라 DesignHub 계정에 이미 남아 있을 법한 범용명도 피한다.
- DesignHub가 "파일명이 중복되어 실패"를 반환하면 기존 파일을 덮어쓰지 말고 더 구체적인 prefix 또는 새 timestamp로 unique 폴더/CSV를 다시 만든다.
- CSV 등록 전에 `fileName` 중복, 누락 PNG, extra PNG를 확인한다.

## Validation

검증은 숫자와 눈검수를 같이 한다.

- 파일이 PNG/WebP이고 alpha 채널이 있는지 확인한다.
- 네 모서리가 투명인지 확인한다.
- 피사체 alpha bbox가 잘리지 않았는지 확인한다.
- key-color 잔여물이 배경인지, 피사체 내부 색/반투명 효과인지 구분한다.
- checkerboard, white, dark 배경에서 최소 3-way preview를 확인한다.
- Photopea를 거친 경우 processed PNG가 존재하고 raw alpha와 같은 basename을 유지하는지 확인한다.
- DesignHub/MiriCanvas용이면 2500px 이상, 350 DPI, tight bbox 같은 해당 프로젝트 기준도 함께 확인한다.
- metadata/preupload CSV가 있는 workflow에서는 업로드할 PNG basename과 CSV `fileName`이 1:1로 맞는지 확인한다.
- metadata CSV가 있는 workflow에서는 각 행의 `keywords`가 20~25개이고 중복 및 production terms가 없는지 확인한다.
- DesignHub용 최종 보고에는 원본 processed 폴더와 실제 업로드용 unique 폴더/CSV를 구분해서 적는다.

간단한 CLI 확인 예:

```bash
sips -g hasAlpha -g pixelWidth -g pixelHeight "<final-alpha.png>"
```

프로젝트에 `node src/cli.mjs validate --run <run>` 같은 검증 명령이 있으면 그 명령을 우선 사용한다.

DesignHub/MiriCanvas run 검증 예:

```bash
node src/cli.mjs validate --run outputs/<run-id>
```

## Complex Transparency Boundary

다음 대상은 chroma-key removal이 실패하거나 피사체를 훼손할 수 있다.

- 머리카락, 털, 깃털
- 연기, 안개, 물보라
- 유리, 액체, 투명/반투명 소재
- 강한 반사, soft shadow, realistic product grounding
- 피사체 색이 모든 실용적인 key color와 충돌하는 경우

이 경우에도 먼저 단순 chroma-key로 가능한지 판단한다. 어렵거나 실패하면 사용자에게 이렇게 묻는다.

```text
이 이미지는 true native transparency가 더 안전할 가능성이 큽니다. 기본 경로는 built-in image_gen + chroma-key 제거지만, native transparency는 CLI fallback의 gpt-image-1.5가 필요하고 OPENAI_API_KEY가 필요합니다. 이 fallback으로 진행할까요?
```

확인 없이 CLI fallback이나 `gpt-image-1.5`로 전환하지 않는다.

## MiriCanvas / DesignHub Notes

- `assets/source-imagegen/` 원본은 보존한다.
- helper alpha PNG는 `assets/raw/`에 두고, Photopea 완료본은 `assets/processed/`에 둔다.
- 배경 제거가 피사체 내부 색을 지우면 실패로 본다.
- 체크보드 배경을 픽셀로 생성하지 않는다. 체크보드는 검수용 preview일 뿐이다.
- 최종 검수는 checkerboard, white, dark 배경에서 한다.
- Photopea/Photoshop action을 사용할 때는 resize와 DPI 처리를 먼저 하고 trim/crop을 마지막에 한다.
- 업로드 후보와 CSV 이름이 같은 배치를 가리키는지 확인한다.
- 키워드는 20~25개를 유지하고, 검색자가 쓸 소재/질감/상황어 중심으로 구성한다.
- `Photopea`, `API`, `PNG`, `2D`, run id, 날짜 같은 제작/관리 용어는 metadata 키워드와 elementName에서 제거한다.
- DesignHub 등록용 파일명은 `job-*`, `image-*`, `output-*`처럼 재사용될 수 있는 범용명을 피하고 주제 slug, 날짜, 시간, 2자리 인덱스를 포함한다.
- 파일명 중복 오류가 나면 이미지 재생성 문제가 아니라 업로드용 basename 충돌로 먼저 판단하고, 새 unique 폴더/CSV를 만들어 재등록 후보로 제공한다.
- 제출, 업로드, 카카오톡 전송은 사용자 확인 없이 하지 않는다.

## Final Report

완료 보고에는 짧게 다음을 포함한다.

- built-in `image_gen`을 사용했는지, CLI fallback을 사용했는지
- source image path
- raw alpha image path
- Photopea processed image path, 또는 Photopea를 생략한 이유
- DesignHub/MiriCanvas용이면 실제 업로드할 unique PNG folder와 matching CSV path
- DesignHub/MiriCanvas용이면 keyword count, duplicate check, removed production terms
- key color와 helper options
- validation 결과
- 미해결 리스크가 있으면 한 줄로 설명

## Test Prompts

스킬을 점검할 때는 `evals/evals.json`의 프롬프트를 사용한다. 실제 image generation은 비용과 시간이 드는 작업이므로, 사용자가 원할 때만 full eval/viewer 루프를 돌린다.
