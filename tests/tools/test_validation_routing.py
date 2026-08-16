"""Regression tests for responsibility-based validation routing."""

from __future__ import annotations

from pathlib import Path

from tools import validation_routing as router

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "validation/profiles.toml"

CONFIG = router.load_config(CONFIG_PATH)
ALL_PROFILES = set(CONFIG.profile_ids)


def states_for(paths: list[str], *, event: str = "pull_request") -> dict[str, str]:
    """Return profile states for a fixture change set."""

    plan = router.classify_paths(CONFIG, paths, event)
    return router.profile_states(plan)


def applicable(paths: list[str], *, event: str = "pull_request") -> set[str]:
    """Return only applicable profiles for a fixture change set."""

    return {
        identifier
        for identifier, state in states_for(paths, event=event).items()
        if state == "applicable"
    }


def test_docs_only_selects_only_docs() -> None:
    assert applicable(["documents/guide.md"]) == {"docs"}


def test_cpp_only_selects_cpp() -> None:
    assert applicable(["cpp/src/example.cpp"]) == {"cpp"}


def test_workflow_only_selects_github_automation() -> None:
    assert applicable([".github/workflows/release.yml"]) == {"github-automation"}


def test_bootstrap_change_selects_real_fresh_clone_acceptance() -> None:
    assert applicable(["scripts/start_repository.sh"]) == {"bootstrap"}


def test_multi_responsibility_change_uses_union() -> None:
    assert applicable(["README.md", "cpp/tests/example_test.cpp"]) == {"docs", "cpp"}


def test_router_change_conservatively_selects_every_profile() -> None:
    assert applicable(["validation/profiles.toml"]) == ALL_PROFILES
    assert applicable(["documents/design/validation-routing.md"]) == ALL_PROFILES


def test_integration_event_selects_every_profile_without_paths() -> None:
    assert applicable([], event="push") == ALL_PROFILES
    assert applicable([], event="workflow_dispatch") == ALL_PROFILES


def test_unclassified_path_falls_back_to_base_project() -> None:
    assert applicable(["LICENSE"]) == {"base-project"}


def test_documented_runtime_file_selects_docs_and_docker() -> None:
    assert applicable(["docker/README.md"]) == {"docs", "docker-runtime"}


def test_non_applicable_failure_cannot_fail_the_change() -> None:
    plan = router.classify_paths(CONFIG, ["README.md"], "pull_request")
    outcomes = {
        "docs": "pass",
        "cpp": "fail",
        "github-automation": "fail",
        "docker-runtime": "fail",
        "bootstrap": "fail",
        "base-project": "fail",
    }
    result = router.aggregate_outcomes(plan, outcomes)
    assert result["docs"] == "pass"
    assert all(
        state == "not_applicable"
        for identifier, state in result.items()
        if identifier != "docs"
    )


def test_path_traversal_is_rejected() -> None:
    for path in ("../outside", "inside/../outside", "/absolute/path"):
        try:
            router.classify_paths(CONFIG, [path], "pull_request")
        except router.RoutingError:
            pass
        else:
            raise AssertionError(f"path traversal must fail closed: {path}")
