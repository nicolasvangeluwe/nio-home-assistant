"""Fixtures for NIO Open Telematics integration tests."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading the custom integration in every HA test."""
    yield
