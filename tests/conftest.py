"""Pytest configuration and fixtures for the test suite."""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before and after each test.

    This ensures test isolation by preserving the original state and
    restoring it after each test, preventing test interdependence.
    """
    # Save original state
    original_activities = copy.deepcopy(activities)

    yield

    # Restore original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Provide a TestClient instance for making requests to the app."""
    return TestClient(app)