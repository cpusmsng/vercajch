"""
API Test Script for Vercajch

Run with: pytest tests/test_api.py -v
Or run specific tests: pytest tests/test_api.py -v -k "test_auth"

Prerequisites:
1. Run seed script first: python -m app.db.seed
2. API must be running on localhost:8000 (or configure TEST_API_URL)
"""
import os
import pytest
import httpx
from typing import Optional

# Configuration
TEST_API_URL = os.getenv("TEST_API_URL", "http://localhost:8000/api")

# Test users from seed data
TEST_USERS = {
    "admin": {"email": "admin@spp-d.sk", "password": "admin123"},
    "manager": {"email": "manager@spp-d.sk", "password": "manager123"},
    "leader": {"email": "leader@spp-d.sk", "password": "leader123"},
    "worker": {"email": "worker1@spp-d.sk", "password": "worker123"},
}


class TokenStore:
    """Store tokens for different users"""
    tokens: dict = {}


@pytest.fixture(scope="module")
def client():
    """HTTP client for API calls"""
    return httpx.Client(base_url=TEST_API_URL, timeout=30.0)


def get_auth_headers(role: str) -> dict:
    """Get authorization headers for a specific role"""
    token = TokenStore.tokens.get(role)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ============= Authentication Tests =============

class TestAuth:
    """Authentication endpoint tests"""

    def test_login_admin(self, client):
        """Test admin login"""
        response = client.post(
            "/auth/login",
            json={
                "email": TEST_USERS["admin"]["email"],
                "password": TEST_USERS["admin"]["password"],
            },
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        TokenStore.tokens["admin"] = data["access_token"]

    def test_login_manager(self, client):
        """Test manager login"""
        response = client.post(
            "/auth/login",
            json={
                "email": TEST_USERS["manager"]["email"],
                "password": TEST_USERS["manager"]["password"],
            },
        )
        assert response.status_code == 200
        TokenStore.tokens["manager"] = response.json()["access_token"]

    def test_login_leader(self, client):
        """Test leader login"""
        response = client.post(
            "/auth/login",
            json={
                "email": TEST_USERS["leader"]["email"],
                "password": TEST_USERS["leader"]["password"],
            },
        )
        assert response.status_code == 200
        TokenStore.tokens["leader"] = response.json()["access_token"]

    def test_login_worker(self, client):
        """Test worker login"""
        response = client.post(
            "/auth/login",
            json={
                "email": TEST_USERS["worker"]["email"],
                "password": TEST_USERS["worker"]["password"],
            },
        )
        assert response.status_code == 200
        TokenStore.tokens["worker"] = response.json()["access_token"]

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            json={"email": "invalid@email.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_get_current_user(self, client):
        """Test getting current user info"""
        response = client.get("/auth/me", headers=get_auth_headers("admin"))
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USERS["admin"]["email"]


# ============= Users Tests =============

class TestUsers:
    """User management endpoint tests"""

    def test_list_users(self, client):
        """Test listing users (requires manager role)"""
        # Worker should not be able to list users
        response = client.get("/users", headers=get_auth_headers("worker"))
        assert response.status_code in [403, 401]

        # Manager should be able to list users
        response = client.get("/users", headers=get_auth_headers("manager"))
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    def test_get_departments(self, client):
        """Test getting departments list"""
        response = client.get("/users/departments", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "name" in data[0]

    def test_get_roles(self, client):
        """Test getting roles list"""
        response = client.get("/users/roles", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "code" in data[0]


# ============= Equipment Tests =============

class TestEquipment:
    """Equipment management endpoint tests"""

    def test_list_equipment(self, client):
        """Test listing equipment"""
        response = client.get("/equipment", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_new_equipment_defaults(self, client):
        """Test getting defaults for new equipment"""
        response = client.get("/equipment/new", headers=get_auth_headers("manager"))
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is None
        assert "status" in data

    def test_get_new_equipment_history(self, client):
        """Test getting history for new equipment (should be empty)"""
        response = client.get("/equipment/new/history", headers=get_auth_headers("manager"))
        assert response.status_code == 200
        data = response.json()
        assert data["checkouts"] == []
        assert data["maintenance"] == []


# ============= Categories Tests =============

class TestCategories:
    """Category management endpoint tests"""

    def test_list_categories(self, client):
        """Test listing categories"""
        response = client.get("/categories", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_category_tree(self, client):
        """Test getting category tree"""
        response = client.get("/categories/tree", headers=get_auth_headers("worker"))
        assert response.status_code == 200


# ============= Locations Tests =============

class TestLocations:
    """Location management endpoint tests"""

    def test_list_locations(self, client):
        """Test listing locations"""
        response = client.get("/locations", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ============= Tags Tests =============

class TestTags:
    """Tag/QR code endpoint tests"""

    def test_tag_lookup_not_found(self, client):
        """Test tag lookup for non-existent tag"""
        response = client.get(
            "/tags/lookup",
            params={"value": "nonexistent-tag-value"},
            headers=get_auth_headers("worker"),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["found"] == False
        assert "tag_type" in data  # Should have tag_type even when not found


# ============= Calibrations Tests =============

class TestCalibrations:
    """Calibration endpoint tests"""

    def test_get_calibrations_for_new_equipment(self, client):
        """Test getting calibrations for new equipment (should be empty)"""
        response = client.get(
            "/calibrations/equipment/new", headers=get_auth_headers("worker")
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_calibration_dashboard(self, client):
        """Test calibration dashboard"""
        response = client.get(
            "/calibrations/dashboard", headers=get_auth_headers("worker")
        )
        assert response.status_code == 200


# ============= Maintenance Tests =============

class TestMaintenance:
    """Maintenance endpoint tests"""

    def test_get_maintenance_stats(self, client):
        """Test getting maintenance statistics"""
        response = client.get("/maintenance/stats", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert "completed" in data
        assert "overdue" in data

    def test_list_maintenance(self, client):
        """Test listing maintenance records"""
        response = client.get("/maintenance", headers=get_auth_headers("worker"))
        assert response.status_code == 200


# ============= Transfers Tests =============

class TestTransfers:
    """Transfer endpoint tests"""

    def test_get_sent_requests(self, client):
        """Test getting sent transfer requests"""
        response = client.get(
            "/transfers/requests/sent", headers=get_auth_headers("worker")
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_received_requests(self, client):
        """Test getting received transfer requests"""
        response = client.get(
            "/transfers/requests/received", headers=get_auth_headers("worker")
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_pending_approvals_as_leader(self, client):
        """Test getting pending approvals (requires leader role)"""
        response = client.get(
            "/transfers/pending-approval", headers=get_auth_headers("leader")
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_pending_approvals_as_worker_forbidden(self, client):
        """Test that workers cannot access pending approvals"""
        response = client.get(
            "/transfers/pending-approval", headers=get_auth_headers("worker")
        )
        assert response.status_code == 403


# ============= Reports Tests =============

class TestReports:
    """Reports endpoint tests"""

    def test_equipment_summary(self, client):
        """Test equipment summary report"""
        response = client.get(
            "/reports/equipment-summary", headers=get_auth_headers("worker")
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data

    def test_checkout_stats_as_leader(self, client):
        """Test checkout stats (requires leader role)"""
        response = client.get(
            "/reports/checkout-stats", headers=get_auth_headers("leader")
        )
        assert response.status_code == 200

    def test_checkout_stats_as_worker_forbidden(self, client):
        """Test that workers cannot access checkout stats"""
        response = client.get(
            "/reports/checkout-stats", headers=get_auth_headers("worker")
        )
        assert response.status_code == 403


# ============= Settings Tests =============

class TestSettings:
    """Settings endpoint tests"""

    def test_get_settings(self, client):
        """Test getting application settings"""
        response = client.get("/settings", headers=get_auth_headers("worker"))
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "features" in data
        assert "user" in data

    def test_get_public_settings(self, client):
        """Test getting public settings (no auth required)"""
        response = client.get("/settings/public")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data


# ============= Health Check =============

class TestHealth:
    """Health check tests"""

    def test_health_endpoint(self, client):
        """Test health endpoint"""
        # Health is at root, not /api
        health_client = httpx.Client(
            base_url=TEST_API_URL.replace("/api", ""), timeout=10.0
        )
        response = health_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
