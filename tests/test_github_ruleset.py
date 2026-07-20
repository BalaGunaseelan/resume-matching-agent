from __future__ import annotations

from pathlib import Path

from resume_matching_agent import github_ruleset


def test_load_ruleset_config_reads_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "ruleset.yml"
    config_path.write_text(
        "name: Main Branch Protection\nenforcement: active\nrules:\n  - type: deletion\n",
        encoding="utf-8",
    )

    config = github_ruleset.load_ruleset_config(config_path)

    assert config["name"] == "Main Branch Protection"
    assert config["rules"] == [{"type": "deletion"}]


def test_build_ruleset_payload_resolves_user_bypass_actor(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake_github_request(method: str, api_url: str, token: str, payload=None):
        calls.append((method, api_url))
        assert token == "token"
        assert payload is None
        return {"id": 84369479}

    monkeypatch.setattr(github_ruleset, "github_request", fake_github_request)
    config = {
        "name": "Main Branch Protection",
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [
            {
                "actor_name": "BalaGunaseelan",
                "actor_type": "User",
                "bypass_mode": "always",
            }
        ],
        "conditions": {"ref_name": {"include": ["main"], "exclude": []}},
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": ["sync"],
                },
            },
        ],
    }

    payload = github_ruleset.build_ruleset_payload(config, "https://api.github.com", "token")

    assert calls == [("GET", "https://api.github.com/users/BalaGunaseelan")]
    assert payload["conditions"]["ref_name"]["include"] == ["refs/heads/main"]
    assert payload["bypass_actors"] == [
        {"actor_id": 84369479, "actor_type": "User", "bypass_mode": "always"}
    ]
    assert payload["rules"][2]["parameters"]["required_status_checks"] == [
        {"context": "sync", "integration_id": None}
    ]


def test_upsert_ruleset_updates_existing_ruleset(monkeypatch) -> None:
    requests: list[tuple[str, str, object | None]] = []

    def fake_github_request(method: str, api_url: str, token: str, payload=None):
        requests.append((method, api_url, payload))
        assert token == "token"
        if method == "GET":
            return [{"id": 7, "name": "Main Branch Protection"}]
        return {"ok": True}

    monkeypatch.setattr(github_ruleset, "github_request", fake_github_request)

    result = github_ruleset.upsert_ruleset(
        "https://api.github.com/repos/BalaGunaseelan/resume-matching-agent",
        "token",
        {"name": "Main Branch Protection", "target": "branch", "rules": []},
    )

    assert result == "Updated ruleset: Main Branch Protection"
    assert requests == [
        (
            "GET",
            "https://api.github.com/repos/BalaGunaseelan/resume-matching-agent/rulesets?includes_parents=false&targets=branch",
            None,
        ),
        (
            "PATCH",
            "https://api.github.com/repos/BalaGunaseelan/resume-matching-agent/rulesets/7",
            {"name": "Main Branch Protection", "target": "branch", "rules": []},
        ),
    ]
