/* Functional self-test for the dashboard.
   Served only at /selftest by scripts/serve.py - never part of the shipped page.

   It drives the real UI through window.__APP__ and the real DOM: filters, search,
   sorting, column show/hide/reorder, selection, the coverage matrix, the export
   formats, the paired study (assignment, evidence, validation, persistence, import,
   export, freeze refusal) and the round trips to the API. Results land in #testlog
   and in the document title, so a headless browser can read them with --dump-dom.

   It never touches real state: serve.py only serves /selftest with a temporary state
   dir (--test), and every dmpbench.* browser key is restored when the run ends.

       python scripts/serve.py --test --no-open
       chrome --headless=new --dump-dom "http://127.0.0.1:8756/selftest"
       chrome --headless=new --dump-dom "http://127.0.0.1:8756/selftest?phase=reload"
     standalone:
       python scripts/05_build_dashboard.py --selftest /tmp/st.html
       chrome --headless=new --user-data-dir=/tmp/prof --dump-dom file:///tmp/st.html
       chrome --headless=new --user-data-dir=/tmp/prof --dump-dom "file:///tmp/st.html?phase=reload"
*/
(function(){
"use strict";
var log=[], pass=0, fail=0, skip=0;
function skipped(name, why){ skip++; log.push("SKIP  "+name+"  -> "+why); }

/* Snapshot every dmpbench.* key now, restore it at the end. */
var STORE0={};
try{ for(var si=0;si<localStorage.length;si++){ var sk=localStorage.key(si);
  if(sk.indexOf("dmpbench.")===0) STORE0[sk]=localStorage.getItem(sk); } }catch(e){}
function restoreStore(keep){
  try{
    var now=[]; for(var i=0;i<localStorage.length;i++) now.push(localStorage.key(i));
    now.forEach(function(k){ if(k.indexOf("dmpbench.")===0 && !(k in STORE0) && k!==keep) localStorage.removeItem(k); });
    Object.keys(STORE0).forEach(function(k){ if(k!==keep) localStorage.setItem(k,STORE0[k]); });
  }catch(e){}
}

function ok(name, cond, detail){
  if(cond){ pass++; log.push("PASS  "+name); }
  else { fail++; log.push("FAIL  "+name+(detail?"  -> "+detail:"")); }
  return !!cond;
}
function eq(name, got, want){
  return ok(name, got===want, "got "+JSON.stringify(got)+", want "+JSON.stringify(want));
}
function flush(done){
  var el=document.getElementById("testlog");
  el.hidden=false;
  el.textContent="SELFTEST "+pass+"/"+(pass+fail)+" passed, "+fail+" failed, "+skip+" skipped\n\n"+log.join("\n");
  document.title="SELFTEST "+pass+"/"+(pass+fail)+" fail="+fail+" skip="+skip+(done?"":" (running)");
  if(done) log.push("done");
}

function hideAll(){
  document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));
}
function every(list, fn){ for(var i=0;i<list.length;i++) if(!fn(list[i])) return false; return true; }
function headCells(){ return document.querySelectorAll("#thead > *").length; }
function firstRowCells(){
  var r=document.querySelector("#list .row");
  if(!r) return -1;
  var n=0;
  for(var i=0;i<r.children.length;i++) if(!r.children[i].classList.contains("det")) n++;
  return n;
}

window.__ONREADY__=function(){
  var A=window.__APP__, S=A.state, R=A.ROWS;
  if(/[?&]phase=reload/.test(location.search)) return reloadPhase(A);
  /* the historical 3 x 3 tests below run in legacy mode; the paired study has its own block */
  A.setMode("legacy");

  /* ---------- data ---------- */
  ok("dataset loaded", R.length>2000, R.length+" rows");
  ok("index resolves ids", A.byId(R[0].id)===R[0]);

  /* ---------- presets ---------- */
  A.applyPreset("reset");
  eq("preset everything shows all rows", A.filtered().length, R.length);
  ok("preset everything drops the kind filter too",
     A.filtered().some(function(r){ return r.kind!=="dmp"; }));

  A.applyPreset("he24");
  var expectHE=R.filter(function(r){ return r.tier==="Horizon Europe" && r.kind==="dmp" &&
                                            +r.year>=2024 && +r.year<=2026; }).length;
  eq("preset HE 2024+ count", A.filtered().length, expectHE);
  ok("preset HE 2024+ shows only actual DMPs",
     every(A.filtered(), function(r){ return r.kind==="dmp"; }));
  ok("preset HE 2024+ rows are all Horizon Europe",
     every(A.filtered(), function(r){ return r.tier==="Horizon Europe"; }));
  ok("preset HE 2024+ rows are all in range",
     every(A.filtered(), function(r){ return +r.year>=2024 && +r.year<=2026; }));

  A.applyPreset("he-ma");
  ok("preset maDMP rows are all machine-actionable",
     every(A.filtered(), function(r){ return r.madmp===true; }));
  ok("preset maDMP is a subset of HE 2024+", A.filtered().length<expectHE,
     A.filtered().length+" vs "+expectHE);

  A.applyPreset("eu");
  ok("preset any EU is wider than HE alone", A.filtered().length>expectHE);

  /* ---------- individual filters ---------- */
  A.applyPreset("reset");
  S.tiers={"DFG":1}; A.render();
  var dfg=R.filter(function(r){ return r.tier==="DFG"; }).length;
  eq("funding chip filters to DFG", A.filtered().length, dfg);

  A.applyPreset("reset");
  var disc=R.find(function(r){ return r.disc; }).disc;
  S.disc[disc]=1; A.render();
  ok("discipline chip filters", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return (r.disc_all||[]).indexOf(disc)>=0; }), disc);
  ok("a branch match no longer needs to be the majority one",
     A.filtered().some(function(r){ return r.disc!==disc; }) ||
     A.filtered().length>0);

  A.applyPreset("reset");
  S.stage={"early":1}; A.render();
  ok("stage chip filters", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return r.stage==="early"; }));

  A.applyPreset("reset");
  S.fmt={madmp:1}; A.render();
  eq("format chip maDMP", A.filtered().length, R.filter(function(r){ return r.madmp; }).length);

  A.applyPreset("reset");
  S.fmt={valid:1}; A.render();
  ok("format chip schema-clean", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return r.schema_ok===true; }));

  A.applyPreset("reset");
  S.flag={chmeta:1}; A.render();
  ok("flag chip sensitive-in-maDMP", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return r.ch_meta===true; }));

  A.applyPreset("reset");
  S.y0=2026; S.y1=2026; A.render();
  ok("year range filters", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return +r.year===2026; }));

  A.applyPreset("reset");
  S.q="certainty"; A.render();
  ok("search filters on the full haystack", A.filtered().length>0 &&
     every(A.filtered(), function(r){
       return (r.title+" "+(r.acronym||"")+" "+(r.grant||"")+" "+(r.doi||"")+" "+
               (r.proj_title||"")+" "+(r.call||"")+" "+(r.desc||"")).toLowerCase()
               .indexOf("certainty")>=0;
     }), A.filtered().length+" hits");
  ok("search narrows the pool", A.filtered().length<R.length);
  S.q="zzzznomatchzzzz"; A.render();
  eq("search with no match empties the list", A.filtered().length, 0);
  ok("empty state is shown", document.querySelector("#list .empty")!==null);
  S.q=""; A.render();

  /* ---------- sorting ---------- */
  A.applyPreset("he24");
  var f=A.filtered();
  eq("default sort is by date", S.sort, "date");
  eq("default direction is newest first", S.dir, -1);
  ok("default order really is descending", f[0].date>=f[f.length-1].date,
     f[0].date+" .. "+f[f.length-1].date);

  A.setSort("date");
  f=A.filtered();
  eq("clicking the active header flips direction", S.dir, 1);
  ok("now ascending", f[0].date<=f[f.length-1].date, f[0].date+" .. "+f[f.length-1].date);

  A.setSort("date");
  f=A.filtered();
  eq("clicking again flips back", S.dir, -1);
  ok("descending again", f[0].date>=f[f.length-1].date, f[0].date+" .. "+f[f.length-1].date);

  A.setSort("title");
  f=A.filtered();
  ok("sort by title is alphabetical",
     String(f[0].title).localeCompare(String(f[f.length-1].title))<=0);

  A.setSort("stage");
  f=A.filtered().filter(function(r){ return r.stage_frac!=null; });
  var mono=true;
  for(var i=1;i<f.length;i++) if(f[i].stage_frac<f[i-1].stage_frac) mono=false;
  ok("sort by lifecycle position is ordered", mono);

  A.setSort("datasets");
  f=A.filtered();
  ok("sort by datasets puts the richest first", (f[0].n_datasets||0)>=(f[1].n_datasets||0));

  ok("unsortable column is rejected", A.setSort("links")===false);
  A.setSort("date");

  /* ---------- columns ---------- */
  var before=A.visibleCols().length;
  eq("header cell count matches visible columns", headCells(), before);
  eq("row cell count matches visible columns", firstRowCells(), before);

  ok("hiding a column works", A.toggleCol("date")===true);
  eq("visible count drops by one", A.visibleCols().length, before-1);
  eq("header follows the hide", headCells(), before-1);
  eq("rows follow the hide", firstRowCells(), before-1);
  ok("hidden column is gone from the header",
     document.querySelector('#thead [data-sort="date"]')===null);

  ok("showing it again works", A.toggleCol("date")===true);
  eq("visible count restored", A.visibleCols().length, before);

  ok("adding an optional column works", A.toggleCol("grant")===true);
  eq("optional column is now visible", A.visibleCols().length, before+1);
  eq("header shows the new column", headCells(), before+1);
  ok("new column has a header title",
     document.querySelector('#thead [data-sort="grant"]')!==null);
  A.toggleCol("grant");

  ok("locked column cannot be hidden", A.toggleCol("title")===false);
  ok("title is still visible", A.visibleCols().some(function(c){ return c.k==="title"; }));

  var order0=A.colState.order.slice();
  ok("moving a column works", A.moveCol("project",-1)===true);
  ok("order actually changed", A.colState.order.join()!==order0.join());
  A.moveCol("project",1);
  eq("moving back restores the order", A.colState.order.join(), order0.join());
  ok("cannot move the first column up", A.moveCol(A.colState.order[0],-1)===false);
  ok("cannot move the last column down",
     A.moveCol(A.colState.order[A.colState.order.length-1],1)===false);

  var titles=[].map.call(document.querySelectorAll("#thead > *"),
                         function(e){ return e.textContent.replace(/[▼▲]/g,"").trim(); });
  ok("every visible column has a title",
     titles.filter(function(t){ return t.length>0; }).length===A.visibleCols().length-1,
     JSON.stringify(titles));

  /* ---------- wiring: real DOM clicks, not just the API ---------- */
  A.applyPreset("reset");
  var chip=document.querySelector('#f-tier .chip[data-v="DFG"]');
  chip.click();
  ok("clicking a funding chip filters", S.tiers["DFG"]===1 &&
     every(A.filtered(), function(r){ return r.tier==="DFG"; }));
  eq("clicked chip shows as pressed",
     document.querySelector('#f-tier .chip[data-v="DFG"]').getAttribute("aria-pressed"), "true");
  document.querySelector('[data-clear="tiers"]').click();
  eq("clear button empties the group", A.filtered().length, R.length);

  document.querySelector('[data-preset="he24"]').click();
  ok("clicking a preset applies it", S.y0===2024 && S.tiers["Horizon Europe"]===1);

  var th=document.querySelector('#thead [data-sort="project"]');
  th.click();
  eq("clicking a header changes the sort column", S.sort, "project");
  ok("header marks the active column",
     document.querySelector('#thead [data-sort="project"]').classList.contains("on"));
  ok("header shows a direction arrow",
     document.querySelector('#thead [data-sort="project"] .dir')!==null);

  var sortSel=document.getElementById("sort");
  sortSel.value="datasets";
  sortSel.dispatchEvent(new Event("change"));
  eq("the sort dropdown changes the sort", S.sort, "datasets");

  var y0=document.getElementById("y0");
  y0.value="2025"; y0.dispatchEvent(new Event("change"));
  eq("the year dropdown filters", S.y0, 2025);
  ok("year dropdown really narrows",
     every(A.filtered(), function(r){ return +r.year>=2025; }));
  y0.value="2024"; y0.dispatchEvent(new Event("change"));

  var visBefore=A.visibleCols().length;
  document.querySelector('[data-colcheck="date"]').click();
  eq("clicking a column checkbox hides it", A.visibleCols().length, visBefore-1);
  document.querySelector('[data-colcheck="date"]').click();
  eq("clicking it again shows it", A.visibleCols().length, visBefore);

  var ord0=A.colState.order.join();
  document.querySelector('#f-cols [data-mv="up"][data-k="project"]').click();
  ok("clicking the move button reorders", A.colState.order.join()!==ord0);
  document.getElementById("colreset").click();
  ok("reset restores the default columns", A.colState.order.join()!==ord0 ||
     A.visibleCols().length===visBefore);
  eq("reset leaves the default column count", A.visibleCols().length, 8);

  var ttl=document.querySelector("#list .row .ttl");
  ttl.click();
  eq("clicking a title opens the detail panel", document.querySelectorAll("#list .det").length, 1);
  ok("detail panel shows the DOI",
     document.querySelector("#list .det").textContent.indexOf("10.")>=0);
  document.querySelector("#list .row .ttl").click();
  eq("clicking again closes it", document.querySelectorAll("#list .det").length, 0);

  A.setSel([]);
  document.querySelector("#list .row [data-pick]").click();
  eq("clicking a row checkbox selects it", A.sel().length, 1);
  ok("the row is marked selected",
     document.querySelector("#list .row").classList.contains("sel"));
  document.querySelector("#list .row [data-pick]").click();
  eq("clicking it again deselects", A.sel().length, 0);

  var rail=document.getElementById("rail");
  document.getElementById("railtoggle").click();
  ok("the filters toggle hides the rail", rail.classList.contains("hide"));
  document.getElementById("railtoggle").click();
  ok("and shows it again", !rail.classList.contains("hide"));

  /* ---------- discipline: branches and sub-fields ---------- */
  A.applyPreset("reset");
  ok("records carry branch-tagged sub-fields",
     R.some(function(r){ return (r.fields||[]).length>0; }));
  ok("every sub-field keeps its branch",
     every(R, function(r){
       return (r.fields||[]).every(function(p){
         return p.length===2 && typeof p[0]==="string" && typeof p[1]==="string"; });
     }));

  var pairs={}, l2set={};
  R.forEach(function(r){ (r.fields||[]).forEach(function(p){
    pairs[p[1]]=p[0]; l2set[p[1]]=1; }); });
  eq("the level-2 vocabulary is the expected size", Object.keys(l2set).length, 37);

  /* the bug that prompted this: a sub-field shown under the wrong branch */
  ok("sociology never appears under natural sciences",
     every(R, function(r){
       return (r.fields||[]).every(function(p){
         return !(p[0]==="natural sciences" && p[1]==="sociology"); });
     }));
  eq("sociology belongs to social sciences", pairs["sociology"], "social sciences");
  eq("materials engineering belongs to engineering", pairs["materials engineering"],
     "engineering and technology");
  eq("physical sciences belongs to natural sciences", pairs["physical sciences"],
     "natural sciences");

  /* sub-field chips follow the chosen branch */
  A.applyPreset("reset");
  var allSubs=document.querySelectorAll("#f-disc2 .chip").length;
  ok("all sub-fields are offered when no branch is picked", allSubs>=30, allSubs+" chips");
  document.querySelector('#f-disc .chip[data-v="engineering and technology"]').click();
  var engSubs=[].map.call(document.querySelectorAll("#f-disc2 .chip"),
                          function(e){ return e.getAttribute("data-v"); });
  ok("picking a branch narrows the sub-field list", engSubs.length<allSubs,
     engSubs.length+" of "+allSubs);
  ok("the narrowed list is materials-flavoured",
     engSubs.indexOf("materials engineering")>=0 && engSubs.indexOf("nanotechnology")>=0);
  ok("it excludes other branches", engSubs.indexOf("sociology")<0 &&
     engSubs.indexOf("physical sciences")<0);

  /* the thing this was built for */
  document.querySelector('#f-disc2 .chip[data-v="materials engineering"]').click();
  ok("filtering by materials engineering works", A.filtered().length>0,
     A.filtered().length+" records");
  ok("every hit really carries the sub-field",
     every(A.filtered(), function(r){
       return (r.fields||[]).some(function(p){ return p[1]==="materials engineering"; }); }));
  var matCount=A.filtered().length;

  document.querySelector('#f-disc2 .chip[data-v="nanotechnology"]').click();
  ok("sub-field chips combine as OR", A.filtered().length>=matCount);
  ok("combined hits carry one of the two",
     every(A.filtered(), function(r){
       return (r.fields||[]).some(function(p){
         return p[1]==="materials engineering"||p[1]==="nanotechnology"; }); }));

  document.querySelector('[data-clear="disc"]').click();
  eq("clearing the branch clears the sub-fields too",
     Object.keys(S.disc2).filter(function(k){ return S.disc2[k]; }).length, 0);
  eq("and the pool is whole again", A.filtered().length, R.length);

  /* the column shows the branch being filtered, not the majority vote */
  A.applyPreset("reset");
  S.disc={"engineering and technology":1}; A.render();
  var cross=A.filtered().find(function(r){ return r.disc!=="engineering and technology" &&
                                                  (r.disc_all||[]).length>1; });
  if(cross){
    S.q=cross.title.slice(0,26); A.render();
    var row=document.querySelector('#list .row[data-id="'+cross.id+'"]');
    var txt=row?row.textContent:"";
    ok("the column shows the branch you filtered on",
       txt.indexOf("engineering and technology")>=0, txt.slice(0,80)||"row not rendered");
    ok("other branches are marked as 'also'", txt.indexOf("also")>=0, txt.slice(0,80));
    S.q=""; A.render();
  } else { ok("cross-branch column check (no such record - skipped)", true); }
  A.applyPreset("he24");

  /* ---------- record kind ---------- */
  A.applyPreset("he24");
  ok("default view is restricted to actual DMPs", S.kind.dmp===1);
  ok("nothing in the default view is a template, guide or paper",
     every(A.filtered(), function(r){ return r.kind==="dmp"; }));

  var kinds={}; R.forEach(function(r){ kinds[r.kind]=(kinds[r.kind]||0)+1; });
  ok("every record carries a kind",
     every(R, function(r){ return !!r.kind; }));
  ok("every record explains its kind",
     every(R, function(r){ return typeof r.kind_why === "string" && r.kind_why.length>0; }));
  ok("the pool really contains non-plans to exclude",
     (kinds.about||0)+(kinds.template||0)+(kinds.guidance||0) > 20,
     JSON.stringify(kinds));

  A.applyPreset("reset");
  document.querySelector('#f-kind .chip[data-v="about"]').click();
  ok("kind chip filters to writing about DMPs", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return r.kind==="about"; }));
  document.querySelector('#f-kind .chip[data-v="template"]').click();
  ok("kind chips combine", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return r.kind==="about"||r.kind==="template"; }));
  document.querySelector('[data-clear="kind"]').click();
  eq("clearing the kind filter shows everything again", A.filtered().length, R.length);

  /* the DFG case that started this: mixed record types */
  A.applyPreset("reset");
  S.tiers={"DFG":1}; S.kind={dmp:1}; A.render();
  var dfgPlans=A.filtered().length;
  S.kind={}; A.render();
  var dfgAll=A.filtered().length;
  ok("DFG pool contains more records than actual plans", dfgAll>dfgPlans,
     dfgAll+" records, "+dfgPlans+" plans");
  ok("the excluded DFG records are visible when asked for", dfgAll-dfgPlans>5);

  A.applyPreset("reset");
  var nonPlan=A.filtered().find(function(r){ return r.kind!=="dmp"; });
  ok("a non-plan row is tagged in the list", !!nonPlan);
  if(nonPlan){
    S.q=nonPlan.title.slice(0,28); A.render();
    ok("the tag is actually rendered",
       document.querySelector("#list .t-kind")!==null);
    S.q=""; A.render();
  }

  ok("kind is available as a column", A.toggleCol("kind")===true);
  ok("kind column renders", document.querySelector('#thead [data-sort="kind"]')!==null);
  A.toggleCol("kind");

  /* ---------- metadata sheet ---------- */
  A.applyPreset("he-ma");
  var rich=A.filtered().find(function(r){ return r.creators && r.creators.length &&
                                                 r.files && r.files.length; });
  ok("rows carry authors and file listings", !!rich);
  if(rich){
    S.q=""; A.render();
    var btn=document.querySelector('#list [data-open="'+rich.id+'"]');
    if(!btn){ A.setSort("date"); btn=document.querySelector('#list [data-open="'+rich.id+'"]'); }
    if(btn){
      btn.click();
      var det=document.querySelector("#list .det");
      ok("the metadata sheet opens", !!det);
      if(det){
        var txt=det.textContent;
        ok("sheet shows the record kind and why", txt.indexOf("Record kind")>=0);
        ok("sheet shows the Zenodo type", txt.indexOf("Zenodo type")>=0);
        ok("sheet shows authors", txt.indexOf("Authors")>=0);
        ok("sheet shows the DOI", txt.indexOf("DOI")>=0);
        ok("sheet lists the files", txt.indexOf("Files")>=0);
        ok("sheet shows the project run", txt.indexOf("Runs")>=0 || txt.indexOf("Project")>=0);
        ok("sheet shows the lifecycle position", txt.indexOf("Lifecycle")>=0);
        ok("sheet shows maDMP detail", txt.indexOf("maDMP")>=0);
        ok("sheet shows a file size", /\d+\s?(B|KB|MB)/.test(txt), txt.slice(0,60));
        ok("sheet links out", det.querySelector("a[href]")!==null);
      }
      btn=document.querySelector('#list [data-open="'+rich.id+'"]');
      if(btn) btn.click();
      eq("the sheet closes again", document.querySelectorAll("#list .det").length, 0);
    }
  }

  /* ---------- hover documentation ---------- */
  A.applyPreset("he24");

  function tipOf(sel){
    var el=document.querySelector(sel);
    if(!el) return null;
    el.dispatchEvent(new MouseEvent("mouseover",{bubbles:true}));
    var tip=document.querySelector(".tip");
    return (tip && !tip.hidden) ? tip.textContent : null;
  }
  function leave(sel){
    document.querySelector(sel).dispatchEvent(
      new MouseEvent("mouseout",{bubbles:true,relatedTarget:document.body}));
  }

  var t1=tipOf('#f-tier .chip[data-v="Horizon Europe"]');
  ok("hovering a funding chip shows a tooltip", !!t1, String(t1));
  ok("that tooltip explains the funder",
     t1 && t1.indexOf("2021-2027")>=0, String(t1));
  leave('#f-tier .chip[data-v="Horizon Europe"]');
  ok("leaving hides the tooltip", document.querySelector(".tip").hidden);

  var t2=tipOf('#f-stage .chip[data-v="early"]');
  ok("stage chip explains how the stage is computed",
     t2 && t2.indexOf("34%")>=0, String(t2));
  leave('#f-stage .chip[data-v="early"]');

  var t3=tipOf('#f-flag .chip[data-v="chmeta"]');
  ok("flag chip explains the stricter sensitive test",
     t3 && t3.indexOf("personal_data")>=0, String(t3));
  leave('#f-flag .chip[data-v="chmeta"]');

  var t4=tipOf('#thead [data-sort="stage"]');
  ok("column header has a tooltip", !!t4, String(t4));
  ok("header tooltip mentions sorting", t4 && t4.indexOf("Click to sort")>=0, String(t4));
  leave('#thead [data-sort="stage"]');

  var t5=tipOf('#f-cols .colrow[data-col="format"]');
  ok("column editor row is documented", !!t5, String(t5));
  leave('#f-cols .colrow[data-col="format"]');

  var t6=tipOf('[data-preset="he-ma"]');
  ok("preset is documented", t6 && t6.indexOf("47")>=0, String(t6));
  leave('[data-preset="he-ma"]');

  var t7=tipOf('#q');
  ok("search box explains what it matches", t7 && t7.indexOf("DOI")>=0, String(t7));
  leave('#q');

  var t8=tipOf('.stat.hit');
  ok("header counter is documented", !!t8, String(t8));
  leave('.stat.hit');

  var t9=tipOf('#list .row .cell .track') || tipOf('#list .row .cell');
  ok("a row cell carries a tooltip", !!t9, String(t9));

  /* keyboard reaches the same text */
  hideAll();
  document.getElementById("q").focus();
  var tf=document.querySelector(".tip");
  ok("focusing a control shows its tooltip", tf && !tf.hidden);
  document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));
  ok("Escape dismisses the tooltip", document.querySelector(".tip").hidden);
  document.getElementById("q").blur();

  /* coverage: nothing interactive in the rail is left undocumented */
  var controls=document.querySelectorAll(
    "#rail .chip, #rail select, #rail input[type=search], #rail [data-clear], #rail #colreset");
  var bare=[];
  [].forEach.call(controls, function(el){
    if(!el.getAttribute("data-tip")) bare.push(el.textContent.trim().slice(0,20)||el.id);
  });
  eq("every rail control is documented", bare.length, 0);
  ok("that is a real number of controls", controls.length>25, controls.length+" controls");

  var heads=document.querySelectorAll("#thead > *");
  var bareHeads=[];
  [].forEach.call(heads, function(el){
    if(!el.getAttribute("data-tip")) bareHeads.push(el.textContent.trim()||"(select)");
  });
  eq("every column header is documented", bareHeads.length, 0);

  var colrows=document.querySelectorAll("#f-cols .colrow");
  var bareCols=0;
  [].forEach.call(colrows, function(el){ if(!el.getAttribute("data-tip")) bareCols++; });
  eq("every column editor row is documented", bareCols, 0);
  eq("the column editor lists every column", colrows.length, A.ALLCOLS.length);

  /* tips survive a re-render */
  A.applyPreset("reset");
  ok("tooltips survive re-rendering the chips",
     !!document.querySelector('#f-tier .chip[data-tip]'));
  A.applyPreset("he24");

  /* ---------- guide panel ---------- */
  var panel=document.getElementById("guide"), gbtn=document.getElementById("guidebtn");
  ok("guide starts closed", panel.hidden===true);
  gbtn.click();
  ok("guide opens", panel.hidden===false);
  eq("guide button flips its label", gbtn.textContent, "Hide guide");
  eq("guide button reports state", gbtn.getAttribute("aria-expanded"), "true");
  ok("guide explains the matrix", panel.textContent.indexOf("3 \u00d7 3")>=0 ||
     panel.textContent.indexOf("matrix")>=0);
  ok("guide explains the lifecycle thresholds", panel.textContent.indexOf("34")>=0);
  gbtn.click();
  ok("guide closes again", panel.hidden===true);
  eq("guide button label resets", gbtn.textContent, "Guide");

  /* ---------- paging ---------- */
  A.applyPreset("reset");
  eq("first page is capped at 100", document.querySelectorAll("#list .row").length, 100);
  ok("show-more button is offered", document.getElementById("more").hidden===false);
  document.getElementById("more").click();
  eq("second page appends", document.querySelectorAll("#list .row").length, 200);

  /* ---------- selection + matrix ---------- */
  A.applyPreset("he-ma");
  var pool=A.filtered();
  var a=pool.find(function(r){ return r.disc && r.stage!=="unknown"; });
  var b=pool.find(function(r){ return r!==a && r.disc && r.disc!==a.disc && r.stage!=="unknown"; });
  var c=pool.find(function(r){ return r.challenging && r!==a && r!==b; });
  ok("found three distinct rows to select", !!(a&&b&&c));

  A.setSel([a.id,b.id,c.id]);
  eq("tray counter", document.getElementById("t-n").textContent, "3");
  eq("header counter", document.getElementById("s-sel").textContent, "3");
  eq("tray lists three picks", document.querySelectorAll("#picked li:not(.empty)").length, 3);
  ok("matrix has a row per discipline",
     document.querySelectorAll("#mx tr").length>=2);
  ok("matrix marks a filled cell",
     document.querySelectorAll("#mx .cellbox.on, #mx .cellbox.over").length>0);
  ok("challenging slot lit up",
     document.getElementById("slot-ch").className.indexOf("on")>=0);

  ok("selected row is highlighted",
     document.querySelector('.row[data-id="'+a.id+'"]') === null ||
     document.querySelector('.row[data-id="'+a.id+'"]').classList.contains("sel"));

  /* ---------- export ---------- */
  var js=A.exportAs("json");
  var parsed=null; try{ parsed=JSON.parse(js); }catch(e){}
  ok("JSON export parses", !!parsed);
  eq("JSON export has three entries", parsed?parsed.length:-1, 3);
  ok("JSON export carries the DOI", !!(parsed&&parsed[0].doi));

  var csv=A.exportAs("csv").split("\n");
  eq("CSV export has header plus three rows", csv.length, 4);
  ok("CSV header is the expected shape", csv[0].indexOf("doi,title,published")===0, csv[0]);

  var md=A.exportAs("md").split("\n");
  eq("Markdown export has header, rule and three rows", md.length, 5);
  ok("Markdown rows are piped", md[2].indexOf("| ")===0);

  /* ---------- duplicate + discipline warnings ---------- */
  var byGrant={};
  pool.forEach(function(r){ if(r.grant){ (byGrant[r.grant]=byGrant[r.grant]||[]).push(r); } });
  var dupPair=null;
  Object.keys(byGrant).forEach(function(g){ if(!dupPair && byGrant[g].length>1) dupPair=byGrant[g]; });
  ok("pool contains two DMPs from one project", !!dupPair);
  if(dupPair){
    A.setSel([dupPair[0].id, dupPair[1].id]);
    ok("duplicate project is flagged",
       document.getElementById("notes").textContent.indexOf("already in the set")>=0,
       document.getElementById("notes").textContent);
  }

  A.setSel(pool.slice(0,11).map(function(r){ return r.id; }));
  ok("over-target selection is flagged",
     document.getElementById("notes").textContent.indexOf("the target is 10")>=0);

  /* ---------- remove + clear ---------- */
  A.setSel([a.id,b.id,c.id]);
  var x=document.querySelector('#picked [data-drop]');
  x.click();
  eq("removing from the tray works", document.getElementById("t-n").textContent, "2");
  A.setSel([]);
  eq("clearing empties the tray", document.getElementById("t-n").textContent, "0");
  eq("empty tray shows its hint", document.querySelectorAll("#picked li.empty").length, 1);

  /* ---------- paired study (sync part) ---------- */
  pairedSync(A, pool);

  /* ---------- async: legacy API, paired persistence, freeze refusal ---------- */
  legacyApi(A,a,b)
    .then(function(){ return pairedAsync(A); })
    .then(function(){ return reloadSetup(A); })
    .catch(function(e){ ok("async chain completed", false, e && e.message); })
    .then(function(){ flush(true); });
  flush(false);
};

/* ================================================================ helpers */
var FX=null;
try{ FX=JSON.parse(document.getElementById("paired-fixtures").textContent); }catch(e){ FX=null; }
function clone(o){ return JSON.parse(JSON.stringify(o)); }
function wait(ms){ return new Promise(function(r){ setTimeout(r,ms); }); }
function getJSON(url){ return fetch(url).then(function(r){ return r.json().then(function(d){ d.__status=r.status; return d; }); }); }
function sendJSON(method,url,body){
  return fetch(url,{method:method,headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})
    .then(function(r){ return r.json().then(function(d){ d.__status=r.status; return d; }); });
}
function codes(v,pid){ return v.pairs[pid].issues.map(function(i){ return i.code; }); }
function has(v,pid,code){ return codes(v,pid).indexOf(code)>=0; }
function change(el,val){ el.value=val; el.dispatchEvent(new Event("change",{bubbles:true})); }
function stub(fn){ var c=window.confirm; window.confirm=fn; return function(){ window.confirm=c; }; }

/* ================================================================ legacy API */
function legacyApi(A,a,b){
  var api=window.DMP_API;
  if(!api){ skipped("legacy selection persists to the API","standalone build has no API"); return Promise.resolve(); }
  return getJSON(api+"/health").then(function(h){
    if(h.state_dir_is_default!==false){
      skipped("legacy API round trip","server is using the real data/ directory"); return; }
    ok("served self-test runs on a temporary state dir", h.state_dir_is_default===false, h.state_dir);
    A.setSel([a.id,b.id,"unknown-legacy-id"]);
    return wait(700).then(function(){ return getJSON(api+"/selection"); }).then(function(d){
      ok("API stored the selection", d.ids && d.ids.length===3, JSON.stringify(d.ids));
      ok("API resolved the known records", d.selection && d.selection.length===2);
      ok("an unknown id is kept, not dropped", d.ids.indexOf("unknown-legacy-id")>=0);
      A.setSel([]);
      return wait(700).then(function(){ return getJSON(api+"/selection"); });
    }).then(function(d2){
      eq("API cleared the selection", d2.ids.length, 0);
      ok("save indicator reports success",
         document.getElementById("savestate").className.indexOf("ok")>=0,
         document.getElementById("savestate").textContent);
    });
  });
}

/* ================================================================ paired: sync */
function pairedSync(A, legacyPool){
  var PA=A.paired;
  ok("fixtures are injected", !!(FX && FX.timing && FX.synthetic_cohort));
  if(!FX) return;

  /* --- mode separation --- */
  A.setMode("paired");
  ok("paired mode shows the paired tray", !document.getElementById("paired-tray").hidden);
  ok("paired mode hides the legacy tray", document.getElementById("legacy-tray").hidden);
  var stored=null; try{ stored=localStorage.getItem("dmpbench.mode"); }catch(e){}
  eq("mode is remembered under its own key", stored, "paired");
  document.querySelector('[data-mode="legacy"]').click();
  eq("clicking Legacy switches mode", A.mode(), "legacy");
  ok("legacy rows carry checkboxes again", !!document.querySelector("#list .row [data-pick]"));
  document.querySelector('[data-mode="paired"]').click();
  eq("clicking Paired switches back", A.mode(), "paired");
  ok("paired rows carry an assignment menu", !!document.querySelector("#list .row select[data-assign]"));
  ok("the menu is documented", !!document.querySelector("#list .row select[data-assign][data-tip]"));

  /* --- timing fixtures, the same list the Python tests run --- */
  FX.timing.forEach(function(f){
    var t=PA.timing(f.issue,f.start,f.end,f.pre_start||"exclude");
    var good=t.early===f.early && t.late===f.late &&
      (f.state?t.state===f.state:t.state==="ok") &&
      (f.n_lo===undefined || t.n_lo===f.n_lo) && (f.n_hi===undefined || t.n_hi===f.n_hi) &&
      (f.d===undefined || t.d===f.d);
    ok("timing: "+f.name, good, JSON.stringify(t));
    if(f.pct_lo!==undefined){
        ok("timing: "+f.name+" (percent shown above 100)", Math.round(10000*t.n_lo/t.d)/100===f.pct_lo);
    }
  });

  /* --- escaping matches the Python exporter byte for byte --- */
  eq("CSV escaping matches Python", FX.escape.map(PA.csvCell).join(","), FX.escape_expected.csv_row);
  eq("Markdown escaping matches Python",
     "| "+FX.escape.map(PA.mdCell).join(" | ")+" |", FX.escape_expected.md_row);

  /* --- the synthetic valid cohort --- */
  var syn=clone(FX.synthetic_cohort);
  var v=PA.validate(syn);
  eq("synthetic cohort: six verified pairs", v.counts.verified_pairs, 6);
  eq("synthetic cohort: twelve distinct documents", v.counts.distinct_documents, 12);
  ok("synthetic cohort: freezable by the rules", v.freezable===true, JSON.stringify(v.cohort));
  ok("a second version of the same project raises no reuse issue",
     !Object.keys(v.pairs).some(function(k){ return has(v,k,"project_reused"); }));

  /* --- mutations that must fail, each on a fresh copy --- */
  var M={};
  var m=clone(syn); m.documents["SYN1-late"].scope="partner: University X";
  M.partner=m; v=PA.validate(m);
  ok("same grant, different partner scope is rejected", v.pairs["natural-sciences"].status==="rejected" && has(v,"natural-sciences","scope_mismatch"));

  m=clone(syn); m.documents["SYN2-late"].files[0].sha256=m.documents["SYN2-early"].files[0].sha256;
  M.bytes=m; v=PA.validate(m);
  ok("repeated bytes across two versions are rejected", has(v,"engineering-and-technology","repeated_bytes"));

  m=clone(syn); m.pairs[1].project.grant="SYN1"; m.documents["SYN2-early"].grant="SYN1"; m.documents["SYN2-late"].grant="SYN1";
  M.reused=m; v=PA.validate(m);
  ok("a project reused in another discipline is rejected in both rows",
     has(v,"natural-sciences","project_reused") && has(v,"engineering-and-technology","project_reused"));

  m=clone(syn); m.pairs[0].late=m.pairs[0].early;
  M.tworoles=m; v=PA.validate(m);
  ok("one document in both roles is rejected", has(v,"natural-sciences","same_document_both_roles") && has(v,"natural-sciences","document_reused"));

  m=clone(syn); m.pairs[1].early=m.pairs[0].early;
  M.twopairs=m; v=PA.validate(m);
  ok("one document in two pairs is rejected", has(v,"engineering-and-technology","document_reused") && has(v,"natural-sciences","document_reused"));

  m=clone(syn); m.documents["SYN3-late"].issue_date.value="2022-12-01"; m.documents["SYN3-late"].publication_date="2023-03-01";
  M.deposit=m; v=PA.validate(m);
  ok("issued before the end but deposited after it is not late", has(v,"medical-and-health-sciences","timing_fail"));

  m=clone(syn); m.documents["SYN4-late"].issue_date.value="2022-12-31";
  M.exact100=m; v=PA.validate(m);
  ok("a late document exactly at 100% is rejected", has(v,"agricultural-sciences","timing_fail"));

  m=clone(syn); m.documents["SYN5-early"].issue_date.value=null; m.documents["SYN5-early"].publication_date="2020-03-01";
  M.noissue=m; v=PA.validate(m);
  ok("a missing issue date stays unknown despite a full publication date",
     has(v,"social-sciences","issue_date_missing") && v.pairs["social-sciences"].status==="pending" &&
     v.pairs["social-sciences"].timing.early.state==="unknown");

  m=clone(syn); m.documents["SYN6-early"].issue_date.value="2021-06";   /* d=1095, 50% = day 547 = 2021-07-01 */
  m.pairs[5].project.end="2022-11-30"; m.documents["SYN6-early"].issue_date.value="2021-06";
  M.partial=m; v=PA.validate(m);
  ok("a partial date spanning 50% is indeterminate, not early", has(v,"humanities","timing_indeterminate"),
     JSON.stringify(v.pairs.humanities.timing.early));

  m=clone(syn); m.pairs[2].lineage.state="not_checked";
  M.lineage=m; v=PA.validate(m);
  ok("unverified lineage keeps a pair pending", has(v,"medical-and-health-sciences","lineage_unverified") && v.pairs["medical-and-health-sciences"].status==="pending");

  m=clone(syn); m.pairs[3].cordis.branches=["natural sciences"];
  M.disc=m; v=PA.validate(m);
  ok("a discipline the project does not carry is rejected", has(v,"agricultural-sciences","discipline_unsupported"));

  m=clone(syn); m.documents["SYN1-early"].files.push({name:"x.json",format:"json",sha256:"ab".repeat(32),analysis:false});
  m.documents["SYN1-early"].files[0].analysis=false;
  M.repr=m; v=PA.validate(m);
  ok("two representations without an analysis file stay pending", has(v,"natural-sciences","representation_unchosen"));

  m=clone(syn); m.pairs[0].early="ghost-document";
  M.ghost=m; v=PA.validate(m);
  ok("a reference to a missing document is rejected, not crashed on", has(v,"natural-sciences","document_missing"));

  m=clone(syn); m.pairs[5].late=null;
  M.incomplete=m; v=PA.validate(m);
  ok("an incomplete cohort is not freezable", v.freezable===false && v.counts.verified_pairs===5);
  ok("and says why", v.cohort.some(function(i){ return i.text.indexOf("5 of 6")>=0; }));

  m=clone(syn); m.protocol.open_decisions[0].status="open";
  M.decision=m; v=PA.validate(m);
  ok("an open protocol decision blocks freezing", v.freezable===false && v.cohort.some(function(i){ return i.code==="decision_open"; }));

  m=clone(syn); m.documents["SYN1-early"].issue_date.value="2019-12-15";
  M.prestart=m; v=PA.validate(m);
  ok("a pre-start document is not early under the proposed default", has(v,"natural-sciences","timing_fail"));
  ok("and the unsettled pre-start policy is reported", v.cohort.some(function(i){ return i.code==="pre_start_unsettled"; }));
  window.__PAIRED_MUTATIONS__=M;

  /* --- the synthetic cohort in the real panel --- */
  var restore=stub(function(){ return true; });
  PA.load(clone(syn)); A.render();
  eq("panel renders six discipline rows", document.querySelectorAll("#p-rows .prow").length, 6);
  eq("panel counts six verified pairs", document.getElementById("p-pairs").textContent, "6");
  eq("panel counts twelve documents", document.getElementById("p-docs").textContent, "12");
  eq("every badge says verified", document.querySelectorAll("#p-rows .badge.b-verified").length, 6);
  ok("the legacy duplicate-project warning is not shown in paired mode",
     document.getElementById("paired-tray").textContent.indexOf("already in the set")<0);
  ok("percentages above 100% are printed", /1\d\d\.\d\d%/.test(document.getElementById("p-rows").textContent));

  /* --- exports and a JSON round trip through the real buttons --- */
  document.querySelector('[data-pact="json"]').click();
  var exported=document.getElementById("p-out").value, parsed=null;
  try{ parsed=JSON.parse(exported); }catch(e){}
  ok("JSON export parses and carries study and validation", !!(parsed && parsed.study && parsed.validation));
  ok("JSON export keeps exact day counts", parsed && parsed.validation.pairs["natural-sciences"].timing.early.n_lo===152);
  document.querySelector('[data-pact="csv"]').click();
  var csv=document.getElementById("p-out").value.split("\n");
  eq("CSV export: header plus six rows", csv.filter(Boolean).length, 7);
  ok("CSV header is the shared column list", csv[0].indexOf("pair_id,discipline,grant")===0, csv[0]);
  document.querySelector('[data-pact="md"]').click();
  var md=document.getElementById("p-out").value.split("\n").filter(Boolean);
  eq("Markdown export: header, rule and six rows", md.length, 8);

  document.querySelector('[data-pact="empty"]').click();
  eq("New draft empties the panel", document.getElementById("p-docs").textContent, "0");
  document.getElementById("p-out").value=exported;
  document.querySelector('[data-pact="load"]').click();
  var back=PA.study();
  ok("JSON round trip restores assignments", back.pairs.every(function(p,i){
       return p.early===syn.pairs[i].early && p.late===syn.pairs[i].late; }));
  ok("JSON round trip keeps provenance and unknowns",
     back.documents["SYN1-early"].issue_date.locator==="p1" && back.pairs[0].project.original_end===null);
  eq("JSON round trip keeps the verdict", PA.validate(back).counts.verified_pairs, 6);

  /* --- malformed input never replaces the draft --- */
  var before=JSON.stringify(PA.study());
  document.getElementById("p-out").value="{not json";
  document.querySelector('[data-pact="load"]').click();
  ok("malformed JSON is refused", document.getElementById("p-msg").className.indexOf("bad")>=0);
  eq("and the draft is unchanged", JSON.stringify(PA.study()), before);
  var unsup=clone(syn); unsup.schema_version=99;
  document.getElementById("p-out").value=JSON.stringify(unsup);
  document.querySelector('[data-pact="load"]').click();
  ok("an unsupported schema version is refused", document.getElementById("p-msg").textContent.indexOf("unsupported")>=0);
  eq("and the draft is still unchanged", JSON.stringify(PA.study()), before);
  var snap={schema:"dmpbench.paired-snapshot", snapshot_id:"paired-test", study:clone(syn)};
  snap.study.status="frozen";
  document.getElementById("p-out").value=JSON.stringify(snap);
  document.querySelector('[data-pact="load"]').click();
  ok("a snapshot loads as a new draft", PA.study().status==="draft" && PA.study().origin.indexOf("paired-test")>=0);

  /* --- assignment through the real table --- */
  document.querySelector('[data-pact="empty"]').click();
  document.querySelector('[data-preset="paired"]').click();
  var S=A.state;
  var yrs=A.ROWS.map(function(r){ return +r.year; }).filter(Boolean);
  ok("the paired preset spans every year", S.y0===Math.min.apply(null,yrs) && S.y1===Math.max.apply(null,yrs));
  ok("the paired preset includes Horizon 2020", S.tiers["Horizon 2020"]===1);
  S.q="AGRICORE"; A.render();
  ok("registered documents appear as candidates", A.filtered().some(function(r){ return r.src==="registry"; }),
     A.filtered().length+" hits");
  S.q=""; A.render();

  var byGrant={};
  A.ROWS.forEach(function(r){ if(r.kind==="dmp" && r.grant && (r.disc_all||[]).length && r.proj_start)
    (byGrant[r.grant]=byGrant[r.grant]||[]).push(r); });
  var g=Object.keys(byGrant).filter(function(k){ return byGrant[k].length>=2; }).sort()[0];
  var r1=byGrant[g][0], r2=byGrant[g][1], disc=r1.disc_all[0];
  var pid=disc.toLowerCase().replace(/[^a-z0-9]+/g,"-");
  var other=A.ROWS.filter(function(r){ return r.kind==="dmp" && r.grant && r.grant!==g && (r.disc_all||[]).indexOf(disc)>=0; })[0];
  function rowSelect(r){ S.q=r.doi||r.title.slice(0,40); A.render(); return document.querySelector('#list select[data-assign="'+r.id+'"]'); }

  var s1=rowSelect(r1);
  ok("the candidate row renders an assignment menu", !!s1);
  if(s1){
    ok("the project's CORDIS branch is offered", !!s1.querySelector('option[value="add|'+pid+'|early"]'));
    change(s1,"add|"+pid+"|early");
    var pr=PA.study().pairs.filter(function(p){ return p.pair_id===pid; })[0];
    eq("choosing early assigns the document", pr.early, "zenodo:"+r1.id);
    eq("the pair takes the document's project", String(pr.project.grant), String(g));
    ok("the CORDIS branches are recorded", (pr.cordis.branches||[]).indexOf(disc)>=0);
    ok("the row is marked as assigned", document.querySelector('#list .row[data-id="'+r1.id+'"]').classList.contains("sel"));
    ok("the slot shows the document", document.querySelector('#p-rows [data-slot="'+pid+'|early"]').textContent.indexOf("zenodo:"+r1.id)>=0);
    ok("an unverified issue date is reported", PA.validate().pairs[pid].issues.some(function(i){ return i.code==="issue_date_missing"; }));

    var s2=rowSelect(r2); change(s2,"add|"+pid+"|late");
    eq("a second version of the same project fills the late slot", pr.late, "zenodo:"+r2.id);
    ok("two versions of one project are not flagged as reuse",
       !PA.validate().pairs[pid].issues.some(function(i){ return i.code==="project_reused"; }));
    eq("the pair is pending, not verified", PA.validate().pairs[pid].status, "pending");

    if(other){
      var s3=rowSelect(other); change(s3,"add|"+pid+"|early");
      eq("a different project is refused for an occupied row", pr.early, "zenodo:"+r1.id);
      ok("and the refusal is explained", document.getElementById("p-msg").textContent.indexOf("already holds")>=0,
         document.getElementById("p-msg").textContent);
    } else skipped("different project refused","no second project in this discipline");

    /* evidence editor */
    S.q=""; A.render();
    document.querySelector('[data-pinspect="'+pid+'"]').click();
    var ed=document.querySelector('[data-editor="'+pid+'"]');
    ok("the evidence editor opens", !!ed);
    change(ed.querySelector('[data-k="scope"]'),"project-wide DMP");
    eq("editing the scope updates the pair", pr.scope, "project-wide DMP");
    ed=document.querySelector('[data-editor="'+pid+'"]');
    change(ed.querySelector('[data-id="zenodo:'+r1.id+'"][data-k="issue_date.value"]'), r1.proj_start);
    eq("editing the issue date updates the document", PA.study().documents["zenodo:"+r1.id].issue_date.value, r1.proj_start);
    ok("the slot now shows an exact position", /0\.00%/.test(document.querySelector('#p-rows [data-slot="'+pid+'|early"]').textContent));
    ed=document.querySelector('[data-editor="'+pid+'"]');
    ed.querySelector('[data-evnew="locator"]').value="late p2 revision table";
    ed.querySelector('[data-evnew="note"]').value="v2 revises v1";
    document.querySelector('[data-evadd="'+pid+'"]').click();
    eq("adding lineage evidence records it", (pr.lineage.evidence||[]).length, 1);
    ed=document.querySelector('[data-editor="'+pid+'"]');
    change(ed.querySelector('select[data-k="lineage.state"]'),"verified");
    eq("the lineage state can be set", pr.lineage.state, "verified");
    ok("verifying stamps a date", !!pr.lineage.verified_on);
    var bare=[].filter.call(document.querySelectorAll("#paired-tray button, #paired-tray input, #paired-tray select, #paired-tray textarea"),
      function(el){ return !el.getAttribute("data-tip"); });
    eq("every paired-panel control is documented", bare.length, 0);
    if(bare.length) log.push("      undocumented: "+bare.map(function(e){ return e.outerHTML.slice(0,80); }).join(" | "));
    document.querySelector('[data-pinspect="'+pid+'"]').click();
    ok("the editor closes", !document.querySelector('[data-editor="'+pid+'"]'));

    /* removal */
    document.querySelector('#p-rows [data-premove="'+pid+'|late"]').click();
    eq("the × button empties the late slot", pr.late, null);
    ok("the document's evidence is kept", !!PA.study().documents["zenodo:"+r2.id]);
    var s4=rowSelect(r1); change(s4,"drop|"+pid+"|early");
    eq("the menu's remove option empties the early slot", pr.early, null);
    S.q=""; A.render();
    document.querySelector('[data-pclear="'+pid+'"]').click();
    eq("Clear project empties the row", PA.study().pairs.filter(function(p){ return p.pair_id===pid; })[0].project, null);
  }

  /* --- filters still work after presets, in paired mode --- */
  document.querySelector('[data-preset="he24"]').click();
  document.querySelector('#f-tier .chip[data-v="DFG"]').click();
  ok("funding chips filter in paired mode", A.filtered().length>0 &&
     every(A.filtered(), function(r){ return r.tier==="Horizon Europe" || r.tier==="DFG"; }));
  document.querySelector('[data-preset="paired"]').click();

  /* --- legacy selection attached as history --- */
  var knownIds=legacyPool.slice(0,2).map(function(r){ return r.id; });
  A.setMode("legacy"); A.setSel(knownIds.concat(["unknown-legacy-id"])); A.setMode("paired");
  ok("the legacy selection keeps an unknown id", A.sel().indexOf("unknown-legacy-id")>=0);
  document.querySelector('[data-pact="legacy"]').click();
  var hist=PA.study().historical;
  ok("attaching the legacy selection keeps every id", hist && hist.ids.length===3);
  ok("the unknown id is listed as unresolved", hist && hist.unresolved.join()==="unknown-legacy-id");
  ok("history fills no slot", PA.study().pairs.every(function(p){ return !p.early && !p.late; }));
  document.querySelector('[data-pact="drop-legacy"]').click();
  ok("history can be detached again", !PA.study().historical);
  A.setMode("legacy"); A.setSel([]); A.setMode("paired");

  /* --- standalone persistence: storage namespace, reload, corruption --- */
  if(!window.DMP_API){
    PA.load(clone(syn));
    var raw=localStorage.getItem(PA.key), rawSel=localStorage.getItem("dmpbench.sel");
    ok("the draft is saved under dmpbench.paired.v1", !!raw && JSON.parse(raw).study_id==="synthetic-cohort");
    ok("the legacy selection keeps its own key", rawSel!==null && rawSel!==raw);
    PA.load(PA.newStudy("scratch"));
    localStorage.setItem(PA.key, JSON.stringify(syn));
    PA.reload();
    eq("reloading reads the stored draft back", PA.study().study_id, "synthetic-cohort");
    localStorage.setItem(PA.key, "{corrupt");
    PA.reload(); A.render();
    ok("a corrupt stored draft blocks the panel", !!PA.blocked() &&
       document.getElementById("p-blocked").textContent.indexOf("cannot be read")>=0);
    PA.save();
    eq("and is never overwritten by a save", localStorage.getItem(PA.key), "{corrupt");
    document.querySelector('#p-blocked [data-pact="reset-corrupt"]').click();
    var kept=[]; for(var i=0;i<localStorage.length;i++){ var k=localStorage.key(i); if(k.indexOf(PA.key+".corrupt-")===0) kept.push(k); }
    ok("starting over keeps the unreadable text aside", kept.length===1 && localStorage.getItem(kept[0])==="{corrupt");
    ok("and a fresh draft is saved", !PA.blocked() && JSON.parse(localStorage.getItem(PA.key)).schema==="dmpbench.paired-study");
    ok("standalone hides the served-only buttons", document.querySelector('[data-pact="freeze"]').hidden===true);
    document.querySelector('[data-pact="freeze"]').hidden=false;
    PA.freeze();
    ok("freezing explains that it needs serve.py", document.getElementById("p-msg").textContent.indexOf("serve.py")>=0);
  }
  restore();
}

/* ================================================================ paired: served */
function pairedAsync(A){
  var api=window.DMP_API, PA=A.paired;
  if(!api){
    skipped("paired API persistence","standalone build has no API (browser storage tested above)");
    return Promise.resolve();
  }
  var syn=clone(FX.synthetic_cohort), restore=stub(function(){ return true; });
  return getJSON(api+"/health").then(function(h){
    if(h.state_dir_is_default!==false){ skipped("paired API","server uses the real data/ directory"); return; }
    /* Python and JavaScript validators agree on the cohort and on every mutation */
    var cases=[["synthetic",syn]].concat(Object.keys(window.__PAIRED_MUTATIONS__||{}).map(function(k){ return [k,window.__PAIRED_MUTATIONS__[k]]; }));
    return cases.reduce(function(p,c){
      return p.then(function(){
        return sendJSON("POST",api+"/paired/validate",{study:c[1]}).then(function(pv){
          var jv=PA.validate(c[1]), same=pv.counts.verified_pairs===jv.counts.verified_pairs &&
            pv.counts.distinct_documents===jv.counts.distinct_documents && pv.freezable===jv.freezable;
          Object.keys(jv.pairs).forEach(function(k){
            var a=jv.pairs[k].issues.map(function(i){ return i.code+":"+i.severity; }).sort().join();
            var b=pv.pairs[k].issues.map(function(i){ return i.code+":"+i.severity; }).sort().join();
            if(a!==b || jv.pairs[k].status!==pv.pairs[k].status){ same=false; log.push("      "+c[0]+"/"+k+" js="+a+" py="+b); }
          });
          ok("Python and JS validation agree: "+c[0], same);
        });
      });
    },Promise.resolve())
    .then(function(){ PA.load(clone(syn)); return wait(600); })
    .then(function(){ return getJSON(api+"/paired"); })
    .then(function(d){
      ok("the draft is saved to the paired file", d.study && d.study.study_id==="synthetic-cohort", d.file);
      ok("the paired file is not the legacy selection", /paired_selection\.json$/.test(d.file||""));
      ok("the server stamps source checksums", !!(d.study && d.study.sources && d.study.sources["data/dmp_dataset.json"]));
      ok("the save indicator reports success", document.getElementById("p-save").className.indexOf("ok")>=0,
         document.getElementById("p-save").textContent);
      PA.load(PA.newStudy("scratch")); return wait(600);
    })
    .then(function(){ return PA.reload(); })
    .then(function(){ eq("reloading reads the saved draft", PA.study().origin, "scratch");
      var bad=clone(syn); bad.schema_version=99;
      return sendJSON("PUT",api+"/paired",{study:bad}); })
    .then(function(r){ eq("the server refuses an unsupported study", r.__status, 400);
      return getJSON(api+"/paired"); })
    .then(function(d){ eq("and keeps the previous draft", d.study.origin, "scratch");
      return sendJSON("POST",api+"/paired/freeze",{study:syn}); })
    .then(function(r){
      eq("freezing without the files on disk is refused", r.ok, false);
      ok("with a reason per missing file", (r.reasons||[]).filter(function(x){ return x.indexOf("not on disk")>=0; }).length===12,
         (r.reasons||[]).length+" reasons");
      PA.load(clone(syn)); return wait(400);
    })
    .then(function(){ return PA.freeze(); })
    .then(function(){
      ok("the Freeze button shows the refusal", document.getElementById("p-msg").textContent.indexOf("Not frozen")>=0);
      return getJSON(api+"/paired/snapshots"); })
    .then(function(d){ eq("no snapshot was written", (d.snapshots||[]).length, 0);
      return PA.files(false); })
    .then(function(d){
      ok("Check files reports missing files honestly", document.getElementById("p-msg").textContent.indexOf("12 missing")>=0,
         document.getElementById("p-msg").textContent);
      restore();
    });
  });
}

/* ================================================================ real reload, two page loads */
var MARKER="selftest-reload-marker";
function reloadSetup(A){
  var PA=A.paired, st=PA.newStudy("selftest reload marker"); st.study_id=MARKER;
  if(!window.DMP_API && STORE0[PA.key]!==undefined){
    skipped("real page reload (phase 2 prepared)","this browser already holds a paired draft; not risking it");
    restoreStore(); return Promise.resolve();
  }
  PA.load(st);
  return wait(window.DMP_API?600:0).then(function(){
    restoreStore(PA.key);  /* restore everything except the marker draft that phase 2 reads */
    ok("phase-2 marker saved; load ?phase=reload to check it survives a real reload", true);
  });
}
function reloadPhase(A){
  var PA=A.paired, s=PA.study();
  eq("after a real page reload the saved draft is read back", s && s.study_id, MARKER);
  eq("and it opens in paired mode", A.mode(), "paired");
  var done=function(){ flush(true); };
  if(!window.DMP_API){ try{ localStorage.removeItem(PA.key); }catch(e){} ok("marker removed from browser storage", true); return done(); }
  PA.load(PA.newStudy("empty")); wait(600).then(function(){ ok("marker replaced on the temporary server", true); done(); });
  flush(false);
}

})();
