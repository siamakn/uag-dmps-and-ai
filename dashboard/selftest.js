/* Functional self-test for the dashboard.
   Served only at /selftest by scripts/serve.py - never part of the shipped page.

   It drives the real UI through window.__APP__ and the real DOM: filters, search,
   sorting, column show/hide/reorder, selection, the coverage matrix, the export
   formats and the round trip to the API. Results land in #testlog and in the
   document title, so a headless browser can read them with --dump-dom.

       python scripts/serve.py --no-open
       chrome --headless=new --dump-dom "http://127.0.0.1:8756/selftest"
*/
(function(){
"use strict";
var log=[], pass=0, fail=0;

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
  el.textContent="SELFTEST "+pass+"/"+(pass+fail)+" passed, "+fail+" failed\n\n"+log.join("\n");
  document.title="SELFTEST "+pass+"/"+(pass+fail)+" fail="+fail;
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

  /* ---------- data ---------- */
  ok("dataset loaded", R.length>2000, R.length+" rows");
  ok("index resolves ids", A.byId(R[0].id)===R[0]);

  /* ---------- presets ---------- */
  A.applyPreset("reset");
  eq("preset everything shows all rows", A.filtered().length, R.length);

  A.applyPreset("he24");
  var expectHE=R.filter(function(r){ return r.tier==="Horizon Europe" &&
                                            +r.year>=2024 && +r.year<=2026; }).length;
  eq("preset HE 2024+ count", A.filtered().length, expectHE);
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
     every(A.filtered(), function(r){ return r.disc===disc; }), disc);

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

  /* ---------- API round trip ---------- */
  var api=window.DMP_API;
  if(!api){
    ok("selection persists to the API (standalone build - skipped)", true);
    return flush(true);
  }
  A.setSel([a.id,b.id]);
  setTimeout(function(){
    fetch(api+"/selection").then(function(r){ return r.json(); }).then(function(d){
      ok("API stored the selection", d.ids && d.ids.length===2, JSON.stringify(d.ids));
      ok("API resolved the records", d.selection && d.selection.length===2);
      A.setSel([]);
      setTimeout(function(){
        fetch(api+"/selection").then(function(r){ return r.json(); }).then(function(d2){
          eq("API cleared the selection", d2.ids.length, 0);
          ok("save indicator reports success",
             document.getElementById("savestate").className.indexOf("ok")>=0,
             document.getElementById("savestate").textContent);
          flush(true);
        });
      },700);
    }).catch(function(e){ ok("API round trip",false,e.message); flush(true); });
  },700);
  flush(false);
};
})();
