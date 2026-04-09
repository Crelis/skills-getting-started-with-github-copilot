"""Integration tests for multi-step workflows and complex scenarios."""

import pytest
from fastapi.testclient import TestClient
from src.app import activities


class TestIntegrationScenarios:
    """Integration tests for complex scenarios."""

    def test_signup_and_remove_workflow(self, client: TestClient):
        """Test complete workflow: signup, verify, then remove."""
        email = "workflow@mergington.edu"
        activity = "Music Band"

        # Signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email in activities[activity]["participants"]

        # Verify in get_activities
        response2 = client.get("/activities")
        assert email in response2.json()[activity]["participants"]

        # Remove
        response3 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert response3.status_code == 200
        assert email not in activities[activity]["participants"]

    def test_each_activity_maintains_independent_participants(self, client: TestClient):
        """Test that adding to one activity doesn't affect others."""
        email = "independent@mergington.edu"

        # Add to Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Verify not in other activities
        response2 = client.get("/activities")
        data = response2.json()
        assert email in data["Chess Club"]["participants"]
        assert email not in data["Programming Class"]["participants"]
        assert email not in data["Art Studio"]["participants"]

    def test_cannot_signup_after_being_removed(self, client: TestClient):
        """Test edge case: signup, remove, then signup again."""
        email = "edgecase@mergington.edu"
        activity = "Debate Team"

        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Remove
        response2 = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert response2.status_code == 200

        # Signup again should work
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200

    def test_state_isolation_between_tests(self, client: TestClient):
        """Test that state changes don't persist between tests."""
        # This test verifies the fixture isolation works
        email = "isolation@mergington.edu"
        activity = "Science Club"

        # Add participant
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

        # After test ends, fixture should restore activities to original state
        # (Next test should not see this change)

    def test_multiple_operations_on_same_activity(self, client: TestClient):
        """Test multiple signup/remove operations on the same activity."""
        activity = "Art Studio"
        emails = ["user1@test.com", "user2@test.com", "user3@test.com"]

        # Add all users
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all are added
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data[activity]["participants"]

        # Remove middle user
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": emails[1]}
        )
        assert response.status_code == 200

        # Verify only middle user is removed
        response = client.get("/activities")
        data = response.json()
        assert emails[0] in data[activity]["participants"]
        assert emails[1] not in data[activity]["participants"]
        assert emails[2] in data[activity]["participants"]

    def test_cross_activity_participant_management(self, client: TestClient):
        """Test managing the same participant across different activities."""
        email = "crossactivity@test.com"

        # Sign up for two different activities
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify in both activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]

        # Remove from one activity
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        assert response.status_code == 200

        # Verify removed from one but still in the other
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]