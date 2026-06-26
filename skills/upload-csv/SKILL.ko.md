---
name: upload-csv
description: MiriCanvas 또는 DesignHub 요소 파일이 업로드 준비된 뒤 Computer Use로 파일 업로드, DesignHub CSV 다운로드, uniqueId 보존, 행 병합, CSV 재업로드가 필요할 때 사용한다.
---

# Imagen Design Hub: 업로드 후 CSV

[English version](SKILL.md)

사용자가 `요소 업로드후 csv업로드`, `upload-csv`, DesignHub upload CSV, metadata upload, CSV merge, uniqueId preservation, post-upload DesignHub metadata를 말할 때 이 경로를 사용한다.

이 스킬은 파일 업로드 이후 metadata 단계용이다. DesignHub 최종 심사 제출을 조용히 진행하면 안 된다.

공유 참고: route별 `contentType` 값과 keyword 규칙이 필요하면 `../../SKILL.ko.md`를 읽는다.

## 필수 Computer Use

이 경로의 실제 DesignHub UI 작업은 모두 `computer-use`를 사용한다.

- Chrome/Finder 스타일 UI 작업에는 `computer-use`를 사용한다: DesignHub 열기, upload control 클릭, 파일 선택, DesignHub CSV 다운로드, 병합 CSV 업로드, 스크롤, 타이핑, UI 상태 확인.
- DesignHub upload/download 단계에 browser automation, direct HTTP call, hidden API, terminal-only shortcut을 사용하지 않는다.
- 로컬 CSV 병합, 행 검증, encoding 확인, 파일 검사는 일반 filesystem과 terminal 도구를 써도 된다.
- 파일 업로드와 CSV metadata 전송은 외부 서비스 상태를 바꾸므로, 특정 파일과 destination에 대한 사용자 확인이 아직 없다면 UI 작업 전에 명시 확인을 받는다.
- 사용자가 별도 외부 제출 단계로 명시하지 않으면 final review submission을 누르지 않는다.

## 필수 순서

1. 사용자가 외부 DesignHub 작업을 명시 확인했을 때만 `computer-use`로 준비된 image/vector/GIF 파일을 업로드한다.
2. 파일 업로드 후 DesignHub가 제공한 CSV를 `computer-use`로 다운로드한다.
3. 다운로드한 CSV를 `fileName`과 `uniqueId`의 source of truth로 취급한다.
4. 준비한 metadata를 다운로드한 행에 병합하되 `uniqueId`를 삭제, 불필요한 재정렬, 재생성하지 않는다.
5. CSV는 no-BOM으로 유지하고 모든 field를 quote한다.
6. 사용자가 해당 외부 작업을 명시 확인했을 때만 `computer-use`로 병합 CSV를 재업로드한다.
7. CSV 업로드 후 DesignHub 완료 메시지나 배너를 확인한다. 처리된 행 수를 기록하고, 파일 업로드, CSV 업로드, 최종 심사 제출을 구분한다.

파일 등록 후 로컬 preupload CSV를 바로 올리지 않는다. DesignHub는 파일 업로드 후에만 `uniqueId`를 부여하므로, 올바른 흐름은 항상 현재 DesignHub CSV를 다운로드하고, 그 전체 파일에 병합한 뒤, 병합한 전체 CSV를 업로드하는 것이다.

## Content Type 값

공식 CSV 값을 정확히 사용한다.

```text
Photo
Photo(Cut-out)
SVG element
PNG element
GIF
Background
```

`JPG background`라고 쓰지 않는다. `Background`를 사용한다.

## 메타데이터 규칙

- JPG background, SVG, GIF 행의 `fileName`은 보통 확장자 없이 쓴다.
- PNG element 흐름에서는 DesignHub 다운로드 CSV가 기대하는 형식에 맞추고, 최종 upload basename을 실제 파일과 맞춘다.
- `uniqueId`는 DesignHub에서 다운로드한 CSV 값을 보존한다.
- 사용자가 다르게 말하지 않으면 `tier`는 `Premium`이다.
- `keywords`는 20~25개의 고유한 구매자 검색어여야 한다.
- `Photopea`, `imagegen`, `PNG`, `JPG`, `SVG`, `GIF`, `CSV`, `Premium`, `DesignHub`, `MiriCanvas`, run ID, 날짜 같은 제작/관리 용어는 사용자가 명시적으로 요구하지 않는 한 제거한다.

## 검증

ready라고 보고하기 전에 확인한다.

- 행 수가 DesignHub에서 다운로드한 CSV와 일치한다.
- 다운로드한 CSV의 모든 `uniqueId` 값이 보존된다.
- 모든 최종 `fileName` 값이 업로드된 파일과 매칭된다.
- 병합 CSV는 새 batch 행만이 아니라 다운로드한 DesignHub CSV의 모든 행을 유지한다.
- `contentType` 값은 공식 목록 중 하나다.
- 각 행의 keyword 중복이 없다.
- 각 행의 keyword 개수가 20~25개다.
- CSV encoding은 UTF-8 without BOM이다.
- 로컬 프로젝트 계약이 quote-all CSV를 요구하면 모든 field가 quote되어 있다.
- 실제 DesignHub file upload, CSV download, CSV upload는 `computer-use`로 수행했다.
- DesignHub가 성공 처리 행 수를 표시했거나 오류 메시지를 그대로 캡처했다.
- 파일 업로드, CSV 업로드, 최종 심사 제출이 실제로 일어났는지 명확히 말한다.
