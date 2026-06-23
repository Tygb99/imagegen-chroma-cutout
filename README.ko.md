# imagegen-chroma-cutout

[English README](README.md)

`image_gen` 결과물을 투명 PNG/WebP 컷아웃으로 만드는 Codex 스킬입니다.

공개 GitHub 저장소에 올려도 재현 가능하도록 다음 흐름을 기준으로 정리했습니다.

1. built-in `image_gen` 도구로 단색 크로마키 배경 이미지를 생성합니다.
2. 생성 원본을 보존합니다.
3. 번들된 `scripts/remove_chroma_key.py` 헬퍼로 크로마키 배경을 제거합니다.
4. 업로드용 PNG 요소라면 번들 runner 또는 프로젝트별 Photopea runner로 crop, resize, DPI 마무리를 합니다.
5. 구매자 검색어 중심의 DesignHub 키워드와 메타데이터를 만듭니다.
6. DesignHub 업로드용이면 processed PNG를 업로드 안전 고유 basename으로 복사하고 매칭 CSV를 만듭니다.
7. alpha, 모서리 투명도, 배경 잔여물, 이미지 크기, DPI, 키워드 개수, CSV basename 매칭, preview 화면을 검증합니다.

## 의존성

크로마키 컷아웃 필수:

- `image_gen` 도구를 사용할 수 있는 Codex 또는 agent 런타임.
- Python 3.10 이상.
- Pillow.
- NumPy.

Python 의존성 설치:

```bash
python3 -m pip install -r requirements.txt
```

NumPy는 크로마키 헬퍼의 벡터화 픽셀 처리에 필요합니다. 2026-06-22 글래스모피즘 12개 배치 기준으로 NumPy CLI 경로가 기존 Pillow 루프 경로보다 약 8.2배 빨랐고, 보이는 key-color 잔여 검증도 통과했습니다.

DesignHub/MiriCanvas 업로드용 PNG 요소 필수:

- Chromium 계열 브라우저의 Photopea.
- 현재 프로젝트에 더 강한 Photopea runner가 없다면 번들된 `scripts/write_photopea_runner.py` runner 생성기.

선택:

- 프로젝트별 Photopea runner. 예: `node src/cli.mjs photopea-runner --run <run-id>`.
- 프로젝트별 검증 명령. 예: MiriCanvas/DesignHub 파이프라인의 `node src/cli.mjs validate --run <run-id>`.

## 저장소 구조

- `src/imagegen_chroma_cutout/`: 재사용 가능한 Python 구현.
- `assets/photopea_runner.html`: 번들 Photopea runner용 브라우저 템플릿.
- `scripts/`: 아래 명령에서 쓰는 얇은 CLI wrapper.

## 헬퍼 사용법

```bash
python3 scripts/remove_chroma_key.py \
  --input source.png \
  --out final-alpha.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

## Photopea Runner

DesignHub/MiriCanvas 업로드용 산출물은 raw alpha PNG에서 멈추면 안 됩니다. Photopea runner를 생성한 뒤 Chrome에서 열고, raw PNG 파일을 선택하고, processed 출력 폴더를 고른 다음 batch를 실행합니다.

```bash
python3 scripts/write_photopea_runner.py \
  --raw-dir outputs/<run-id>/assets/raw \
  --processed-dir outputs/<run-id>/assets/processed \
  --out outputs/<run-id>/photopea/runner.html
```

runner는 투명 영역 기준 trim, 목표 크기 범위로 resize, Photopea PNG export, 브라우저 내 PNG DPI metadata 패치를 수행합니다. 로컬 프로젝트에 `node src/cli.mjs photopea-runner --run <run-id>`처럼 더 강한 runner가 있으면 그 프로젝트 runner를 우선 사용합니다.

## DesignHub 파일명 중복 방지

DesignHub는 현재 CSV 내부에 중복이 없어도 계정에 이미 사용된 `fileName`과 충돌하면 메타데이터 등록을 거절할 수 있습니다. `job-001-01` 같은 범용 이름은 업로드용 메타데이터에 쓰지 않는 편이 안전합니다.

업로드 전용 PNG 폴더와 매칭 CSV를 만듭니다.

```bash
python3 scripts/prepare_designhub_unique_upload.py \
  --csv outputs/<run-id>/metadata/preupload.csv \
  --images-dir outputs/<run-id>/assets/processed \
  --out-dir outputs/<run-id>/assets/processed-designhub-unique-YYYYMMDD-HHmm \
  --out-csv outputs/<run-id>/metadata/designhub-preupload-unique-YYYYMMDD-HHmm.csv \
  --prefix short-topic-slug-YYYYMMDD-HHmm
```

복사된 PNG 폴더와 생성된 CSV를 한 쌍으로 업로드합니다. PNG basename과 CSV `fileName`이 1:1로 맞도록 만들어집니다.

## DesignHub 키워드 규칙

DesignHub 메타데이터 키워드는 제작 과정 설명이 아니라 구매자가 검색할 단어로 만듭니다.

- 쉼표로 구분한 키워드 20~25개를 사용합니다. 기본 목표는 25개입니다.
- 공백과 대소문자 차이를 정리한 뒤 중복을 제거합니다.
- 앞쪽 8~12개에는 핵심 소재, 재질, 스타일 키워드를 둡니다.
- 뒤쪽에는 사용 장면, 분위기, 계절, 관련 오브젝트로 확장합니다.
- `Photopea`, `API`, `후처리`, `프롬프트`, `imagegen`, `배경제거`, `PNG`, `2D`, `350DPI`, `투명배경`, run id, `DesignHub`, `MiriCanvas`, `CSV`, `Premium`, `클립아트`, `디자인소스` 같은 제작/파일/관리/채움말은 반드시 제거합니다.
- `elementName`도 짧고 사람이 읽는 제목으로 두고, 제작 용어를 넣지 않습니다.

좋은 방향의 예:

```text
글래스모피즘,비눗방울,물방울,크리스탈,홀로그램,하이라이트,광택,파스텔,여름,배너장식
```

한국어 workflow에서는 한국어 검색어를 기본으로 하고, 실제 검색어로 유용한 외래어만 함께 넣습니다.

## 라이선스

MIT. 원문은 [LICENSE](LICENSE), 한국어 번역은 [LICENSE.ko.md](LICENSE.ko.md)를 참고하세요.
