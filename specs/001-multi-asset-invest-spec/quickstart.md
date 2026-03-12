# Quickstart: 멀티에셋 투자 인텔리전스 플랫폼

**Branch**: `001-multi-asset-invest-spec`  
**대상**: 로컬 개발 환경에서 api·web·worker·DB 기동 방법(구현 후 사용).

---

## 사전 요구사항

- **uv** (Python 패키지/가상환경): https://docs.astral.sh/uv/ — `curl -LsSf https://astral.sh/uv/install.sh | sh` 또는 `pip install uv`
- Python 3.14+ (uv가 자동 관리 가능)
- Node.js 18+ (Vue·npm/pnpm)
- Docker + docker compose (인프라·배포용 권장)
- 로컬만 쓸 경우: PostgreSQL 14+ 직접 설치 가능

---

## 0. 인프라 기동 (docker-compose)

DB를 Docker로 띄우면 로컬에 PostgreSQL 설치 없이 개발 가능하다.

```bash
# 프로젝트 루트에서
docker compose -f infra/docker-compose.yml up -d

# 연결 문자열 (기본값)
# DATABASE_URL=postgresql://app:app@localhost:5433/multi_asset_invest
```

마이그레이션은 아래 2단계에서 api 쪽 도구로 실행한다. Redis는 캐시·메시지 큐용으로 포함되어 있으며, 연결은 `redis://localhost:6380/0` (기본).

---

## 1. 저장소 및 의존성

```bash
git clone <repo> && cd multi-asset-invest
git checkout 001-multi-asset-invest-spec
```

```bash
# Python (uv): API · Worker
# https://docs.astral.sh/uv/
cd apps/api   && uv sync
cd apps/worker && uv sync

# Web
cd apps/web && pnpm install   # or npm ci
```

---

## 2. 데이터베이스

docker-compose로 DB를 띄운 경우:

```bash
export DATABASE_URL=postgresql://app:app@localhost:5433/multi_asset_invest
cd apps/api && uv run alembic upgrade head   # or 프로젝트에서 채택한 마이그레이션 도구
```

로컬 PostgreSQL을 쓰는 경우: `createdb multi_asset_invest` 후 위와 동일하게 마이그레이션 실행.  
환경 변수 예: `DATABASE_URL=postgresql://user:pass@localhost:5433/multi_asset_invest`

---

## 3. 기동 순서

**터미널 1 – API**

```bash
cd apps/api
export DATABASE_URL=postgresql://...
uv run uvicorn src.main:app --reload --port 8000
```

**터미널 2 – Web**

```bash
cd apps/web
pnpm dev
```

(프록시 또는 API base URL을 `http://localhost:8000` 등으로 설정)

**터미널 3 – Worker**

```bash
cd apps/worker
export DATABASE_URL=postgresql://...
uv run python -m src.main   # or celery/스케줄러 실행 방식
```

---

## 4. 확인

- API: http://localhost:8000/docs (OpenAPI)
- Web: http://localhost:5173 (또는 설정된 포트)
- 대시보드 로그인 후 최근 이벤트·시그널·포트폴리오 요약 노출 여부 확인
- 관리자: 웹 UI에서 수집 소스(크롤 대상 URL·소스 이름·활성 여부)를 등록·수정·비활성화할 수 있으며(FR-002-2), 수동 크롤 트리거 시 워커가 활성 소스 목록을 사용한다.

---

## 5. 인프라·배포 (docker-compose)

- **인프라만**: `docker compose -f infra/docker-compose.yml up -d` 로 PostgreSQL 기동. 개발 시 api/web/worker는 로컬에서 실행(0~3단계).
- **전체 스택**: 추후 `apps/api`, `apps/web`, `apps/worker`용 Dockerfile을 두고, `infra/docker-compose.yml`(또는 `infra/docker-compose.full.yml`)에서 서비스로 포함하면 한 번에 배포·실행 가능.
