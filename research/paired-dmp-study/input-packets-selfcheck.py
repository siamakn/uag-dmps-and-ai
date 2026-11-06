#!/usr/bin/env python3
"""Synthetic checks for packet boundaries, mapping and corruption detection."""
import importlib.util
import tempfile
from pathlib import Path

path = Path(__file__).with_name('input-packets.py')
spec = importlib.util.spec_from_file_location('packets', str(path))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
xml = ('''<html xmlns="http://www.w3.org/1999/xhtml"><body><doc>
<page width="10" height="20"><flow><block><line><word xMin="1">é😀</word><word xMin="2">end</word></line></block></flow></page>
<page width="10" height="20"/>
<page width="10" height="20"><flow><block><line><word xMin="3">''' + 'x' * 24001 + '''</word></line></block></flow></page>
</doc></body></html>''').encode('utf-8')
pages = m.parse_xml(xml)
assert len(pages) == 3 and not pages[1]['lines']
assert pages[0]['lines'][0]['words'][0]['text'] == 'é😀'
assert m.units('é😀') == 3
chunks = m.make_chunks(pages)
assert [[p['page'] for p in c] for c in chunks] == [[1, 2], [3]]
assert m.units(m.page_text(pages[2])) > m.BUDGET
assert ''.join(m.page_text(p) for c in chunks for p in c) == ''.join(map(m.page_text, pages))
# Use a directory under ROOT because document metadata records a relative path.
with tempfile.TemporaryDirectory(dir=str(m.ROOT / 'data/paired-dmp-corpus/input-packets')) as tmp:
    dest = Path(tmp)
    doc = {'project': 'fixture', 'role': 'early', 'pdf': 'fixture.pdf', 'sha256': 'fixture'}
    result = m.build_document(doc, xml, dest, True)
    assert result['page_count'] == 3 and result['line_count'] == 2 and result['word_count'] == 3
    assert result['chunks'][1]['over_engineering_budget']
    assert result == m.build_document(doc, xml, dest, False)
    (dest / 'chunk-001.txt').write_text('corrupt', encoding='utf-8')
    try:
        m.build_document(doc, xml, dest, False)
    except ValueError:
        pass
    else:
        raise AssertionError('corruption was not detected')
print('Synthetic Unicode, empty-page, oversized-page, coverage and corruption checks passed')
