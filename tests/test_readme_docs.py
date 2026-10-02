# Copyright (c) 2026 Adrien40
# SPDX-License-Identifier: GPL-3.0-only

"""The documentation rules marked `done` must have a section in both READMEs."""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
RULES = yaml.safe_load(
    (ROOT / "custom_components" / "hydrao_custom" / "quality_scale.yaml").read_text()
)["rules"]

# rule -> heading keywords, per README
SECTIONS = {
    "docs-data-update": {
        "README.md": r"how data is updated",
        "README.fr.md": r"mise à jour des données",
    },
    "docs-examples": {
        "README.md": r"automation examples",
        "README.fr.md": r"exemples d'automatisations",
    },
    "docs-known-limitations": {
        "README.md": r"known limitations",
        "README.fr.md": r"limitations connues",
    },
    "docs-use-cases": {
        "README.md": r"use cases",
        "README.fr.md": r"cas d'usage",
    },
}


def status_of(name):
    value = RULES[name]
    return value if isinstance(value, str) else value["status"]


@pytest.mark.parametrize("readme", ["README.md", "README.fr.md"])
@pytest.mark.parametrize("rule", sorted(SECTIONS))
def test_docs_rule_status_matches_the_readmes(rule, readme):
    text = (ROOT / readme).read_text(encoding="utf-8")
    has_section = bool(
        re.search(
            rf"^#+ .*{SECTIONS[rule][readme]}", text, re.IGNORECASE | re.MULTILINE
        )
    )

    assert (status_of(rule) == "done") is has_section


@pytest.mark.parametrize("readme", ["README.md", "README.fr.md"])
def test_automation_examples_are_valid_yaml(readme):
    text = (ROOT / readme).read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)

    assert len(blocks) >= 3
    for block in blocks:
        assert yaml.safe_load(block)
