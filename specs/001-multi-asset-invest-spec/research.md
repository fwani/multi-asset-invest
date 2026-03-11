# Research: 멀티에셋 투자 인텔리전스 플랫폼

**Branch**: `001-multi-asset-invest-spec` | **Phase 0 output**

## 1. 기술 스택

### 1.1 API 서버: Python + FastAPI

- **Decision**: Python 3.11+, FastAPI
- **Rationale**: 스펙에서 api를 Python으로 명시. FastAPI는 비동기 지원·자동 OpenAPI·타입 힌트로 API·worker 간 스키마 공유에 유리.
- **Alternatives considered**: Django REST (무겁고 동기 중심), Flask (비동기·스키마 도구가 추가 작업 필요).

### 1.2 웹 프론트: Vue 3

- **Decision**: Vue 3 (Composition API), Pinia, Vue Router
- **Rationale**: 스펙에서 대시보드용 웹을 Vue로 명시. Vue 3는 대시보드급 SPA에 적합하고, 이벤트·시그널·포트폴리오 등 도메인 모듈 분리가 쉬움.
- **Alternatives considered**: React (스펙과 불일치), Svelte (팀/운영 관점에서 Vue가 지정됨).

### 1.3 워커: Python 비동기 파이프라인

- **Decision**: Python 기반 크롤러 + 이벤트 추출 + 자산 영향·시그널 생성 파이프라인. DB 직접 접근으로 결과 저장.
- **Rationale**: 스펙상 Redis를 캐시·메시지 큐로 채택. 크롤·이벤트 추출·시그널 생성은 Redis 큐(Celery·RQ·Taskiq 등)로 worker에 전달하고, 대시보드·조회는 Redis 캐시로 응답 가속.
- **Alternatives considered**: Node.js 워커(스펙이 Python), DB 폴링만 사용(스펙에서 Redis 채택).

### 1.4 스토리지: PostgreSQL

- **Decision**: PostgreSQL 단일 주 스토어. api·worker 공통 접근.
- **Rationale**: 스펙 명시. 이벤트·시그널·포트폴리오·주문·포지션 등 관계형 모델에 적합. Redis는 캐시·메시지 큐 전용으로 별도 사용.
- **Alternatives considered**: MongoDB(관계·트랜잭션 요구에 비해 과함), Redis 단독 스토어(영속성·쿼리 요구에 부적합).

## 2. 도메인·통합

### 2.1 크롤링 및 정책 준수

- **Decision**: 무료 공개 소스만 대상. 각 소스 robots.txt·User-Agent·요청 빈도 준수. 수집 결과에 출처·시점·유형 메타데이터 부여.
- **Rationale**: 스펙 FR-001, FR-002 및 Assumptions에 명시.
- **Alternatives considered**: 유료 피드(비용·범위 외), 무제한 요청(정책 위험).

### 2.2 이벤트 추출·자산 영향·시그널 알고리즘

- **Decision**: 구체적 알고리즘(규칙 기반·통계·ML)은 구현 단계에서 결정. 스펙은 "이벤트/영향/시그널이 생성·저장·조회된다" 수준만 요구.
- **Rationale**: 스펙 Assumptions에 명시.
- **Alternatives considered**: 스펙 단계에서 ML 스택 고정(과도한 구속).

### 2.3 api–worker 협업

- **Decision**: 초기에는 DB 공유만. worker가 크롤 → 이벤트 추출 → 자산 영향 → 시그널 생성 후 PostgreSQL에 직접 저장. api는 해당 테이블 조회·CRUD.
- **Rationale**: Redis 큐로 api·worker 분리. worker가 큐에서 크롤·이벤트 추출·시그널 생성 작업을 소비하고 결과를 PostgreSQL에 저장. api는 DB 조회·캐시(Redis)로 응답.
- **Alternatives considered**: api가 워커 HTTP 호출(큐가 트래픽·재시도·지연 분리에 유리), DB 폴링만 사용(스펙에서 Redis 채택).

### 2.4 관리자 수집 소스 설정 (FR-002-2)

- **Decision**: 수집 소스(크롤 대상 URL·소스 이름·활성 여부)를 PostgreSQL에 crawl_sources 테이블로 저장. API에서 CRUD 제공(관리자 전용 또는 역할 기반). 웹 관리자 화면에서 등록·조회·수정·비활성화. 워커는 크롤 실행 시 DB에서 is_active=true인 소스 목록을 조회하여 각 소스별로 크롤을 수행한다. 설정 변경은 이후 수집 작업부터 적용된다.
- **Rationale**: 스펙 FR-002-2 및 PRD "수집 소스 설정(관리자)" 요구. 코드 하드코딩 대신 UI로 소스 관리 시 운영·테스트·다중 소스 확장이 용이함.
- **Alternatives considered**: 환경 변수·설정 파일만 사용(UI 없음, 스펙 불일치), Redis에만 저장(영속성·조회 일관성에 DB가 유리).

## 3. 성능·규모

### 3.1 대시보드 3초 로드

- **Decision**: 대시보드용 전용 API(또는 단일 aggregate 엔드포인트)로 최근 이벤트·시그널·포트폴리오 요약을 한 번에 반환. Redis 캐시로 해당 응답·자주 조회되는 데이터를 캐시하여 3초 로드 목표 달성.
- **Rationale**: SC-001. 100명 동시 사용 규모면 단일 DB + 인덱스·쿼리 최적화로 충분할 가능성 높음.
- **Alternatives considered**: 화면별 다수 API 호출(워터폴·체감 지연 증가).

### 3.2 이벤트 5분 이내 반영

- **Decision**: 수집·추출 파이프라인을 주기적(예: 1~5분) 실행하거나, 수집 완료 트리거로 실행. 저장 직후 목록/대시보드에서 조회 가능하도록.
- **Rationale**: SC-002. 배치 주기 + DB 쓰기로 충족. 실시간 스트리밍은 비목표.
- **Alternatives considered**: 실시간 큐 기반(초기에는 불필요한 복잡도).

## 4. 테스트

- **Decision**: api·worker는 pytest, web은 Vitest + Vue Test Utils. 통합 테스트(DB·API)·계약 테스트(API 스키마·엔드포인트) 포함.
- **Rationale**: 3-tier 구조에서 API 계약이 프론트·백엔드 협업의 기준. 스펙의 Acceptance Scenarios를 통합/ E2E로 검증.
- **Alternatives considered**: E2E만 의존(느리고 불안정), 단위만(통합·계약 누락).
