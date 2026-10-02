# Copyright (c) 2026 Adrien40
# SPDX-License-Identifier: GPL-3.0-only

"""Guards for .github/dependabot.yml: the configuration must stay valid, point
at real directories, and never let Dependabot bump the test requirements that
are frozen on the minimum Home Assistant release."""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent

# The only pins in requirements-test.txt that Dependabot may update.
# Everything else follows Home Assistant's own versions (test_compatibility.py).
FREE_TO_BUMP = {"mypy"}


@pytest.fixture(scope="module")
def config():
    return yaml.safe_load((ROOT / ".github" / "dependabot.yml").read_text())


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def test_the_configuration_is_version_2_with_updates(config):
    assert config["version"] == 2
    assert config["updates"]


def test_every_update_targets_a_known_ecosystem_and_a_real_directory(config):
    for update in config["updates"]:
        assert update["package-ecosystem"] in {"github-actions", "pip"}
        assert (ROOT / update["directory"].lstrip("/")).is_dir()
        assert update["schedule"]["interval"]


def test_both_github_actions_and_pip_are_watched(config):
    ecosystems = {update["package-ecosystem"] for update in config["updates"]}

    assert ecosystems == {"github-actions", "pip"}


def test_the_frozen_test_requirements_are_all_ignored(config):
    pip = next(u for u in config["updates"] if u["package-ecosystem"] == "pip")
    ignored = {normalize(rule["dependency-name"]) for rule in pip["ignore"]}
    pinned = {
        normalize(match.group(1))
        for match in re.finditer(
            r"^([A-Za-z0-9._-]+)==",
            (ROOT / "requirements-test.txt").read_text(),
            re.MULTILINE,
        )
    }

    assert pinned - ignored == FREE_TO_BUMP
