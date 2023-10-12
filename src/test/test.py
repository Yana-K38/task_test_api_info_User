import json

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_all_users():
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)


def test_get_user_by_id():
    user_id = 1
    response = client.get(f"/users/{user_id}/")
    assert response.status_code == 200
    user = response.json()
    assert isinstance(user, dict)


def test_search_users():
    search_query = "Anna"
    response = client.get(f"/users/search_user?search_query={search_query}")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
