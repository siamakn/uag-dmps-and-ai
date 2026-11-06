#!/usr/bin/env python3
"""Assemble the reviewed proposal locally; stdlib only, no network or selection writes."""
import collections
import copy
import datetime
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
CORPUS = ROOT / "data" / "paired-dmp-corpus"
BRANCHES = ["natural sciences", "engineering and technology", "medical and health sciences",
            "agricultural sciences", "social sciences", "humanities"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def preserve(source, target, expected):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if digest(target) != expected:
            raise ValueError("Refusing to replace changed source bytes: " + str(target))
    else:
        if not source.exists() or digest(source) != expected:
            raise ValueError("Missing or changed reviewed source: " + str(source))
        shutil.copyfile(str(source), str(target))
    return relative(target)


def classification(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<ul\s+aria-labelledby="fieldofscience[^\"]*"[^>]*>(.*?)</ul>', text, re.S)
    if not match:
        raise ValueError("CORDIS field list not found: " + str(path))
    paths = []
    for item in re.findall(r'<li\b[^>]*>(.*?)</li>', match.group(1), re.S):
        labels = [html.unescape(re.sub(r'<[^>]+>', '', value)).strip()
                  for value in re.findall(r'<a\b[^>]*>(.*?)</a>', item, re.S)]
        if labels:
            if labels[0] not in BRANCHES:
                raise ValueError("Unexpected classification path: " + repr(labels))
            paths.append(labels)
    if not paths:
        raise ValueError("No CORDIS paths: " + str(path))
    counts = collections.Counter(p[0] for p in paths)
    maximum = max(counts.values())
    return {"paths": paths, "branch_path_counts": dict(counts),
            "dominant_branches": sorted(k for k, v in counts.items() if v == maximum),
            "dominance_rule": "most_frequent_top_level_branch_among_current_leaf_paths; ties_retained"}


def bibliographic(record_id, dataset):
    if record_id is None:
        return {}
    cached = Path('/tmp/humanities-search') / (record_id + '.bin')
    if cached.exists():
        try:
            record = json.loads(cached.read_text(encoding='utf-8'))
            if str(record.get('id')) == record_id and 'metadata' in record:
                meta = record['metadata']
                return {"title": meta.get('title'), "doi": record.get('doi') or meta.get('doi'),
                        "creators": [c.get('name') for c in meta.get('creators', [])],
                        "publication_date": meta.get('publication_date'),
                        "files": [{"name": f.get('key'), "size": f.get('size'),
                                   "source_file_url": f.get('links', {}).get('self')}
                                  for f in record.get('files', [])],
                        "source": "cached_full_Zenodo_record", "source_sha256": digest(cached)}
        except (ValueError, UnicodeError):
            pass
    record = dataset.get(record_id, {})
    return {
        "title": record.get('title'), "doi": record.get('doi'), "creators": record.get('creators', []),
        "publication_date": record.get('date'), "files": record.get('files', []),
        "funding_tier": record.get('tier'), "source": "local_derived_dataset_snapshot"}


def main():
    review_path = BASE / 'pair-review.json'
    review = json.loads(review_path.read_text(encoding='utf-8'))
    dataset = {r['id']: r for r in json.loads((ROOT / 'data/dmp_dataset.json').read_text(encoding='utf-8'))}
    pairs = [copy.deepcopy(p) for p in review['pairs']
             if p.get('eligibility_status', '').startswith('supported_candidate')]
    assert len(pairs) == 6
    assert {p['proposed_slot'] for p in pairs} == set(BRANCHES)
    assert len({p['grant'] for p in pairs}) == 6
    pairs.sort(key=lambda p: BRANCHES.index(p['proposed_slot']))
    legacy_hash = digest(ROOT / 'data/selection.json')
    for pair in pairs:
        evidence = pair['end_evidence']
        source = Path(evidence['path'])
        target = CORPUS / 'sources' / ('cordis-' + pair['grant'] + '.html')
        evidence['local_path'] = preserve(source, target, evidence['sha256'])
        evidence.pop('path', None)
        pair['current_classification'] = classification(target)
        assert pair['proposed_slot'] in pair['current_classification']['branch_path_counts']
        for role in ['early', 'late']:
            document = pair[role]
            record_id = document.get('record_id')
            doc_id = record_id or document['document_id']
            document['local_pdf'] = preserve(Path(document['cached_pdf']),
                CORPUS / pair['grant'] / (doc_id + '.pdf'), document['sha256'])
            document.pop('cached_pdf', None)
            document['bibliographic_snapshot'] = bibliographic(record_id, dataset)
            metadata_cache = document.pop('metadata_cache', None)
            metadata_source = Path(metadata_cache) if metadata_cache else (
                Path('/tmp/humanities-search') / (record_id + '.bin') if record_id else None)
            if metadata_source and metadata_source.exists():
                try:
                    record = json.loads(metadata_source.read_text(encoding='utf-8'))
                except (ValueError, UnicodeError):
                    if metadata_cache:
                        raise
                    record = None
                if isinstance(record, dict) and str(record.get('id')) == record_id and 'metadata' in record:
                    metadata_hash = digest(metadata_source)
                    document['metadata_snapshot_local'] = preserve(metadata_source,
                        CORPUS / 'sources' / ('zenodo-' + record_id + '.json'), metadata_hash)
                    document['metadata_snapshot_sha256'] = metadata_hash
            if record_id:
                for f in document['bibliographic_snapshot']['files']:
                    if f.get('size') == document['bytes']:
                        document['source_filename'] = f['name']
                        document['source_file_url'] = f.get('source_file_url') or (
                            'https://zenodo.org/records/' + record_id + '/files/' + quote(f['name']) + '?download=1')
                        document['source_url_note'] = 'full_record_file_link_or_standard_path_from_observed_record_filename'
                        break
            assert document.get('record_url') or document.get('source_file_url')
    manifest = {
        "schema_version": 1, "proposal_id": "paired-dmp-proposal-v1-2026-11-04",
        "prepared_date": "2026-11-04", "timezone": "Europe/Berlin",
        "status": "six_pair_proposal_not_frozen_for_benchmark_execution",
        "selection_basis": "purposive_metadata_based_verified_same_scope_version_pairs; no_quality_scores",
        "coverage": {"projects": 6, "documents": 12, "disciplines": 6},
        "protocol": {"date_basis": "document_version_dates_with_original_source_labels_retained",
            "early_fraction_max_inclusive": 0.5, "late_fraction_min_exclusive": 1.0,
            "pre_start_documents": "none_selected; policy_not_material_to_this_proposal",
            "project_end": "latest_authoritative_CORDIS_snapshot_including_extensions",
            "discipline": "any_documented_current_CORDIS_branch; one_slot_per_project; dominance_and_ties_reported",
            "representation": "PDF; machine_actionable_format_preference_not_required_for_eligibility",
            "scientific_scope": "six_project_paired_pilot_not_representative_discipline_sample"},
        "review": {"document_identity_timing_and_provenance": "independent_agent_checks",
                   "report": "research/paired-dmp-study/pair-review.md",
                   "human_quality_assessments": "not_performed", "human_protocol": "not_yet_finalized"},
        "software": {"repository": "https://github.com/usadellab/dmp-eva",
                     "working_commit": "b80b43de820d46440d982eb99b2b3da8f4c2f818",
                     "refresh_before_campaign_freeze": True},
        "source_rights": "original_terms_preserved; source_PDFs_not_relicensed_by_repository; public_manifest_links_only",
        "unresolved_before_model_execution": ["human_reference_protocol_and_labels", "actual_model_provider_configuration",
            "confirm_intended_model_submission_terms_for_AGRICORE; blanket_reuse_licence_not_identified"],
        "reserves": [
            {"project": "FAIR-EASE", "slot": "agricultural sciences", "status": "provisional_rights_conflict",
             "user_action": "user_will_seek_clarification_using_rights-clarification.md", "external_message_sent": False},
            {"project": "FERTIMANURE", "slot": "agricultural sciences", "status": "additional_lead_not_independently_reviewed_in_core"},
            {"project": "RECAP", "status": "excluded_from_agriculture_current_CORDIS_membership_not_supported"}],
        "input_sha256": {"pair-review.json": digest(review_path),
                         "data/dmp_dataset.json": digest(ROOT / 'data/dmp_dataset.json')},
        "historical_selection_sha256": legacy_hash, "pairs": pairs}
    (BASE / 'cohort-proposal.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Proposed six-project paired DMP set', '',
        'Prepared 2026-11-04. **Six proposed pairs, twelve exact PDF files.** Identity, timing and current CORDIS membership have been independently checked. This is a reviewable proposal, not a completed human reference dataset or an executed benchmark.', '',
        'The [canonical manifest](cohort-proposal.json) retains exact files/hashes, source-date labels, discrepancies, source URLs, project extensions and current discipline paths. Percentages below use document version dates, never repository deposits. Ranges retain competing version-related date statements.', '',
        '| Assigned discipline | Project / programme | Earlier document dates | Earlier position | Later document date | Later position |',
        '| --- | --- | --- | --- | --- | --- |']
    for pair in pairs:
        docs = [pair['early'], pair['late']]
        values = []
        for doc in docs:
            dates = sorted({d['date'] for d in doc['document_dates']})
            dates_text = dates[0] if len(dates) == 1 else dates[0] + ' to ' + dates[-1]
            link = doc.get('record_url') or doc['source_file_url']
            values.extend(['[' + dates_text + '](' + link + ')',
                '–'.join(dict.fromkeys('{:.2f}%'.format(100 * x) for x in doc['fraction_interval']))])
        tier = 'Horizon 2020' if pair['project'] in ['EGI-ACE', 'NANOFACTS', 'AGRICORE'] else 'Horizon Europe'
        lines.append('| {} | {} / {} | {} | {} | {} | {} |'.format(pair['proposed_slot'], pair['project'], tier, *values))
    lines += ['', '## How to interpret this proposal', '',
        '- The current CORDIS end date, including observed extensions, governs all calculations. Original-end sensitivity is retained for NANOFACTS and AGRICORE; complete amendment histories were not independently obtained.',
        '- Engineering uses EGI-ACE membership despite its dominant natural-sciences classification; medical uses NANOFACTS membership despite engineering dominance; humanities uses RECHARGE membership. Current CORDIS paths tie humanities/medical for RECHARGE (the older dataset chose medical), and natural/agricultural for AGRICORE. Each project occupies one slot only.',
        '- All twelve chosen representations are PDFs. Three projects are Horizon Europe and three Horizon 2020; five later versions are dated 2024 or newer. Format, programme and recency are preferences, with verified pairing and timing as hard conditions.',
        '- RECHARGE has a late cover dated five days after its repository publication. Early dates in RECHARGE, NANOFACTS, SUSTRACK and iMagine have differently labelled dates; their retained alternatives stay within the early window. Labels and discrepancies remain in the manifest.',
        '- AGRICORE meets the public-download criterion, but no blanket document reuse licence was identified. Public sharing of this proposal uses links and checksums; model-submission and redistribution terms remain to be settled. Other files retain their recorded CC or attribution terms.',
        '- FAIR-EASE remains provisional while the user obtains clarification of conflicting repository/PDF licence statements. RECAP is excluded from agriculture because current CORDIS contradicts its stored agricultural membership.',
        '- Source files and CORDIS snapshots are retained locally in data/paired-dmp-corpus/ (ignored by Git). They are not embedded in the dashboard and are not licensed under the repository code/documentation licence.', '',
        '## Next scientific work', '',
        'Fix the human reference instrument, reviewer allocation, calibration and phase mapping; resolve the intended-use question above; then freeze the protocol and actual tool/model configuration. Human reviewers must supply the reference judgments. No quality ratings were used to select these documents.', '']
    (BASE / 'cohort-proposal.md').write_text('\n'.join(lines), encoding='utf-8')
    assert digest(ROOT / 'data/selection.json') == legacy_hash
    print('Prepared six pairs and preserved twelve PDF files; historical selection unchanged.')


if __name__ == '__main__':
    main()
