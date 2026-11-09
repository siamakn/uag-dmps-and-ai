"""Run the selection dashboard locally, with a small API behind it.

    python scripts/serve.py                     # UI + API on one port, opens a browser
    python scripts/serve.py --api-port 8757     # split: UI on 8756, API on 8757
    python scripts/serve.py --port 9000         # pick your own
    python scripts/serve.py --no-open           # do not launch a browser

Ports default to 8756 (UI) and 8757 (API), away from the usual 3000/5000/8000/8080
crowd. If a chosen port is busy the server steps up to the next free one and tells
you which it took.

Why a backend at all, when dashboard/dashboard.html already works from disk: the
standalone file can only keep your selection in browser storage. Served this way,
the selection is written to data/selection.json - a real file you can commit, diff
and hand to the next script. The API also serves the maDMP files straight from
data/madmp-corpus/, so inspecting one does not need a round trip to Zenodo.

Endpoints
    GET  /                      the dashboard
    GET  /selftest              the dashboard plus the functional self-test
    GET  /api/health            liveness and what is loaded
    GET  /api/dmps              the dataset the dashboard renders
    GET  /api/stats             pool counts and the discipline x stage matrix
    GET  /api/selection         the saved selection, resolved to full records
    PUT  /api/selection         {"ids": [...]} -> writes data/selection.json
    GET  /api/madmp/<file>      one maDMP file from the local corpus

  paired study (separate storage; never touches data/selection.json)
    GET  /api/paired            the paired-study draft, or 409 if the file is corrupt
    PUT  /api/paired            {"study": {...}} -> writes data/paired_selection.json
    POST /api/paired/validate   {"study": {...}} -> the Python validation result
    POST /api/paired/files      {"study": {...}, "download": bool} -> local file checksums
    POST /api/paired/freeze     {"study": {...}} -> immutable data/paired-snapshots/<id>.json
    GET  /api/paired/snapshots  the frozen snapshots on disk

  human-review pilot (separate storage under <state-dir>/review/)
    GET  /api/review            review drafts + locked records; 409 if the draft file is corrupt
    PUT  /api/review/state      {"state": {...}} -> review/review_state.json (drafts only)
    POST /api/review/submit     {"submission": {"record", "raw_response"}} -> review/records/<id>.json
                                (created once, never rewritten; 409 if the id exists)
    POST /api/review/validate   {"record": {...}} -> schema + pilot checks, no write
    GET  /api/review/source/<artifact_id>   a task's source PDF (whitelisted artifacts only)

--state-dir DIR keeps selection.json, paired_selection.json and paired-snapshots/ in DIR
instead of data/. /selftest refuses to run against the real data/ directory, because the
harness saves and clears selections; use --test (a fresh temporary state dir) instead.

Stdlib only. Binds to 127.0.0.1, so nothing is exposed off this machine.
"""
import argparse
import collections
import datetime
import errno
import json
import os
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import paired  # noqa: E402
import review  # noqa: E402

UI_PORT = 8756
API_PORT = 8757
PATHS = {}
STATE = {"rows": [], "payload": [], "html": "", "html_test": "", "api_base": "/api"}


def set_state_dir(state_dir):
    state_dir = os.path.abspath(state_dir or common.DATA)
    os.makedirs(state_dir, exist_ok=True)
    PATHS.update(
        state=state_dir,
        default=state_dir == os.path.abspath(common.DATA),
        selection=os.path.join(state_dir, "selection.json"),
        paired=os.path.join(state_dir, paired.STUDY_FILE),
    )


set_state_dir(common.DATA)


def paired_boot():
    return {"empty": paired.new_study(), "proposal": paired.proposal_to_study(),
            "registry": paired.registry_rows(), "sources": paired.source_hashes()}


# ----------------------------------------------------------------- data
def load_state(api_base):
    rows = common.load_dataset()
    payload = common.payload_rows(rows)
    tpl_path = os.path.join(common.DASHBOARD, "template.html")
    if not os.path.exists(tpl_path):
        raise SystemExit("dashboard/template.html is missing")
    tpl = open(tpl_path, encoding="utf-8").read()
    boot = '<script>window.DMP_API=%s;</script>' % json.dumps(api_base)
    count = "{:,}".format(len(payload)).replace(",", " ")

    pboot = common.boot_json(paired_boot())
    rboot = common.boot_json(review.boot())

    def fill(boot_block):
        return (tpl.replace("__BOOT__", boot_block)
                   .replace("__DATA__", "null")
                   .replace("__PAIRED__", pboot)
                   .replace("__REVIEW__", rboot)
                   .replace("__COUNT__", count))

    html = fill(boot)

    # /selftest serves the same page with the test harness injected ahead of the
    # app script, so it can hook window.__ONREADY__. Never part of a built file.
    html_test = ""
    test_path = os.path.join(common.DASHBOARD, "selftest.js")
    if os.path.exists(test_path):
        html_test = fill(boot + common.selftest_block())

    STATE.update(rows=rows, payload=payload, html=html, html_test=html_test,
                 api_base=api_base)
    return len(payload)


def read_selection():
    if not os.path.exists(PATHS["selection"]):
        return []
    try:
        d = json.load(open(PATHS["selection"], encoding="utf-8"))
    except Exception:
        return []
    return d.get("ids", []) if isinstance(d, dict) else []


def write_selection(ids):
    index = {r["id"]: r for r in STATE["payload"]}
    # ids the current dataset does not know are kept, never silently dropped
    ids = [str(i) for i in ids]
    picked = [index[i] for i in ids if i in index]
    doc = {
        "saved": datetime.datetime.now().isoformat(timespec="seconds"),
        "count": len(ids),
        "ids": ids,
        "unresolved": [i for i in ids if i not in index],
        "matrix": matrix_of(picked),
        "selection": [{
            "doi": r["doi"], "zenodo": r["url"], "title": r["title"],
            "published": r["date"], "funder": r["tier"], "grant": r["grant"],
            "project": r["acronym"], "discipline": r["disc"], "stage": r["stage"],
            "stage_position": r["stage_frac"], "madmp": r["madmp"],
            "datasets": r["n_datasets"], "schema_clean": r["schema_ok"],
            "challenging": r["challenging"],
        } for r in picked],
    }
    tmp = PATHS["selection"] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PATHS["selection"])
    return doc


# ----------------------------------------------------------------- paired study
def write_paired(study, replace_corrupt=False):
    """Save a paired-study draft. Never overwrites a corrupt file unless asked, and then
    keeps its bytes next to it first."""
    reason = paired.check_study(study)
    if reason:
        return 400, {"error": "refused: " + reason}
    if study.get("status") == "frozen":
        return 400, {"error": "refused: a frozen study is a snapshot; load it as a new draft instead"}
    path = PATHS["paired"]
    _, err = paired.read_study(path)
    kept = None
    if err:
        if not replace_corrupt:
            return 409, {"error": err, "corrupt": True}
        stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        kept = path.replace(".json", ".corrupt-%s.json" % stamp)
        os.replace(path, kept)
    study["updated"] = paired.now_iso()
    study["sources"] = paired.source_hashes()
    paired.write_atomic(path, paired.canonical(study))
    return 200, {"ok": True, "file": path, "updated": study["updated"], "kept_corrupt_file": kept}


def list_snapshots():
    d = os.path.join(PATHS["state"], paired.SNAPSHOT_DIR)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        if name.endswith(".json"):
            full = os.path.join(d, name)
            out.append({"snapshot_id": name[:-5], "path": full,
                        "content_hash_ok": paired.verify_snapshot(full)})
    return out


def matrix_of(picked):
    m = collections.defaultdict(lambda: {"early": 0, "mid": 0, "late": 0})
    for r in picked:
        d = r.get("disc") or "unclassified"
        if r.get("stage") in ("early", "mid", "late"):
            m[d][r["stage"]] += 1
    return {k: dict(v) for k, v in m.items()}


def stats():
    rows = STATE["payload"]
    he24 = [r for r in rows if r["tier"] == "Horizon Europe" and (r["year"] or "") >= "2024"]
    cell = collections.Counter((r["disc"], r["stage"]) for r in he24
                               if r["disc"] and r["stage"] in ("early", "mid", "late"))
    discs = [d for d, _ in collections.Counter(
        r["disc"] for r in he24 if r["disc"]).most_common()]
    return {
        "records": len(rows),
        "madmps": sum(1 for r in rows if r["madmp"]),
        "by_tier": dict(collections.Counter(r["tier"] for r in rows)),
        "by_stage": dict(collections.Counter(r["stage"] for r in rows)),
        "horizon_europe_2024plus": {
            "records": len(he24),
            "madmps": sum(1 for r in he24 if r["madmp"]),
            "projects": len({r["grant"] for r in he24 if r["grant"]}),
            "matrix": {d: {s: cell[(d, s)] for s in ("early", "mid", "late")}
                       for d in discs},
        },
    }


# ----------------------------------------------------------------- http
class Handler(BaseHTTPRequestHandler):
    server_version = "dmpbench/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        if "--verbose" in sys.argv:
            sys.stderr.write("  %s %s\n" % (self.command, self.path))

    # --- helpers
    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # only ever reachable from this machine; needed when UI and API are split
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_OPTIONS(self):
        self._send(204)

    def do_HEAD(self):
        self.do_GET()

    # --- routes
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"

        if path in ("/", "/index.html"):
            if not STATE["html"]:
                return self._send(404, b"UI is served on the other port")
            return self._send(200, STATE["html"].encode("utf-8"),
                              "text/html; charset=utf-8")

        if path == "/selftest":
            # The harness saves and clears selections. Against the real data/ that
            # would destroy the user's work, so it only runs with a separate state dir.
            if PATHS["default"]:
                return self._send(409, b"/selftest writes and clears selections, so it will not run "
                                       b"against data/. Start the server with --test (a fresh "
                                       b"temporary state dir) or --state-dir DIR.")
            # rebuilt from disk on every request so editing the harness or the
            # template does not need a server restart
            try:
                load_state(STATE["api_base"])
            except Exception as e:
                return self._send(500, ("rebuild failed: %s" % e).encode("utf-8"))
            if not STATE.get("html_test"):
                return self._send(404, b"dashboard/selftest.js is not present")
            return self._send(200, STATE["html_test"].encode("utf-8"),
                              "text/html; charset=utf-8")

        if path == "/api/health":
            return self._json({"ok": True, "records": len(STATE["payload"]),
                               "selection": len(read_selection()),
                               "corpus": os.path.isdir(common.CORPUS),
                               "state_dir": PATHS["state"],
                               "state_dir_is_default": PATHS["default"]})
        if path == "/api/paired":
            study, err = paired.read_study(PATHS["paired"])
            if err:
                return self._json({"error": err, "corrupt": True, "file": PATHS["paired"]}, 409)
            return self._json({"study": study, "file": PATHS["paired"]})
        if path == "/api/review":
            state, err = review.read_state(PATHS["state"])
            subs, bad = review.list_records(PATHS["state"])
            body = {"state": state, "records": subs, "unreadable": bad,
                    "dir": review.paths(PATHS["state"])["dir"]}
            if err:
                body.update(error=err, corrupt=True)
                return self._json(body, 409)
            return self._json(body)
        if path.startswith("/api/review/source/"):
            from urllib.parse import unquote
            full = review.servable_artifact(unquote(path[len("/api/review/source/"):]))
            if not full:
                return self._json({"error": "no such source artifact"}, 404)
            with open(full, "rb") as f:
                return self._send(200, f.read(), "application/pdf")
        if path == "/api/paired/snapshots":
            return self._json({"snapshots": list_snapshots()})
        if path == "/api/dmps":
            return self._json({"count": len(STATE["payload"]), "rows": STATE["payload"]})
        if path == "/api/stats":
            return self._json(stats())
        if path == "/api/selection":
            ids = read_selection()
            index = {r["id"]: r for r in STATE["payload"]}
            return self._json({"ids": ids,
                               "selection": [index[i] for i in ids if i in index]})
        if path.startswith("/api/madmp/"):
            from urllib.parse import unquote
            name = os.path.basename(unquote(path[len("/api/madmp/"):]))
            target = os.path.join(common.CORPUS, name)
            # basename() already strips any traversal; this re-checks the result
            if not os.path.isfile(target) or os.path.dirname(
                    os.path.abspath(target)) != os.path.abspath(common.CORPUS):
                return self._json({"error": "no such maDMP file", "file": name}, 404)
            with open(target, "rb") as f:
                return self._send(200, f.read(), "application/json; charset=utf-8")

        return self._json({"error": "not found", "path": path}, 404)

    def do_PUT(self):
        self.do_POST()

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        if path.startswith("/api/review"):
            return self._review_post(path)
        if path.startswith("/api/paired"):
            return self._paired_post(path)
        if path != "/api/selection":
            return self._json({"error": "not found"}, 404)
        try:
            body = self._body()
            ids = body.get("ids", []) if isinstance(body, dict) else body
            if not isinstance(ids, list):
                raise ValueError("expected an ids list")
        except Exception as e:
            return self._json({"error": "bad request: %s" % e}, 400)
        doc = write_selection(ids)
        return self._json({"ok": True, "count": doc["count"], "file": PATHS["selection"]})

    def _review_post(self, path):
        try:
            body = self._body()
            if not isinstance(body, dict):
                raise ValueError("expected a JSON object")
        except Exception as e:
            return self._json({"error": "bad request: %s" % e}, 400)
        if path == "/api/review/state":
            code, res = review.write_state(PATHS["state"], body.get("state"), bool(body.get("replace_corrupt")))
            return self._json(res, code)
        if path == "/api/review/submit":
            code, res = review.submit(PATHS["state"], body.get("submission"))
            return self._json(res, code)
        if path == "/api/review/validate":
            rec = body.get("record")
            if not isinstance(rec, dict):
                return self._json({"error": "expected {\"record\": {...}}"}, 400)
            existing = {s["record"]["record_id"] for s in review.list_records(PATHS["state"])[0]}
            problems = review.validate_record(rec, existing)
            return self._json({"valid": not problems, "problems": problems})
        return self._json({"error": "not found"}, 404)

    def _paired_post(self, path):
        try:
            body = self._body()
            study = body.get("study") if isinstance(body, dict) else None
            if not isinstance(study, dict):
                raise ValueError("expected {\"study\": {...}}")
        except Exception as e:
            return self._json({"error": "bad request: %s" % e}, 400)
        if path == "/api/paired":
            code, res = write_paired(study, bool(body.get("replace_corrupt")))
            return self._json(res, code)
        reason = paired.check_study(study)
        if reason:
            return self._json({"error": "refused: " + reason}, 400)
        if path == "/api/paired/validate":
            return self._json(paired.validate(study))
        if path == "/api/paired/files":
            facts = paired.file_facts(study)
            if body.get("download"):
                facts = paired.download_missing(study, facts)
            return self._json({"facts": facts})
        if path == "/api/paired/freeze":
            try:
                ok, res = paired.freeze(study, PATHS["state"])
            except FileExistsError:
                return self._json({"ok": False, "reasons": ["a snapshot with this id already exists"]}, 409)
            res["ok"] = ok
            return self._json(res, 200 if ok else 422)
        return self._json({"error": "not found"}, 404)


class ApiOnly(Handler):
    """Same routes, minus the UI - used when the API runs on its own port."""

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path in ("/", "/index.html"):
            return self._json({"error": "the dashboard is on the UI port"}, 404)
        return Handler.do_GET(self)


class Server(ThreadingHTTPServer):
    # HTTPServer sets allow_reuse_address, which on Windows lets a second process
    # bind a port another process already holds. That silently breaks the
    # busy-port fallback below, so turn it off and let the bind fail properly.
    allow_reuse_address = False
    daemon_threads = True


BUSY = {errno.EADDRINUSE, errno.EACCES, 10048, 10013, 98}


def bind(port, handler, tries=20):
    """Take the requested port, or the next free one above it."""
    for p in range(port, port + tries):
        try:
            return Server(("127.0.0.1", p), handler), p
        except OSError as e:
            if e.errno not in BUSY:
                raise
    raise SystemExit("no free port between %d and %d" % (port, port + tries - 1))


def main():
    ap = argparse.ArgumentParser(description="Serve the DMP selection dashboard locally.")
    ap.add_argument("--port", type=int, default=UI_PORT, help="UI port (default %d)" % UI_PORT)
    ap.add_argument("--api-port", type=int, default=None,
                    help="serve the API on its own port (default: same as the UI)")
    ap.add_argument("--no-open", action="store_true", help="do not launch a browser")
    ap.add_argument("--verbose", action="store_true", help="log every request")
    ap.add_argument("--state-dir", default=None,
                    help="where selection.json, paired_selection.json and paired-snapshots/ live "
                         "(default: data/)")
    ap.add_argument("--test", action="store_true",
                    help="use a fresh temporary state dir; required for /selftest")
    args = ap.parse_args()

    common.ensure_dirs()
    if args.test:
        set_state_dir(tempfile.mkdtemp(prefix="dmpbench-test-"))
    elif args.state_dir:
        set_state_dir(args.state_dir)
    servers = []
    if args.api_port is None:
        ui, ui_port = bind(args.port, Handler)
        n = load_state("/api")
        api_port = ui_port
        servers.append(ui)
    else:
        api, api_port = bind(args.api_port, ApiOnly)
        ui, ui_port = bind(args.port, Handler)
        n = load_state("http://127.0.0.1:%d/api" % api_port)
        servers += [api, ui]

    url = "http://127.0.0.1:%d/" % ui_port
    print("DMP Selection Bench")
    print("  dashboard   %s" % url)
    print("  api         http://127.0.0.1:%d/api" % api_port)
    print("  dataset     %d records, %d maDMPs"
          % (n, sum(1 for r in STATE["payload"] if r["madmp"])))
    print("  selection   %s" % PATHS["selection"])
    print("  paired      %s" % PATHS["paired"])
    if not PATHS["default"]:
        print("  state dir   %s  (not data/; /selftest enabled)" % PATHS["state"])
    if args.port != ui_port or (args.api_port and args.api_port != api_port):
        print("  note: a requested port was busy, moved up to the next free one")
    print("  ctrl-c to stop")
    sys.stdout.flush()

    for s in servers[:-1]:
        threading.Thread(target=s.serve_forever, daemon=True).start()
    if not args.no_open:
        # No browser on a headless box (a bare Ubuntu server, WSL without a
        # desktop). Failing to open one is not a reason to make noise.
        def open_browser():
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Timer(0.4, open_browser).start()
    try:
        servers[-1].serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        for s in servers:
            s.shutdown()


if __name__ == "__main__":
    main()
