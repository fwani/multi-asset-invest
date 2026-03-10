# PRD: 멀티에셋 투자 분석 및 실행 플랫폼

## 1. 제품 개요 (Product Overview)

### 제품 이름 (working title)
예시  
- Atlas  
- MacroGraph  
- SignalOS  
- Investor AI  

(나중에 정해도 됩니다)

### 목표
뉴스, 정책, 시장 데이터를 분석하여 **멀티에셋 투자 의사결정을 지원하는 플랫폼**

지원 자산:

- 주식
- 암호화폐
- 외환
- 금 / 원자재
- 채권

핵심 기능:

- 뉴스 기반 이벤트 분석
- 자산 영향 분석
- 투자 시그널 생성
- 포트폴리오 관리
- 자동/반자동 주문 실행

---

# 2. 문제 정의 (Problem)

현재 투자 환경 문제:

1️⃣ 정보 과부하  

- 뉴스
- 블로그
- 정치 발언
- 정책
- 경제 지표

→ 사람이 모두 해석하기 어려움

2️⃣ 자산 간 연결 이해 어려움

예:

- 금리 상승 → 채권 하락
- 지정학 → 금 상승
- 정책 → 특정 산업 영향

3️⃣ 뉴스 → 투자 행동까지 연결되지 않음

현재 시스템:

```
뉴스 → 사람 해석 → 투자 판단
```

목표 시스템:

```
뉴스 → 이벤트 → 자산 영향 → 시그널 → 주문
```

---

# 3. 제품 목표 (Goals)

### 주요 목표

1️⃣ 멀티에셋 이벤트 분석 플랫폼 구축  

2️⃣ 뉴스/정책 → 자산 영향 자동 분석  

3️⃣ 투자 시그널 생성  

4️⃣ 주문 자동화 가능 구조

---

### 비목표 (Non-goals)

초기 버전에서 하지 않는 것:

- 고빈도 트레이딩
- 완전 자동 투자
- 초저지연 거래
- 브로커 자체 구축

---

# 4. 사용자 (Users)

### Primary user

개인 투자자 / 퀀트 개발자

특징:

- 다양한 자산 투자
- 뉴스 기반 투자
- 전략 테스트 필요

---

### Secondary user

AI Agent / 자동 전략

---

# 5. 핵심 기능 (Core Features)

## 5.1 데이터 수집

데이터 소스:

- 뉴스
- 블로그
- 정책 발표
- 정치 발언
- 경제 지표
- 시장 데이터
- 공시

데이터 유형:

```
text
market data
macro data
policy data
```

---

## 5.2 이벤트 분석

뉴스 → 이벤트 구조화

예:

뉴스

```
"미국 금리 인상 가능성"
```

구조화

```
Event:
type = monetary_policy
country = US
impact = interest_rate_up
```

---

## 5.3 자산 영향 모델

이벤트 → 자산 영향

예

```
금리 상승
→ 채권 하락
→ 성장주 하락
→ 달러 상승
→ 금 하락
```

---

## 5.4 시그널 생성

예

```
Signal:
asset = gold
direction = buy
confidence = 0.72
reason = geopolitical_risk
```

---

## 5.5 포트폴리오 관리

기능

- 자산 배분
- 리밸런싱
- 리스크 관리
- 성과 분석

---

## 5.6 주문 실행

브로커 API 연결

예

- 증권사 API
- crypto exchange API

가능 기능

- 주문 생성
- 포지션 관리
- 자동 리밸런싱

---

# 6. 온톨로지 모델 (Domain Model)

핵심 객체

```
Asset
Company
Country
Currency
Policy
Event
News
Signal
Order
Position
Portfolio
```

관계

```
News -> mentions -> Asset
Policy -> affects -> Sector
Event -> impacts -> Asset
Signal -> recommends -> Order
Portfolio -> holds -> Asset
```

---

# 7. 액션 (Actions)

플랫폼이 실행할 수 있는 작업

```
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

# 8. 시스템 아키텍처

```
Data Ingestion
↓
Entity Extraction
↓
Event Detection
↓
Ontology Layer
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

# 9. 성공 지표 (Success Metrics)

예

- 시그널 정확도
- 전략 Sharpe ratio
- 사용자 유지율
- 포트폴리오 성과

---

# 10. 향후 확장 (Future)

- AI 투자 에이전트
- 자동 포트폴리오 관리
- 전략 마켓플레이스
- 멀티 사용자 플랫폼

---

# 중요한 조언

PRD에서 **가장 중요한 부분은 사실 이것입니다**

```
Event → Asset Impact → Signal
```

이게 이 제품의 **핵심 엔진**입니다.
