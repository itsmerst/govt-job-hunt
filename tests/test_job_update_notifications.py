import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import telegram_job_bot


class JobUpdateNotificationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.state_path = Path(self.temp_dir.name) / "state.json"
        self.database_path = Path(self.temp_dir.name) / "jobs.json"
        self.job = {
            "id": 1,
            "name": "Test recruitment",
            "eligibility_filters": {
                "gate_required": False,
                "max_qualification_level": "bachelor",
                "branches": ["it"],
                "min_age": 25,
                "max_age": 30,
            },
            "salary": "₹50,000",
        }
        self.config = {
            "db_path": str(self.database_path),
            "user_branches": ["it"],
            "user_age_min": 25,
            "user_age_max": 30,
        }

    def test_changed_job_content_requires_a_new_notification(self):
        state = telegram_job_bot.JobState(str(self.state_path))
        state.mark(self.job)
        updated_job = dict(self.job, salary="₹60,000")

        self.assertTrue(state.needs_notification(updated_job))

    def test_unchanged_job_content_is_not_resent(self):
        state = telegram_job_bot.JobState(str(self.state_path))
        state.mark(self.job)

        self.assertFalse(state.needs_notification(self.job))

    def test_legacy_state_is_seeded_without_resending(self):
        self.state_path.write_text(
            json.dumps({"notified": {"1": {"name": self.job["name"]}}}),
            encoding="utf-8",
        )
        state = telegram_job_bot.JobState(str(self.state_path))

        self.assertFalse(state.needs_notification(self.job))
        self.assertEqual(
            state.data["notified"]["1"]["fingerprint"],
            telegram_job_bot.job_fingerprint(self.job),
        )

    def test_relative_database_path_is_resolved_from_application_directory(self):
        self.assertEqual(
            telegram_job_bot.resolve_file_path("jobs_database.json"),
            telegram_job_bot.APP_DIR / "jobs_database.json",
        )


class RefreshNotificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_refresh_sends_update_for_changed_existing_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            database_path = Path(temp_dir) / "jobs.json"
            state = telegram_job_bot.JobState(str(state_path))
            old_job = {
                "id": 1,
                "name": "Test recruitment",
                "eligibility_filters": {
                    "gate_required": False,
                    "max_qualification_level": "bachelor",
                    "branches": ["it"],
                    "min_age": 25,
                    "max_age": 30,
                },
                "salary": "₹50,000",
            }
            state.mark(old_job)
            new_job = dict(old_job, salary="₹60,000")
            database_path.write_text(
                json.dumps({"last_updated": "2026-10-06", "jobs": [new_job]}),
                encoding="utf-8",
            )
            context = SimpleNamespace(
                bot_data={
                    "config": {
                        "db_path": str(database_path),
                        "user_branches": ["it"],
                        "user_age_min": 25,
                        "user_age_max": 30,
                    },
                    "state": state,
                }
            )

            with patch.object(
                telegram_job_bot, "send_to_all", new_callable=AsyncMock, return_value=1
            ) as send:
                result = await telegram_job_bot.check_new_jobs(context)

            self.assertEqual(result["updated"], 1)
            self.assertEqual(result["pushed"], 0)
            send.assert_awaited_once()
            self.assertEqual(
                state.data["notified"]["1"]["fingerprint"],
                telegram_job_bot.job_fingerprint(new_job),
            )


if __name__ == "__main__":
    unittest.main()
