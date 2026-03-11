# REST API Contract (요약)

**Base URL**: `/api/v1` (또는 환경별 prefix)  
**인증**: Bearer token / session (구현 시 결정). 미인증 시 401.

---

## 1. 이벤트 (Event)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /events | 목록 조회. 쿼리: type, country, from_date, to_date, limit, offset |
| GET | /events/{id} | 단건 조회. 출처(뉴스)·추출 속성 포함 |
| GET | /events/{id}/impacts | 해당 이벤트의 자산 영향 목록 |

**응답(목록)**: `{ "items": [ Event ], "total": number }`  
**Event**: id, event_type, country_id, actor, impact_type, occurred_at, source_summary, confidence, extracted_at

---

## 2. 자산 영향 (AssetImpact)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /events/{event_id}/impacts | 이벤트별 영향 (위와 동일) |
| GET | /assets/{asset_id}/impacts | 자산별 영향. 쿼리: from_date, to_date, limit |

**AssetImpact**: id, event_id, asset_id, direction, strength, computed_at

---

## 3. 시그널 (Signal)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /signals | 목록. 쿼리: asset_id, direction, from_date, limit, offset |
| GET | /signals/{id} | 단건. 연관 이벤트·자산 영향 근거 포함 |
| POST | /signals/{id}/create-order-draft | 시그널 기반 주문 초안 생성 (Body 없음). 응답: Order draft |

**Signal**: id, asset_id, direction, confidence, reason, generated_at, related_event_ids

---

## 4. 포트폴리오 (Portfolio)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /portfolios | 현재 사용자 포트폴리오 목록 |
| POST | /portfolios | 생성. Body: { name } |
| GET | /portfolios/{id} | 단건. 포지션·총평가·비중·리스크 요약 |
| PATCH | /portfolios/{id} | 수정. name, is_execution_linked(실행 연동 지정) |
| GET | /portfolios/{id}/performance | 기간별 성과. 쿼리: from_date, to_date |
| GET | /portfolios/{id}/rebalance | 목표 배분 대비 현재·리밸런싱 필요량. 목표 배분은 PATCH로 설정 |
| PATCH | /portfolios/{id}/target-allocation | 목표 자산 배분 설정. Body: [ { asset_id, weight_pct } ] |

**Portfolio**: id, user_id, name, is_execution_linked, total_value, positions[], risk_metrics_summary

---

## 5. 주문 (Order)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /orders/drafts | 주문 초안 생성(시그널 없이 직접). Body: asset_id, order_type, side, quantity, price? |
| GET | /orders/drafts/{id} | 초안 단건 (확인·수정용) |
| PUT | /orders/drafts/{id} | 초안 수정 |
| POST | /orders/drafts/{id}/submit | 제출 → 브로커/거래소 전송. Body 없음 |
| GET | /orders | 이력·상태 조회. 쿼리: portfolio_id, status, from_date, limit |
| GET | /orders/{id} | 단건. 상태·체결 정보 |

**Order**: id, portfolio_id, asset_id, order_type, side, quantity, price, status, signal_id?, submitted_at, updated_at  
**Status**: draft | pending | partial_filled | filled | cancelled

---

## 6. 대시보드

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /dashboard | 한 번에 최근 이벤트·시그널·포트폴리오 요약·알림 (SC-001 3초 로드 목표) |

**응답**: `{ events: Event[], signals: Signal[], portfolio_summary: {}, notifications: Notification[] }`

---

## 7. 알림 (Notification)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /notifications | 목록. 쿼리: unread_only, limit |
| PATCH | /notifications/{id}/read | 읽음 처리 |

---

## 8. 보고서 (Report)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /reports | 생성. Body: { from_date, to_date, portfolio_id?, sections[] } |
| GET | /reports/{id} | 조회 또는 내보내기용 URL/스트림 |

---

## 9. 자산·마스터

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /assets | 지원 자산 목록. 쿼리: asset_type, limit (FR-018) |
| GET | /assets/{id} | 단건 |

**Asset**: id, symbol, name, asset_type, currency_id, exchange, sector_id, country_id

---

## 10. 수집 소스 (Crawl Source) — 관리자 (FR-002-2)

관리자는 웹 UI에서 데이터 수집 소스(크롤 대상 URL·소스 이름·활성 여부)를 등록·조회·수정·비활성화한다. 설정은 워커 크롤 파이프라인에서 사용되며, 변경 시 이후 수집 작업부터 적용된다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /crawl-sources | 목록. 쿼리: is_active, limit, offset |
| GET | /crawl-sources/{id} | 단건 |
| POST | /crawl-sources | 등록. Body: { base_url, source_name, is_active? } |
| PATCH | /crawl-sources/{id} | 수정. base_url, source_name, is_active |
| DELETE | /crawl-sources/{id} | 삭제 또는 비활성화(정책에 따라) |

**CrawlSource**: id, base_url, source_name, is_active, created_at, updated_at  
워커는 활성(is_active=true) 소스만 크롤 대상으로 조회한다.

---

에러 응답: `{ "detail": string, "code"?: string }`. 4xx/5xx + detail. 지원 자산 외 주문·실행 시 400 + 명확한 메시지.
