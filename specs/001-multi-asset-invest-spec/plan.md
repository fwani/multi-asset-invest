# Implementation Plan: 멀티에셋 투자 인텔리전스 플랫폼

**Branch**: `001-multi-asset-invest-spec` | **Date**: 2026-03-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-asset-invest-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

뉴스·정책·경제 지표를 수집·이벤트 추출 → 자산 영향 → 투자 시그널 생성 → 포트폴리오·주문 실행까지 연결하는 멀티에셋 플랫폼. 모노레포 3-tier(API·웹·워커)로 구현하며, PostgreSQL 단일 스토어, Python 백엔드·워커, Vue 대시보드로 설계한다.

**수집 소스 설정 (FR-002-2)**: 관리자는 웹 UI에서 데이터 수집 소스(크롤 대상 URL·소스 이름·활성 여부 등)를 등록·조회·수정·비활성화할 수 있다. 설정은 API가 PostgreSQL의 crawl_sources(또는 동일 목적 테이블)에 저장하고, 워커의 크롤 파이프라인은 활성 소스 목록을 DB 또는 API에서 조회하여 사용한다. 변경 시 이후 수집 작업부터 적용된다.

## Technical Context

**Language/Version**: Python 3.14+ (api, worker), Vue 3 (web)  
**Primary Dependencies**: FastAPI(api), Vue 3 + Pinia/Vue Router(web), 비동기 워커(크롤러·이벤트·시그널 파이프라인)  
**Storage**: PostgreSQL (주 스토어). Redis (캐시·메시지 큐).  
**Testing**: pytest (api, worker), Vitest/Vue Test Utils (web), 통합·계약 테스트  
**Target Platform**: Linux 서버(api, worker), 브라우저(web)  
**Project Type**: 모노레포 웹 애플리케이션(api + frontend + worker)  
**Performance Goals**: 대시보드 초기 로드 3초 이내, 뉴스 수집 후 이벤트 목록 반영 5분 이내  
**Constraints**: 일일 뉴스 ~1만 건·이벤트 ~5천 건, 동시 사용자 ~100명 수준에서 정상 동작  
**Scale/Scope**: apps/api, apps/web, apps/worker, packages(선택), infra(선택)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`가 프로젝트별로 커스터마이즈되지 않은 템플릿 상태이므로, 별도 게이트를 적용하지 않고 스펙 기반 설계를 진행한다. 추후 헌법이 확정되면 이 플랜에 대한 준수 여부를 재검토한다.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/
├── api/                    # REST API (Python). 인증, 이벤트/시그널/포트폴리오/주문 CRUD, 브로커 연동, 알림
│   ├── src/ or app/
│   │   ├── models/
│   │   ├── services/
│   │   ├── api/ or routes/
│   │   └── ...
│   └── tests/
├── web/                    # 대시보드 (Vue). 이벤트·시그널·포트폴리오·주문 초안 UI, API만 호출
│   ├── src/
│   │   ├── components/
│   │   ├── pages/ or views/
│   │   ├── services/
│   │   └── ...
│   └── tests/
└── worker/                 # 크롤러 + 이벤트 추출 + 자산 영향·시그널 파이프라인 (Python, 비동기)
    ├── src/ or app/
    │   ├── crawlers/
    │   ├── pipelines/ or jobs/
    │   └── ...
    └── tests/

packages/                   # (선택) 공용 타입·유틸
infra/                      # docker-compose(PostgreSQL 등), 배포용 인프라 정의
│   └── docker-compose.yml  # DB·캐시 등. 추후 api/web/worker 이미지 추가 가능
```

**Structure Decision**: 스펙의 "모노레포 3-tier"에 따라 apps/api, apps/web, apps/worker로 분리. api·worker는 PostgreSQL 공통 접근, web은 API만 호출. 수집 소스 설정(FR-002-2)은 api에서 CRUD·저장, web 관리자 화면에서 UI 제공, worker는 활성 소스 목록을 DB에서 조회하여 크롤 시작점으로 사용한다.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

현재 Constitution이 템플릿 상태이므로 위반 항목 없음. 비워둠.
