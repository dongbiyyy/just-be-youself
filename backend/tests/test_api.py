import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # triggers startup -> create_all + initial admin
        yield c


@pytest.fixture(scope="module")
def auth_headers(client):
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login_and_me(client, auth_headers):
    r = client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "admin"
    assert r.json()["role"] == "superadmin"


def test_company_crud_and_search(client, auth_headers):
    payload = {
        "name": "测试母公司A",
        "credit_code": "TESTAAA0001",
        "legal_representative": "张测试",
        "reg_capital": 1000000,
    }
    r = client.post("/api/companies", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    parent_id = r.json()["id"]

    child = {"name": "测试子公司A", "parent_company_id": parent_id}
    r = client.post("/api/companies", json=child, headers=auth_headers)
    assert r.status_code == 201
    child_id = r.json()["id"]

    r = client.get("/api/companies", params={"q": "母公司"}, headers=auth_headers)
    assert r.status_code == 200
    assert any(c["id"] == parent_id for c in r.json())

    r = client.get(f"/api/companies/{parent_id}/tree", headers=auth_headers)
    assert r.status_code == 200
    tree = r.json()
    assert tree["id"] == parent_id
    assert any(ch["id"] == child_id for ch in tree["children"])

    r = client.get("/api/search", params={"q": "TESTAAA"}, headers=auth_headers)
    assert r.status_code == 200
    assert any(h["type"] == "company" and h["id"] == parent_id for h in r.json())


def test_person_position_shareholding(client, auth_headers):
    # Person
    p = {
        "name": "李测试",
        "id_card": "110101199001011234",
        "phone": "13900000001",
    }
    r = client.post("/api/persons", json=p, headers=auth_headers)
    assert r.status_code == 201, r.text
    person_id = r.json()["id"]
    assert r.json()["id_card_last4"] == "1234"

    # Company for position
    r = client.post("/api/companies", json={"name": "任职测试公司A"}, headers=auth_headers)
    company_id = r.json()["id"]

    # Position
    r = client.post(
        "/api/positions",
        json={
            "person_id": person_id,
            "company_id": company_id,
            "position_type": "董事",
            "start_date": "2023-01-01",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text

    # Shareholding
    r = client.post(
        "/api/shareholdings",
        json={
            "company_id": company_id,
            "shareholder_type": "person",
            "shareholder_id": person_id,
            "ratio": 30,
            "amount": 300000,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text

    # Search by id-card last 4
    r = client.get("/api/search", params={"q": "1234"}, headers=auth_headers)
    assert r.status_code == 200
    assert any(h["type"] == "person" and h["id"] == person_id for h in r.json())


def test_dashboard_and_recompute(client, auth_headers):
    r = client.post("/api/dashboard/alerts/recompute", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "new_conflicts" in body and "new_term_expiries" in body

    r = client.get("/api/dashboard/summary", headers=auth_headers)
    assert r.status_code == 200
    summary = r.json()
    assert summary["companies"] >= 1
    assert summary["persons"] >= 1


def test_excel_template_download(client, auth_headers):
    r = client.get("/api/imports/templates/companies", headers=auth_headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(r.content) > 100
