#!/usr/bin/env python3
"""Offline, deterministic candidate-family inventory; never determines eligibility."""
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().with_suffix('.json')
DATA = ROOT / 'data/dmp_dataset.json'
BRANCHES = ['natural sciences', 'engineering and technology', 'medical and health sciences',
            'agricultural sciences', 'social sciences', 'humanities']
TIERS = ['Horizon Europe', 'Horizon 2020', 'Other EU']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def md_grants(path):
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
        projects = obj.get('dmp', {}).get('project') or []
        if isinstance(projects, dict):
            projects = [projects]
        out = set()
        for project in projects:
            for funding in project.get('funding') or []:
                out.update(re.findall(r'\b\d{6,9}\b', str(funding.get('grant_id') or '')))
        return sorted(out)
    except (OSError, ValueError, AttributeError, TypeError):
        return []

def main():
    rows = json.loads(DATA.read_text(encoding='utf-8'))
    groups = collections.defaultdict(list)
    rejected = collections.Counter()
    hashes = {}
    for r in rows:
        if r.get('kind') != 'dmp':
            rejected['not classified dmp'] += 1
            continue
        if r.get('tier') not in TIERS:
            rejected['not EU tier'] += 1
            continue
        grant = str(r.get('grant') or '').strip()
        if not grant:
            rejected['no stored grant'] += 1
            continue
        evidence = []
        numbers = sorted(set(str(f.get('number') or '').strip() for f in r.get('funders', []) if f.get('number')))
        if grant in numbers:
            evidence.append('stored funding number')
        mf = r.get('madmp_file') or ''
        path = ROOT / 'data/madmp-corpus' / Path(mf).name
        if mf and path.is_file():
            hashes[str(path.relative_to(ROOT))] = sha(path)
            if grant in md_grants(path):
                evidence.append('stored maDMP project funding grant_id')
        if not evidence:
            rejected['stored grant not independently present in retained funding fields'] += 1
            continue
        item = {k:r.get(k) for k in ('id','doi','url','title','date','version','tier','grant','acronym',
                'proj_title','proj_start','proj_end','disc','disc_all','files','madmp','madmp_file','access')}
        item['grant_evidence'] = evidence
        item['all_stored_funding_numbers'] = numbers
        item['multiple_funding_numbers'] = len(numbers) > 1
        if mf and path.is_file():
            item['local_madmp_sha256'] = hashes[str(path.relative_to(ROOT))]
        groups[grant].append(item)
    families = []
    for grant, records in sorted(groups.items()):
        records.sort(key=lambda r: str(r['id']))
        name_size = collections.defaultdict(set)
        filehash = collections.defaultdict(set)
        for r in records:
            for f in r.get('files') or []:
                name_size[(f.get('name'), f.get('size'))].add(r['id'])
            if r.get('local_madmp_sha256'):
                filehash[r['local_madmp_sha256']].add(r['id'])
        prim = sorted(set(r['disc'] for r in records if r.get('disc')))
        all_disc = sorted(set(d for r in records for d in r.get('disc_all') or []))
        families.append({'grant':grant, 'records':records, 'record_count':len(records),
            'primary_branches':prim, 'all_branches':all_disc,
            'hazards':{'duplicate_local_madmp_sha256': [{'sha256':h,'record_ids':sorted(ids)} for h,ids in sorted(filehash.items()) if len(ids)>1],
                       'matching_name_and_size': [{'name':n,'size':s,'record_ids':sorted(ids)} for (n,s),ids in sorted(name_size.items(), key=lambda x: str(x[0])) if len(ids)>1],
                       'multiple_stored_funding_numbers':any(r['multiple_funding_numbers'] for r in records),
                       'scope_unverified':True}})
    # Queue is a retrieval order, not an eligibility or final-ranking rule.
    def rank(f):
        tier = min(TIERS.index(r['tier']) for r in f['records'])
        dates = [r['date'] for r in f['records'] if re.fullmatch(r'\d{4}(?:-\d{2}(?:-\d{2})?)?', str(r.get('date') or ''))]
        latest_year = max([int(d[:4]) for d in dates] or [0])
        return (tier, -latest_year, f['grant'])
    queues = {}
    for branch in BRANCHES:
        multi = [f for f in families if f['record_count'] >= 2 and branch in f['all_branches']]
        single = [f for f in families if f['record_count'] == 1 and branch in f['all_branches']]
        queues[branch] = {'multi_record_grants': [f['grant'] for f in sorted(multi,key=rank)],
                          'one_record_grants': [f['grant'] for f in sorted(single,key=rank)],
                          'multi_primary_count':sum(branch in f['primary_branches'] for f in multi),
                          'multi_all_count':len(multi), 'one_primary_count':sum(branch in f['primary_branches'] for f in single), 'one_all_count':len(single)}
    inputs = {'data/dmp_dataset.json':sha(DATA), 'scripts/01_harvest_records.py':sha(ROOT/'scripts/01_harvest_records.py'),
              'scripts/04_build_dataset.py':sha(ROOT/'scripts/04_build_dataset.py')}
    for p in sorted((ROOT/'data/raw').glob('*.jsonl')):
        inputs[str(p.relative_to(ROOT))] = sha(p)
    obj = {'purpose':'Offline discovery only; same grant does not prove same scope or distinct versions; issue dates not extracted.',
           'inputs_sha256':inputs, 'local_madmp_sha256':dict(sorted(hashes.items())),
           'selection_rule':'kind=dmp, EU tier, stored grant present in retained funding number or local selected maDMP funding grant_id; no publication date cutoff',
           'queue_order':'Horizon Europe, Horizon 2020, Other EU; most recent valid publication year descending; grant lexical. Publication date is not issue date or eligibility.',
           'excluded_row_counts':dict(sorted(rejected.items())), 'included_records':sum(f['record_count'] for f in families),
           'family_count':len(families),'multi_record_families':sum(f['record_count']>=2 for f in families),
           'one_record_families':sum(f['record_count']==1 for f in families), 'branch_queues':queues,'families':families}
    OUT.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Wrote',OUT, 'families',len(families),'records',obj['included_records'])
    for b,q in queues.items(): print(b, q['multi_primary_count'],q['multi_all_count'],q['one_primary_count'],q['one_all_count'])

if __name__ == '__main__': main()
