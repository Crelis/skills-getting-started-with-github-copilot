"""Tests for GET /activities endpoint."""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """Test that GET /activities returns the list of all activities."""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Verify all activities are returned
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Music Band" in data
        assert "Debate Team" in data
        assert "Science Club" in data

    def test_get_activities_structure(self, client: TestClient):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
            assert isinstance(activity["max_participants"], int)

    def test_get_activities_returns_participants(self, client: TestClient):
        """Test that activities return their current participants."""
        response = client.get("/activities")
        data = response.json()

        # Verify Chess Club has initial participants
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_response_format(self, client: TestClient):
        """Test that the response is properly formatted JSON."""
        response = client.get("/activities")

        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_root_redirect(self, client: TestClient):
        """Test that GET / redirects to the static index.html."""
        # Create a client that doesn't follow redirects
        from fastapi.testclient import TestClient
        from src.app import app
        no_redirect_client = TestClient(app, follow_redirects=False)

        response = no_redirect_client.get("/")

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"