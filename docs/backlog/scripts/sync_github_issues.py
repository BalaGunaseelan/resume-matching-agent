#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_ERROR = 2

MANAGED_MARKER = "managed-by: backlog-csv-sync"
BACKLOG_ID_PATTERN = re.compile(r"backlog-id:\s*([A-Za-z0-9_-]+)")

TYPE_LABEL_COLORS = {
    "epic": "5319e7",
    "feature": "1d76db",
    "story": "0e8a16",
}

PRIORITY_LABEL_COLORS = {
    "high": "b60205",
    "medium": "fbca04",
    "low": "0e8a16",
}

DEFAULT_LABEL_COLOR = "6e7781"


@dataclass
class BacklogRow:
    issue_type: str
    backlog_id: str
    title: str
    parent: str
    milestone: str
    priority: str
    area: str
    dependencies: str
    acceptance_criteria: str


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync GitHub issues from backlog CSV."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        required=True,
        help="Path to the backlog CSV file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations without writing to GitHub.",
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
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "backlog-csv-sync-script",
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


def parse_backlog_csv(csv_path: Path) -> list[BacklogRow]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows: list[BacklogRow] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "IssueType",
            "ID",
            "Title",
            "Parent",
            "Milestone",
            "Priority",
            "Area",
            "Dependencies",
            "AcceptanceCriteria",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

        for index, source in enumerate(reader, start=2):
            backlog_id = (source.get("ID") or "").strip()
            title = (source.get("Title") or "").strip()
            issue_type = (source.get("IssueType") or "").strip().lower()
            if not backlog_id or not title or not issue_type:
                raise ValueError(
                    f"Invalid row at line {index}: ID, Title, and IssueType are required"
                )

            rows.append(
                BacklogRow(
                    issue_type=issue_type,
                    backlog_id=backlog_id,
                    title=title,
                    parent=(source.get("Parent") or "").strip(),
                    milestone=(source.get("Milestone") or "").strip(),
                    priority=(source.get("Priority") or "").strip().lower(),
                    area=(source.get("Area") or "").strip().lower(),
                    dependencies=(source.get("Dependencies") or "").strip(),
                    acceptance_criteria=(source.get("AcceptanceCriteria") or "").strip(),
                )
            )

    return rows


def fetch_all_open_and_closed_issues(base_repo_api: str, token: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode({"state": "all", "per_page": 100, "page": page})
        data = github_request(
            "GET",
            f"{base_repo_api}/issues?{query}",
            token,
        )
        if not data:
            break
        # Pull requests are also returned by this endpoint; skip those.
        issues.extend([item for item in data if "pull_request" not in item])
        if len(data) < 100:
            break
        page += 1
    return issues


def fetch_all_milestones(base_repo_api: str, token: str) -> list[dict[str, Any]]:
    milestones: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode({"state": "all", "per_page": 100, "page": page})
        data = github_request(
            "GET",
            f"{base_repo_api}/milestones?{query}",
            token,
        )
        if not data:
            break
        milestones.extend(data)
        if len(data) < 100:
            break
        page += 1
    return milestones


def ensure_label(base_repo_api: str, token: str, name: str, color: str, dry_run: bool) -> None:
    encoded_name = urllib.parse.quote(name, safe="")
    label_url = f"{base_repo_api}/labels/{encoded_name}"
    try:
        github_request("GET", label_url, token)
        return
    except RuntimeError as exc:
        if " -> 404:" not in str(exc):
            raise

    if dry_run:
        print(f"[DRY-RUN] Create label: {name}")
        return

    github_request(
        "POST",
        f"{base_repo_api}/labels",
        token,
        payload={
            "name": name,
            "color": color,
            "description": "Managed by backlog CSV sync workflow",
        },
    )
    print(f"Created label: {name}")


def ensure_milestones(
    base_repo_api: str,
    token: str,
    rows: list[BacklogRow],
    dry_run: bool,
) -> dict[str, int]:
    wanted = {row.milestone for row in rows if row.milestone}
    existing = fetch_all_milestones(base_repo_api, token)
    by_title = {item["title"]: item["number"] for item in existing}

    for title in sorted(wanted):
        if title in by_title:
            continue
        if dry_run:
            print(f"[DRY-RUN] Create milestone: {title}")
            continue
        created = github_request(
            "POST",
            f"{base_repo_api}/milestones",
            token,
            payload={"title": title},
        )
        by_title[title] = created["number"]
        print(f"Created milestone: {title}")

    return by_title


def build_labels(row: BacklogRow) -> list[str]:
    labels = ["managed:backlog-csv"]
    labels.append(f"type:{row.issue_type}")
    if row.priority:
        labels.append(f"priority:{row.priority}")
    if row.area:
        labels.append(f"area:{row.area}")
    return labels


def split_dependencies(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split("|") if item.strip()]


def render_body(
    row: BacklogRow,
    id_to_issue_number: dict[str, int],
) -> str:
    parent_ref = ""
    if row.parent:
        parent_number = id_to_issue_number.get(row.parent)
        parent_ref = f"#{parent_number}" if parent_number else row.parent

    deps = split_dependencies(row.dependencies)
    dep_refs: list[str] = []
    for dep in deps:
        dep_number = id_to_issue_number.get(dep)
        dep_refs.append(f"#{dep_number}" if dep_number else dep)

    dependency_line = ", ".join(dep_refs) if dep_refs else "None"
    parent_line = parent_ref if parent_ref else "None"

    lines = [
        "<!-- managed-by: backlog-csv-sync -->",
        f"<!-- backlog-id: {row.backlog_id} -->",
        "",
        "## Backlog Metadata",
        f"- Backlog ID: {row.backlog_id}",
        f"- Type: {row.issue_type}",
        f"- Parent: {parent_line}",
        f"- Dependencies: {dependency_line}",
    ]
    if row.milestone:
        lines.append(f"- Milestone: {row.milestone}")

    lines.extend(
        [
            "",
            "## Acceptance Criteria",
            row.acceptance_criteria or "TBD",
            "",
            "## Sync Notes",
            "This issue is managed by CSV sync automation. Manual edits may be overwritten.",
        ]
    )
    return "\n".join(lines)


def extract_backlog_id(issue_body: str | None) -> str | None:
    if not issue_body:
        return None
    if MANAGED_MARKER not in issue_body:
        return None
    match = BACKLOG_ID_PATTERN.search(issue_body)
    if not match:
        return None
    return match.group(1)


def sync_issues(
    base_repo_api: str,
    token: str,
    rows: list[BacklogRow],
    dry_run: bool,
) -> None:
    ensure_label(base_repo_api, token, "managed:backlog-csv", "0366d6", dry_run)

    for issue_type in sorted({row.issue_type for row in rows}):
        color = TYPE_LABEL_COLORS.get(issue_type, DEFAULT_LABEL_COLOR)
        ensure_label(base_repo_api, token, f"type:{issue_type}", color, dry_run)

    for priority in sorted({row.priority for row in rows if row.priority}):
        color = PRIORITY_LABEL_COLORS.get(priority, DEFAULT_LABEL_COLOR)
        ensure_label(base_repo_api, token, f"priority:{priority}", color, dry_run)

    for area in sorted({row.area for row in rows if row.area}):
        ensure_label(base_repo_api, token, f"area:{area}", DEFAULT_LABEL_COLOR, dry_run)

    milestones = ensure_milestones(base_repo_api, token, rows, dry_run)

    existing_issues = fetch_all_open_and_closed_issues(base_repo_api, token)
    managed_by_backlog_id: dict[str, dict[str, Any]] = {}
    for issue in existing_issues:
        backlog_id = extract_backlog_id(issue.get("body"))
        if backlog_id:
            managed_by_backlog_id[backlog_id] = issue

    id_to_issue_number: dict[str, int] = {}
    for backlog_id, issue in managed_by_backlog_id.items():
        id_to_issue_number[backlog_id] = issue["number"]

    for row in rows:
        payload = {
            "title": row.title,
            "body": render_body(row, id_to_issue_number),
            "labels": build_labels(row),
            "state": "open",
        }
        if row.milestone and row.milestone in milestones:
            payload["milestone"] = milestones[row.milestone]

        if row.backlog_id in managed_by_backlog_id:
            issue_number = managed_by_backlog_id[row.backlog_id]["number"]
            id_to_issue_number[row.backlog_id] = issue_number
            if dry_run:
                print(f"[DRY-RUN] Update issue #{issue_number} from {row.backlog_id}")
            else:
                github_request(
                    "PATCH",
                    f"{base_repo_api}/issues/{issue_number}",
                    token,
                    payload=payload,
                )
                print(f"Updated issue #{issue_number} from {row.backlog_id}")
        else:
            if dry_run:
                print(f"[DRY-RUN] Create issue for {row.backlog_id}: {row.title}")
                continue
            created = github_request(
                "POST",
                f"{base_repo_api}/issues",
                token,
                payload=payload,
            )
            id_to_issue_number[row.backlog_id] = created["number"]
            managed_by_backlog_id[row.backlog_id] = created
            print(f"Created issue #{created['number']} for {row.backlog_id}")

    # Second pass to refresh body text with issue-number references now that all
    # backlog IDs are fully mapped.
    for row in rows:
        if row.backlog_id not in id_to_issue_number:
            continue
        issue_number = id_to_issue_number[row.backlog_id]
        body_payload = {"body": render_body(row, id_to_issue_number)}
        if dry_run:
            print(f"[DRY-RUN] Refresh issue #{issue_number} links for {row.backlog_id}")
            continue
        github_request(
            "PATCH",
            f"{base_repo_api}/issues/{issue_number}",
            token,
            payload=body_payload,
        )

    csv_ids = {row.backlog_id for row in rows}
    stale_ids = sorted(set(managed_by_backlog_id.keys()).difference(csv_ids))
    for stale_id in stale_ids:
        issue_number = managed_by_backlog_id[stale_id]["number"]
        if dry_run:
            print(f"[DRY-RUN] Close issue #{issue_number}; backlog ID {stale_id} removed")
            continue
        github_request(
            "PATCH",
            f"{base_repo_api}/issues/{issue_number}",
            token,
            payload={"state": "closed"},
        )
        print(f"Closed issue #{issue_number}; backlog ID {stale_id} removed from CSV")


def run(csv_path: Path, dry_run: bool) -> int:
    token = ("" if "GITHUB_TOKEN" not in os_environ() else os_environ()["GITHUB_TOKEN"]).strip()
    repository = (
        "" if "GITHUB_REPOSITORY" not in os_environ() else os_environ()["GITHUB_REPOSITORY"]
    ).strip()

    if not token:
        print("Error: GITHUB_TOKEN is required.", file=sys.stderr)
        return EXIT_ERROR
    if not repository or "/" not in repository:
        print("Error: GITHUB_REPOSITORY must be set as owner/repo.", file=sys.stderr)
        return EXIT_ERROR

    owner, repo = repository.split("/", 1)
    base_repo_api = f"https://api.github.com/repos/{owner}/{repo}"

    rows = parse_backlog_csv(csv_path)
    sync_issues(base_repo_api, token, rows, dry_run)
    return EXIT_SUCCESS


def os_environ() -> dict[str, str]:
    # Isolated helper to make environment lookups easy to mock in tests.
    import os

    return os.environ


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    try:
        return run(args.csv, args.dry_run)
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())