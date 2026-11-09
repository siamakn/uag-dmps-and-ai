#!/usr/bin/env python3
"""Offline publication-date triage of saved version leads; never eligibility."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def full_date(value):
    if not isinstance(value, str) or len(value) != 10:
        return None
    try:
        parsed = datetime.date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    dataset_path = ROOT / 'data/dmp_dataset.json'
    versions_path = ROOT / 'data/paired-discovery/versions.json'
    dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
    versions = json.loads(versions_path.read_text(encoding='utf-8'))
    index = {str(row['id']): row for row in dataset}
    candidates = []
    incomplete = []
    seen = set()
    for lead in versions['leads']:
        known = [index[str(key)] for key in lead['in_dataset'] if str(key) in index]
        for row in known:
            if row.get('tier') not in ('Horizon Europe', 'Horizon 2020'):
                continue
            key = (str(row['grant']), str(lead['concept']))
            if key in seen:
                continue
            seen.add(key)
            start, end = full_date(row.get('proj_start')), full_date(row.get('proj_end'))
            if not start or not end or end <= start:
                incomplete.append({'grant': row['grant'], 'concept': lead['concept'],
                                   'reason': 'missing_or_invalid_cached_project_dates'})
                continue
            items = {str(v['id']): {'id': str(v['id']), 'date': v['published'],
                                   'title': v['title'], 'origin': 'absent_from_dataset'}
                     for v in lead['absent_from_dataset']}
            for v in known:
                items[str(v['id'])] = {'id': str(v['id']), 'date': v['date'],
                                      'title': v['title'], 'origin': 'in_dataset'}
            early, late, undated = [], [], []
            for item in items.values():
                date = full_date(item['date'])
                if not date:
                    undated.append(item['id'])
                    continue
                n, d = (date - start).days, (end - start).days
                item.update({'url': 'https://zenodo.org/records/' + item['id'],
                             'publication_elapsed_days': n, 'cached_duration_days': d})
                if 0 <= n and 2 * n <= d:
                    early.append(item)
                if n > d:
                    late.append(item)
            if undated:
                incomplete.append({'grant': row['grant'], 'concept': lead['concept'],
                                   'reason': 'non_full_publication_dates', 'ids': undated})
            if early and late:
                candidates.append({'grant': str(row['grant']), 'acronym': row['acronym'],
                                   'tier': row['tier'], 'concept': str(lead['concept']),
                                   'cached_branches': row.get('disc_all', []),
                                   'cached_start': start.isoformat(), 'cached_end': end.isoformat(),
                                   'publication_early_leads': sorted(early, key=lambda v: (v['date'], v['id'])),
                                   'publication_late_leads': sorted(late, key=lambda v: (v['date'], v['id'])),
                                   'eligibility': 'not_established'})
    candidates.sort(key=lambda r: (r['tier'] != 'Horizon Europe', not bool(r['cached_branches']), r['acronym']))
    return {'schema_version': 1, 'kind': 'publication_only_followup_triage_not_pair_selection',
            'source_hashes': {str(p.relative_to(ROOT)): digest(p) for p in (dataset_path, versions_path)},
            'version_discovery_generated': versions.get('generated'),
            'saved_version_leads': len(versions['leads']),
            'EU_grant_concept_families_screened': len(seen),
            'candidate_families': len(candidates),
            'with_cached_CORDIS_branch': sum(bool(r['cached_branches']) for r in candidates),
            'limitations': ['Publication dates are discovery aids, not DMP issue dates.',
                            'Cached project ends and branches are not latest-authority checks.',
                            'Missing or partial dates are not assigned a point date.',
                            'Different concepts and external revisions remain outside this screen.',
                            'No PDF, accessibility, licence, scope or lineage verification is performed.',
                            'The original six-pair proposal and all selections remain untouched.'],
            'incomplete_date_cases': incomplete, 'candidates': candidates}


if __name__ == '__main__':
    result = build()
    path = HERE / 'version-followup-screen.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('{}: {} publication-only families, {} with cached classification'.format(
        path.name, result['candidate_families'], result['with_cached_CORDIS_branch']))
