"""Step 5 - build the standalone dashboard as a single self-contained HTML file.

The dataset is embedded directly in the page, so the result opens from disk with
no server and no network access. For the version that saves your selection to
data/selection.json instead of to browser storage, run scripts/serve.py.

    python scripts/05_build_dashboard.py
    python scripts/05_build_dashboard.py --selftest OUT.html   # standalone test build

The paired-study boot block (empty draft, the cohort proposal as an unverified draft,
the study-document registry and source checksums) is embedded the same way, so the
standalone page carries the same study fields and validation as the served one.
--selftest writes a separate file with the test harness injected; it never touches
dashboard/dashboard.html.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import paired  # noqa: E402


def build(selftest=False):
    payload = common.payload_rows(common.load_dataset())
    blob = common.boot_json(payload)
    pboot = common.boot_json({"empty": paired.new_study(), "proposal": paired.proposal_to_study(),
                              "registry": paired.registry_rows(), "sources": paired.source_hashes()})
    tpl_path = os.path.join(common.DASHBOARD, "template.html")
    html = open(tpl_path, encoding="utf-8").read()
    html = (html.replace("__BOOT__", common.selftest_block() if selftest else "")
                .replace("__DATA__", blob)
                .replace("__PAIRED__", pboot)
                .replace("__COUNT__", "{:,}".format(len(payload)).replace(",", " ")))
    for token in ("__BOOT__", "__DATA__", "__PAIRED__", "__COUNT__"):
        assert token not in html, "template placeholder %s was not filled" % token
    return html, len(payload)


def main():
    ap = argparse.ArgumentParser(description="Build the standalone dashboard.")
    ap.add_argument("--selftest", metavar="OUT", help="write a standalone test build to OUT instead")
    a = ap.parse_args()
    common.ensure_dirs()
    html, n = build(selftest=bool(a.selftest))
    out = a.selftest or os.path.join(common.DASHBOARD, "dashboard.html")
    if a.selftest and os.path.abspath(out) == os.path.abspath(os.path.join(common.DASHBOARD, "dashboard.html")):
        raise SystemExit("refusing to write the test harness into dashboard/dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d rows, %.2f MB)" % (out, n, os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
