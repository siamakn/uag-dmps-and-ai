"""Step 5 - build the standalone dashboard as a single self-contained HTML file.

The dataset is embedded directly in the page, so the result opens from disk with
no server and no network access. For the version that saves your selection to
data/selection.json instead of to browser storage, run scripts/serve.py.

    python scripts/05_build_dashboard.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def main():
    common.ensure_dirs()
    payload = common.payload_rows(common.load_dataset())

    # "<\/" is a valid JSON escape for "/" and stops the browser from ending the
    # <script> block early if any title happens to contain "</script>".
    blob = json.dumps(payload, ensure_ascii=False,
                      separators=(",", ":")).replace("</", "<\\/")

    tpl_path = os.path.join(common.DASHBOARD, "template.html")
    html = open(tpl_path, encoding="utf-8").read()
    html = (html.replace("__BOOT__", "")
                .replace("__DATA__", blob)
                .replace("__COUNT__", "{:,}".format(len(payload)).replace(",", " ")))
    for token in ("__BOOT__", "__DATA__", "__COUNT__"):
        assert token not in html, "template placeholder %s was not filled" % token

    out = os.path.join(common.DASHBOARD, "dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d rows, %.2f MB)"
          % (out, len(payload), os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
