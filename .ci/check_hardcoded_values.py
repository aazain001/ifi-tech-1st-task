#!/usr/bin/env python3
"""
Parameter Decoupling Validation

Implements the check devops_framework_v1.txt already documents but never enforced:
"checks that all workspace target strings and connection paths are fully dynamic...
a script never contains hardcoded private workspace names."

Two different rules, because two different kinds of value need different treatment:

CATEGORY A - must never appear as a literal anywhere in deployable pipeline/notebook/SQL
logic, full stop. These are the values that got turned into pipeline parameters, a
VL_PlatformConfig variable, or an ELT.Config row - so there is never a legitimate reason
for the raw literal to reappear (that would mean someone bypassed the parameter and
hardcoded it again). VL_PlatformConfig's own Default value set is the one legitimate home
for these, since that IS where the Dev default is supposed to live.

CATEGORY B - connection IDs and notebook lakehouse-attachment metadata. Fabric does not
allow these to be pipeline expressions or variable-library references (see
docs/engineering_guide.txt), so the literal legitimately lives in the committed pipeline/
notebook source - that is what fabric-cicd's parameter.yml find_replace rewrites at deploy
time. The thing worth checking here is NOT "does this literal appear" (it is expected to),
but "does parameter.yml actually have a find_replace entry for it" - i.e. would deploying
to Test/Prod actually rewrite this, or did someone add a new connection/lakehouse without
wiring it into parameter.yml.

Add a new value here the same day you parameterize it, so a regression is caught the next
time someone reintroduces a hardcoded copy - accidentally or by copy-pasting an example.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PARAMETER_YML = REPO_ROOT / "parameter.yml"

SCAN_ROOTS = ["platform", "bronze", "silver", "gold", "governance", "operations"]
SCAN_EXTENSIONS = {".json", ".py", ".sql", ".yml", ".yaml", ".ipynb"}

# value -> (label, set of relative paths where it is the expected/canonical home)
CATEGORY_A_FORBIDDEN = {
    "controlDB-78d6902e-70ea-4fb0-b51e-af3f2aaee3b7": (
        "Control database name (should be @pipeline().parameters.ControlDatabase)",
        {"platform/config/VL_PlatformConfig.VariableLibrary/variables.json"},
    ),
    "AUS Eastern Standard Time": (
        "Hardcoded timezone (should come from ELT.Config via uf_GetAestDateTime)",
        {
            "platform/control-db/Script.PostDeployment.sql",
            "platform/config/VL_PlatformConfig.VariableLibrary/variables.json",
        },
    ),
    "WideWorldImporters": (
        "Source-system-specific sample value (belongs only in the WWI test harness)",
        {"silver/notebooks/tests/L1Transform-Test-WWI.Notebook/notebook-content.py"},
    ),
}

# value -> label. Presence in source is expected; presence in parameter.yml is what's checked.
CATEGORY_B_MUST_BE_IN_PARAMETER_YML = {
    "78e8d795-a55c-412e-9b76-47ba404b4d51": "Control DB connection ID",
    "a0a57e51-5032-4e46-b0f0-493c9d2f51c9": "Source SQL connection ID",
    "84da5653_bc83_445d_8f44_e1371107aad4": "Bronze lakehouse linked service name",
    "8d8d00a7-0e8a-4e3b-8c0e-8dcafac7adec": "Dev workspace ID",
    "c6c5024f-de55-45ca-a79a-decbe16235e3": "Bronze lakehouse ID",
    "cc80a0ab-603d-4df9-bdfc-c35a7e8ab095": "Silver lakehouse ID",
}


def relative_posix(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def iter_scan_files():
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in SCAN_EXTENSIONS:
                yield path


def check_category_a():
    violations = []
    for path in iter_scan_files():
        rel_path = relative_posix(path)
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for value, (label, allowed_paths) in CATEGORY_A_FORBIDDEN.items():
            if rel_path in allowed_paths:
                continue
            if value in content:
                line_no = content[: content.index(value)].count("\n") + 1
                violations.append((rel_path, line_no, label, value))
    return violations


def check_category_b():
    if not PARAMETER_YML.exists():
        return [("parameter.yml", 0, "parameter.yml is missing entirely", "")]
    yml_content = PARAMETER_YML.read_text(encoding="utf-8", errors="ignore")
    missing = []
    for value, label in CATEGORY_B_MUST_BE_IN_PARAMETER_YML.items():
        if value not in yml_content:
            missing.append(("parameter.yml", 0, f"{label} has no find_replace entry", value))
    return missing


def main() -> int:
    violations = check_category_a() + check_category_b()

    if violations:
        print("Parameter Decoupling Validation FAILED\n")
        for rel_path, line_no, label, value in violations:
            where = f"{rel_path}:{line_no}" if line_no else rel_path
            print(f"  {where}")
            print(f"    {label}" + (f": {value!r}" if value else "") + "\n")
        print(
            "Fix: for Category A values, replace the literal with a pipeline parameter, "
            "a VL_PlatformConfig variable, or an ELT.Config row. For Category B values "
            "(connection IDs, notebook lakehouse metadata), add a find_replace entry to "
            "parameter.yml - the literal itself is expected to stay in the pipeline/"
            "notebook source. See docs/engineering_guide.txt."
        )
        return 1

    print("Parameter Decoupling Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
