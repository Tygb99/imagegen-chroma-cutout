---
name: png-element
description: MiriCanvas 또는 DesignHub PNG 요소 작업에 사용한다. imagegen source art, chroma-key 배경 제거, 투명 PNG 컷아웃, Photopea 마무리, 업로드 안전 PNG basename, PNG element CSV 행을 다룬다.
---

# Imagen Design Hub: PNG 요소

[English version](SKILL.md)

사용자가 `png요소`, 투명 PNG, cutout, sticker, element, 배경 제거, Photopea, 업로드용 alpha asset을 말할 때 이 경로를 사용한다.

공유 참고: 전체 DesignHub route map이 필요하면 `../../SKILL.ko.md`를 읽는다.

## 핵심 규칙

- source 생성에는 built-in `image_gen`을 사용한다.
- 완전히 평평한 단색 chroma-key 배경으로 생성한다.
- imagegen에 투명 배경이나 체크보드 배경을 요청하지 않는다.
- key color는 피사체와 겹치지 않는 색을 고른다. 피사체가 비슷한 보라색을 쓰지 않을 때만 `#8000ff`를 기본값으로 쓴다. 초록 피사체에는 magenta를 쓰고, 파란 피사체에는 blue를 피한다.
- imagegen 프롬프트에 key color를 피사체 내부에 쓰지 말라고 명시한다.
- 독립 PNG 요소를 여러 개 만들 때는 요소마다 source 이미지를 따로 생성한다. 여러 요소를 한 장에 몰아 만든 뒤 잘라 쓰지 않는다. 분리 후 확대하면 계단현상과 약한 anti-aliasing이 드러날 수 있다.
- source 파일은 `assets/source-imagegen/`에 보존한다.
- 먼저 `../../scripts/chroma_key.py`를 실행해 `assets/raw/`로 출력한다.
- DesignHub PNG 요소 작업에는 `.system/imagegen/remove_chroma_key.py`를 사용하지 않는다.
- 사용자가 비교나 fallback을 명시적으로 요청하지 않으면 `../../scripts/remove_chroma_key.py`를 사용하지 않는다.
- 업로드용 DesignHub PNG는 Photopea 또는 프로젝트 Photopea runner를 거쳐 `assets/processed/`로 마무리한다.
- review contact sheet는 검토용 산출물일 뿐이다. 최종 업로드 PNG를 contact sheet에서 잘라 만들지 않는다.

## Chroma-Key Helper

edge-connected cleanup으로 실행한다.

```bash
python ../../scripts/chroma_key.py \
  --input "<source.png>" \
  --output "<raw-alpha.png>" \
  --background "<KEY_COLOR>" \
  --tolerance 48 \
  --scope edge \
  --dpi 350
```

피사체 내부의 key color와 가까운 디테일이 사라지면 tolerance를 넓히지 말고 더 안전한 배경색으로 다시 생성한다.

넓은 global tolerance보다 edge-connected 제거를 우선한다. global tolerance는 선풍기, 오브젝트, 패턴 내부의 색이 key color와 가까울 때 피사체 디테일을 같이 지울 수 있다. 내부 디테일이 손상되면 enclosed removal을 낮추거나 더 안전한 key color로 다시 생성한 뒤 결과를 채택한다.

chroma-key 제거와 Photopea 마무리 후에는 체크보드, 흰색, 어두운 배경에서 edge를 확대 검수한다. outline이 아직 계단형이거나 jagged하면 원래 per-element source에서 finishing을 다시 하거나 요소별로 다시 생성한다. 로컬에서 확대한 crop을 upload-ready로 받아들이지 않는다.

## 산출물 계약

- 최종 업로드 후보는 alpha가 있는 PNG 파일이다.
- 프로젝트가 다르게 말하지 않으면 tight alpha bbox를 사용한다.
- 현재 MiriCanvas DesignHub 제출 흐름에서는 최종 PNG를 350 DPI, 한 변 최소 2500 px로 유지한다.
- CSV 행의 `contentType` 값은 `PNG element`다.
- 키워드는 20~25개의 고유한 구매자 검색어여야 한다.
- DesignHub 업로드 전에 reupload collision 가능성이 있으면 `../../scripts/prepare_designhub_unique_upload.py`로 업로드 안전 고유 basename을 준비한다.

## 검증

batch ready라고 말하기 전에 모두 확인한다.

- alpha channel이 존재한다.
- 투명 모서리가 통과한다.
- 체크보드, 흰색, 어두운 preview에서 visible key-color fringe가 없다.
- key color와 비슷하다는 이유로 피사체 내부 디테일이 지워지지 않았다.
- 확대 검수에서 edge가 계단형이 아니라 anti-aliased 상태다.
- 피사체가 잘리지 않았다.
- 각 최종 PNG는 자체 source asset 또는 full-resolution per-element source에서 왔고, cropped combined sheet에서 온 것이 아니다.
- 업로드용 PNG 요소를 요청받았다면 Photopea processed 출력이 존재한다.
- CSV basename이 최종 PNG basename과 일치한다.
- 사용자가 명시적으로 확인하지 않았다면 외부 DesignHub 업로드/제출은 수행하지 않았다.
