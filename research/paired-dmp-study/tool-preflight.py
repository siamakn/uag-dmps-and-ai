#!/usr/bin/env python3
"""No-model, offline browser checks of immutable DMP-EVA functions (stdlib only).

Run: python3 research/paired-dmp-study/tool-preflight.py
Requires cached exact source bytes under /tmp/dmp-eva-evolution (override --source-dir)
and Google Chrome (override --chrome). Does not download source or call the app/model.
Writes tool-preflight.json beside this script unless --output is supplied.
"""
import argparse
import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tempfile

COMMIT = 'b80b43de820d46440d982eb99b2b3da8f4c2f818'
EXPECTED = {
    'eva.json': '8f0c169d51219a80d6fcb13bb517eb7f65c0a6471853e1b32d20f5cc92c612f9',
    'js/api-config.js': '0f9ab8329f0cb89a329bdfcf9897bdf23947a869d6d088c91addc4c562aa9e0e',
    'js/criteria-extractor.js': '6c33859a7ae0be13b63cea52b436cd8a46f83aa54892a5a042457ff9f8999006',
    'js/evaluator.20260423a.js': '987e8829a9c62369e6a9b0187697aa15ec1defa1357e504fdf3789a98a3af1c2',
    'js/file-parser.20260423a.js': 'c0bf844fde574119ea69190bd1afba10e10b2c3637031d8949eb9eb7c4e1bc71',
    'js/llm-service.js': '9af182a7249222aaff30e57e9e686839a4f67c6c67ee861d136ae5a58df8608b',
}

GUARDS = r'''
window.blockedNetworkCalls = [];
const deny = kind => (...args) => {
  blockedNetworkCalls.push({kind, target: String(args[0] || '')});
  throw new Error('NETWORK DISABLED IN PREFLIGHT: ' + kind);
};
window.fetch = deny('fetch');
window.XMLHttpRequest = class { constructor() { deny('XMLHttpRequest')(); } };
window.WebSocket = class { constructor(url) { deny('WebSocket')(url); } };
window.EventSource = class { constructor(url) { deny('EventSource')(url); } };
Object.defineProperty(navigator, 'sendBeacon', {value: deny('sendBeacon')});
window.RTCPeerConnection = class { constructor() { deny('RTCPeerConnection')(); } };
localStorage.clear();
'''

TESTS = r'''
(async () => {
 const out = {completed: false, checks: [], results: {}};
 const check = (name, condition, detail) => out.checks.push({name, passed: !!condition, detail});
 const phaseGuide = prompt => prompt.userPrompt.split('PHASE-SPECIFIC SCORING INSTRUCTIONS:\n')[1];
 try {
  const eva = JSON.parse(document.getElementById('eva').textContent);
  const defaultCriteria = CriteriaExtractor.extractCriteria(JSON.stringify(eva), 'proposal');
  const dmp = 'Synthetic DMP statement with "double quotes". No research data or human labels.';
  const prompt = LLMService.buildEvaluationPrompt(defaultCriteria, dmp, 'proposal');
  const ids = defaultCriteria.categories.map(c => c.id);
  const absentDescriptions = defaultCriteria.categories.filter(c => !prompt.userPrompt.includes(c.description)).map(c => c.id);
  const absentNames = defaultCriteria.categories.filter(c => !prompt.userPrompt.includes(c.name)).map(c => c.id);
  const probeCriteria = {categories: [{id:'1a',name:'UNIQUE_CRITERION_NAME_X482',description:'UNIQUE_RUBRIC_WORDING_X482'}]};
  const probe = LLMService.buildEvaluationPrompt(probeCriteria, dmp, 'proposal');
  localStorage.setItem('dmpCustomPrompt', JSON.stringify({...LLMService.getDefaultPrompt(), criteriaContext:'UNIQUE_CONTEXT_X482 {criteriaText}'}));
  const customContextProbe = LLMService.buildEvaluationPrompt(probeCriteria, dmp, 'proposal');
  localStorage.removeItem('dmpCustomPrompt');
  out.results.prompt = {ids, absentNames, absentDescriptions, defaultPrompt:prompt,
    probePrompt:probe, customCriteriaContextPrompt:customContextProbe};
  check('default_ids_14_omit_3c_5d', ids.length === 14 && !ids.includes('3c') && !ids.includes('5d'), ids);
  check('default_prompt_contains_ids', prompt.userPrompt.includes(ids.join(' ')), ids.join(' '));
  check('default_criterion_wording_absent', absentDescriptions.length === 14 && absentNames.length === 14, {absentNames,absentDescriptions});
  check('distinctive_name_description_context_absent', !probe.userPrompt.includes('UNIQUE_CRITERION_NAME_X482') && !probe.userPrompt.includes('UNIQUE_RUBRIC_WORDING_X482') && !customContextProbe.userPrompt.includes('UNIQUE_CONTEXT_X482'), 'Synthetic markers, not subjective similarity');
  check('prompt_replaces_double_quotes', !prompt.userPrompt.includes('"double quotes"') && prompt.userPrompt.includes("'double quotes'"), dmp);

  const phases = ['proposal','mid','end','proposal_early_stage','mid_project','end_project'];
  out.results.phases = phases.map(phase => {
    const criteria = CriteriaExtractor.extractCriteria(JSON.stringify(eva), phase);
    const built = LLMService.buildEvaluationPrompt(criteria, dmp, phase);
    return {input:phase, stageKey:criteria.stageKey, firstCriterionDescription:criteria.categories[0].description, actualPromptGuidance:phaseGuide(built)};
  });
  const phaseRows = out.results.phases;
  check('short_phase_rubric_map', phaseRows.slice(0,3).every((r,i) => r.stageKey === phases[i+3]), phaseRows.slice(0,3));
  check('all_short_phase_prompts_use_early', phaseRows.slice(0,3).every(r => r.actualPromptGuidance.includes('PROPOSAL / EARLY STAGE')), phaseRows.slice(0,3));
  check('all_long_phase_rubrics_use_early', phaseRows.slice(3).every(r => r.stageKey === 'proposal_early_stage'), phaseRows.slice(3));
  check('long_phase_prompt_map', phaseRows[3].actualPromptGuidance.includes('PROPOSAL / EARLY STAGE') && phaseRows[4].actualPromptGuidance.includes('MID-PROJECT') && phaseRows[5].actualPromptGuidance.includes('END-PROJECT'), phaseRows.slice(3));

  const syntheticCriteria = {categories:[{id:'1a',name:'Positive'},{id:'1b',name:'Explicit zero'},{id:'2a',name:'No evidence unit'}]};
  const raw = {p:[['Synthetic positive unit',['1a'],90,'Synthetic score only'],['Synthetic zero unit',['1b'],0,'Synthetic score only']]};
  const processed = Evaluator.processResults(raw,syntheticCriteria,'Synthetic original text');
  const summary = Evaluator.generateSummary(processed);
  const allZero = Evaluator.processResults({p:[['Zero',['1a'],0,'Synthetic']]},syntheticCriteria,'Synthetic');
  out.results.aggregation = {inputCriteria:syntheticCriteria,inputRaw:raw,processed,summary,allZero};
  check('native_category_scores_90_0_0', JSON.stringify(processed.categories.map(c=>c.score)) === '[90,0,0]', processed.categories);
  check('native_overall_excludes_zero', processed.overallScore === 90 && summary.averageScore === 30, {overallScore:processed.overallScore,summaryAverage:summary.averageScore});
  check('all_zero_overall_is_zero', allZero.overallScore === 0, allZero.overallScore);

  const parserCases = [['ascii','A'.repeat(30720)+'TAIL'],['emoji','😀'.repeat(15360)+'TAIL'],['split_surrogate','A'.repeat(30719)+'😀TAIL']];
  out.results.parser = [];
  for (const [label,text] of parserCases) {
    const file = new File([text],label+'.txt',{type:'text/plain'});
    const parsed = await FileParser.parseFile(file);
    out.results.parser.push({label,inputUTF16Units:text.length,inputUTF8Bytes:file.size,outputUTF16Units:parsed.text.length,outputUTF8Bytes:new TextEncoder().encode(parsed.text).length,truncated:parsed.truncated,originalTextLength:parsed.originalTextLength,equalsExpectedPrefix:parsed.text===text.slice(0,30720),lastCodeUnit:parsed.text.charCodeAt(parsed.text.length-1)});
  }
  let pdfError = null;
  try { await FileParser.parseFile(new File(['%PDF-1.4 synthetic'],'synthetic.pdf',{type:'application/pdf'})); } catch(e) { pdfError=e.message; }
  out.results.pdfError = pdfError;
  check('parser_returns_first_30720_utf16_units', out.results.parser.every(r => r.truncated && r.outputUTF16Units===30720 && r.originalTextLength===r.inputUTF16Units && r.equalsExpectedPrefix), out.results.parser);
  check('parser_limit_not_utf8_bytes', out.results.parser[1].outputUTF8Bytes===61440, out.results.parser[1]);
  check('parser_can_split_surrogate', out.results.parser[2].lastCodeUnit===0xD83D, out.results.parser[2]);
  check('pdf_native_parser_rejects', pdfError==='Unsupported file type: .pdf', pdfError);

  out.results.candidateTexts = [];
  const candidateTexts = JSON.parse(document.getElementById('candidateTexts').textContent);
  await Promise.all(candidateTexts.map(async doc => {
    const file = new File([doc.text], doc.text_file.split('/').pop(), {type:'text/plain'});
    const parsed = await FileParser.parseFile(file);
    const parsedBytes = new TextEncoder().encode(parsed.text);
    const row = {project:doc.project,grant:doc.grant,role:doc.role,representation:doc.representation,text_file:doc.text_file,input_sha256:doc.text_sha256,
      inputUTF16Units:doc.text.length,originalTextLength:parsed.originalTextLength,
      outputUTF16Units:parsed.text.length,outputUTF8Bytes:parsedBytes.length,truncated:parsed.truncated,
      retainedFractionUTF16:parsed.text.length/doc.text.length,
      equalsExpectedPrefix:parsed.text===doc.text.slice(0,30720),
      expectedPrefixSHA256:doc.expected_prefix_sha256};
    out.results.candidateTexts.push(row);
    check('candidate_parser_'+doc.grant+'_'+doc.role+'_'+doc.representation, row.equalsExpectedPrefix && row.outputUTF16Units===Math.min(row.inputUTF16Units,30720) && row.originalTextLength===row.inputUTF16Units && row.truncated===(row.inputUTF16Units>30720), row);
  }));

  const profile = {endpoint:'https://invalid.invalid/never-sent',additionalHeaders:{'Content-Type':'application/json'},requiresAPIKey:false,modelParamName:'model',messagesParamName:'messages',temperature:0.17,seed:12345,maxTokens:321,responseFormat:'json_object',disableThinking:true,streamEnabled:false};
  const messages = [{role:'user',content:'Synthetic request never sent.'}];
  const config = APIConfig.generateFetchConfig(profile,'','synthetic-model',messages);
  const body = JSON.parse(config.options.body);
  out.results.request = {profile,config,body};
  check('request_omits_temperature_seed', !Object.hasOwn(body,'temperature') && !Object.hasOwn(body,'seed'), Object.keys(body));
  check('request_sends_outputcap_and_optional_settings', body.max_tokens===321 && body.enable_thinking===false && body.response_format.type==='json_object', body);
  check('request_model_and_messages_propagate', body.model==='synthetic-model' && JSON.stringify(body.messages)===JSON.stringify(messages), body);
  check('no_network_functions_invoked', blockedNetworkCalls.length===0, blockedNetworkCalls);
  out.completed = true;
 } catch (e) { out.error = {message:e.message,stack:e.stack}; }
 out.blockedNetworkCalls = blockedNetworkCalls;
 out.browser = {userAgent:navigator.userAgent};
 out.passed = out.completed && out.checks.every(c=>c.passed);
 document.getElementById('result').textContent = JSON.stringify(out);
 document.title = out.passed ? 'PREFLIGHT PASSED' : 'PREFLIGHT FAILED';
})();
'''


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and dict(attrs).get('id') == 'result':
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=Path('/tmp/dmp-eva-evolution'))
    parser.add_argument('--chrome', default='/usr/bin/google-chrome')
    parser.add_argument('--text-manifest', type=Path, help='Optional text-extraction.json: parse hash-verified candidate TXT inputs, without model calls')
    parser.add_argument('--output', type=Path, default=Path(__file__).with_suffix('.json'))
    args = parser.parse_args()
    sources = {}
    receipts = {}
    for name, expected in EXPECTED.items():
        path = args.source_dir / ('latest--' + name.replace('/', '--'))
        data = path.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise SystemExit('Source hash mismatch: ' + str(path))
        sources[name] = data.decode('utf-8')
        if '</script' in sources[name].lower():
            raise SystemExit('Source contains HTML script terminator; use a different safe embedding method.')
        receipts[name] = {'sha256':actual, 'bytes':len(data), 'immutable_url':'https://raw.githubusercontent.com/usadellab/dmp-eva/'+COMMIT+'/'+name}
    version = subprocess.check_output([args.chrome, '--version'], text=True).strip()
    candidate_texts = []
    candidate_manifest = None
    if args.text_manifest:
        manifest_bytes = args.text_manifest.read_bytes()
        candidate_manifest = {'path':str(args.text_manifest),'sha256':hashlib.sha256(manifest_bytes).hexdigest()}
        repo_root = Path(__file__).resolve().parents[2]
        for doc in json.loads(manifest_bytes)['documents']:
            representations = [('layout', doc['text_file'], doc['text_sha256'])]
            if doc.get('reading_order_alternative'):
                alt = doc['reading_order_alternative']
                representations.append(('reading_order', alt['text_file'], alt['sha256']))
            for representation, text_file, expected_hash in representations:
                data = (repo_root / text_file).read_bytes()
                if hashlib.sha256(data).hexdigest() != expected_hash:
                    raise SystemExit('Candidate text hash mismatch: '+text_file)
                text = data.decode('utf-8')
                prefix = text.encode('utf-16-le')[:30720*2].decode('utf-16-le',errors='surrogatepass')
                prefix_hash = hashlib.sha256(prefix.encode('utf-8',errors='replace')).hexdigest()
                candidate_texts.append({**{k:doc[k] for k in ['project','grant','role']},'representation':representation,'text_file':text_file,'text_sha256':expected_hash,'expected_prefix_sha256':prefix_hash,'text':text})
    with tempfile.TemporaryDirectory(prefix='dmp-eva-preflight-') as temporary:
        temp = Path(temporary)
        page = temp / 'harness.html'
        script_order = ['js/api-config.js','js/criteria-extractor.js','js/evaluator.20260423a.js','js/file-parser.20260423a.js','js/llm-service.js']
        document = '<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; connect-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>PREFLIGHT WAITING</title><pre id="result">pending</pre>'
        document += '<script>'+GUARDS+'</script>'
        document += '<script type="application/json" id="eva">'+sources['eva.json']+'</script>'
        document += '<script type="application/json" id="candidateTexts">'+json.dumps(candidate_texts,ensure_ascii=True).replace('<','\\u003c')+'</script>'
        document += ''.join('<script>'+sources[name]+'</script>' for name in script_order)
        document += '<script>'+TESTS+'</script>'
        page.write_text(document, encoding='utf-8')
        command = [args.chrome,'--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--disable-background-networking','--disable-component-update','--disable-sync','--metrics-recording-only','--no-first-run','--no-default-browser-check','--proxy-server=http://127.0.0.1:9','--host-resolver-rules=MAP * ~NOTFOUND','--user-data-dir='+str(temp/'profile'),'--virtual-time-budget=10000','--dump-dom',page.as_uri()]
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=40)
        extracted = ResultParser()
        extracted.feed(completed.stdout)
        raw_result = ''.join(extracted.parts)
        if completed.returncode != 0 or raw_result == 'pending' or not raw_result:
            Path('/tmp/dmp-eva-preflight-failed.html').write_text(document,encoding='utf-8')
            Path('/tmp/dmp-eva-preflight-failed-dom.html').write_text(completed.stdout,encoding='utf-8')
            raise SystemExit('Chrome harness did not complete (exit '+str(completed.returncode)+'):\n'+completed.stderr[-5000:])
        browser_result = json.loads(raw_result)
        harness_hash = hashlib.sha256(document.encode('utf-8')).hexdigest()
    result = {
        'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commit':COMMIT,
        'scope':'Five groups of synthetic browser function checks; no app orchestration, model request, provider test, benchmark or human-label validation.',
        'candidate_text_manifest':candidate_manifest,
        'chrome_version':version,
        'source_files':receipts,
        'harness_sha256':harness_hash,
        'reproducer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'network_controls':['No remote scripts or resources; embedded exact source bytes','CSP default-src none / connect-src none','fetch/XHR/WebSocket/EventSource/sendBeacon/RTCPeerConnection stubs throw','Chrome background networking disabled; proxy to loopback port 9; DNS rules reject external names','Fresh isolated temporary browser profile deleted after execution'],
        'chrome_arguments_without_temporary_paths':[arg for arg in command if not arg.startswith('--user-data-dir=') and not arg.startswith('file:')],
        'chrome_exit_code':completed.returncode,
        'runtime':browser_result,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output':str(args.output),'passed':browser_result['passed'],'checks':len(browser_result['checks']),'blockedNetworkCalls':browser_result['blockedNetworkCalls']},indent=2))
    return 0 if browser_result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
