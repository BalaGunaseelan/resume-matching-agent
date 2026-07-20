from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or update a GitHub repository ruleset from a YAML file."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the YAML ruleset definition.",
    )
    return parser


def github_request(
    method: str,
    api_url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"******",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "resume-matching-agent-ruleset-script",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(api_url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed: {method} {api_url} -> {exc.code}: {message}"
        ) from exc


def load_ruleset_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Ruleset config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise ValueError("Ruleset config must deserialize to an object.")

    return config


def normalize_ref_name_pattern(value: str) -> str:
    if value.startswith("refs/") or value.startswith("~"):
        return value
    return f"refs/heads/{value}"


def normalize_conditions(config: dict[str, Any]) -> dict[str, Any]:
    conditions = config.get("conditions") or {}
    if not isinstance(conditions, dict):
        raise ValueError("conditions must be an object")

    ref_name = conditions.get("ref_name") or {}
    if not isinstance(ref_name, dict):
        raise ValueError("conditions.ref_name must be an object")

    include = ref_name.get("include") or []
    exclude = ref_name.get("exclude") or []
    if not isinstance(include, list) or not isinstance(exclude, list):
        raise ValueError("conditions.ref_name.include and exclude must be arrays")

    return {
        "ref_name": {
            "include": [normalize_ref_name_pattern(str(item)) for item in include],
            "exclude": [normalize_ref_name_pattern(str(item)) for item in exclude],
        }
    }


def resolve_bypass_actor(
    config_actor: dict[str, Any],
    api_root: str,
    token: str,
) -> dict[str, Any]:
    actor_type = str(config_actor.get("actor_type", "")).strip()
    actor_name = str(config_actor.get("actor_name", "")).strip()
    bypass_mode = str(config_actor.get("bypass_mode", "always")).strip() or "always"

    if actor_type != "User":
        raise ValueError(
            "Only User bypass actors are currently supported by the repository ruleset script."
        )
    if not actor_name:
        raise ValueError("bypass_actors[].actor_name is required")

    actor = github_request(
        "GET",
        f"{api_root}/users/{urllib.parse.quote(actor_name, safe='')}",
        token,
    )
    actor_id = actor.get("id")
    if not isinstance(actor_id, int):
        raise ValueError(f"Unable to resolve GitHub user ID for {actor_name}")

    return {
        "actor_id": actor_id,
        "actor_type": actor_type,
        "bypass_mode": bypass_mode,
    }


def normalize_rule(rule: dict[str, Any]) -> dict[str, Any]:
    rule_type = str(rule.get("type", "")).strip()
    if not rule_type:
        raise ValueError("rules[].type is required")

    normalized: dict[str, Any] = {"type": rule_type}
    parameters = rule.get("parameters")
    if parameters is None:
        return normalized
    if not isinstance(parameters, dict):
        raise ValueError(f"rules[{rule_type}].parameters must be an object")

    normalized_parameters = dict(parameters)
    if rule_type == "required_status_checks":
        required_checks = normalized_parameters.get("required_status_checks") or []
        if not isinstance(required_checks, list):
            raise ValueError("required_status_checks.parameters.required_status_checks must be a list")
        normalized_parameters["required_status_checks"] = [
            {"context": item, "integration_id": None}
            if isinstance(item, str)
            else item
            for item in required_checks
        ]

    normalized["parameters"] = normalized_parameters
    return normalized


def build_ruleset_payload(
    config: dict[str, Any],
    api_root: str,
    token: str,
) -> dict[str, Any]:
    bypass_actors = config.get("bypass_actors") or []
    if not isinstance(bypass_actors, list):
        raise ValueError("bypass_actors must be an array")

    rules = config.get("rules") or []
    if not isinstance(rules, list) or not rules:
        raise ValueError("rules must be a non-empty array")

    payload = {
        "name": str(config.get("name", "")).strip(),
        "target": str(config.get("target", "branch")).strip() or "branch",
        "enforcement": str(config.get("enforcement", "")).strip(),
        "bypass_actors": [
            resolve_bypass_actor(actor, api_root, token) for actor in bypass_actors
        ],
        "conditions": normalize_conditions(config),
        "rules": [normalize_rule(rule) for rule in rules],
    }

    if not payload["name"]:
        raise ValueError("name is required")
    if not payload["enforcement"]:
        raise ValueError("enforcement is required")

    return payload


def upsert_ruleset(
    base_repo_api: str,
    token: str,
    payload: dict[str, Any],
) -> str:
    existing_rulesets = github_request(
        "GET",
        f"{base_repo_api}/rulesets?includes_parents=false&targets={urllib.parse.quote(payload['target'])}",
        token,
    )
    if not isinstance(existing_rulesets, list):
        raise ValueError("Unexpected rulesets response from GitHub API")

    for ruleset in existing_rulesets:
        if ruleset.get("name") != payload["name"]:
            continue
        ruleset_id = ruleset.get("id")
        github_request(
            "PATCH",
            f"{base_repo_api}/rulesets/{ruleset_id}",
            token,
            payload=payload,
        )
        return f"Updated ruleset: {payload['name']}"

    github_request(
        "POST",
        f"{base_repo_api}/rulesets",
        token,
        payload=payload,
    )
    return f"Created ruleset: {payload['name']}"


def os_environ() -> dict[str, str]:
    import os

    return os.environ


def run(config_path: Path) -> int:
    token = os_environ().get("GITHUB_TOKEN", "").strip()
    repository = os_environ().get("GITHUB_REPOSITORY", "").strip()

    if not token:
        print("Error: GITHUB_TOKEN is required.", file=sys.stderr)
        return EXIT_ERROR
    if not repository or "/" not in repository:
        print("Error: GITHUB_REPOSITORY must be set as owner/repo.", file=sys.stderr)
        return EXIT_ERROR

    config = load_ruleset_config(config_path)
    owner, repo = repository.split("/", 1)
    api_root = "https://api.github.com"
    base_repo_api = f"{api_root}/repos/{owner}/{repo}"
    payload = build_ruleset_payload(config, api_root, token)
    print(upsert_ruleset(base_repo_api, token, payload))
    return EXIT_SUCCESS


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    try:
        return run(args.config)
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
