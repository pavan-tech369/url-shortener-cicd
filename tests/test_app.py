from unittest.mock import patch
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"URL Shortener" in response.data

@patch("app.db")
def test_shorten_and_redirect(mock_db, client):
    mock_db.set.return_value = True
    res = client.post("/shorten", json={"url": "https://github.com/pavan-tech369"})
    assert res.status_code == 201
    data = res.get_json()
    assert "short_code" in data

    mock_db.get.return_value = "https://github.com/pavan-tech369"
    redirect_res = client.get(f"/{data['short_code']}")
    assert redirect_res.status_code == 302
    assert redirect_res.location == "https://github.com/pavan-tech369"

def test_shorten_missing_url(client):
    res = client.post("/shorten", json={})
    assert res.status_code == 400