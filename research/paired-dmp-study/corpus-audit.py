"""Read-only local inventory; writes only corpus-audit.json beside this script.

Run from any directory: python3 research/paired-dmp-study/corpus-audit.py
No network requests, corpus regeneration, or selection changes.
"""
import calendar
import collections
import datetime
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_suffix('.json')
BRANCHES = ['natural sciences', 'engineering and technology',
            'medical and health sciences', 'agricultural sciences',
            'social sciences', 'humanities']
EU = {'Horizon Europe', 'Horizon 2020', 'Other EU'}
rows = json.loads((ROOT / 'data/dmp_dataset.json').read_text())


def date_interval(value):
    try:
        if len(value) == 4:
            return datetime.date(int(value), 1, 1), datetime.date(int(value), 12, 31)
        if len(value) == 7:
            year, month = map(int, value.split('-'))
            return (datetime.date(year, month, 1),
                    datetime.date(year, month, calendar.monthrange(year, month)[1]))
        if len(value) == 10:
            d = datetime.date.fromisoformat(value)
            return d, d
    except (ValueError, TypeError):
        pass
    return None


def position(row):
    try:
        p, s, e = [datetime.date.fromisoformat(row[k])
                   for k in ('date', 'proj_start', 'proj_end')]
        n, d = (p - s).days, (e - s).days
        if len(row['date']) == 10 and d > 0:
            role = ('early' if 0 <= 2*n <= d else
                    'late' if n > d else 'pre-start' if n < 0 else 'middle')
            return {'elapsed_days': n, 'duration_days': d, 'fraction': n/d,
                    'early_late_role': role}
    except (ValueError, TypeError):
        pass
    return None


def interval_role(row):
    try:
        start, end = [datetime.date.fromisoformat(row[k])
                      for k in ('proj_start', 'proj_end')]
        bounds = date_interval(row['date'])
        if bounds and end > start:
            lo, hi = bounds
            if lo >= start and 2*(hi-start).days <= (end-start).days:
                return 'early'
            if lo > end:
                return 'late'
    except (ValueError, TypeError):
        pass
    return ''


def eligible(row, recent=False, he=False):
    return (row['kind'] == 'dmp' and row['tier'] in EU and row['grant']
            and row['disc'] and row['access'] == 'public' and row['files']
            and (not recent or row['year'] >= '2024')
            and (not he or row['tier'] == 'Horizon Europe'))


def groups(recent=False, he=False, intervals=False):
    grants = collections.defaultdict(lambda: {'early': [], 'late': []})
    for row in rows:
        if not eligible(row, recent, he):
            continue
        pos = position(row)
        role = interval_role(row) if intervals else (pos or {}).get('early_late_role')
        if role in ('early', 'late'):
            grants[row['grant']][role].append(row)
    return {k: v for k, v in grants.items() if v['early'] and v['late']}


def summary(grants):
    return {
        'grants': len(grants),
        'record_combinations': sum(len(v['early'])*len(v['late']) for v in grants.values()),
        'primary_disc_grants': {b: sum(any(x['disc'] == b for x in v['early'])
                                      for v in grants.values()) for b in BRANCHES},
        'disc_all_grants': {b: sum(any(b in x['disc_all'] for x in v['early'])
                                  for v in grants.values()) for b in BRANCHES},
    }


def compact(row):
    fields = ('id', 'doi', 'url', 'title', 'date', 'version', 'grant', 'acronym',
              'tier', 'disc', 'disc_all', 'proj_start', 'proj_end', 'stage_src',
              'stage', 'stage_frac', 'access', 'files', 'madmp', 'madmp_file')
    out = {k: row.get(k) for k in fields}
    out['exact_position'] = position(row)
    out['interval_role'] = interval_role(row)
    return out


raw_paths = sorted((ROOT / 'data/raw').glob('*.jsonl'))
raw = {}
for path in raw_paths:
    for line in path.read_text().splitlines():
        value = json.loads(line)
        raw[str(value['id'])] = value
selection = json.loads((ROOT / 'data/selection.json').read_text())
by_id = {x['id']: x for x in rows}
selection_rows = [by_id[x] for x in selection['ids'] if x in by_id]
inputs = [ROOT / 'data/dmp_dataset.json', ROOT / 'data/selection.json',
          ROOT / 'AGENTS.md', ROOT / 'scripts/common.py',
          ROOT / 'scripts/01_harvest_records.py', ROOT / 'scripts/04_build_dataset.py',
          ROOT / 'dashboard/template.html'] + raw_paths
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in inputs}
rounding_mismatches = []
for row in rows:
    p = position(row)
    f = row['stage_frac']
    if p and f is not None and (
            (0 <= 2*p['elapsed_days'] <= p['duration_days']) != (0 <= f <= .5)
            or (p['elapsed_days'] > p['duration_days']) != (f > 1)):
        rounding_mismatches.append(compact(row))

report = {
    'audit_date': '2026-11-03',
    'method': {
        'early': '0 <= 2 * (publication - project_start).days <= (project_end - project_start).days',
        'late': '(publication - project_start).days > (project_end - project_start).days',
        'filters': 'kind=dmp; EU tier; nonempty grant and primary CORDIS discipline; public record; listed file',
        'exact_dates': 'YYYY-MM-DD only; integer day comparison, not stage label or rounded stage_frac',
        'interval_dates': 'YYYY-MM spans calendar month; YYYY spans year; accept only when entire interval qualifies',
        'identity_warning': 'Same-grant combinations are leads, not verified versions of the same DMP/scope.',
        'access_warning': 'Public record + listed file is not verified public downloadable file access.',
    },
    'input_sha256': hashes,
    'inventory': {
        'rows': len(rows), 'kind_counts': dict(collections.Counter(x['kind'] for x in rows)),
        'tier_counts': dict(collections.Counter(x['tier'] for x in rows)),
        'raw_unique_records': len(raw),
        'raw_fields': sorted({k for x in raw.values() for k in x}),
        'date_string_lengths': dict(collections.Counter(len(x['date'] or '') for x in rows)),
        'nonempty_version_strings': sum(bool(x['version']) for x in rows),
        'local_cordis_files': [str(p.relative_to(ROOT)) for p in (ROOT / 'data/cordis').glob('*')],
    },
    'summary': {name: summary(groups(recent, he, intervals))
                for name, recent, he, intervals in [
                    ('EU_full_dates', False, False, False),
                    ('HE_full_dates', False, True, False),
                    ('EU_both_2024plus_full_dates', True, False, False),
                    ('HE_both_2024plus_full_dates', True, True, False),
                    ('EU_safe_intervals', False, False, True),
                    ('HE_safe_intervals', False, True, True)]},
    'selection': {'saved': selection.get('saved'), 'count': len(selection['ids']),
                  'resolved': len(selection_rows),
                  'distinct_grants': len({x['grant'] for x in selection_rows}),
                  'records': [compact(x) for x in selection_rows]},
    'rounding_threshold_mismatches': rounding_mismatches,
    'same_grant_leads_full_dates': {k: {role: [compact(x) for x in v[role]]
                                      for role in ('early', 'late')}
                                  for k, v in sorted(groups().items())},
    'additional_leads_with_safe_intervals': {
        k: {role: [compact(x) for x in v[role]] for role in ('early', 'late')}
        for k, v in sorted(groups(intervals=True).items()) if k not in groups()},
}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report['summary'], indent=2))
print('Wrote', OUT.relative_to(ROOT))
