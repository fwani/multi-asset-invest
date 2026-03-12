# Tasks: 멀티에셋 투자 인텔리전스 플랫폼

**Input**: Design documents from `/specs/001-multi-asset-invest-spec/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: 스펙에서 TDD/테스트 선행을 명시하지 않아 별도 테스트 태스크는 두지 않음. 필요 시 통합·계약 테스트는 Polish 단계 또는 스토리 내에서 추가.

**Organization**: User story 단위로 그룹하여 각 스토리를 독립 구현·검증 가능하게 구성.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 실행 가능(다른 파일, 선행 태스크 없음)
- **[Story]**: 해당 유저 스토리(US1~US7)
- 설명에 구체적 파일 경로 포함

## Path Conventions

- **api**: `apps/api/app/` (models, services, api/routes)
- **web**: `apps/web/src/` (components, pages, services)
- **worker**: `apps/worker/app/` (crawlers, pipelines)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 모노레포 및 api·web·worker 프로젝트 초기화

- [x] T001 Create monorepo directories apps/api, apps/web, apps/worker per plan.md structure
- [x] T002 Initialize apps/api with FastAPI, PostgreSQL driver (async), Redis client, requirements in apps/api/requirements.txt
- [x] T003 Initialize apps/web with Vue 3, Pinia, Vue Router, Vite in apps/web/
- [x] T004 Initialize apps/worker with Python, Redis queue client, PostgreSQL driver in apps/worker/requirements.txt
- [x] T005 [P] Configure linting and formatting (e.g. ruff/eslint) for apps/api and apps/web

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DB·인증·Redis·API/Worker 기반. 이 단계 완료 전에는 유저 스토리 작업 불가.

- [x] T006 Setup PostgreSQL migrations (Alembic or similar) and define all tables from data-model.md in apps/api/
- [x] T007 [P] Implement User, Asset, Country, Currency, Sector models in apps/api/app/models/
- [x] T008 [P] Implement News, Event, AssetImpact, Signal models in apps/api/app/models/ (worker가 쓰고 api가 조회)
- [x] T009 [P] Implement Portfolio, Position, Order, Notification models in apps/api/app/models/
- [x] T010 Implement auth dependency (e.g. JWT or session placeholder) in apps/api/app/deps.py
- [x] T011 Implement Redis connection (cache + queue client) in apps/api/app/core/redis.py
- [x] T012 Implement API app factory, router mount, global error handler in apps/api/app/main.py
- [x] T013 Implement Redis queue consumer and DB connection bootstrap in apps/worker/app/main.py
- [x] T014 Seed minimal Asset, Country, Currency, Sector master data (migration or script in apps/api/)

**Checkpoint**: Foundation ready — 유저 스토리 구현 시작 가능

---

## Phase 3: User Story 1 - 뉴스·정책에서 이벤트 확인 (Priority: P1) — MVP

**Goal**: 뉴스/정책 수집 → 이벤트 추출·저장 → 이벤트 목록·상세 조회(API·웹)

**Independent Test**: 뉴스/정책 텍스트 입력 시 이벤트 유형·국가·영향·시점이 구조화되어 목록·상세에 표시됨.

- [x] T015 [US1] Implement EventService (list, get by id, filters) in apps/api/app/services/event_service.py
- [x] T016 [US1] Implement GET /api/v1/events, GET /api/v1/events/{id} in apps/api/app/api/events.py
- [x] T017 [US1] Implement crawler stub (one source, robots.txt-aware) in apps/worker/app/crawlers/
- [x] T018 [US1] Implement event extractor stub (text → Event attributes) in apps/worker/app/pipelines/event_extractor.py
- [x] T019 [US1] Implement pipeline job: crawl → save News → extract → save Event, enqueue via Redis in apps/worker/app/pipelines/
- [x] T019a [US1] Implement POST /api/v1/worker/trigger (enqueue crawl/pipeline job to Redis) in apps/api/app/api/ (수동 크롤·파이프라인 트리거)
- [x] T020 [US1] Add events API client in apps/web/src/services/api/events.ts
- [x] T021 [US1] Create events list page with filters in apps/web/src/pages/EventsList.vue
- [x] T022 [US1] Create event detail page (출처·추출 속성) in apps/web/src/pages/EventDetail.vue
- [x] T022a [US1] Add worker trigger API client and UI (수동 크롤 실행 버튼/영역) in apps/web/src/ (events 목록 또는 전용 트리거 영역)
- [x] T022b [US1] Add CrawlSource model and migration (crawl_sources table: base_url, source_name, is_active, created_at, updated_at) per data-model.md §2.13 in apps/api/
- [x] T022c [US1] Implement CrawlSourceService (list, get, create, update, delete or disable) in apps/api/app/services/crawl_source_service.py
- [x] T022d [US1] Implement GET/POST/PATCH/DELETE /api/v1/crawl-sources per contracts/api.md §10 in apps/api/app/api/crawl_sources.py (FR-002-2)
- [x] T022e [US1] Worker: load active crawl sources from DB in crawl pipeline and use them as crawl start points (replace or extend stub_crawler default) in apps/worker/app/pipelines/ and apps/worker/app/crawlers/
- [x] T022f [US1] Add crawl sources API client and admin UI page (list, add, edit, disable) in apps/web/src/ (관리자 수집 소스 설정 FR-002-2)

**Checkpoint**: US1 완료 — 이벤트 목록·상세 독립 검증 가능

---

## Phase 4: User Story 2 - 이벤트가 자산에 미치는 영향 보기 (Priority: P1)

**Goal**: 이벤트별·자산별 자산 영향 조회(API·웹)

**Independent Test**: 이벤트 선택 시 영향받는 자산·방향·강도 표시; 자산별 영향 목록 조회 가능.

- [x] T023 [P] [US2] Implement AssetImpactService in apps/api/app/services/asset_impact_service.py
- [x] T024 [US2] Implement GET /api/v1/events/{id}/impacts, GET /api/v1/assets/{id}/impacts in apps/api/app/api/impacts.py
- [x] T025 [US2] Implement asset impact calculation step (rule stub) and save AssetImpact in apps/worker/app/pipelines/impact_calculator.py
- [x] T026 [US2] Add impacts API client and event detail impacts section in apps/web/src/
- [x] T027 [US2] Create assets impacts view (자산별 정렬·필터) in apps/web/src/pages/AssetImpacts.vue
- [x] T027a [P] [US2] Implement AssetService (list, get) and GET /api/v1/assets, GET /api/v1/assets/{id} per contracts/api.md (FR-018) in apps/api/app/services/asset_service.py, apps/api/app/api/assets.py
- [x] T027b [US2] Add assets API client in apps/web/src/services/api/assets.ts
- [x] T027c [US2] Create assets list page (지원 자산 목록, 유형별 필터) in apps/web/src/pages/AssetsList.vue
- [x] T027d [US2] Add asset filter/select to impacts view using assets API (자산 선택 시 해당 자산 영향 조회) in apps/web/src/pages/AssetImpacts.vue
- [x] T027e [P] [US2] Implement AssetService.create and POST /api/v1/assets (create asset, body: symbol, name, asset_type, currency_id, exchange, sector_id, country_id) in apps/api/src/services/asset_service.py, apps/api/src/api/assets.py
- [x] T027f [US2] Add asset create API client (createAsset) in apps/web/src/services/api/assets.ts and asset add form/UI (자산 추가 폼) in apps/web/src/pages/AssetsList.vue or dedicated page

**Checkpoint**: US2 완료 — 이벤트·자산 영향 독립 검증 가능

---

## Phase 5: User Story 3 - 투자 시그널 확인 및 활용 (Priority: P1)

**Goal**: 시그널 생성(worker)·저장·목록·상세 조회 및 시그널→주문 초안 생성 API

**Independent Test**: 이벤트·영향 기반 시그널 생성 후 목록에서 자산·방향·신뢰도·사유 확인, 상세에서 연관 이벤트 추적 가능.

- [ ] T028 [P] [US3] Implement SignalService (list, get, filters) in apps/api/app/services/signal_service.py
- [ ] T029 [US3] Implement GET /api/v1/signals, GET /api/v1/signals/{id}, POST /api/v1/signals/{id}/create-order-draft in apps/api/app/api/signals.py
- [ ] T030 [US3] Implement signal generator stub (event+impact → Signal) and pipeline step in apps/worker/app/pipelines/signal_generator.py
- [ ] T031 [US3] Add signals API client in apps/web/src/services/api/signals.ts
- [ ] T032 [US3] Create signals list page (자산별·시간순 필터·정렬) in apps/web/src/pages/SignalsList.vue
- [ ] T033 [US3] Create signal detail page (연관 이벤트·자산 영향 근거) in apps/web/src/pages/SignalDetail.vue

**Checkpoint**: US3 완료 — 시그널 목록·상세·초안 생성 독립 검증 가능

---

## Phase 6: User Story 4 - 포트폴리오 조회 및 자산 배분 관리 (Priority: P2)

**Goal**: 복수 포트폴리오 CRUD, 실행 연동 1개 지정, 성과·리밸런싱 목표·비중 비교

**Independent Test**: 포트폴리오 목록·전환·상세(자산·비중·평가·리스크), 성과 조회, 목표 배분 설정 시 리밸런싱 필요량 표시.

- [ ] T034 [P] [US4] Implement PortfolioService, PositionService in apps/api/app/services/
- [ ] T035 [US4] Implement GET/POST/PATCH /portfolios, GET /portfolios/{id}, performance, rebalance, target-allocation per contracts/api.md in apps/api/app/api/portfolios.py
- [ ] T036 [US4] Implement portfolio risk and performance calculation helpers in apps/api/app/services/portfolio_service.py
- [ ] T037 [US4] Add portfolios API client in apps/web/src/services/api/portfolios.ts
- [ ] T038 [US4] Create portfolios list and switch view in apps/web/src/pages/Portfolios.vue
- [ ] T039 [US4] Create portfolio detail page (포지션·비중·리스크·성과) in apps/web/src/pages/PortfolioDetail.vue
- [ ] T040 [US4] Create target allocation and rebalance view in apps/web/src/pages/PortfolioRebalance.vue

**Checkpoint**: US4 완료 — 포트폴리오·리밸런싱 독립 검증 가능

---

## Phase 7: User Story 5 - 시그널 기반 주문 실행 (Priority: P2)

**Goal**: 주문 초안 생성·수정·제출, 상태 추적, 체결 시 포지션 반영(브로커 연동은 스텁 가능)

**Independent Test**: 시그널/직접 주문 초안 생성 → 확인·수정 후 제출 → 주문 상태 조회, 체결 시 포지션 반영 확인.

- [ ] T041 [P] [US5] Implement OrderService (drafts, submit, list, get) in apps/api/app/services/order_service.py
- [ ] T042 [US5] Implement POST/GET/PUT /orders/drafts, POST drafts/{id}/submit, GET /orders per contracts/api.md in apps/api/app/api/orders.py
- [ ] T043 [US5] Implement broker/exchange adapter stub (submit order, sync status) in apps/api/app/services/broker_adapter.py
- [ ] T044 [US5] Implement order fill → position update logic in apps/api/app/services/order_service.py
- [ ] T045 [US5] Add orders API client in apps/web/src/services/api/orders.ts
- [ ] T046 [US5] Create order draft confirm/edit and submit flow in apps/web/src/pages/OrderSubmit.vue
- [ ] T047 [US5] Create orders history and status view in apps/web/src/pages/OrdersList.vue

**Checkpoint**: US5 완료 — 주문 초안·제출·상태·포지션 반영 독립 검증 가능

---

## Phase 8: User Story 6 - 대시보드에서 이벤트·시그널·포트폴리오 한눈에 보기 (Priority: P2)

**Goal**: 단일 대시보드 API + Redis 캐시, 웹 대시보드 페이지(요약·알림·상세 이동)

**Independent Test**: 로그인 후 대시보드에서 최근 이벤트·시그널·포트폴리오 요약·알림 표시, 항목 클릭 시 상세 화면 이동.

- [ ] T048 [US6] Implement GET /api/v1/dashboard aggregate (events, signals, portfolio_summary, notifications) in apps/api/app/api/dashboard.py
- [ ] T049 [US6] Add Redis cache for dashboard response in apps/api/app/services/dashboard_service.py (SC-001 3초 목표)
- [ ] T050 [US6] Add dashboard API client in apps/web/src/services/api/dashboard.ts
- [ ] T051 [US6] Create dashboard page (이벤트·시그널·포트폴리오 요약·알림) in apps/web/src/pages/Dashboard.vue
- [ ] T052 [US6] Wire dashboard as default route and add navigation to event/signal/portfolio detail

**Checkpoint**: US6 완료 — 대시보드 독립 검증 가능

---

## Phase 9: User Story 7 - 리스크·성과 보고서 생성 (Priority: P3)

**Goal**: 보고서 생성·조회·내보내기(API·웹)

**Independent Test**: 기간·항목 선택 후 성과·리스크·시그널·거래 이력 포함 보고서 생성, 조회 또는 파일 내보내기 가능.

- [ ] T053 [P] [US7] Implement ReportService (generate, get, export) in apps/api/app/services/report_service.py
- [ ] T054 [US7] Implement POST /api/v1/reports, GET /api/v1/reports/{id} in apps/api/app/api/reports.py
- [ ] T055 [US7] Add reports API client in apps/web/src/services/api/reports.ts
- [ ] T056 [US7] Create report create and view/export page in apps/web/src/pages/Report.vue

**Checkpoint**: US7 완료 — 보고서 독립 검증 가능

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: 알림·에러 처리·문서·quickstart 검증 등

- [ ] T057 Implement NotificationService and GET /notifications, PATCH /notifications/{id}/read in apps/api/app/api/notifications.py
- [ ] T058 Add in-app notification area and read state in apps/web (대시보드 또는 레이아웃)
- [ ] T059 [P] Add GET /api/v1/assets to api and assets client in apps/web for FR-018 support
- [ ] T060 Run quickstart.md flow: infra up, api + web + worker run, smoke check
- [ ] T061 [P] Update README and docs with run instructions and env vars

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 선행 없음.
- **Phase 2 (Foundational)**: Phase 1 완료 후 진행. 모든 유저 스토리 블로킹.
- **Phase 3~9 (User Stories)**: Phase 2 완료 후 진행. 스토리 간 순서는 P1→P2→P3 권장이나, US4~US7은 US1~US3 기반만 있으면 병렬 가능.
- **Phase 10 (Polish)**: 원하는 스토리까지 완료 후 진행.

### User Story Dependencies

- **US1 (P1)**: Foundation만 필요. MVP 권장.
- **US2 (P1)**: US1(Event) 완료 시 자연스럽게 영향 조회 가능.
- **US3 (P1)**: US1·US2(Event, AssetImpact) 기반으로 시그널 생성.
- **US4 (P2)**: Foundation(User, Portfolio, Position)만 있으면 독립 구현 가능.
- **US5 (P2)**: US3(시그널)·US4(포트폴리오)와 연동되나, 주문·포지션만으로도 독립 검증 가능.
- **US6 (P2)**: US1·US3·US4 완료 시 대시보드 내용 채움. API만 먼저 구현 후 웹만 붙여도 됨.
- **US7 (P3)**: US4·US5(포트폴리오·주문) 데이터 기반.

### Parallel Opportunities

- Phase 1: T005 [P]
- Phase 2: T007, T008, T009 [P] 동시 가능.
- Phase 3+: 동일 스토리 내 모델/서비스/라우트는 순서 유지; 다른 스토리(US4, US5, US6, US7)는 인력 있으면 병렬 진행 가능.

---

## Implementation Strategy

### MVP First (US1만)

1. Phase 1 Setup 완료
2. Phase 2 Foundational 완료
3. Phase 3 User Story 1 완료
4. **STOP**: 이벤트 목록·상세로 "무슨 이벤트가 있었는지" 검증 후 배포/데모

### Incremental Delivery

1. Setup + Foundational → 기반 완료
2. US1 → 이벤트 가치 검증 (MVP)
3. US2 → 자산 영향 검증
4. US3 → 시그널 검증
5. US4 → 포트폴리오 검증
6. US5 → 주문 실행 검증
7. US6 → 대시보드 진입점 검증
8. US7 → 보고서 검증
9. Polish → 알림·문서·quickstart

### Parallel Team Strategy

- Phase 2 완료 후: A=US1, B=US2, C=US4 등으로 스토리 단위 병렬 가능. US5는 US3·US4와 연동 후 진행 권장.

---

## Notes

- [P] 태스크는 서로 다른 파일·영역에서 선행 없이 병렬 가능.
- [USn] 라벨로 스토리 추적. 각 스토리 완료 시점에 독립 검증 가능하도록 구성.
- 구현 시 contracts/api.md 및 data-model.md 참고.
- Redis 큐: worker 파이프라인은 Redis 큐에서 작업 소비; api는 필요 시 큐에 작업 enqueue (예: 수동 크롤 트리거).
- FR-002-2: T022b~T022f는 관리자 수집 소스 설정(크롤 대상 URL·소스 이름·활성 여부 등록·조회·수정·비활성화). API에 CrawlSource CRUD, 워커는 활성 소스 목록을 DB에서 조회하여 크롤 시작점으로 사용, 웹에 관리자 UI 제공.
