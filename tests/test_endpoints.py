"""Tests for the documented NIO service endpoints."""

import unittest

from _load import load_module

const = load_module("const")


class TestNioEndpoints(unittest.TestCase):
    def test_authorization_uses_portal_host(self) -> None:
        """Browser authorization and API calls use their documented hosts."""
        self.assertEqual(
            f"{const.AUTHORIZE_BASE_URL}{const.AUTHORIZE_PATH}",
            "https://open-eu.nio.com/oauth2/authorize",
        )
        self.assertEqual(const.API_BASE_URL, "https://open-api-eu.nio.com")
