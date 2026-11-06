#!/usr/bin/env python3
"""Verify the proposed corpus against preserved evidence, without network or writes."""
import datetime
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
BRANCHES = {"natural sciences", "engineering and technology", "medical and health sciences",
            "agricultural sciences", "social sciences", "humanities"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((BASE / 'cohort-proposal.json').read_text(encoding='utf-8'))
    pairs = manifest['pairs']
    require(len(pairs) == 6, 'Expected six projects')
    require(len({p['grant'] for p in pairs}) == 6, 'A project occupies multiple slots')
    require({p['proposed_slot'] for p in pairs} == BRANCHES, 'Incomplete discipline coverage')
    hashes = set()
    for pair in pairs:
        require(pair['lineage_check'] == 'supported', 'Missing same-scope lineage: ' + pair['project'])
        require(pair['proposed_slot'] in pair['current_classification']['branch_path_counts'],
                'Assigned discipline is absent from preserved current classification')
        start = datetime.date.fromisoformat(pair['project_start'])
        end = datetime.date.fromisoformat(pair['latest_authoritative_end'])
        duration = (end - start).days
        require(duration > 0 and duration == pair['duration_days'], 'Invalid project duration')
        source = ROOT / pair['end_evidence']['local_path']
        require(source.exists(), 'Missing CORDIS snapshot: ' + str(source))
        require(hashlib.sha256(source.read_bytes()).hexdigest() == pair['end_evidence']['sha256'],
                'CORDIS snapshot bytes changed')
        for role in ['early', 'late']:
            document = pair[role]
            if document.get('metadata_snapshot_local'):
                metadata = ROOT / document['metadata_snapshot_local']
                require(metadata.exists(), 'Missing source metadata snapshot')
                require(hashlib.sha256(metadata.read_bytes()).hexdigest() == document['metadata_snapshot_sha256'],
                        'Source metadata snapshot bytes changed')
            path = ROOT / document['local_pdf']
            require(path.exists(), 'Missing source PDF: ' + str(path))
            raw = path.read_bytes()
            require(raw.startswith(b'%PDF-'), 'Source is not a PDF: ' + str(path))
            require(len(raw) == document['bytes'], 'PDF size changed: ' + str(path))
            digest = hashlib.sha256(raw).hexdigest()
            require(digest == document['sha256'], 'PDF bytes changed: ' + str(path))
            require(digest not in hashes, 'The same PDF was used for multiple document roles')
            hashes.add(digest)
            for item in document['document_dates']:
                numerator = (datetime.date.fromisoformat(item['date']) - start).days
                require(numerator == item['numerator_days'], 'Stored day count mismatch')
                require(abs(numerator / duration - item['fraction']) < 1e-12, 'Stored fraction mismatch')
                require(0 <= 2 * numerator <= duration if role == 'early' else numerator > duration,
                        'Source-labelled document date fails role threshold: ' + pair['project'])
    selection = ROOT / 'data/selection.json'
    require(hashlib.sha256(selection.read_bytes()).hexdigest() == manifest['historical_selection_sha256'],
            'Historical selection changed since proposal assembly; investigate rather than overwrite')
    print('PASS: six distinct projects, six disciplines, twelve distinct PDF hashes,')
    print('all recorded date alternatives within role thresholds, six CORDIS snapshots,')
    print('and historical dashboard selection unchanged. This is provenance verification, not human assessment.')


if __name__ == '__main__':
    main()
