import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "renderer", Path(__file__).with_name("render-readme.py")
)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RenderTests(unittest.TestCase):
    def test_contributions_filter_and_sort(self):
        def entry(name, day, private=False, empty=False):
            return {"repository": {"nameWithOwner": name, "url": "https://github.com/" + name,
                                   "description": None, "isPrivate": private},
                    "contributions": {"nodes": [] if empty else [{"occurredAt": day}]}}
        entries = [entry("user/old", "2026-01-01"), entry("user/private", "2026-10-01", True),
                   entry("User/User", "2026-10-01"), entry("user/empty", "", empty=True),
                   entry("user/new", "2026-09-01")]
        lines = renderer.recent_contributions(entries, "user")
        self.assertEqual(lines, ["- [user/new](https://github.com/user/new) - ",
                                 "- [user/old](https://github.com/user/old) - "])

    def test_substituted_text_is_literal(self):
        template = "Header\n{{ /* RECENT_REPOS */ }}\n{{ /* RECENT_STARS */ }}\nFooter"
        result = renderer.render(template, {
            "RECENT_REPOS": ['{{ /* RECENT_STARS */ }} {{ dangerous }}'],
            "RECENT_STARS": ["a star"],
        })
        self.assertEqual(result, "Header\n\n{{ /* RECENT_STARS */ }} {{ dangerous }}\n\na star\nFooter")

    def test_missing_or_duplicate_marker_fails(self):
        for template in ["", "{{ /* RECENT_REPOS */ }}" * 2]:
            with self.assertRaises(ValueError):
                renderer.render(template, {"RECENT_REPOS": []})

    @patch.object(renderer.time, "sleep")
    @patch.object(renderer.subprocess, "run")
    def test_transient_failure_retries(self, run, sleep):
        run.side_effect = [subprocess.CalledProcessError(1, "gh"),
                           subprocess.CompletedProcess("gh", 0, json.dumps({"ok": True}))]
        self.assertEqual(renderer.api(["test"]), {"ok": True})
        self.assertEqual(run.call_count, 2)
        sleep.assert_called_once_with(5)

    @patch.object(renderer.time, "sleep")
    @patch.object(renderer.subprocess, "run")
    def test_persistent_failure_is_not_silenced(self, run, sleep):
        run.side_effect = subprocess.TimeoutExpired("gh", 60)
        with self.assertRaisesRegex(RuntimeError, "after 3 attempts"):
            renderer.api(["test"])
        self.assertEqual(run.call_count, 3)

    @patch.object(renderer.time, "sleep")
    @patch.object(renderer.subprocess, "run")
    def test_graphql_errors_are_not_partial_success(self, run, sleep):
        run.return_value = subprocess.CompletedProcess("gh", 0, '{"errors": [{}], "data": {}}')
        with self.assertRaises(RuntimeError):
            renderer.api(["graphql"])


if __name__ == "__main__":
    unittest.main()
