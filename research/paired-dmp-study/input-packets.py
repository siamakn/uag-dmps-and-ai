#!/usr/bin/env python3
"""Build or verify candidate page-mapped inputs; no network or model calls."""
import argparse
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'research/paired-dmp-study'
ASSETS = ROOT / 'data/paired-dmp-corpus/input-packets'
MANIFEST = STUDY / 'input-packets.json'
PROPOSAL = STUDY / 'cohort-proposal.json'
BUDGET = 24000
NS = '{http://www.w3.org/1999/xhtml}'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def units(s):
    return len(s.encode('utf-16-le')) // 2


def parse_xml(data):
    root = ET.fromstring(data)
    pages = []
    for pn, page in enumerate(root.iter(NS + 'page'), 1):
        lines = []
        for fi, flow in enumerate(page.findall(NS + 'flow'), 1):
            for bi, block in enumerate(flow.findall(NS + 'block'), 1):
                for li, line in enumerate(block.findall(NS + 'line'), 1):
                    lid = 'p{:04d}-f{:04d}-b{:04d}-l{:04d}'.format(pn, fi, bi, li)
                    words = [{'id': lid + '-w{:04d}'.format(wi), 'text': ''.join(w.itertext()),
                              'bbox': dict(w.attrib)}
                             for wi, w in enumerate(line.findall(NS + 'word'), 1)]
                    lines.append({'id': lid, 'flow': fi, 'block': bi, 'line': li,
                                  'bbox': dict(line.attrib), 'words': words})
        # Fail closed if Poppler produces an unexpected hierarchy.
        if sum(len(x['words']) for x in lines) != len(list(page.iter(NS + 'word'))):
            raise ValueError('unmapped word on page {}'.format(pn))
        if len(lines) != len(list(page.iter(NS + 'line'))):
            raise ValueError('unmapped line on page {}'.format(pn))
        pages.append({'page': pn, 'dimensions': dict(page.attrib), 'lines': lines})
    if not pages:
        raise ValueError('no pages in bbox XML')
    return pages


def page_text(page):
    # IDs are explicit navigation markers; spaces join Poppler word elements.
    return '[PAGE {:04d}]\n'.format(page['page']) + ''.join(
        '[{}] {}\n'.format(line['id'], ' '.join(w['text'] for w in line['words']))
        for line in page['lines'])


def make_chunks(pages, budget=BUDGET):
    chunks, current = [], []
    for page in pages:
        s = page_text(page)
        if current and units(''.join(page_text(p) for p in current) + s) > budget:
            chunks.append(current)
            current = []
        current.append(page)
        if units(s) > budget:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def build_document(doc, xml, dest, write):
    pages = parse_xml(xml)
    chunks = make_chunks(pages)
    full = ''.join(page_text(p) for p in pages)
    files = {'bbox.xml': xml, 'pages.json': (json.dumps(pages, ensure_ascii=False, indent=2) + '\n').encode('utf-8'),
             'pages.txt': full.encode('utf-8')}
    summaries = []
    for i, chunk in enumerate(chunks, 1):
        name = 'chunk-{:03d}.txt'.format(i)
        content = ''.join(page_text(p) for p in chunk)
        files[name] = content.encode('utf-8')
        summaries.append({'file': name, 'pages': [p['page'] for p in chunk],
                          'lines': sum(len(p['lines']) for p in chunk),
                          'words': sum(len(l['words']) for p in chunk for l in p['lines']),
                          'utf16_units': units(content), 'over_engineering_budget': units(content) > BUDGET})
    # Exact sequence equality verifies each source page, line and word once, including empty pages.
    assert [p['page'] for c in chunks for p in c] == [p['page'] for p in pages]
    assert ''.join(files[x['file']].decode('utf-8') for x in summaries) == full
    if write:
        dest.mkdir(parents=True, exist_ok=True)
        # Remove obsolete generated chunks only; source PDFs and other assets are untouched.
        for old in dest.glob('chunk-*.txt'):
            old.unlink()
        for name, content in files.items():
            (dest / name).write_bytes(content)
    else:
        actual_names = {p.name for p in dest.glob('chunk-*.txt')}
        if actual_names != {x['file'] for x in summaries}:
            raise ValueError('missing or extra chunk files: {}'.format(dest))
        for name, content in files.items():
            if (dest / name).read_bytes() != content:
                raise ValueError('asset mismatch: {}'.format(dest / name))
    return {'project': doc['project'], 'role': doc['role'], 'pdf': doc['pdf'],
            'pdf_sha256': doc['sha256'], 'asset_dir': str(dest.relative_to(ROOT)),
            'page_count': len(pages), 'line_count': sum(len(p['lines']) for p in pages),
            'word_count': sum(len(l['words']) for p in pages for l in p['lines']),
            'pages': [{'page': p['page'], 'dimensions': p['dimensions'], 'lines': len(p['lines']),
                       'words': sum(len(l['words']) for l in p['lines']), 'utf16_units': units(page_text(p)),
                       'over_engineering_budget': units(page_text(p)) > BUDGET} for p in pages],
            'chunks': summaries, 'files_sha256': {name: sha(content) for name, content in files.items()}}


def sources():
    proposal = json.loads(PROPOSAL.read_text(encoding='utf-8'))
    docs = []
    for pair in proposal['pairs']:
        for role in ('early', 'late'):
            d = pair[role]
            docs.append({'project': pair['project'], 'role': role, 'pdf': d['local_pdf'],
                         'sha256': d['sha256'], 'grant': pair['grant'], 'record': str(d['record_id']) if d['record_id'] else Path(d['local_pdf']).stem})
    if len(docs) != 12 or len({d['pdf'] for d in docs}) != 12:
        raise ValueError('expected 12 unique proposed PDFs')
    return docs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='verify existing assets without extraction or downloads')
    args = parser.parse_args()
    docs = sources()
    existing = json.loads(MANIFEST.read_text(encoding='utf-8')) if args.verify else None
    if args.verify and existing['proposal_sha256'] != sha(PROPOSAL.read_bytes()):
        raise ValueError('proposal changed since generation')
    version = existing['pdftotext_version'] if args.verify else subprocess.run(
        ['pdftotext', '-v'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout.decode('utf-8').strip()
    results = []
    for d in docs:
        pdf = ROOT / d['pdf']
        if sha(pdf.read_bytes()) != d['sha256']:
            raise ValueError('PDF hash mismatch: {}'.format(pdf))
        dest = ASSETS / d['grant'] / d['record']
        if args.verify:
            xml = (dest / 'bbox.xml').read_bytes()
        else:
            proc = subprocess.run(['pdftotext', '-bbox-layout', '-enc', 'UTF-8', str(pdf), '-'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if proc.stderr:
                print('pdftotext {}: {}'.format(pdf, proc.stderr.decode('utf-8', 'replace')), file=sys.stderr)
            xml = proc.stdout
        results.append(build_document(d, xml, dest, not args.verify))
    manifest = {'schema_version': 1, 'status': 'candidate_only_not_frozen',
                'proposal': str(PROPOSAL.relative_to(ROOT)), 'proposal_sha256': sha(PROPOSAL.read_bytes()),
                'pdftotext_version': version, 'python_version': existing['python_version'] if args.verify else sys.version,
                'script_sha256': sha(Path(__file__).read_bytes()), 'command': 'pdftotext -bbox-layout -enc UTF-8 <pdf> -',
                'engineering_budget_utf16_units': BUDGET, 'budget_is_provider_context_limit': False,
                'documents': results}
    if args.verify:
        if manifest != existing:
            raise ValueError('manifest mismatch')
        print('Verified {} PDFs and packet assets'.format(len(results)))
    else:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Prepared {} PDFs'.format(len(results)))


if __name__ == '__main__':
    main()
