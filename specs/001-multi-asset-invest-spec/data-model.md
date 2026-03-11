# Data Model: 멀티에셋 투자 인텔리전스 플랫폼

**Branch**: `001-multi-asset-invest-spec` | **Phase 1 output**

스펙의 Key Entities와 FR 요구사항을 기반으로 한 엔티티·관계·검증·상태 정의.

---

## 1. 엔티티 요약

| 엔티티 | 설명 | 주 저장소 |
|--------|------|-----------|
| User | 인증된 사용자. 포트폴리오·주문 소유자. | api |
| Asset | 투자 대상 자산(주식·암호화폐·외환·채권·금·원자재 등) | api/worker |
| News | 수집된 텍스트 소스(뉴스·블로그 등) | worker |
| Event | 뉴스/데이터에서 추출된 시장 이벤트 | worker → api 조회 |
| AssetImpact | 이벤트–자산 영향(방향·강도) | worker |
| Signal | 투자 시그널(자산·방향·신뢰도·사유·연관 이벤트) | worker → api 조회 |
| Portfolio | 사용자별 자산 구성(복수 가능). 실행 연동 포트폴리오 1개/사용자 | api |
| Position | 포트폴리오 내 보유 포지션 | api |
| Order | 주문(초안 → 제출 → 상태 추적) | api |
| Notification | 인앱 알림 | api |
| Policy / Indicator | 정책·경제 지표(이벤트/영향 입력) | worker |
| Company, Country, Currency, Sector | 온톨로지·엔티티(이벤트·자산 관계) | api/worker |
| CrawlSource | 수집 소스(크롤 대상 URL·이름·활성 여부). 관리자 UI 설정(FR-002-2) | api 저장, worker 조회 |

---

## 2. 엔티티 상세

### 2.1 User

- **역할**: 인증·소유권. 포트폴리오·주문·알림 소유.
- **필드(예)**: id, external_id(auth 연동), email, display_name, created_at, updated_at.
- **관계**: 1:N Portfolio, 1:N Order, 1:N Notification. 실행용 Portfolio 1개만 지정(FR-009-1).
- **검증**: 인증 제공자와 일치하는 식별자 보유.

### 2.2 Asset

- **역할**: 시그널·포지션·주문의 대상. FR-018 자산 유형 지원.
- **필드(예)**: id, symbol, name, asset_type(enum: stock, crypto, fx, bond, commodity_gold, commodity_other 등), currency_id, exchange, sector_id, country_id, created_at, updated_at.
- **관계**: N:1 Currency, Sector, Country. AssetImpact, Position, Order, Signal에서 참조.
- **검증**: asset_type은 지원 목록 내만 허용. 미지원 자산 참조 시 "미지원" 표시·실행 차단(Edge Case).

### 2.3 News

- **역할**: 크롤링된 텍스트 소스. 메타데이터·출처·시점(FR-002).
- **필드(예)**: id, source, url, title, body, published_at, collected_at, type, metadata(JSON), created_at.
- **관계**: 1:N Event(추출된 이벤트).
- **검증**: 출처·시점·유형 필수. robots.txt 등 정책 준수는 수집 레이어에서 보장.

### 2.4 Event

- **역할**: 뉴스/정책에서 추출된 시장 이벤트(FR-003, FR-004).
- **필드(예)**: id, news_id, event_type, country_id, actor, impact_type, occurred_at, source_summary, confidence, extracted_at, metadata(JSON).
- **관계**: N:1 News. 1:N AssetImpact, N:M Signal(연관 이벤트).
- **검증**: event_type·occurred_at·출처 정보 존재. 목록 조회·필터·정렬 지원.

### 2.5 AssetImpact

- **역할**: 이벤트가 자산에 미치는 영향(FR-005, FR-006).
- **필드(예)**: id, event_id, asset_id, direction(up/down/neutral), strength(magnitude), computed_at.
- **관계**: N:1 Event, Asset.
- **검증**: direction·strength 범위 정의. 이벤트별·자산별 조회 지원.

### 2.6 Signal

- **역할**: 투자 행동 제안(FR-007, FR-008).
- **필드(예)**: id, asset_id, direction(buy/sell/reduce/hedge), confidence, reason, generated_at, metadata(JSON). 연관 event_ids(배열 또는 조인 테이블).
- **관계**: N:1 Asset. N:M Event(연관 이벤트). 1:N Order(시그널 기반 주문 초안).
- **검증**: 자산·방향·신뢰도·사유·시점 존재. 지원 자산만 노출·실행(FR-018).

### 2.7 Portfolio

- **역할**: 사용자별 자산 구성. 복수 보유 가능. 실행 연동 1개만(FR-009, FR-009-1).
- **필드(예)**: id, user_id, name, is_execution_linked(boolean), target_allocation(JSON 또는 별도 테이블), created_at, updated_at.
- **관계**: N:1 User. 1:N Position. 1:N Order(해당 포트폴리오로 제출된 주문).
- **검증**: 사용자당 is_execution_linked=true인 포트폴리오는 최대 1개. 목표 배분·리밸런싱 필요량 계산(FR-011).

### 2.8 Position

- **역할**: 포트폴리오 내 보유 포지션(FR-009, FR-013).
- **필드(예)**: id, portfolio_id, asset_id, quantity, entry_price, current_price, unrealized_pnl, updated_at.
- **관계**: N:1 Portfolio, Asset.
- **검증**: quantity·가격 비음. 체결된 주문에 따라 갱신.

### 2.9 Order

- **역할**: 주문 초안 → 사용자 확인·수정 후 제출 → 상태 추적(FR-012, FR-013, FR-014).
- **필드(예)**: id, user_id, portfolio_id(실행용), asset_id, order_type(market/limit/stop 등), side(buy/sell), quantity, price(nullable), signal_id(nullable), status, external_id(브로커/거래소), submitted_at, updated_at.
- **관계**: N:1 User, Portfolio, Asset. N:1 Signal(선택). 상태는 아래 상태 전이 참고.
- **검증**: 지원 자산만 허용. 제출은 사용자 동작 후에만 전송. 체결 시 지정 포트폴리오의 포지션에만 반영.

**상태 전이**: draft → pending → partial_filled | filled | cancelled. (draft: 초안, pending: 제출됨 대기, partial_filled/filled/cancelled: 최종 상태.)

### 2.10 Notification

- **역할**: 인앱 알림(FR-016). 대시보드·앱 내 알림 영역 표시.
- **필드(예)**: id, user_id, type(event/signal/risk 등), title, body, read_at, created_at.
- **관계**: N:1 User.
- **검증**: 읽음/안 읽음. 기간·타입별 조회.

### 2.11 Policy / Indicator

- **역할**: 정책·경제 지표. 이벤트 또는 자산 영향 분석 입력.
- **필드(예)**: id, source, name, value, released_at, metadata(JSON). (구현 시 Event와 유사하게 취급하거나 별도 테이블.)

### 2.12 Company, Country, Currency, Sector

- **역할**: 온톨로지. 이벤트·자산의 국가·산업·통화 등 관계.
- **필드(예)**: id, code, name, type. 필요 시 hierarchy.

### 2.13 CrawlSource (FR-002-2)

- **역할**: 관리자가 웹 UI에서 등록·조회·수정·비활성화하는 데이터 수집 소스. 워커 크롤 파이프라인의 시작점(URL·소스 이름)으로 사용된다.
- **필드(예)**: id, base_url, source_name, is_active, created_at, updated_at. (선택: schedule_cron, priority 등)
- **관계**: 없음(독립 설정 엔티티). News.source는 문자열로 저장되며, 크롤 시점의 CrawlSource.source_name과 매핑 가능.
- **검증**: base_url 유효 형식. is_active=false인 소스는 워커가 크롤 대상에서 제외. 변경 시 이후 수집 작업부터 적용.

---

## 3. 관계 다이어그램(요약)

```text
User ──1:N── Portfolio ──1:N── Position ──N:1── Asset
  │                │                           │
  │                └──1:N── Order ──N:1────────┘
  │                           │
  └──1:N── Notification      N:1
                            Signal ──N:1── Asset
                                  ──N:M── Event
News ──1:N── Event ──1:N── AssetImpact ──N:1── Asset
```

---

## 4. 구현 참고

- **api**: User, Asset, Portfolio, Position, Order, Notification, Company/Country/Currency/Sector CRUD·조회. CrawlSource CRUD(관리자용, FR-002-2). Event/Signal/AssetImpact는 worker가 저장·api는 조회.
- **worker**: News, Event, AssetImpact, Signal 생성·저장. Policy/Indicator, 크롤러 메타데이터. 크롤 시 활성 CrawlSource 목록을 DB에서 조회하여 수집 시작점으로 사용.
- **공통**: Asset, Country, Currency, Sector 등 마스터는 api에서 관리하고 worker는 참조만 하거나, 초기 시드 후 공유 DB에서 읽기.
- **인덱스**: Event(occurred_at, event_type), Signal(generated_at, asset_id), Order(user_id, status, submitted_at), Position(portfolio_id), 대시보드용 집계 쿼리(최근 N건).
