# imagen-design-hub

[English README](README.md)

[![GitHub stars](https://img.shields.io/github/stars/Tygb99/imagen-design-hub?style=social)](https://github.com/Tygb99/imagen-design-hub/stargazers)

`image_gen`, 로컬 source art, vector export, animation 파일로 MiriCanvas / DesignHub 산출물을 준비하는 Codex 스킬입니다.

네 가지 주요 경로를 다룹니다.

1. **JPG 배경 요소**: built-in `image_gen`으로 자연스러운 배경 이미지를 만들고, source PNG를 보존한 뒤, 최종 JPG와 `contentType=Background` CSV를 만듭니다.
2. **투명 PNG 요소**: 단색 크로마키 배경으로 생성하고, 번들 헬퍼로 배경을 제거한 뒤, 필요하면 Photopea로 업로드용 PNG를 마무리하고 메타데이터를 만듭니다.
3. **SVG 요소**: 단순 vector 일러스트를 SVG cleanup, 색상 수 검사, `contentType=SVG element` 경로로 보냅니다.
4. **GIF 요소**: 움직이는 일러스트 frame을 GIF encode/playback 검사와 `contentType=GIF` 경로로 보냅니다.

이 스킬은 source, final, review sheet, prompt log, CSV를 분리해서 DesignHub 업로드 전에 배치를 검수할 수 있게 합니다.

## 플러그인 스킬 분리

개인 플러그인은 다섯 개의 좁은 스킬 엔트리를 제공합니다.

- `png-element`: PNG 요소, 크로마키 제거, Photopea 마무리, `contentType=PNG element`.
- `jpg-background`: JPG 배경과 `contentType=Background`.
- `svg-beta`: SVG 요소 후보. 시각 검증 전까지는 beta 경로로 둡니다.
- `gif-beta`: GIF 요소 후보. playback과 투명도 검증 전까지는 beta 경로로 둡니다.
- `upload-csv`: Computer Use로 DesignHub 파일 업로드, CSV 다운로드, 병합 CSV 업로드를 진행하고 `uniqueId`를 보존하는 단계.

## Codex 플러그인 설치

공개 플러그인은 다음 명령으로 설치합니다.

```bash
npx github:Tygb99/imagen-design-hub
```

비대화형 설치:

```bash
npx --yes github:Tygb99/imagen-design-hub
```

npx 없이 수동 설치:

```bash
git clone https://github.com/Tygb99/imagen-design-hub.git ~/plugins/imagen-design-hub
node ~/plugins/imagen-design-hub/scripts/register_marketplace.mjs
```

설치 스크립트는 `~/plugins/imagen-design-hub`를 `~/.agents/plugins/marketplace.json`에 등록합니다.

## 자동 업데이트

플러그인은 Codex 새 세션 시작 시 업데이트를 확인하는 `SessionStart` hook을 포함합니다.

- 자동 업데이트는 git checkout으로 설치한 경우에만 동작합니다.
- hook은 `git fetch`와 `git pull --ff-only`를 사용합니다.
- 로컬 변경사항이 있으면 덮어쓰지 않고 업데이트를 건너뜁니다.
- 단순 복사 설치본은 건드리지 않습니다. 업데이트를 받으려면 git 기반 설치 스크립트로 다시 설치하세요.

## 공개 페이지 Preview

- Main page: <https://tygb99.github.io/imagen-design-hub/>
- 브랜치 preview 목록: <https://tygb99.github.io/imagen-design-hub/branches/>
- 브랜치 URL 패턴: `https://tygb99.github.io/imagen-design-hub/branches/<branch-slug>/`

브랜치 slug는 브랜치 이름을 소문자로 바꾸고 `/` 같은 구분자를 `-`로 바꾼 값입니다. 예를 들어 `codex/clean-landing-reference`는 `/branches/codex-clean-landing-reference/`에 공개됩니다.

## 의존성

이미지 생성 필수:

- built-in `image_gen` 도구를 사용할 수 있는 Codex 또는 agent 런타임.

로컬 처리 필수:

- Python 3.10 이상.
- Pillow.
- 크로마키 헬퍼용 NumPy.

필요할 때만 Python 의존성을 설치합니다.

```bash
python -m pip install -r requirements.txt
```

Windows PowerShell에서는 스킬 디렉터리에서 다음처럼 실행합니다.

```powershell
py -3 -m pip install -r requirements.txt
```

업로드용 PNG 요소 필수:

- Chromium 계열 브라우저의 Photopea.
- 현재 프로젝트에 더 강한 Photopea runner가 없다면 번들된 `scripts/write_photopea_runner.py` runner 생성기.

SVG/GIF 요소 작업 필수:

- SVG 산출물용 실제 vector editor/export 경로.
- animation playback, 투명도, 크기, 용량을 확인할 GIF encoder/player.

## 저장소 구조

- `SKILL.md`: 라우팅과 검증 지침.
- `SKILL.ko.md`: 한국어 스킬 지침.
- `src/imagegen_chroma_cutout/`: 호환성을 위해 기존 패키지명을 유지한 재사용 Python 구현.
- `scripts/chroma_key.py`: 프로젝트 helper에서 복사한 primary edge-connected 크로마키 alpha 헬퍼.
- `scripts/remove_chroma_key.py`: legacy soft-matte 크로마키 헬퍼. 명시적인 비교나 fallback 때만 사용.
- `scripts/write_photopea_runner.py`: 번들 Photopea runner 생성기.
- `scripts/prepare_designhub_unique_upload.py`: PNG 요소 배치용 업로드 안전 basename/CSV 헬퍼.
- `assets/photopea_runner.html`: 번들 Photopea runner용 브라우저 템플릿.
- `evals/evals.json`: 라우팅 테스트 프롬프트.
- `references/designhub-element-guide-map.ko.md`: 공식 DesignHub 요소 가이드 링크 맵과 타입 규칙 요약.

## DesignHub JPG 배경 경로

수영장 물빛, 종이 질감, 빛반사, 자연스러운 패턴처럼 generated bitmap 품질이 중요한 배경은 imagegen을 우선합니다.

권장 로컬 구조:

```text
outputs/<run-id>/assets/source-imagegen-batch/
outputs/<run-id>/assets/background-jpg-imagegen/
outputs/<run-id>/metadata/
outputs/<run-id>/review/
outputs/<run-id>/logs/
```

배경 JPG CSV 규칙:

- `fileName`: basename만 사용하고 `.jpg`는 제거
- `uniqueId`: DesignHub가 준 값이 아니면 빈칸
- `tier`: `Premium`
- `contentType`: `Background`

## 투명 PNG 요소 경로

PNG 요소는 `scripts/chroma_key.py`와 Photopea 경로를 사용합니다. DesignHub PNG 요소 작업에서는 built-in `.system/imagegen`의 `remove_chroma_key.py` helper를 사용하지 않습니다.

```bash
python scripts/chroma_key.py \
  --input source.png \
  --output final-alpha.png \
  --background "#8000ff" \
  --tolerance 48 \
  --scope edge \
  --dpi 350
```

Windows PowerShell:

```powershell
py -3 ./scripts/chroma_key.py `
  --input "./source.png" `
  --output "./final-alpha.png" `
  --background "#8000ff" `
  --tolerance 48 `
  --scope edge `
  --dpi 350
```

DesignHub/MiriCanvas 업로드용 PNG라면 Photopea runner를 만들거나 프로젝트 runner를 사용합니다.

```bash
python scripts/write_photopea_runner.py \
  --raw-dir outputs/<run-id>/assets/raw \
  --processed-dir outputs/<run-id>/assets/processed \
  --out outputs/<run-id>/photopea/runner.html
```

## SVG와 GIF 요소 경로

SVG는 명확한 피사체, 완전히 제거된 배경, 5개 이하 색상을 가진 단순하고 색상 변경 가능한 vector 일러스트에 사용합니다. raster 이미지만 embed한 SVG는 제출하지 않습니다.

GIF는 명확한 피사체와 제거된 배경을 가진 움직이는 일러스트/아트 요소에 사용합니다. 정지 이미지를 GIF로 저장한 것만으로는 부족하며, 촬영 footage는 권한이 필요한 MP4 동영상 경로입니다.

CSV 규칙:

- SVG: `contentType=SVG element`, 확장자 없는 `fileName`.
- GIF: `contentType=GIF`, 확장자 없는 `fileName`.

공식 요소 가이드 페이지 맵, 파일 규격, 조합 요소 경계는 `references/designhub-element-guide-map.ko.md`를 참고합니다.

Windows PowerShell:

```powershell
py -3 ./scripts/write_photopea_runner.py `
  --raw-dir "outputs/<run-id>/assets/raw" `
  --processed-dir "outputs/<run-id>/assets/processed" `
  --out "outputs/<run-id>/photopea/runner.html"
```

## DesignHub 키워드 규칙

- 구매자 검색어 중심의 키워드 20~25개를 사용합니다.
- 중복을 제거합니다.
- `Photopea`, `API`, `imagegen`, `PNG`, `JPG`, `SVG`, `GIF`, `MP4`, `2D`, `350DPI`, run ID, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스` 같은 제작/파일/관리/채움말은 제거합니다.
- `elementName`은 짧고 사람이 읽는 제목으로 둡니다.

## 라이선스

MIT. 원문은 [LICENSE](LICENSE), 한국어 번역은 [LICENSE.ko.md](LICENSE.ko.md)를 참고하세요.
