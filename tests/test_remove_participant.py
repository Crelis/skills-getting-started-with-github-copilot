"""Tests for DELETE /activities/{activity_name}/participants endpoint."""

import pytest
from fastapi.testclient import TestClient
from src.app import activities


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client: TestClient):
        """Test successful removal of a participant from an activity."""
        email = "michael@mergington.edu"

        # Verify participant exists before deletion
        assert email in activities["Chess Club"]["participants"]

        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

        # Verify participant was actually removed
        assert email not in activities["Chess Club"]["participants"]

    def test_remove_multiple_participants(self, client: TestClient):
        """Test removing multiple different participants."""
        activity = "Tennis Club"
        email1 = "jessica@mergington.edu"
        email2 = "ryan@mergington.edu"

        response1 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email1}
        )
        response2 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email2}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        assert email1 not in activities[activity]["participants"]
        assert email2 not in activities[activity]["participants"]

    def test_remove_nonexistent_activity_returns_404(self, client: TestClient):
        """Test that removing from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/participants",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client: TestClient):
        """Test that removing non-existent participant returns 404."""
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "nonexistent@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_remove_participant_then_readd(self, client: TestClient):
        """Test that a removed participant can be added back."""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Remove
        response1 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email not in activities[activity]["participants"]

        # Re-add
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        assert email in activities[activity]["participants"]

    def test_remove_from_activity_with_many_participants(self, client: TestClient):
        """Test removing from activity that has multiple participants."""
        activity = "Gym Class"
        email_to_remove = "john@mergington.edu"
        other_emails = ["olivia@mergington.edu"]

        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email_to_remove}
        )

        assert response.status_code == 200
        assert email_to_remove not in activities[activity]["participants"]

        # Other participants should remain
        for email in other_emails:
            assert email in activities[activity]["participants"]

    def test_remove_participant_case_sensitivity(self, client: TestClient):
        """Test that participant removal is case-sensitive."""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Try to remove with different case
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": "Michael@Mergington.edu"}  # Different case
        )

        # Should fail because emails are case-sensitive
        assert response.status_code == 404
        # Original participant should still be there
        assert email in activities[activity]["participants"]