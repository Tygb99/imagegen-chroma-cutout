# Imagen Design Hub 디자인 시스템

## 1. 분위기와 정체성

Imagen Design Hub는 시각 asset을 다루는 차분한 제작 벤치처럼 느껴져야 한다. 정확하고, 물빛이 있으며, 운영 도구답게 또렷하다. 핵심 시그니처는 water-print tooling이다. 부드러운 수면 caustic 이미지 위에 메타데이터, 포맷 검증, 업로드 준비 상태가 정돈된 레일처럼 올라온다.

## 2. 색상

### 팔레트

| 역할 | 토큰 | Light | Dark | 용도 |
|------|-------|-------|------|------|
| Surface/primary | --surface-primary | #F6FBFA | #101817 | 페이지 배경 |
| Surface/secondary | --surface-secondary | #E9F4F2 | #172321 | 교차 섹션 |
| Surface/elevated | --surface-elevated | #FFFFFF | #1D2B28 | 패널, 노트 |
| Surface/ink | --surface-ink | #172321 | #F6FBFA | 어두운 히어로 워시 |
| Text/primary | --text-primary | #172321 | #F6FBFA | 제목, 본문 |
| Text/secondary | --text-secondary | #50635F | #BACBC7 | 보조 문구 |
| Text/tertiary | --text-tertiary | #72827E | #83948F | 희미한 라벨 |
| Border/default | --border-default | #C9DAD6 | #31443F | 구분선, 외곽선 |
| Border/subtle | --border-subtle | #DDEBE8 | #263631 | 부드러운 분리 |
| Accent/primary | --accent-primary | #087E8B | #38B7C4 | 주요 액션, 링크 |
| Accent/secondary | --accent-secondary | #E56B4F | #F28A6C | 대비, 주의 |
| Accent/quiet | --accent-quiet | #B7E3D8 | #245D57 | 부드러운 채움 |
| Status/success | --status-success | #1D8A5F | #62C98E | 준비 완료 |
| Status/warning | --status-warning | #C98422 | #E8B75A | 주의 |
| Status/error | --status-error | #C94D4D | #EA7A7A | 오류 |
| Status/info | --status-info | #087E8B | #38B7C4 | 정보 |

### 규칙

- 표면에는 물빛 계열을 쓰고, 액션에는 teal accent를 사용한다.
- coral accent는 대비가 필요한 순간에만 사용하고 섹션 전체를 지배하지 않는다.
- format/status chip은 의미를 가진다. 배경과 SVG는 teal, 준비된 PNG는 green, GIF motion이나 거절 위험은 coral이다.

## 3. 타이포그래피

### 스케일

| 레벨 | 크기 | 굵기 | 행간 | 자간 | 용도 |
|------|------|------|------|------|------|
| Display | clamp(44px, 8vw, 88px) | 760 | 0.95 | 0 | 히어로 제목 |
| H1 | clamp(34px, 5vw, 56px) | 740 | 1.05 | 0 | 섹션 리드 |
| H2 | 30px | 700 | 1.2 | 0 | 섹션 제목 |
| H3 | 21px | 700 | 1.3 | 0 | 패널 제목 |
| Body/lg | 19px | 450 | 1.6 | 0 | 리드 문단 |
| Body | 16px | 450 | 1.6 | 0 | 기본 본문 |
| Body/sm | 14px | 500 | 1.45 | 0 | 보조 정보 |
| Caption | 12px | 650 | 1.35 | 0.04em | 메타데이터 라벨 |
| Overline | 11px | 760 | 1.3 | 0.08em | 대문자 라벨 |

### 폰트 스택

- Primary: Aptos, Segoe UI, ui-sans-serif, system-ui, sans-serif
- Mono: Cascadia Code, SFMono-Regular, Consolas, Liberation Mono, monospace

### 규칙

- 제품 문구에는 primary stack, 파일 경로와 CSV 헤더와 치수에는 mono stack을 사용한다.
- 음수 자간은 사용하지 않는다.

## 4. 간격과 레이아웃

### 기준 단위

모든 간격은 4px 기준에서 파생한다.

| 토큰 | 값 | 용도 |
|------|----|------|
| --space-1 | 4px | 매우 좁은 간격 |
| --space-2 | 8px | chip, 아이콘-라벨 |
| --space-3 | 12px | 조밀한 그룹 |
| --space-4 | 16px | 기본 inline padding |
| --space-5 | 20px | 패널 padding |
| --space-6 | 24px | 섹션 내부 그룹 |
| --space-8 | 32px | grid gap |
| --space-10 | 40px | 조밀한 섹션 |
| --space-12 | 48px | 섹션 헤더 |
| --space-16 | 64px | 페이지 rhythm |
| --space-20 | 80px | 히어로 간격 |
| --space-24 | 96px | 큰 섹션 구분 |

### 그리드

- 최대 콘텐츠 폭: 1180px
- 컬럼 시스템: 비대칭 12컬럼, desktop gutter 24px, mobile gutter 16px
- 브레이크포인트: sm 640px, md 768px, lg 1024px, xl 1280px

### 규칙

- desktop에서는 비대칭 구성을 허용하지만 mobile에서는 단일 컬럼으로 접는다.
- card radius는 8px 이하로 유지한다.

## 5. 컴포넌트

### Command Button
- **구조**: 텍스트와 작은 CSS arrow mark가 있는 anchor 또는 button.
- **변형**: primary, secondary.
- **간격**: 세로 --space-3, 가로 --space-4.
- **상태**: hover, active, focus-visible.
- **접근성**: 명확한 focus ring과 설명 가능한 label.
- **모션**: transform과 opacity만 사용.

### Pipeline Row
- **구조**: label, format badge, output status, 짧은 근거.
- **변형**: background-jpg, png-element, svg-element, gif-element, metadata.
- **간격**: padding --space-4, 내부 gap --space-2.
- **상태**: hover highlight.
- **접근성**: 색상만으로 의미를 전달하지 않는다.
- **모션**: hover 때 약한 translate.

### Star Link
- **구조**: SVG star icon, label, mono count badge가 GitHub stargazers로 연결된다.
- **변형**: hero, footer.
- **간격**: 세로 --space-3, 가로 --space-4, 내부 gap --space-2.
- **상태**: hover, active, focus-visible, API fallback count.
- **접근성**: 설명 가능한 link label과 눈에 보이는 count text.
- **모션**: hover와 active에서 약한 translate.

### Workflow Visual
- **구조**: 프로젝트에 보존한 imagegen bitmap을 16:9 framed surface 안에 배치한다.
- **변형**: hero figure, feature media crop.
- **간격**: 주변 copy와 --space-6 이상 간격을 두고, compact technical label 외의 텍스트 overlay는 쓰지 않는다.
- **상태**: static image, responsive crop.
- **접근성**: hero image에는 설명 가능한 alt text를 두고, 장식용 crop은 hidden 처리한다.
- **모션**: 자동 animation은 쓰지 않는다.

### Workflow Explainer
- **구조**: 짧은 소개 문구와 production step을 담은 순서형 텍스트 목록을 나란히 배치한다.
- **변형**: JPG background path, PNG element path, SVG element path, GIF element path, CSV validation path.
- **간격**: visual workflow board와 --space-8 이상 분리하고, item padding은 --space-4를 쓴다.
- **상태**: static documentation surface.
- **접근성**: 색에 의존하지 않는 label과 semantic ordered list를 사용한다.
- **모션**: 사용하지 않는다.

## 6. 모션과 상호작용

### 타이밍

| 타입 | 시간 | easing | 용도 |
|------|------|--------|------|
| Micro | 120ms | ease-out | 버튼 press |
| Standard | 240ms | cubic-bezier(0.16, 1, 0.3, 1) | hover, focus |
| Emphasis | 520ms | cubic-bezier(0.16, 1, 0.3, 1) | 히어로 load |

### 규칙

- transform, opacity, filter만 animate한다.
- prefers-reduced-motion을 존중한다.
- CSS만 사용하고 페이지 runtime dependency를 만들지 않는다.

## 7. 깊이와 표면

### 전략

혼합 전략이지만 절제한다. 기본은 tonal shift와 1px border이고, shadow는 hero control surface에만 쓴다.

| 레벨 | 값 | 용도 |
|------|----|------|
| Subtle | 0 1px 2px rgba(23, 35, 33, 0.06) | 작은 raised control |
| Default | 0 18px 50px rgba(23, 35, 33, 0.16) | hero panel |

| 타입 | 값 | 용도 |
|------|----|------|
| Default | 1px solid var(--border-default) | 패널, 구분선 |
| Subtle | 1px solid var(--border-subtle) | 섹션 분리 |
