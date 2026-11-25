"""Exact JSON text survives browser transport without changing saved decisions."""

import asyncio
import json
import shutil
import subprocess
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.exceptions import Unauthorized

from custom_components.nio_telematics import vehicle_dashboard as dashboard
from custom_components.nio_telematics.car_dashboard.ledger import Ledger
from custom_components.nio_telematics.dashboard_backup import (
    MAX_BYTES,
    TEXT_TRANSFER_BYTES,
    decode_backup_text,
    make_backup,
    parse_backup,
    serialize_backup,
    validate_backup_text_size,
)

VIN = "A" * 17


def decided_history():
    ledger = Ledger({"capacity_kwh": 90, "full_range_km": 557})
    start = 1795590000.0
    for at, odo, soc in (
        (0, 1000, 60.5),
        (600, 1005, 59.5),
        (3600, 1010, 58.5),
        (4200, 1015, 57.5),
        (7200, 1020, 56.5),
    ):
        ledger.ingest(start + at, odo, None, soc_pct=soc)
    gaps = ledger.unaccounted_intervals()
    ledger.resolve_gap(gaps[0]["id"], gaps[0]["fingerprint"], "manual", 2, 0.6, "EUR")
    ledger.resolve_gap(gaps[1]["id"], gaps[1]["fingerprint"], "ignored")
    ledger.data["parked_losses"] = [
        {
            "start": start + 9000,
            "end": start + 9600,
            "kwh": 54.45,
            "end_energy": 0.0,
            "complete": True,
        },
        {
            "start": start + 10000,
            "end": start + 10060,
            "kwh": 0.9,
            "end_energy": 40.0,
            "complete": True,
        },
        {
            "start": start + 11000,
            "end": start + 11060,
            "kwh": 1.0,
            "end_energy": 39.0,
            "complete": True,
        },
    ]
    ledger.data["charges"]["public-test"] = {
        "id": "public-test",
        "kind": "dismissed",
        "category": "other",
        "start": start + 9600,
        "end": start + 9620,
        "odo": 1020.0,
        "kwh": 54.45,
        "estimated_kwh": 54.45,
        "cost_eur": None,
        "price_eur_kwh": None,
        "confirmed": False,
        "currency": "EUR",
    }
    for row in ledger.measurement_error_intervals():
        ledger.set_measurement_error(row["id"], row["fingerprint"], True)
    ledger.data["parked_losses"][1]["complete"] = False
    ledger.data["parked_losses"].pop()
    return ledger.data


class BackupTextTests(unittest.TestCase):
    @unittest.skipUnless(
        shutil.which("node"), "Node is required for real browser JSON semantics"
    )
    def test_browser_text_roundtrip_preserves_ids_fingerprints_and_stale_priorities(
        self,
    ):
        original = decided_history()
        text = serialize_backup(make_backup(VIN, {}, original))
        # The browser may parse for display, but sends the ORIGINAL file text.
        script = (
            "let s='';process.stdin.on('data',x=>s+=x);"
            "process.stdin.on('end',()=>{const file=JSON.parse(s).result;"
            "JSON.parse(file);process.stdout.write(JSON.stringify({backup_json:file}));});"
        )
        request = subprocess.run(
            [shutil.which("node"), "-e", script],
            input=json.dumps({"result": text}),
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        ).stdout
        _, restored = parse_backup(
            decode_backup_text(json.loads(request)["backup_json"]), VIN
        )
        self.assertEqual(
            json.dumps(restored, sort_keys=True), json.dumps(original, sort_keys=True)
        )
        before, after = (
            Ledger({"capacity_kwh": 90, "full_range_km": 557}, data=original),
            Ledger({"capacity_kwh": 90, "full_range_km": 557}, data=restored),
        )
        self.assertEqual(
            before.measurement_error_intervals(), after.measurement_error_intervals()
        )
        self.assertEqual(before.unaccounted_intervals(), after.unaccounted_intervals())
        self.assertEqual(
            [r["state"] for r in after.measurement_error_intervals()],
            ["excluded", "stale"],
        )
        self.assertIsInstance(restored["parked_losses"][0]["end_energy"], float)
        after.data["parked_losses"][0]["kwh"] += 0.1
        self.assertEqual(after.measurement_error_intervals()[0]["state"], "stale")

    def test_text_is_bounded_before_parsing_and_rejects_ambiguous_json(self):
        with patch(
            "custom_components.nio_telematics.dashboard_backup.json.loads",
            side_effect=AssertionError("must not parse"),
        ):
            with self.assertRaisesRegex(ValueError, "8 MB"):
                decode_backup_text("é" * (MAX_BYTES // 2 + 1))
        self.assertEqual(decode_backup_text("{}" + " " * (TEXT_TRANSFER_BYTES - 4)), {})
        for value in ("[]", "null", "0", "{bad}", '{"a":1,"a":2}', '{"a":NaN}'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_backup_text(value)

    def test_quoted_wire_budget_at_and_over_bound_including_escaping_and_utf8(self):
        for char in ("a", '"', "\\", "\n", "é", "😀"):
            with self.subTest(char=repr(char)):
                cost = len(json.dumps(char, ensure_ascii=False).encode("utf-8")) - 2
                count, remainder = divmod(TEXT_TRANSFER_BYTES - 2, cost)
                text = char * count + "a" * remainder
                self.assertEqual(
                    len(json.dumps(text, ensure_ascii=False).encode("utf-8")),
                    TEXT_TRANSFER_BYTES,
                )
                validate_backup_text_size(text)
                with self.assertRaisesRegex(ValueError, "safe text transfer"):
                    validate_backup_text_size(text + "a")
        with patch(
            "custom_components.nio_telematics.dashboard_backup.json.loads",
            side_effect=AssertionError("must not parse"),
        ):
            with self.assertRaisesRegex(ValueError, "safe text transfer"):
                decode_backup_text("{}" + " " * (TEXT_TRANSFER_BYTES - 3))
        with self.assertRaisesRegex(ValueError, "safe text transfer"):
            serialize_backup({"content": '"' * (TEXT_TRANSFER_BYTES // 2)})


class BackupWebsocketTests(unittest.TestCase):
    def setUp(self):
        self.original = decided_history()
        self.entry = SimpleNamespace(
            entry_id="test",
            domain="nio_telematics",
            data={"vin": VIN},
            options={"unrelated": {"keep": True}},
        )
        self.stored = {"nio_car_dashboard.test": deepcopy(self.original)}
        self.manager = {
            "recorders": {},
            "settings": {"test": {"old": True}},
            "store": SimpleNamespace(async_save=AsyncMock()),
        }
        self.tasks = []
        self.connection = SimpleNamespace(
            user=SimpleNamespace(is_admin=True), send_result=Mock(), send_error=Mock()
        )
        self.hass = SimpleNamespace(
            data={"nio_telematics_car_dashboard": self.manager},
            config_entries=SimpleNamespace(
                async_get_entry=lambda _: self.entry,
                async_update_entry=lambda entry, **kw: setattr(
                    entry, "options", kw["options"]
                ),
            ),
            async_create_background_task=self.schedule,
        )

        def store(hass, version, key, **kwargs):
            async def save(value):
                self.stored[key] = deepcopy(value)

            async def load():
                return deepcopy(self.stored.get(key))

            async def remove():
                self.stored.pop(key, None)

            return SimpleNamespace(
                async_save=save, async_load=load, async_remove=remove
            )

        self.patches = [
            patch.object(dashboard, "Store", side_effect=store),
            patch.object(dashboard, "preferences_for_entry", return_value={}),
            patch.object(
                dashboard,
                "_check_import_preferences",
                side_effect=lambda h, e, p: {
                    "battery_capacity_kwh": 90,
                    "full_range_km": 557,
                    **p,
                },
            ),
            patch.object(dashboard, "_vehicle", return_value={"entities": {}}),
            patch.object(dashboard, "async_reconcile_ledger", new=AsyncMock()),
        ]
        for item in self.patches:
            item.start()
        self.addCleanup(lambda: [item.stop() for item in reversed(self.patches)])

    def schedule(self, coro, *args, **kwargs):
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task

    def call(self, action, **values):
        self.connection.send_error.reset_mock()
        self.connection.send_result.reset_mock()
        message = {
            "id": 1,
            "type": "nio_telematics/vehicle_dashboard/backup",
            "entry_id": "test",
            "action": action,
            **values,
        }

        async def run():
            dashboard.websocket_backup(
                self.hass,
                self.connection,
                dashboard.websocket_backup._ws_schema(message),
            )
            await asyncio.gather(*self.tasks)

        asyncio.run(run())
        self.tasks = []
        return (
            self.connection.send_result.call_args.args[1]
            if self.connection.send_result.called
            else None
        )

    def test_actual_admin_export_preview_restore_accepts_text_and_legacy_object(self):
        legacy = self.call("export")
        self.assertIsInstance(legacy, dict)
        text = self.call("export", serialized=True)
        self.assertIsInstance(text, str)
        for payload in ({"backup": legacy}, {"backup_json": text}):
            preview = self.call("preview", **payload)
            self.assertEqual(preview["current"]["revision"], self.original["revision"])
            self.assertEqual(self.stored["nio_car_dashboard.test"], self.original)
        self.call(
            "restore",
            backup_json=text,
            expected_revision=self.original["revision"],
            confirmation="RESTORE",
        )
        self.assertFalse(
            self.connection.send_error.called, self.connection.send_error.call_args
        )
        self.assertEqual(
            json.dumps(self.stored["nio_car_dashboard.test"], sort_keys=True),
            json.dumps(self.original, sort_keys=True),
        )
        self.assertEqual(self.entry.options["unrelated"], {"keep": True})

    def test_xor_action_bounds_confirmation_revision_and_admin_guards(self):
        backup = make_backup(VIN, {}, self.original)
        text = serialize_backup(backup)
        cases = [
            ("export", {"backup_json": text}),
            ("preview", {}),
            ("preview", {"backup": backup, "backup_json": text}),
            ("preview", {"backup_json": text, "serialized": True}),
            ("preview", {"backup_json": text, "confirmation": "RESTORE"}),
            (
                "restore",
                {
                    "backup_json": text,
                    "confirmation": "RESTORE",
                    "expected_revision": -1,
                },
            ),
            (
                "restore",
                {"backup_json": text, "expected_revision": self.original["revision"]},
            ),
            ("preview", {"backup_json": " " * (MAX_BYTES + 1)}),
        ]
        for action, payload in cases:
            with self.subTest(action=action, keys=list(payload)):
                self.call(action, **payload)
                self.assertEqual(
                    self.connection.send_error.call_args.args[1], "invalid_backup"
                )
                self.assertEqual(self.stored["nio_car_dashboard.test"], self.original)
        self.connection.user.is_admin = False
        with self.assertRaises(Unauthorized):
            self.call("export", serialized=True)

    def test_text_restore_failure_rolls_back_history_options_and_settings(self):
        backup = make_backup(VIN, {}, self.original)
        backup["history"]["revision"] += 1
        old_options = deepcopy(self.entry.options)
        old_settings = deepcopy(self.manager["settings"])
        with patch.object(
            dashboard,
            "async_reconcile_ledger",
            new=AsyncMock(side_effect=ValueError("test rejection")),
        ):
            self.call(
                "restore",
                backup_json=serialize_backup(backup),
                expected_revision=self.original["revision"],
                confirmation="RESTORE",
            )
        self.assertEqual(self.connection.send_error.call_args.args[1], "invalid_backup")
        self.assertEqual(self.stored["nio_car_dashboard.test"], self.original)
        self.assertEqual(self.entry.options, old_options)
        self.assertEqual(self.manager["settings"], old_settings)
