"""Tests for NIO's wrapped OAuth response."""

import unittest

from _load import load_module

oauth = load_module("oauth")


class TestNioOAuthEnvelope(unittest.TestCase):
    def test_unwrap_token_response(self) -> None:
        token = {
            "access_token": "access",
            "refresh_token": "refresh",
            "expires_in": 7200,
            "token_type": "Bearer",
            "scope": "vehicle:energy:read",
        }
        self.assertEqual(
            oauth.unwrap_token_response(
                {"request_id": "redacted", "result_code": "success", "data": token}
            ),
            token,
        )

    def test_invalid_payloads_are_rejected(self) -> None:
        payloads = (
            {"result_code": "invalid_grant", "data": {}},
            {"result_code": "success", "data": None},
            {"result_code": "success", "data": {"access_token": "access"}},
        )
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(
                oauth.InvalidTokenResponseError
            ):
                oauth.unwrap_token_response(payload)
