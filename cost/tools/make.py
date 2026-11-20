"""Build the IAM-native LLM gateway estimate: the English and Japanese workbooks
and markdown snapshots in cost/.

Usage: python make.py [cost_estimate_template.xlsx]

Needs openpyxl (requirements.txt) and a checkout of cost-estimate-template,
whose tools/ do the generic work (see template_tools.py). The template
defaults to the one in that checkout.

For each language: fill a copy of the template (fill.py), check its structure
against the template (check.py), recalculate its Summary from the filled cells
and compare it with the model, and write the markdown (md.py). When
ai-gateway-on-aws is checked out next to this repository (or
LGW_REPO is set), its estimate is recomputed and compared with the [LGW]
figures that section 7 quotes. Exits with status 1 if a check fails or a
Japanese string is missing.
"""
import json
import os
import pathlib
import subprocess
import sys

import md
import model as M
import template_tools
from check import recalc, structure
from estimate import compute
from fill import fill
from snapshot import Translator
from tx import JA

OUT = pathlib.Path(__file__).resolve().parents[1]
FILES = {"en": (md.XLSX, md.MD), "jp": (md.XLSX_JP, md.MD_JP)}
LGW_REPO = pathlib.Path(os.environ.get("LGW_REPO") or OUT.parents[1] / "ai-gateway-on-aws")

LGW_PROBE = """
import json, model as M
from estimate import compute, T_OT, U_PM, U_PD
rows, envs = M.estimate_rows()
r = compute(rows, M.RATES, M.DAYS, M.PARAMS)
ex = (sum(i['qty'] for i in r.items if i['type'] == T_OT and i['key'] != 'con' and i['unit'] == U_PM) +
      sum(i['qty'] for i in r.items if i['type'] == T_OT and i['key'] != 'con' and i['unit'] == U_PD) / M.DAYS)
u = sum(x['usd'] for x in M.usage()['Expected'].values()) * M.FX
print(json.dumps(dict(initial=r.initial, monthly=r.monthly, effort=r.effort, effort_excl_con=ex, dev=r.dev, pm=r.pm,
                      ot=r.ot, rc=r.rc, cont_ot=r.cont_ot, cont_rc=r.cont_rc, usage_expected=u,
                      env_usd=dict(zip(('prod', 'dr', 'dev', 'stg'), (M.tot(e) for e in envs))))))
"""


def check_lgw():
    """Recompute [LGW] from its repository and compare with model.LGW. Returns problems."""
    tools = LGW_REPO / "cost" / "tools"
    if not (tools / "model.py").is_file():
        print(f"[LGW] not found at {LGW_REPO}: section 7 uses the figures in model.LGW unchecked")
        return []
    head = subprocess.run(["git", "-C", str(LGW_REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    p = subprocess.run([sys.executable, "-c", LGW_PROBE], cwd=tools, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    if p.returncode:
        return [f"[LGW] could not be recomputed: {p.stderr.strip().splitlines()[-1]}"]
    got, bad = json.loads(p.stdout), []
    for k, want in M.LGW.items():
        if k == "commit":
            continue
        g = got[k]
        pairs = [(f"{k}.{x}", want[x], g[x]) for x in want] if isinstance(want, dict) else [(k, want, g)]
        bad += [f"[LGW] {name} is {b} at {head}, {a} in model.LGW" for name, a, b in pairs if abs(a - b) > 0.01]
    print(f"[LGW] recomputed at {head}: " + ("matches model.LGW" if not bad else f"{len(bad)} differences"))
    return bad


def main(template):
    failed = check_lgw()
    for lang, (xlsx, mdfile) in FILES.items():
        T = Translator(lang, JA)
        est, _ = md.estimate(lang, T)
        project = dict(M.PROJECT, name=T(M.PROJECT["name"]), prepared_by=T(M.PROJECT["prepared_by"]))
        fill(template, OUT / xlsx, project, est["items"], est["assumptions"], est["exclusions"],
             params=M.PARAMS, rates=M.RATES, days=M.DAYS)
        failed += [f"{xlsx}: {p}" for p in structure(template, OUT / xlsx)]
        want = compute(est["items"], M.RATES, M.DAYS, M.PARAMS)
        _, got = recalc(OUT / xlsx)
        for k in ("initial", "monthly", "c60", "c61", "effort"):
            if abs(getattr(want, k) - getattr(got, k)) > 0.001:
                failed.append(f"{xlsx}: {k} is {getattr(got, k)} in the workbook, {getattr(want, k)} in the model")
        if got.checks != want.checks:
            failed.append(f"{xlsx}: checks {got.checks} in the workbook, {want.checks} in the model")
        failed += [f"{xlsx}: check {k} = {v}" for k, v in got.checks.items() if abs(v) >= 0.5]
        text, missing = md.render(lang)
        (OUT / mdfile).write_text(text)
        failed += [f"{mdfile}: no Japanese for {s!r}" for s in dict.fromkeys(T.missing + missing)]
        print(f"{lang}: {len(est['items'])} line items; initial {got.initial:,.0f}, monthly {got.monthly:,.2f}, "
              f"grand total ({M.PARAMS.months} months) {got.grand():,.0f} excl. tax; checks {got.checks}")
    for f in failed:
        print("FAILED:", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else template_tools.TEMPLATE))
