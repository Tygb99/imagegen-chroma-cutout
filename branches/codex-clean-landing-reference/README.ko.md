# imagen-design-hub

[English README](README.md)

[![GitHub stars](https://img.shields.io/github/stars/Tygb99/imagen-design-hub?style=social)](https://github.com/Tygb99/imagen-design-hub/stargazers)

`image_gen`으로 MiriCanvas / DesignHub용 비트맵 산출물을 만드는 Codex 스킬입니다.

두 가지 주요 경로를 다룹니다.

1. **JPG 배경 요소**: built-in `image_gen`으로 자연스러운 배경 이미지를 만들고, source PNG를 보존한 뒤, 최종 JPG와 `contentType=Background` CSV를 만듭니다.
2. **투명 PNG 요소**: 단색 크로마키 배경으로 생성하고, 번들 헬퍼로 배경을 제거한 뒤, 필요하면 Photopea로 업로드용 PNG를 마무리하고 메타데이터를 만듭니다.

이 스킬은 source, final, review sheet, prompt log, CSV를 분리해서 DesignHub 업로드 전에 배치를 검수할 수 있게 합니다.

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

## 저장소 구조

- `SKILL.md`: 라우팅과 검증 지침.
- `SKILL.ko.md`: 한국어 스킬 지침.
- `src/imagegen_chroma_cutout/`: 호환성을 위해 기존 패키지명을 유지한 재사용 Python 구현.
- `scripts/remove_chroma_key.py`: 크로마키 배경을 alpha로 바꾸는 헬퍼.
- `scripts/write_photopea_runner.py`: 번들 Photopea runner 생성기.
- `scripts/prepare_designhub_unique_upload.py`: PNG 요소 배치용 업로드 안전 basename/CSV 헬퍼.
- `assets/photopea_runner.html`: 번들 Photopea runner용 브라우저 템플릿.
- `evals/evals.json`: 라우팅 테스트 프롬프트.

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

PNG 요소는 크로마키 헬퍼와 Photopea 경로를 사용합니다.

```bash
python scripts/remove_chroma_key.py \
  --input source.png \
  --out final-alpha.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

Windows PowerShell:

```powershell
py -3 ./scripts/remove_chroma_key.py `
  --input "./source.png" `
  --out "./final-alpha.png" `
  --auto-key border `
  --soft-matte `
  --transparent-threshold 12 `
  --opaque-threshold 220 `
  --despill
```

DesignHub/MiriCanvas 업로드용 PNG라면 Photopea runner를 만들거나 프로젝트 runner를 사용합니다.

```bash
python scripts/write_photopea_runner.py \
  --raw-dir outputs/<run-id>/assets/raw \
  --processed-dir outputs/<run-id>/assets/processed \
  --out outputs/<run-id>/photopea/runner.html
```

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
- `Photopea`, `API`, `imagegen`, `PNG`, `JPG`, `2D`, `350DPI`, run ID, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스` 같은 제작/파일/관리/채움말은 제거합니다.
- `elementName`은 짧고 사람이 읽는 제목으로 둡니다.

## 라이선스

MIT. 원문은 [LICENSE](LICENSE), 한국어 번역은 [LICENSE.ko.md](LICENSE.ko.md)를 참고하세요.
