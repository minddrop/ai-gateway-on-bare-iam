"""Find the cost-estimate-template checkout and put its tools/ on sys.path.

The template and the generic scripts (estimate.py, fill.py, check.py,
snapshot.py) live in the cost-estimate-template repository. By default it is
expected next to this repository (../cost-estimate-template); set
COST_ESTIMATE_TEMPLATE to its path otherwise.
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("COST_ESTIMATE_TEMPLATE") or
                    pathlib.Path(__file__).resolve().parents[3] / "cost-estimate-template")
TEMPLATE = ROOT / "cost_estimate_template.xlsx"

if not (ROOT / "tools" / "estimate.py").is_file():
    raise SystemExit(f"cost-estimate-template not found at {ROOT}: clone it there or set COST_ESTIMATE_TEMPLATE")
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
