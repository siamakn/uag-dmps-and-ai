"""Step 3 - check every downloaded maDMP against the RDA DMP Common Standard.

This is a deliberately small checker rather than a full JSON Schema validator:
it walks the official maDMP schema and reports required properties that are
absent or empty, values outside an enum, and wrong primitive types. That covers
what matters for judging whether a file is a usable maDMP, with no third-party
dependency to install.

Findings are informational. Most real maDMPs on Zenodo have some - the common
one is a distribution object with no title and no data_access - and that
incompleteness is itself interesting for a DMP review benchmark.

    python scripts/03_check_schema.py
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SCHEMA_URL = ("https://raw.githubusercontent.com/RDA-DMP-Common/"
              "RDA-DMP-Common-Standard/master/examples/JSON/JSON-schema/1.2/"
              "maDMP-schema-1.2.json")
SCHEMA_PATH = os.path.join(common.DATA, "maDMP-schema-1.2.json")


def load_schema():
    if not os.path.exists(SCHEMA_PATH):
        print("fetching RDA maDMP schema 1.2")
        with open(SCHEMA_PATH, "wb") as f:
            f.write(common.fetch(SCHEMA_URL,
                                 headers={"User-Agent": common.HEADERS["User-Agent"]}))
    return json.load(open(SCHEMA_PATH, encoding="utf-8"))


def resolve(node, root, depth=0):
    while isinstance(node, dict) and "$ref" in node and depth < 10:
        ref = node["$ref"]
        depth += 1
        if not ref.startswith("#/"):
            return node
        cur = root
        for part in ref[2:].split("/"):
            cur = cur[part]
        node = cur
    return node


def check(inst, sch, root, path, errs):
    sch = resolve(sch, root)
    if not isinstance(sch, dict):
        return
    t = sch.get("type")
    if t == "object" or (isinstance(t, list) and "object" in t) or "properties" in sch:
        if not isinstance(inst, dict):
            errs.append("%s: expected object, got %s" % (path, type(inst).__name__))
            return
        for r in sch.get("required", []):
            if r not in inst or inst[r] is None:
                errs.append("%s.%s: absent required" % (path, r))
            elif inst[r] == "":
                errs.append("%s.%s: empty required" % (path, r))
        for k, sub in (sch.get("properties") or {}).items():
            if k in inst and inst[k] is not None:
                check(inst[k], sub, root, "%s.%s" % (path, k), errs)
    elif t == "array" or "items" in sch:
        if not isinstance(inst, list):
            errs.append("%s: expected array, got %s" % (path, type(inst).__name__))
            return
        for i, x in enumerate(inst):
            check(x, sch.get("items", {}), root, "%s[%d]" % (path, i), errs)
    else:
        if "enum" in sch and inst not in sch["enum"]:
            errs.append("%s: value %s not in enum %s"
                        % (path, json.dumps(inst)[:40], sch["enum"]))
        if t == "string" and not isinstance(inst, str):
            errs.append("%s: expected string, got %s" % (path, type(inst).__name__))
        if (sch.get("format") == "date-time" and isinstance(inst, str)
                and not re.match(r"^\d{4}-\d{2}-\d{2}[T ]", inst)):
            errs.append("%s: not a date-time: %s" % (path, inst[:25]))


def main():
    common.ensure_dirs()
    schema = load_schema()
    results, clean = {}, 0
    for p in sorted(glob.glob(os.path.join(common.CORPUS, "*.json"))):
        name = os.path.basename(p)
        try:
            o = json.load(open(p, encoding="utf-8-sig"))
        except Exception as e:
            results[name] = ["unparseable: %s" % str(e)[:60]]
            continue
        if not (isinstance(o, dict) and "dmp" in o):
            continue
        errs = []
        check(o, schema, schema, "$", errs)
        results[name] = errs
        if not errs:
            clean += 1
    out = os.path.join(common.DATA, "schema_findings.json")
    json.dump(results, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("checked %d maDMP files: %d clean, %d with findings"
          % (len(results), clean, len(results) - clean))

    tally = {}
    for errs in results.values():
        for e in errs:
            key = re.sub(r"\[\d+\]", "[]", e).split(":")[0]
            tally[key] = tally.get(key, 0) + 1
    print("most frequent findings:")
    for k, n in sorted(tally.items(), key=lambda x: -x[1])[:8]:
        print("  %6d  %s" % (n, k))


if __name__ == "__main__":
    main()
