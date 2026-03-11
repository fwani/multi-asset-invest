# 1. 제품 개요 (Product Overview)

## 1.1 제품 이름 (Working Title)

현재 프로젝트의 임시 이름은 다음과 같은 방향을 고려한다.

후보 예시:

- **Atlas** — 글로벌 자산 흐름을 지도처럼 분석하는 플랫폼
- **MacroGraph** — 거시경제와 자산 관계를 그래프로 분석
- **SignalOS** — 투자 시그널 생성 운영체제
- **Investor AI** — AI 기반 투자 분석 플랫폼

최종 제품 이름은 **브랜딩 및 제품 방향 확정 이후 결정**한다.

현재 PRD에서는 **Multi-Asset Investment Intelligence Platform** 으로 지칭한다.

---

# 1.2 제품 정의

본 제품은 **뉴스, 정책, 거시경제 데이터, 시장 데이터를 분석하여 멀티에셋 투자 의사결정을 지원하는 플랫폼**이다.

플랫폼은 다음과 같은 흐름을 자동화한다.

```
뉴스 / 정책 / 데이터
        ↓
이벤트 추출
        ↓
자산 영향 분석
        ↓
투자 시그널 생성
        ↓
포트폴리오 관리
        ↓
주문 실행
```

이 시스템은 단순한 **뉴스 요약 AI**가 아니라,  

**“이벤트 기반 투자 분석 엔진”**을 핵심으로 한다.

---

# 1.3 지원 자산 (Supported Assets)

초기 버전에서는 다음 자산군을 지원한다.

### 금융 자산

- 주식 (Equities)
- 암호화폐 (Crypto)
- 외환 (FX)
- 채권 (Bonds)

### 실물 / 대체 자산

- 금 (Gold)
- 원자재 (Commodities)

향후 확장 가능 자산:

- ETF
- 옵션
- 파생상품
- 부동산 지수

---

# 1.4 핵심 기능 요약

플랫폼은 다음 5가지 핵심 기능으로 구성된다.

### 1️⃣ 데이터 수집

다양한 투자 관련 데이터를 통합 수집한다.

데이터 유형:

- 뉴스
- 블로그
- 정치 발언
- 정책 발표
- 경제 지표
- 시장 데이터
- 기업 공시

---

### 2️⃣ 이벤트 분석

텍스트 데이터에서 **경제 / 정책 / 지정학 이벤트를 자동 추출**한다.

예:

```
뉴스:
"미국 연준이 금리 인상을 시사"

이벤트 구조화:

Event:
type = monetary_policy
country = US
impact = interest_rate_increase
```

---

### 3️⃣ 자산 영향 분석

이벤트가 금융 자산에 미치는 영향을 모델링한다.

예:

```
금리 상승

→ 채권 가격 하락
→ 성장주 하락
→ 달러 상승
→ 금 가격 하락
```

이 단계에서 **자산 간 관계 그래프**가 사용된다.

---

### 4️⃣ 투자 시그널 생성

자산 영향 분석 결과를 기반으로 **투자 행동 가능한 시그널**을 생성한다.

예:

```
Signal
asset = gold
direction = buy
confidence = 0.72
reason = geopolitical_risk
```

---

### 5️⃣ 포트폴리오 및 주문 실행

사용자는 생성된 시그널을 기반으로

- 포트폴리오 구성
- 리스크 관리
- 자동/반자동 주문

을 수행할 수 있다.

브로커 및 거래소 API와 연동된다.

---

# 1.5 제품의 핵심 가치 (Core Value Proposition)

본 제품이 해결하려는 핵심 문제는 다음과 같다.

현재 투자 과정:

```
뉴스 → 사람 해석 → 투자 판단
```

이 시스템의 목표:

```
뉴스 → 이벤트 → 자산 영향 → 시그널 → 주문
```

즉,

**정보 → 투자 행동까지의 전체 파이프라인을 자동화**하는 것이다.

---

# 1.6 제품 포지셔닝

본 제품은 다음 시스템들의 중간 영역에 위치한다.

| 영역 | 대표 제품 |
|---|---|
| 뉴스 분석 | Bloomberg, Reuters |
| 데이터 플랫폼 | Palantir |
| 트레이딩 시스템 | QuantConnect |
| 포트폴리오 관리 | Portfolio trackers |

본 제품은 위 영역을 통합하여 **"투자 의사결정 OS"** 를 목표로 한다.

---
# 2. 문제 정의 (Problem)

## 2.1 투자 환경의 구조적 문제

현대 금융 시장에서 투자 의사결정은 다음과 같은 구조적 문제를 가진다.

### 1️⃣ 정보 과부하 (Information Overload)

투자자는 다음과 같은 다양한 정보 소스를 지속적으로 분석해야 한다.

- 뉴스
- 블로그 및 분석 글
- 정치 발언
- 정책 발표
- 경제 지표
- 기업 공시
- 시장 데이터

정보의 양과 속도가 매우 빠르게 증가하면서 개인 투자자가 모든 정보를 실시간으로 분석하는 것은 사실상 불가능하다.

결과적으로 중요한 이벤트를 놓치거나 늦게 반응하는 문제가 발생한다.

---

### 2️⃣ 이벤트와 자산 영향의 연결 어려움

시장 이벤트는 여러 자산에 복합적인 영향을 미친다.

예:

```
금리 상승
→ 채권 가격 하락
→ 성장주 하락
→ 달러 상승
→ 금 가격 하락
```

```
지정학적 갈등
→ 금 상승
→ 원유 상승
→ 주식 시장 하락
```

이러한 관계는 다음과 같은 특징을 가진다.

- 다수 자산에 동시에 영향
- 시간 지연 발생
- 상황에 따라 영향 방향 변화

투자자가 이러한 관계를 지속적으로 추적하고 분석하는 것은 매우 어렵다.

---

### 3️⃣ 뉴스와 투자 행동 사이의 단절

현재 대부분의 투자 과정은 다음과 같은 구조를 가진다.

```
뉴스
→ 인간의 해석
→ 투자 판단
→ 주문 실행
```

이 과정은 다음과 같은 문제를 가진다.

- 해석의 주관성
- 반응 속도 지연
- 반복적인 수작업 분석
- 전략 일관성 부족

---

### 2.2 기존 시스템의 한계

현재 시장에는 다음과 같은 유형의 시스템이 존재한다.

#### 뉴스 플랫폼

예:

- Bloomberg
- Reuters
- Financial Times

문제:

- 뉴스 제공 중심
- 투자 행동으로 직접 연결되지 않음

---

#### 데이터 분석 플랫폼

예:

- Palantir
- Databricks
- Snowflake

문제:

- 데이터 분석 중심
- 투자 의사결정 엔진이 아님

---

#### 트레이딩 플랫폼

예:

- TradingView
- QuantConnect

문제:

- 가격 데이터 기반 전략 중심
- 뉴스/정책 이벤트 분석 부족

---

### 2.3 핵심 문제 정의

현재 투자 시스템은 다음 기능이 분리되어 있다.

```
정보 수집
분석
투자 판단
주문 실행
```

이로 인해 투자 의사결정 과정이 비효율적이다.

---

### 2.4 해결하려는 핵심 문제

본 제품은 다음 문제를 해결하는 것을 목표로 한다.

1. 뉴스, 정책, 시장 데이터를 통합적으로 분석할 수 있는 시스템 부재  
2. 이벤트와 자산 영향 관계를 구조적으로 분석할 수 있는 도구 부족  
3. 분석 결과가 투자 행동으로 자동 연결되지 않는 문제  

---

### 2.5 목표 시스템 구조

본 제품은 다음과 같은 파이프라인을 구축한다.

```
뉴스 / 정책 / 데이터
        ↓
이벤트 추출
        ↓
자산 영향 분석
        ↓
투자 시그널 생성
        ↓
포트폴리오 관리
        ↓
주문 실행
```

이를 통해 투자 의사결정 과정의 자동화 및 구조화를 달성한다.
# 3. 제품 목표 (Goals)

## 3.1 주요 목표 (Primary Goals)

### 1️⃣ 멀티에셋 이벤트 분석 플랫폼 구축

뉴스, 정책, 경제 데이터 등 다양한 정보 소스를 분석하여 **금융 시장 이벤트를 구조화된 데이터로 변환하는 플랫폼**을 구축한다.

시스템은 다음 정보를 자동으로 추출해야 한다.

- 이벤트 유형
- 관련 국가
- 관련 산업
- 관련 자산
- 이벤트 강도
- 이벤트 발생 시점

---

### 2️⃣ 뉴스 및 정책 기반 자산 영향 분석

텍스트 기반 정보에서 발생하는 이벤트가 **어떤 자산에 어떤 영향을 미치는지 분석하는 시스템**을 구축한다.

예:

```
Event: 금리 인상

Impact:
bond → down
growth_stock → down
usd → up
gold → down
```

자산 간 관계와 거시경제 영향을 기반으로 영향 분석을 수행한다.

---

### 3️⃣ 투자 시그널 생성 시스템

이벤트 분석과 자산 영향 모델을 기반으로 **투자 시그널을 자동 생성하는 엔진**을 구축한다.

시그널은 다음 정보를 포함한다.

```
asset
direction
confidence
reason
timestamp
```

시그널은 다음 투자 행동으로 연결될 수 있다.

- 매수
- 매도
- 포지션 축소
- 헤지

---

### 4️⃣ 포트폴리오 관리 기능 제공

사용자가 다양한 자산을 통합적으로 관리할 수 있도록 포트폴리오 관리 기능을 제공한다.

기능:

- 자산 배분 관리
- 리밸런싱
- 리스크 관리
- 성과 분석

---

### 5️⃣ 주문 실행 자동화 구조

브로커 및 거래소 API와 연동하여 **투자 시그널을 주문으로 연결할 수 있는 실행 시스템**을 구축한다.

가능 기능:

- 주문 생성
- 포지션 관리
- 자동 리밸런싱
- 반자동 전략 실행

---

## 3.2 비목표 (Non-goals)

초기 제품 버전에서 포함하지 않는 기능은 다음과 같다.

### 1️⃣ 고빈도 트레이딩

밀리초 단위 초저지연 거래 시스템은 구축하지 않는다.

---

### 2️⃣ 완전 자동 투자

초기 버전에서는 사용자의 승인 없이 자산을 자동으로 운용하는 시스템을 목표로 하지 않는다.

---

### 3️⃣ 초저지연 거래 인프라

거래소에 직접 연결되는 초저지연 인프라는 구축 대상이 아니다.

---

### 4️⃣ 브로커 인프라 구축

증권사나 거래소 역할을 수행하는 자체 브로커 시스템은 구축하지 않는다.
# 4. 사용자 (Users)

## 4.1 Primary User

### 개인 투자자 (Individual Investor)

다양한 자산에 투자하며 뉴스, 정책, 거시경제 정보를 기반으로 투자 의사결정을 하는 사용자.

특징:

- 멀티에셋 투자 수행
- 뉴스 및 거시경제 이벤트에 관심
- 투자 전략을 분석하고 개선하려는 성향
- 데이터 기반 의사결정을 선호

사용 목적:

- 시장 이벤트 분석
- 자산 영향 이해
- 투자 시그널 확인
- 포트폴리오 관리
- 주문 실행

---

### 퀀트 개발자 (Quant Developer)

데이터 기반 투자 전략을 설계하고 테스트하는 사용자.

특징:

- 투자 전략 개발
- 데이터 분석 수행
- 자동화된 투자 시스템 구축 관심

사용 목적:

- 이벤트 기반 전략 개발
- 시그널 생성 로직 실험
- 전략 백테스트
- 자동화 전략 실행

---

## 4.2 Secondary User

### AI Agent

플랫폼 내부 또는 외부에서 동작하는 자동화된 투자 에이전트.

특징:

- 이벤트 분석 데이터 활용
- 자산 영향 모델 활용
- 자동 전략 실행

사용 목적:

- 이벤트 기반 투자 전략 수행
- 포트폴리오 관리 자동화
- 시장 이벤트 대응

---

## 4.3 사용자 목표

사용자가 이 플랫폼을 통해 달성하려는 주요 목표는 다음과 같다.

``` id="ag93l1"
시장 이벤트 빠르게 이해
→ 자산 영향 분석
→ 투자 시그널 생성
→ 포트폴리오 관리
→ 투자 실행
```

사용자는 다양한 데이터와 분석 결과를 기반으로 **보다 구조적이고 빠른 투자 의사결정**을 수행할 수 있어야 한다.
# 5. 핵심 기능 (Core Features)

## 5.1 데이터 수집 (Data Ingestion)

플랫폼은 다양한 투자 관련 데이터를 수집하고 통합한다.

### 데이터 소스

- 뉴스
- 블로그
- 정책 발표
- 정치 발언
- 경제 지표
- 시장 데이터
- 기업 공시

### 데이터 유형

```
text
market_data
macro_data
policy_data
financial_reports
```

### 주요 기능

- 데이터 소스 연결
- 실시간 및 배치 데이터 수집
- 데이터 정규화
- 메타데이터 생성
- 데이터 저장 및 인덱싱
- **수동 트리거**: API를 통한 크롤·파이프라인 작업 실행 요청(운영·테스트·즉시 반영용). 요청 시 작업이 큐에 enqueue되고 워커가 비동기 처리한다.
- **수집 소스 설정(관리자)**: 관리자는 웹 UI에서 크롤 대상 소스(URL·소스 이름·활성 여부 등)를 등록·수정·비활성화할 수 있다. 설정 변경 시 이후 크롤·이벤트 추출부터 반영된다.

---

# 5.2 이벤트 분석 (Event Analysis)

텍스트 기반 데이터에서 시장 이벤트를 추출하고 구조화한다.

### 입력 데이터

- 뉴스 기사
- 정책 발표
- 정치 발언
- 경제 리포트

### 이벤트 구조 예시

```
Event
type = monetary_policy
country = US
actor = Federal_Reserve
impact = interest_rate_increase
timestamp = 2026-03-01
source = news
```

### 주요 기능

- 엔티티 추출
- 이벤트 유형 분류
- 이벤트 파라미터 추출
- 이벤트 저장

---

# 5.3 자산 영향 모델 (Asset Impact Model)

이벤트가 금융 자산에 미치는 영향을 분석한다.

### 영향 분석 예시

```
Event: interest_rate_increase

Impact:
bond → down
growth_stock → down
usd → up
gold → down
```

### 모델 구성 요소

- 자산 관계 모델
- 거시경제 영향 모델
- 산업 영향 모델
- 국가 영향 모델

### 주요 기능

- 이벤트 기반 영향 계산
- 자산 간 관계 분석
- 영향 강도 계산

---

# 5.4 시그널 생성 (Signal Generation)

이벤트 분석과 자산 영향 모델을 기반으로 투자 시그널을 생성한다.

### 시그널 구조

```
Signal
asset
direction
confidence
reason
timestamp
event_reference
```

### 시그널 예시

```
asset = gold
direction = buy
confidence = 0.72
reason = geopolitical_risk
timestamp = 2026-03-02
```

### 주요 기능

- 이벤트 기반 시그널 생성
- 자산별 시그널 생성
- 시그널 점수 계산
- 시그널 저장

---

# 5.5 포트폴리오 관리 (Portfolio Management)

사용자가 다양한 자산을 통합적으로 관리할 수 있도록 지원한다.

### 관리 기능

- 자산 배분 관리
- 포지션 관리
- 리밸런싱
- 리스크 관리
- 성과 분석

### 데이터 구조

```
Portfolio
Position
Asset
Allocation
Risk
Performance
```

### 주요 기능

- 포트폴리오 생성
- 포지션 추적
- 포트폴리오 성과 분석
- 리밸런싱 실행

---

# 5.6 주문 실행 (Execution)

플랫폼은 브로커 및 거래소 API와 연결하여 주문을 실행한다.

### 연결 대상

- 증권사 API
- 암호화폐 거래소 API

### 주문 유형

```
market_order
limit_order
stop_order
rebalance_order
```

### 주요 기능

- 주문 생성
- 주문 제출
- 주문 상태 추적
- 포지션 업데이트
- 거래 기록 관리
# 6. 온톨로지 모델 (Domain Model)

## 6.1 개요

플랫폼은 투자 관련 데이터를 구조적으로 표현하기 위해 **온톨로지 기반 도메인 모델**을 사용한다.

온톨로지는 금융 시장의 객체와 관계를 정의하며, 다음 분석 과정의 기반이 된다.

``` 
News → Event → Asset Impact → Signal → Order
```

---

# 6.2 핵심 객체 (Core Entities)

플랫폼의 주요 도메인 객체는 다음과 같다.

```
Asset
Company
Country
Currency
Sector
Policy
Event
News
Indicator
Signal
Order
Position
Portfolio
```

---

# 6.3 객체 정의

## Asset

투자 대상이 되는 금융 자산.

속성

```
id
name
symbol
asset_type
currency
exchange
sector
country
```

asset_type 예시

```
stock
crypto
fx
commodity
bond
etf
```

---

## Company

기업 정보를 표현하는 객체.

속성

```
id
name
ticker
sector
country
market_cap
```

---

## Country

국가 단위 경제 및 정책 정보를 표현한다.

속성

```
id
name
currency
region
```

---

## Currency

통화 정보를 표현한다.

속성

```
id
code
country
```

---

## Sector

산업 분류를 표현한다.

속성

```
id
name
industry_group
```

---

## Policy

정부 또는 중앙은행 정책.

속성

```
id
type
country
actor
policy_action
timestamp
```

예

```
interest_rate_change
sanction
trade_policy
regulation
```

---

## Event

뉴스 또는 데이터에서 추출된 시장 이벤트.

속성

```
id
type
country
actor
related_assets
related_sectors
impact_type
timestamp
source
confidence
```

예

```
monetary_policy
geopolitical_event
economic_indicator
corporate_event
regulation
```

---

## News

텍스트 기반 정보 소스.

속성

```
id
title
content
source
timestamp
entities
```

---

## Indicator

경제 지표.

속성

```
id
name
country
value
previous_value
timestamp
```

예

```
CPI
GDP
unemployment_rate
interest_rate
```

---

## Signal

투자 행동을 제안하는 객체.

속성

```
id
asset
direction
confidence
reason
event_reference
timestamp
```

direction

```
buy
sell
reduce
hedge
```

---

## Order

실제 시장 주문.

속성

```
id
asset
order_type
side
quantity
price
status
timestamp
```

order_type

```
market
limit
stop
```

---

## Position

보유 중인 투자 포지션.

속성

```
id
asset
quantity
entry_price
current_price
unrealized_pnl
```

---

## Portfolio

사용자의 전체 자산 구성.

속성

```
id
owner
positions
total_value
risk_metrics
performance
```

---

# 6.4 주요 관계 (Relationships)

온톨로지 객체 간 주요 관계는 다음과 같다.

```
News → mentions → Company
News → mentions → Country
News → mentions → Asset

Policy → affects → Sector
Policy → affects → Asset

Event → derived_from → News
Event → impacts → Asset
Event → impacts → Sector
Event → related_to → Country

Indicator → affects → Asset
Indicator → affects → Currency

Signal → generated_from → Event
Signal → recommends → Order

Portfolio → holds → Position
Position → references → Asset
```

---

# 6.5 데이터 흐름

온톨로지 객체는 다음 흐름으로 연결된다.

```
News
↓
Entity Extraction
↓
Event
↓
Asset Impact
↓
Signal
↓
Order
↓
Position
↓
Portfolio
```
# 7. 액션 (Actions)

## 7.1 개요

액션은 플랫폼이 수행할 수 있는 **투자 관련 실행 작업**을 의미한다.

액션은 다음 객체들을 기반으로 실행된다.

```text
Signal
Portfolio
Position
Market Data
Risk Model
```

액션은 시스템 내부 엔진, 사용자 요청, 또는 자동 전략에 의해 호출될 수 있다.

---

# 7.2 액션 목록 (Action Types)

플랫폼이 지원하는 주요 액션은 다음과 같다.

```text
create_signal
open_position
close_position
rebalance_portfolio
reduce_exposure
hedge_position
generate_report
alert_user
```

---

# 7.3 액션 정의

## create_signal

이벤트 분석과 자산 영향 분석을 기반으로 투자 시그널을 생성한다.

입력

```text
event
asset
impact_score
```

출력

```text
Signal
```

---

## open_position

지정된 자산에 새로운 투자 포지션을 생성한다.

입력

```text
asset
direction
quantity
order_type
price
```

결과

```text
Order 생성
Position 생성
```

---

## close_position

현재 보유 중인 포지션을 청산한다.

입력

```text
position_id
order_type
price
```

결과

```text
Order 생성
Position 종료
```

---

## rebalance_portfolio

포트폴리오의 자산 비중을 목표 비율에 맞게 조정한다.

입력

```text
portfolio_id
target_allocation
```

작업

```text
자산 비중 계산
필요 주문 생성
```

---

## reduce_exposure

특정 자산 또는 포트폴리오의 리스크 노출을 감소시킨다.

입력

```text
asset
risk_level
portfolio_id
```

결과

```text
포지션 축소
```

---

## hedge_position

특정 포지션의 리스크를 줄이기 위해 헤지 포지션을 생성한다.

입력

```text
position_id
hedge_asset
hedge_ratio
```

결과

```text
헤지 주문 생성
```

---

## generate_report

투자 활동 및 포트폴리오 상태에 대한 보고서를 생성한다.

출력

```text
portfolio_performance
risk_metrics
signal_history
trade_history
```

---

## alert_user

시장 이벤트, 시그널 생성, 포트폴리오 변화 등에 대해 사용자에게 알림을 전송한다.

입력

```text
event
signal
portfolio_change
risk_alert
```

출력

```text
notification
```
# 8. 시스템 아키텍처 (System Architecture)

## 8.1 아키텍처 개요

플랫폼은 데이터 수집부터 투자 실행까지의 전체 파이프라인을 구성하는 모듈형 아키텍처로 설계된다.

```text
Data Ingestion
↓
Entity Extraction
↓
Event Detection
↓
Ontology Layer
↓
Asset Impact Engine
↓
Signal Engine
↓
Execution Engine
↓
Portfolio Manager
↓
User Interface
```

---

## 8.1.1 프로젝트 구조 및 기술 스택

프로젝트는 **모노레포 3-tier 구조**로 구성하며, 백엔드·프론트엔드·비동기 워커·DB를 명확히 분리한다.

### 레포지토리 구조

```text
multi-asset-invest/
├── apps/
│   ├── api/          # REST API 서버 — 인증, 이벤트/시그널/포트폴리오/주문 CRUD, 브로커 연동, 알림
│   ├── web/          # 대시보드용 웹 프론트엔드 (이벤트·시그널·포트폴리오·주문 초안 확인/제출 UI)
│   └── worker/       # 크롤러 + 이벤트 추출 + 자산 영향·시그널 생성 파이프라인 (비동기 작업)
├── packages/         # (선택) 공용 타입·유틸
├── infra/            # (선택) DB·캐시·스케줄러 등 인프라 정의
├── docs/
├── specs/
└── ...
```

- **api**: 사용자 요청 처리, 포트폴리오·주문·시그널·이벤트 조회/생성, 브로커·거래소 연동 호출, 인앱 알림 제공.
- **web**: 대시보드, 이벤트·시그널·포트폴리오·주문 초안 확인·제출 UI. API만 호출.
- **worker**: 크롤링(robots.txt 준수), 수집 → 이벤트 추출 → 자산 영향 → 시그널 생성. Redis 큐로 API와 분리하여 비동기 처리. API는 필요 시 큐에 작업을 넣어 크롤·이벤트 추출 등을 수동 트리거할 수 있다.
- **DB**: api·worker가 공통 접근. 주 스토어는 PostgreSQL. **Redis**는 캐시(대시보드·조회 응답 등)와 메시지 큐(크롤·이벤트 추출·시그널 생성 작업) 용도로 사용한다.

### 기술 스택

| 영역 | 선택 |
|------|------|
| 백엔드(api, worker) | **Python** |
| 프론트엔드(web) | **Vue** (웹 기반) |
| DB | **PostgreSQL** (주 스토어) |
| 캐시·큐 | **Redis** (캐시, 메시지 큐 — worker 작업·대시보드 등) |

---

# 8.2 주요 시스템 구성 요소

## Data Ingestion Layer

외부 데이터 소스를 수집하고 저장하는 계층.

수집 대상

```text
news
blogs
policy announcements
political statements
economic indicators
market data
financial reports
```

주요 기능

```text
data source connection
data collection
data normalization
metadata generation
data storage
```

---

## Entity Extraction Layer

텍스트 데이터에서 주요 엔티티를 추출한다.

추출 대상

```text
company
country
currency
sector
asset
policy
economic_indicator
```

주요 기능

```text
named entity recognition
entity linking
entity normalization
```

---

## Event Detection Layer

뉴스 및 데이터에서 시장 이벤트를 탐지하고 구조화한다.

입력

```text
news
policy announcements
economic reports
```

출력

```text
Event
```

예

```text
type = monetary_policy
country = US
impact = interest_rate_increase
```

---

## Ontology Layer

금융 시장의 객체와 관계를 정의하는 도메인 모델 계층.

관리 객체

```text
Asset
Company
Country
Currency
Sector
Policy
Event
News
Indicator
Signal
Order
Position
Portfolio
```

주요 기능

```text
entity relationship management
knowledge graph representation
domain data storage
```

---

## Asset Impact Engine

이벤트가 자산에 미치는 영향을 계산한다.

입력

```text
Event
Asset Relationships
Market Data
```

출력

```text
Asset Impact
```

주요 기능

```text
event impact calculation
asset dependency analysis
impact strength estimation
```

---

## Signal Engine

자산 영향 분석을 기반으로 투자 시그널을 생성한다.

입력

```text
Event
Asset Impact
Market Data
Portfolio State
```

출력

```text
Signal
```

주요 기능

```text
signal generation
confidence scoring
signal prioritization
```

---

## Execution Engine

투자 시그널을 주문으로 변환하고 거래를 실행한다.

입력

```text
Signal
Portfolio State
Risk Rules
```

출력

```text
Order
Position Update
```

주요 기능

```text
order creation
order submission
order tracking
position update
```

---

## Portfolio Manager

사용자의 포트폴리오를 관리한다.

관리 객체

```text
Portfolio
Position
Asset Allocation
Risk Metrics
Performance
```

주요 기능

```text
portfolio tracking
risk management
rebalancing
performance analysis
```

---

## User Interface

사용자가 시스템과 상호작용하는 인터페이스.

주요 기능

```text
dashboard
portfolio view
signal monitoring
event visualization
order execution
reporting
```

---

# 8.3 시스템 데이터 흐름

플랫폼의 주요 데이터 흐름은 다음과 같다.

```text
External Data
↓
Data Ingestion
↓
Entity Extraction
↓
Event Detection
↓
Ontology Storage
↓
Asset Impact Analysis
↓
Signal Generation
↓
Portfolio Decision
↓
Order Execution
↓
Position Update
↓
User Interface
```
# 9. 성공 지표 (Success Metrics)

## 9.1 투자 성과 지표

플랫폼에서 생성된 시그널과 전략의 투자 성과를 평가한다.

주요 지표

```text
return
sharpe_ratio
max_drawdown
win_rate
profit_factor
```

설명

- **Return**: 전략 또는 포트폴리오의 총 수익률  
- **Sharpe Ratio**: 위험 대비 수익률  
- **Max Drawdown**: 최대 손실 폭  
- **Win Rate**: 수익 거래 비율  
- **Profit Factor**: 총 수익 대비 총 손실 비율

---

# 9.2 시그널 품질 지표

생성된 투자 시그널의 품질을 평가한다.

주요 지표

```text
signal_accuracy
signal_return
signal_hit_rate
signal_latency
```

설명

- **Signal Accuracy**: 시그널 방향 예측 정확도  
- **Signal Return**: 시그널 기반 거래 수익률  
- **Signal Hit Rate**: 목표 가격 도달 비율  
- **Signal Latency**: 이벤트 발생 이후 시그널 생성까지의 시간

---

# 9.3 이벤트 분석 정확도

이벤트 추출 및 분석 시스템의 정확도를 평가한다.

주요 지표

```text
event_detection_accuracy
entity_extraction_accuracy
event_classification_accuracy
```

설명

- **Event Detection Accuracy**: 뉴스에서 이벤트를 올바르게 추출한 비율  
- **Entity Extraction Accuracy**: 기업, 국가, 자산 등의 엔티티 인식 정확도  
- **Event Classification Accuracy**: 이벤트 유형 분류 정확도

---

# 9.4 사용자 지표

플랫폼 사용성과 사용자 유지율을 평가한다.

주요 지표

```text
daily_active_users
monthly_active_users
user_retention_rate
strategy_usage_rate
```

설명

- **Daily Active Users (DAU)**: 일일 활성 사용자 수  
- **Monthly Active Users (MAU)**: 월간 활성 사용자 수  
- **User Retention Rate**: 일정 기간 후 사용자 유지율  
- **Strategy Usage Rate**: 전략 기능 사용 비율

---

# 9.5 시스템 성능 지표

플랫폼의 안정성과 처리 성능을 평가한다.

주요 지표

```text
data_ingestion_latency
event_processing_latency
signal_generation_latency
system_uptime
```

설명

- **Data Ingestion Latency**: 데이터 수집 지연 시간  
- **Event Processing Latency**: 이벤트 분석 처리 시간  
- **Signal Generation Latency**: 시그널 생성 시간  
- **System Uptime**: 시스템 가동 시간 비율

# 10. 향후 확장 (Future)

## 10.1 AI 투자 에이전트

플랫폼의 이벤트 분석, 자산 영향 모델, 시그널 생성 기능을 활용하여 **자동화된 투자 에이전트**를 구축한다.

가능 기능

```text
event monitoring
signal evaluation
portfolio decision
risk management
automated execution
```

AI 에이전트는 다음 데이터를 기반으로 투자 결정을 수행한다.

```text
Event
Asset Impact
Signal
Portfolio State
Market Data
```

---

# 10.2 자동 포트폴리오 관리

포트폴리오 관리 기능을 확장하여 **자동 자산 배분 및 리스크 관리 시스템**을 구축한다.

가능 기능

```text
dynamic asset allocation
risk-based rebalancing
volatility control
drawdown protection
```

포트폴리오 관리 시스템은 다음 데이터를 활용한다.

```text
market data
event signals
risk metrics
portfolio state
```

---

# 10.3 전략 마켓플레이스

사용자가 투자 전략을 생성하고 공유할 수 있는 전략 플랫폼을 구축한다.

가능 기능

```text
strategy creation
strategy sharing
strategy ranking
strategy subscription
strategy performance tracking
```

전략은 다음 요소를 기반으로 정의된다.

```text
event rules
signal rules
risk rules
portfolio rules
execution rules
```

---

# 10.4 멀티 사용자 플랫폼

플랫폼을 확장하여 여러 사용자가 동시에 사용할 수 있는 **멀티 사용자 투자 플랫폼**을 구축한다.

가능 기능

```text
multi-user accounts
portfolio separation
strategy sharing
team collaboration
permission management
```

---

# 10.5 데이터 확장

데이터 범위를 확장하여 더 다양한 분석을 지원한다.

확장 데이터

```tex
social media sentiment
alternative data
satellite data
supply chain data
on-chain crypto data
```

---

# 10.6 분석 기능 확장

이벤트 기반 분석을 확장하여 다양한 시장 분석 기능을 제공한다.

확장 기능

```text
macro scenario simulation
event impact simulation
cross-asset correlation analysis
risk scenario analysis
```