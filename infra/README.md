# 인프라

## docker-compose

로컬·배포용 인프라를 Docker Compose로 띄운다.

```bash
# 프로젝트 루트에서
docker compose -f infra/docker-compose.yml up -d
```

- **postgres**: PostgreSQL 16. DB명 `multi_asset_invest`, 사용자/비밀번호 `app`/`app`. 포트 5433.
- **redis**: Redis 7. 캐시(대시보드·조회 응답) 및 메시지 큐(worker 작업) 용도. 포트 6380.

api·web·worker 앱은 구현 후 각각 Dockerfile을 두고, 이 compose에 서비스를 추가하거나 별도 `docker-compose.full.yml`로 전체 스택을 정의할 수 있다.
