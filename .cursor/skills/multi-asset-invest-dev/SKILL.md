---
name: multi-asset-invest-dev
description: Provides project context, structure, and commands for the Multi-Asset Investment Intelligence Platform (api, worker, web monorepo). Use when implementing features, running tests, adding API/worker/web code, or when the user asks about project setup, specs, or PRD.
---

# multi-asset-invest 개발 컨텍스트

## 프로젝트 개요

- **목적**: 뉴스·정책·거시 데이터를 수집해 이벤트 추출 → 자산 영향 → 시그널 → 포트폴리오·주문 실행까지 지원하는 멀티에셋 투자 인텔리전스 플랫폼.
- **구성**: 모노레포 3앱 — **api**(FastAPI), **worker**(Python 비동기 크롤·파이프라인), **web**(Vue 3 + Pinia/Vue Router).
- **스택**: PostgreSQL(주 스토어), Redis(캐시·메시지 큐), Python 3.11+(api·worker), Vue 3(web). 패키지: api/worker는 **uv**, web은 **pnpm**.

## 디렉터리 구조

```text
apps/
  api/          # FastAPI, Alembic 마이그레이션
    src/
    tests/
  worker/       # 크롤러·이벤트·시그널 파이프라인
    src/
    data/       # 로컬/스텁 데이터
  web/          # Vue 3 프론트
docs/           # PRD 등 제품 문서
specs/
  001-multi-asset-invest-spec/   # 피처 스펙·태스크·퀵스타트
    spec.md
    tasks.md
    quickstart.md
infra/          # docker-compose 등
.cursor/
  rules/        # 개발 가이드라인 (alwaysApply)
  commands/     # speckit.* (스펙 기반 구현·태스크·체크리스트 등)
  skills/       # 본 스킬 포함 프로젝트 스킬
```

## 핵심 문서

| 용도 | 경로 |
|------|------|
| 제품 요구사항·시나리오 | `docs/prd.md` |
| 피처 스펙·FR·엔티티·성공 기준 | `specs/001-multi-asset-invest-spec/spec.md` |
| 구현 태스크 목록 | `specs/001-multi-asset-invest-spec/tasks.md` |
| 로컬 기동·의존성·DB·기동 순서 | `specs/001-multi-asset-invest-spec/quickstart.md` |

구현·리뷰 시 해당 FR/User Story/엔티티를 스펙·PRD에서 참조해 일치시킨다.

## 명령어 (앱별)

**공통·인프라**

- DB 기동: `docker compose -f infra/docker-compose.yml up -d`
- DB URL 예: `postgresql://app:app@localhost:5433/multi_asset_invest`, Redis: `redis://localhost:6380/0`

**API** (`apps/api`)

- 의존성: `uv sync`
- 마이그레이션: `uv run alembic upgrade head` (필요 시 `DATABASE_URL` 설정)
- 서버: `uv run uvicorn src.main:app --reload --port 8000`
- 린트: `ruff check .`
- 테스트: `pytest` (프로젝트 규칙: `cd src` 후 `pytest` 또는 앱 루트에서 실행 방식 확인)

**Worker** (`apps/worker`)

- 의존성: `uv sync`
- 실행: `uv run python -m src.main`
- 린트: `ruff check .`
- 테스트: `pytest`

**Web** (`apps/web`)

- 의존성: `pnpm install` (또는 `npm ci`)
- 개발 서버: `pnpm dev`
- 테스트: Vitest + Vue Test Utils (스펙 기준)

## 코드·스펙 일치

- **모델·API**: api의 모델·서비스·엔드포인트는 스펙의 Key Entities·FR과 맞춘다. worker가 api DB/API를 사용할 경우 스키마·계약을 공유한다.
- **크롤·파이프라인**: worker의 크롤 소스·파이프라인은 FR-001, FR-002, FR-002-2(수집 소스 관리)를 준수한다. robots.txt·요청 빈도 등 로봇 정책 준수.
- **스펙 기반 작업**: `.cursor/commands/`의 speckit 명령(speckit.implement, speckit.tasks 등)으로 스펙·태스크·체크리스트를 따라 구현할 수 있다.

## 스킬 적용 시점

- 이 리포지터리에서 기능 구현·버그 수정·테스트·린트 실행 시.
- "프로젝트 구조", "어디서 실행", "스펙/PRD 어디 있나" 질의 시.
- api/worker/web 중 특정 앱만 다룰 때 다른 앱 경로·역할을 참고할 때.
