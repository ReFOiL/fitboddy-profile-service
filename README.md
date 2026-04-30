# profile-service

Сервис клиентских профилей/анкеты. Хранит данные профиля и валидирует доступ через `auth-service` и `tenant-service` (marketplace relation access).

## Stack

- FastAPI + Pydantic
- SQLAlchemy + Alembic
- Poetry
- Postgres (prod) / SQLite (tests)
- HTTP integration: auth-service, tenant-service

## API

- `GET /health`
- `GET /ready`
- `PUT /api/v1/profiles/{user_id}` - upsert профиля
- `GET /api/v1/profiles/{user_id}` - получить профиль

Оба profile endpoint требуют `Authorization: Bearer <access_token>`.
 
### Правила доступа

- `client` может читать/обновлять только свой профиль.
- `trainer` может читать/обновлять профиль клиента только при `active` relation в marketplace.
- `trainer` может работать со своим профилем.

## ENV

- `DATABASE_URL`
- `AUTH_SERVICE_URL` (например `http://auth-service`)
- `TENANT_SERVICE_URL` (например `http://tenant-service`)
- `HTTP_TIMEOUT_SECONDS`

## Local run

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn --app-dir lib presentation.http.main:app --reload --port 8000
```

## Tests

```bash
poetry run pytest tests/unit -q
```
