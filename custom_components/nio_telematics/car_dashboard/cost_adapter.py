"""Optional Recorder backfill and durable per-session cost checkpoints."""

from copy import deepcopy
from functools import partial

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.history import get_significant_states
from homeassistant.util import dt as dt_util

from .cost_split import SOURCE_KEYS, VERSION, numeric, split_session


class CostRecorder:
    def __init__(self, owner):
        self.owner = owner
        self.last_query = 0.0

    async def refresh(self, now):
        owner = self.owner
        mapping = owner.settings.get("cost_sources", {})
        if set(mapping) != set(SOURCE_KEYS):
            return
        data = owner.ledger.data
        results = data.setdefault("cost_split_results", {})
        progress = data.setdefault("cost_split_progress", {})
        tracks = data.setdefault("cost_tracks", {})
        profile = tuple(mapping[k] for k in SOURCE_KEYS)

        def signature(c):
            return [VERSION, c["start"], c["end"], c["kwh"], c.get("cost_eur")]

        charges = [
            c
            for c in data["charges"].values()
            if c["kind"] == "home" and not c.get("ongoing") and not c.get("manual_cost")
        ]
        pending = [
            c
            for c in charges
            if results.get(c["id"], {}).get("signature") != signature(c)
            or (
                results.get(c["id"], {}).get("status") != "complete"
                and c["end"] > now - 86400
                and results.get(c["id"], {}).get("attempted_at", 0) < now - 60
            )
        ]
        states = {
            k: owner.hass.states.get(entity_id) for k, entity_id in mapping.items()
        }
        current_energy = numeric(states["energy"].state) if states["energy"] else None
        current_total = (
            numeric(states["total_cost"].state) if states["total_cost"] else None
        )
        live_signature = [current_energy, current_total]
        previous_live = data.get("cost_live_signature")
        if (
            not pending
            and previous_live == live_signature
            and (current_energy is None or data.get("cost_live_status") == "complete")
        ):
            return
        starts = [c["start"] for c in pending]
        if self.last_query:
            starts.append(self.last_query - 180)
        else:
            starts.append(now - 12 * 86400)
        if data.get("cost_live_status") not in (None, "complete"):
            starts.append(now - 12 * 86400)
        # Checkpoints contain already priced prefixes, independent of Recorder
        # retention. Query only the unpriced suffix after a process restart.
        for p in tracks.values():
            if (
                current_energy is not None
                and abs(p.get("energy", -1) - current_energy) <= 0.0011
            ):
                starts.append(p["t"] - 5)
        begin = max(now - 12 * 86400, min(starts))
        rows = await get_instance(owner.hass).async_add_executor_job(
            partial(
                get_significant_states,
                owner.hass,
                dt_util.utc_from_timestamp(begin),
                dt_util.utc_from_timestamp(now + 1),
                list(mapping.values()),
                include_start_time_state=True,
                significant_changes_only=True,
                minimal_response=False,
                no_attributes=True,
            )
        )
        sources = {
            k: [
                {"t": s.last_updated.timestamp(), "v": numeric(s.state)}
                for s in rows.get(entity_id, [])
            ]
            for k, entity_id in mapping.items()
        }
        # Recorder may still be committing the current batch. Live observations
        # supplement that suffix; they never replace historic dated readings.
        for k, state in states.items():
            if state:
                sources[k].append(
                    {"t": state.last_updated.timestamp(), "v": numeric(state.state)}
                )
        self.last_query = now
        before = deepcopy(
            {
                k: data.get(k)
                for k in (
                    "cost_split_results",
                    "cost_split_progress",
                    "cost_tracks",
                    "cost_live_signature",
                    "cost_live_status",
                )
            }
        )
        for charge in pending:
            seed = progress.get(charge["id"])
            if not seed:
                seed = next(
                    (
                        dict(p, start=charge["start"])
                        for p in tracks.values()
                        if abs(p["start"] - charge["start"]) <= 180
                        and p.get("profile") == list(profile)
                        and p["energy"] <= charge["kwh"] + 0.0011
                    ),
                    None,
                )
            if charge["end"] < begin and not seed:
                result, checkpoint = {"status": "missing_start"}, None
            else:
                result, checkpoint = await owner.hass.async_add_executor_job(
                    split_session, dict(charge), sources, seed
                )
            result["signature"] = signature(charge)
            result["attempted_at"] = now
            results[charge["id"]] = result
            if checkpoint:
                progress[charge["id"]] = checkpoint
        if current_energy is not None and current_total is not None:
            zeros = [r["t"] for r in sources["energy"] if r["v"] == 0]
            saved = [
                p
                for p in tracks.values()
                if p.get("profile") == list(profile)
                and p["energy"] <= current_energy + 0.0011
            ]
            start = max(zeros + [p["start"] for p in saved], default=None)
            if start is not None:
                seed = tracks.get(str(start))
                live = {
                    "start": start,
                    "end": now,
                    "kwh": current_energy,
                    "cost_eur": current_total,
                }
                result, checkpoint = await owner.hass.async_add_executor_job(
                    split_session, live, sources, seed
                )
                if checkpoint:
                    checkpoint["profile"] = list(profile)
                    tracks[str(start)] = checkpoint
                data["cost_live_status"] = result["status"]
                history = owner.hass.states.get(owner.settings["home_history"])
                active_id = (
                    history.attributes.get("active_session_id") if history else None
                )
                if active_id is not None:
                    result["signature"] = [
                        VERSION,
                        start,
                        now,
                        current_energy,
                        current_total,
                    ]
                    results["home-" + str(active_id)] = result
        data["cost_live_signature"] = live_signature
        after = {k: data.get(k) for k in before}
        if before != after:
            owner.ledger.changed()

    def enrich(self, snapshot):
        results = self.owner.ledger.data.get("cost_split_results", {})
        snapshot["charges"] = [dict(c) for c in snapshot["charges"]]
        for charge in snapshot["charges"]:
            result = results.get(charge["id"], {})
            if (
                result.get("status") == "complete"
                and not charge.get("manual_cost")
                and charge.get("kwh") is not None
                and charge.get("cost_eur") is not None
                and abs(result["cost_split_kwh"] - charge["kwh"]) <= 0.0011
                and abs(result["cost_split_total_eur"] - charge["cost_eur"]) <= 0.00001
            ):
                charge.update(
                    {
                        k: v
                        for k, v in result.items()
                        if k not in ("status", "signature", "attempted_at")
                    }
                )
        active = snapshot.get("active_home_charge")
        if active and results.get(active["id"], {}).get("status") == "complete":
            active.update(
                {
                    k: v
                    for k, v in results[active["id"]].items()
                    if k not in ("status", "signature", "attempted_at")
                }
            )
        snapshot["cost_recording"] = {
            "version": VERSION,
            "configured": bool(self.owner.settings.get("cost_sources")),
        }
        return snapshot
