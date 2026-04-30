from fastapi.testclient import TestClient

from application.use_cases import AccessContext
from presentation.http.main import app

def _client() -> TestClient:
    return TestClient(app)


def test_health() -> None:
    with _client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_ready() -> None:
    with _client() as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}


def _mock_access_context(*, user_id: str, role: str, tenant_id: str = "tenant-1") -> None:
    app.state.profile_handler._access_service.authorize_profile_access = lambda *_args, **_kwargs: AccessContext(
        user_id=user_id,
        role=role,
        tenant_id=tenant_id,
    )


def test_upsert_and_get_profile_for_client_self() -> None:
    with _client() as client:
        _mock_access_context(user_id="client-1", role="client")
        upsert_response = client.put(
            "/api/v1/profiles/client-1",
            headers={"Authorization": "Bearer token"},
            json={
                "full_name": "Client One",
                "city": "Sydney",
                "bio": "Love morning workouts",
                "goal": "weight_loss",
                "experience_level": "beginner",
                "workout_location": "home",
                "equipment": ["dumbbells", "resistance_bands"],
                "limitations": "none",
                "medical_notes": None,
            },
        )
        assert upsert_response.status_code == 200
        assert upsert_response.json()["goal"] == "weight_loss"

        get_response = client.get(
            "/api/v1/profiles/client-1",
            headers={"Authorization": "Bearer token"},
        )
        assert get_response.status_code == 200
        body = get_response.json()
        assert body["user_id"] == "client-1"
        assert body["full_name"] == "Client One"
        assert body["equipment"] == ["dumbbells", "resistance_bands"]


def test_client_cannot_edit_other_user_profile() -> None:
    with _client() as client:
        _mock_access_context(user_id="client-1", role="client")
        response = client.put(
            "/api/v1/profiles/client-2",
            headers={"Authorization": "Bearer token"},
            json={
                "full_name": "Client Two",
                "city": None,
                "bio": None,
                "goal": "muscle_gain",
                "experience_level": "intermediate",
                "workout_location": "gym",
                "equipment": [],
                "limitations": None,
                "medical_notes": None,
            },
        )
        assert response.status_code == 403


def test_client_profile_requires_questionnaire_fields() -> None:
    with _client() as client:
        _mock_access_context(user_id="client-1", role="client")
        response = client.put(
            "/api/v1/profiles/client-1",
            headers={"Authorization": "Bearer token"},
            json={
                "full_name": "Client One",
                "city": "Sydney",
                "bio": "Bio",
                "goal": None,
                "experience_level": None,
                "workout_location": None,
                "equipment": [],
                "limitations": None,
                "medical_notes": None,
            },
        )
        assert response.status_code == 400
        assert "goal is required" in response.json()["detail"]


def test_trainer_can_edit_client_profile() -> None:
    with _client() as client:
        _mock_access_context(user_id="trainer-1", role="trainer")
        response = client.put(
            "/api/v1/profiles/client-3",
            headers={"Authorization": "Bearer token"},
            json={
                "full_name": "Client Three",
                "city": "Melbourne",
                "bio": "Trainer updated profile",
                "goal": "muscle_gain",
                "experience_level": "advanced",
                "workout_location": "gym",
                "equipment": ["barbell"],
                "limitations": "knee",
                "medical_notes": "monitor pain",
            },
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == "client-3"
        assert response.json()["city"] == "Melbourne"


def test_internal_questionnaire_status_endpoint() -> None:
    with _client() as client:
        _mock_access_context(user_id="client-5", role="client")
        upsert_response = client.put(
            "/api/v1/profiles/client-5",
            headers={"Authorization": "Bearer token"},
            json={
                "full_name": "Client Five",
                "city": None,
                "bio": None,
                "goal": "maintenance",
                "experience_level": "beginner",
                "workout_location": "home",
                "equipment": ["none"],
                "limitations": None,
                "medical_notes": None,
            },
        )
        assert upsert_response.status_code == 200

        status_response = client.get("/api/v1/profiles/internal/client-5/questionnaire-status")
        assert status_response.status_code == 200
        assert status_response.json() == {"user_id": "client-5", "is_completed": True}


def test_profile_meta_endpoint() -> None:
    with _client() as client:
        response = client.get("/api/v1/profiles/meta")
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body["goals"], list)
        assert isinstance(body["levels"], list)
        assert isinstance(body["workout_locations"], list)
        assert isinstance(body["equipment"], list)
        assert any(item["value"] == "home" for item in body["workout_locations"])


def test_missing_bearer_token_returns_401() -> None:
    with _client() as client:
        response = client.get("/api/v1/profiles/client-1")
        assert response.status_code == 401


def test_avatar_upload_requires_s3_configuration() -> None:
    with _client() as client:
        _mock_access_context(user_id="client-1", role="client")
        response = client.post(
            "/api/v1/profiles/client-1/avatar",
            headers={"Authorization": "Bearer token"},
            files={"file": ("avatar.jpg", b"fake-bytes", "image/jpeg")},
        )
        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]


def test_avatar_upload_success() -> None:
    class _FakeStorage:
        async def upload_avatar(self, *, user_id: str, filename: str, data: bytes) -> str:
            assert user_id == "client-1"
            assert filename == "avatar.jpg"
            assert data
            return "avatars/client-1/fake.jpg"

    with _client() as client:
        _mock_access_context(user_id="client-1", role="client")
        app.state.profile_handler._runtime._avatar_storage = _FakeStorage()
        response = client.post(
            "/api/v1/profiles/client-1/avatar",
            headers={"Authorization": "Bearer token"},
            files={"file": ("avatar.jpg", b"fake-bytes", "image/jpeg")},
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == "client-1"
        assert response.json()["avatar_url"] == "/api/v1/profiles/media/avatars/client-1/fake.jpg"


def test_trainer_can_save_own_profile_without_questionnaire() -> None:
    with _client() as client:
        _mock_access_context(user_id="trainer-1", role="trainer")
        response = client.put(
            "/api/v1/profiles/trainer-1",
            headers={"Authorization": "Bearer token"},
            json={
                "full_name": "Coach Alex",
                "city": "Brisbane",
                "bio": "Strength trainer",
                "goal": None,
                "experience_level": None,
                "workout_location": None,
                "equipment": [],
                "limitations": None,
                "medical_notes": None,
            },
        )
        assert response.status_code == 200
        assert response.json()["goal"] is None
        assert response.json()["experience_level"] is None


def test_avatar_media_proxy_success() -> None:
    class _FakeStorage:
        async def download_media(self, object_name: str) -> tuple[bytes, str]:
            assert object_name == "avatars/client-1/fake.jpg"
            return b"img-bytes", "image/jpeg"

    with _client() as client:
        app.state.profile_handler._runtime._avatar_storage = _FakeStorage()
        response = client.get("/api/v1/profiles/media/avatars/client-1/fake.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/jpeg")
        assert response.content == b"img-bytes"