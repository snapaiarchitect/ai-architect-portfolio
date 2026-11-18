#!/usr/bin/env python3
"""Build the GMI Savings Tracker charts for the portfolio, in the same Plotly style as charts/*.html.

Reads the tracker's published tables (site_data/*.csv of EVO3-Ecosystem/gmi-savings-tracker-v3) and writes
charts/gmi_<tab>.html, one page per tracker tab. Every figure in a title is computed from the data here, never typed.

    python scripts/build_gmi_charts.py /path/to/gmi-savings-tracker-v3/site_data
"""
import json
import sys
from pathlib import Path

import pandas as pd

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "site_data")
OUT = Path(__file__).resolve().parent.parent / "charts"
AS_OF = "2026-11-13"
SOURCE = f"Source: Maryland Open Data Portal via the GMI Savings Tracker (testing ground v3), data as of {AS_OF}"
GOLD, CYAN, CYAN_HI, GREEN, RED, MUTED = "#f59e0b", "#06b6d4", "#22d3ee", "#22c55e", "#f87171", "#64748b"
PALETTE = [GOLD, CYAN, "#a78bfa", "#34d399", "#f472b6", "#60a5fa", "#fbbf24"]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ | GMI Savings Tracker</title>
<script src="https://cdn.plot.ly/plotly-3.5.0.min.js"></script>
<style>
  body { margin:0; padding:0; background:#0a0e1a; color:#f0f0f0; font-family:'Segoe UI',Roboto,sans-serif; }
  #chart { width:100vw; height:100vh; }
  .title-bar { position:absolute; top:12px; left:20px; right:20px; z-index:10; pointer-events:none; }
  .title-bar h1 { margin:0; font-size:18px; color:#f0f0f0; font-weight:600; line-height:1.25; }
  .title-bar p  { margin:4px 0 0; font-size:12px; color:#8892b0; }
  .foot { position:absolute; left:20px; right:20px; bottom:6px; z-index:10; font-size:11px; color:#8892b0; pointer-events:none; }
</style>
</head>
<body>
<div class="title-bar">
  <h1>__TITLE__</h1>
  <p>__SUB__</p>
</div>
<div id="chart"></div>
<div class="foot">__FOOT__</div>
<script>
var D = __DATA__;
var GOLD='#f59e0b', CYAN='#06b6d4', GREEN='#22c55e', RED='#f87171', MUTED='#64748b';
var PALETTE = __PALETTE__;
var base = {
  paper_bgcolor:'#0a0e1a', plot_bgcolor:'#0a0e1a',
  font:{family:'Segoe UI,Roboto,sans-serif', color:'#f0f0f0', size:12},
  margin:{t:92, b:92, l:70, r:24},
  hoverlabel:{bgcolor:'#1a2234', bordercolor:'#1f2d44', font:{color:'#f0f0f0'}},
  legend:{orientation:'h', y:-0.12, font:{color:'#94a3b8'}},
  xaxis:{gridcolor:'#1f2d44', zerolinecolor:'#1f2d44', linecolor:'#1f2d44', tickfont:{color:'#94a3b8'}},
  yaxis:{gridcolor:'#1f2d44', zerolinecolor:'#1f2d44', linecolor:'#1f2d44', tickfont:{color:'#94a3b8'}}
};
function merge(a,b){var o=JSON.parse(JSON.stringify(a));for(var k in b){if(b[k]&&typeof b[k]==='object'&&!Array.isArray(b[k])&&o[k]&&typeof o[k]==='object'){o[k]=merge(o[k],b[k]);}else{o[k]=b[k];}}return o;}
var config = {responsive:true, displayModeBar:false};
__JS__
</script>
</body>
</html>
"""


def money(v, d=1):
    return f"${v / 1e9:.{d}f}B" if abs(v) >= 1e9 else f"${v / 1e6:.{d}f}M"


def write(tab, title, sub, js, data, foot=SOURCE):
    html = (PAGE.replace("__TITLE__", title).replace("__SUB__", sub).replace("__FOOT__", foot)
            .replace("__PALETTE__", json.dumps(PALETTE)).replace("__JS__", js)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=float)))
    (OUT / f"gmi_{tab}.html").write_text(html, encoding="utf-8")
    print("wrote", f"charts/gmi_{tab}.html", f"{len(html) // 1024} KB")


def read(name):
    return pd.read_csv(SRC / f"{name}.csv")


def over():
    t = read("totals_by_fy")
    d = {"fy": t.fiscal_year.tolist(), "b": (t.total_payments / 1e9).round(3).tolist(),
         "rec": t.payment_records.tolist(), "ven": t.vendors.tolist(), "ag": t.agencies.tolist()}
    first, last = t.iloc[0], t.iloc[-1]
    title = f"State payments grew from {money(first.total_payments)} in FY{int(first.fiscal_year)} to {money(last.total_payments)} in FY{int(last.fiscal_year)}"
    sub = "Total payments by Maryland State fiscal year (July 1 to June 30), nominal dollars. Hover a bar for records, agencies and vendors."
    js = """
var op = D.fy.map(function(y){return y===2026?0.65:1;});
var tr = {type:'bar', x:D.fy, y:D.b, marker:{color:GOLD, opacity:op, line:{color:'#0a0e1a',width:1}},
  customdata:D.fy.map(function(y,i){return [D.rec[i],D.ag[i],D.ven[i]];}),
  hovertemplate:'<b>FY%{x}</b><br>$%{y:.1f}B paid<br>%{customdata[0]:,} payment records<br>%{customdata[1]} agencies, %{customdata[2]:,} vendors<extra></extra>'};
var i22=D.fy.indexOf(2022), i26=D.fy.indexOf(2026);
var layout = merge(base,{
  xaxis:{dtick:1, tickprefix:'FY', tickangle:-45}, yaxis:{title:{text:'$ billions'}, ticksuffix:'B', tickprefix:'$', rangemode:'tozero'}, showlegend:false,
  annotations:[
   {x:2022,y:D.b[i22],ax:-70,ay:-60,text:'FY2022 as published includes a second<br>$874.5M block (a source issue the<br>tracker reports, not a saving)',showarrow:true,arrowcolor:'#94a3b8',font:{size:11,color:'#94a3b8'},align:'left'},
   {x:2026,y:D.b[i26],ax:-20,ay:-46,text:'Latest year<br>in the data',showarrow:true,arrowcolor:'#94a3b8',font:{size:11,color:'#94a3b8'}}]
});
Plotly.newPlot('chart',[tr],layout,config);
"""
    write("over", title, sub, js, d)


def areas():
    a = read("f_area")
    x = a[(a.stage == "Actual") & a.area.notna()]
    tab = x.pivot_table(index="fiscal_year", columns="area", values="spend", aggfunc="sum").fillna(0)
    order = tab.sum().sort_values(ascending=False).index.tolist()
    tot = tab.sum().sum()
    top = order[0]
    title = f"{top} is {tab[top].sum() / tot:.0%} of the {money(tot)} spent in six focus areas, FY{tab.index.min()}-FY{tab.index.max()}"
    sub = "Actual controllable spending by focus area and fiscal year. Click a legend entry to hide or show an area."
    d = {"fy": tab.index.tolist(), "areas": order, "v": {k: (tab[k] / 1e9).round(3).tolist() for k in order}}
    js = """
var tr = D.areas.map(function(a,i){return {type:'bar',name:a,x:D.fy,y:D.v[a],marker:{color:PALETTE[i%PALETTE.length]},
  hovertemplate:'<b>'+a+'</b><br>FY%{x}: $%{y:.2f}B<extra></extra>'};});
var layout = merge(base,{barmode:'stack', xaxis:{dtick:1,tickprefix:'FY',tickangle:-45}, yaxis:{title:{text:'$ billions'},tickprefix:'$',ticksuffix:'B'}, legend:{y:-0.18}});
Plotly.newPlot('chart',tr,layout,config);
"""
    write("areas", title, sub, js, d)


def track():
    s = read("d_savings_status").copy()
    s["item"] = s["item"].str.replace(r"\s*\(.*?\)", "", regex=True)
    s = s.dropna(subset=["before", "after"])
    n = s.status.value_counts()
    fell = int(n.get("Seen", 0) + n.get("Payments fell", 0))
    title = (f"Of {len(s)} GMI savings items checked against payments, {fell} show payments falling, {int(n.get('Payments did not fall', 0))} do not, "
             f"{int(n.get('Not seen yet', 0))} are not seen yet and {int(n.get('Projected only', 0))} are projected only")
    sub = "Payments to the matching vendors, FY2025 to FY2026 ($ millions, log scale). Green: payments fell. Gold: not seen yet. Red: payments did not fall."
    d = {"item": s["item"].tolist(), "before": (s.before / 1e6).round(2).tolist(), "after": (s.after / 1e6).round(2).tolist(),
         "status": s.status.tolist(), "reported": (s.reported / 1e6).round(2).where(s.reported.notna(), None).tolist(), "id": s.check_id.tolist()}
    js = """
var col={'Seen':GREEN,'Payments fell':GREEN,'Payments did not fall':RED,'Not seen yet':GOLD,'Projected only':MUTED};
var order=D.item.map(function(_,i){return i;}).sort(function(a,b){return D.before[a]-D.before[b];});
var y=order.map(function(i){return D.id[i]+' '+(D.item[i].length>52?D.item[i].slice(0,51)+'…':D.item[i]);});
var lines=[]; order.forEach(function(i,k){lines.push({type:'line',x0:D.before[i],x1:D.after[i],y0:k,y1:k,line:{color:'#334155',width:3}});});
function trace(name,key,color){return {type:'scatter',mode:'markers',name:name,x:order.map(function(i){return D[key][i];}),y:y,
  marker:{size:11,color:color||order.map(function(i){return col[D.status[i]];}),line:{color:'#0a0e1a',width:1}},
  customdata:order.map(function(i){return [D.status[i],D.reported[i]===null?'not given':'$'+D.reported[i]+'M',D.before[i],D.after[i]];}),
  hovertemplate:'<b>%{y}</b><br>Status: %{customdata[0]}<br>Reported saving: %{customdata[1]}<br>FY2025: $%{customdata[2]}M, FY2026: $%{customdata[3]}M<extra></extra>'};}
var layout=merge(base,{shapes:lines,xaxis:{type:'log',title:{text:'Payments to matching vendors, $ millions (log scale)'},tickvals:[1,3,10,30,100],ticktext:['$1M','$3M','$10M','$30M','$100M']},
  yaxis:{automargin:true,tickfont:{size:11,color:'#cbd5e1'}},margin:{l:330},legend:{y:-0.2}});
Plotly.newPlot('chart',[trace('FY2025 (before)','before','#64748b'),trace('FY2026 (after, coloured by status)','after')],layout,config);
"""
    write("track", title, sub, js, d)


def opp():
    o = read("d_opps")
    g = (o.groupby("detector")[["likely", "high"]].sum() / 1e6).sort_values("high", ascending=False)
    b = read("d_detector_backtest")
    bt = b.groupby(["detector", "cohort"])[["units", "flagged_next"]].sum()
    bt["share"] = bt.flagged_next / bt.units
    dets = g.index.tolist()
    flagged = [round(float(bt.loc[(x, "Flagged"), "share"]), 3) for x in dets]
    nf_units = [int(bt.loc[(x, "Flagged"), "units"]) for x in dets]
    nn_units = [int(bt.loc[(x, "Not flagged"), "units"]) for x in dets]
    notf = [round(float(bt.loc[(x, "Not flagged"), "share"]), 3) for x in dets]
    title = f"{len(o)} leads worth up to {money(o.high.sum())} a year ({money(o.likely.sum())} likely); they overlap and are not additive"
    sub = "Left: leads by detector. Right: of units flagged in an earlier year, the share flagged again the next year, against units not flagged (reruns as of earlier years; hover for unit counts, small for Tail spend)."
    d = {"det": dets, "likely": g.likely.round(1).tolist(), "high": g.high.round(1).tolist(), "n": o.groupby("detector").size().reindex(dets).tolist(), "fl": flagged, "nf": notf, "uf": nf_units, "un": nn_units}
    js = """
var t1=[{type:'bar',name:'Likely',x:D.det,y:D.likely,marker:{color:GOLD},customdata:D.n,hovertemplate:'<b>%{x}</b><br>Likely: $%{y}M a year<br>%{customdata} leads<extra></extra>'},
        {type:'bar',name:'High end',x:D.det,y:D.high,marker:{color:CYAN},hovertemplate:'<b>%{x}</b><br>High end: $%{y}M a year<extra></extra>'}];
var t2=[{type:'bar',name:'Flagged earlier',x:D.det,y:D.fl,xaxis:'x2',yaxis:'y2',marker:{color:GOLD},customdata:D.uf,hovertemplate:'<b>%{x}</b><br>Flagged again next year: %{y:.0%}<br>%{customdata} units flagged earlier<extra></extra>'},
        {type:'bar',name:'Not flagged earlier',x:D.det,y:D.nf,xaxis:'x2',yaxis:'y2',marker:{color:MUTED},customdata:D.un,hovertemplate:'<b>%{x}</b><br>Flagged next year: %{y:.0%}<br>%{customdata} units not flagged earlier<extra></extra>'}];
var layout=merge(base,{grid:{rows:1,columns:2,pattern:'independent',xgap:0.12},barmode:'group',
  yaxis:{title:{text:'$ millions a year'},tickprefix:'$',ticksuffix:'M'},
  yaxis2:{tickformat:'.0%',range:[0,1],gridcolor:'#1f2d44',tickfont:{color:'#94a3b8'}},
  xaxis2:{tickfont:{color:'#94a3b8'},gridcolor:'#1f2d44'}, legend:{y:-0.2}});
Plotly.newPlot('chart',t1.concat(t2),layout,config);
"""
    write("opp", title, sub, js, d)


def calc():
    p = read("d_plan50").copy()
    p["cl"], p["ch"] = p.low.cumsum(), p.high.cumsum()
    final = p.cumulative.iloc[-1]
    title = f"A conditional path reaches {money(final)} (range {money(p.cl.iloc[-1])} to {money(p.ch.iloc[-1])}) against GMI's $50M target"
    sub = "Savings added step by step: GMI's reported rates first, then assumed savings from statewide contracts. Conditional on reported savings recurring and on the stated assumptions."
    d = {"step": p.step.tolist(), "action": p.action.tolist(), "basis": p.basis.tolist(), "cum": (p.cumulative / 1e6).round(2).tolist(),
         "lo": (p.cl / 1e6).round(2).tolist(), "hi": (p.ch / 1e6).round(2).tolist(), "s": (p.saving / 1e6).round(2).tolist()}
    js = """
var band=[{type:'scatter',mode:'lines',x:D.step,y:D.hi,line:{width:0},hoverinfo:'skip',showlegend:false},
 {type:'scatter',mode:'lines',name:'Assumed range',x:D.step,y:D.lo,fill:'tonexty',fillcolor:'rgba(6,182,212,0.18)',line:{width:0},hoverinfo:'skip'}];
var line={type:'scatter',mode:'lines+markers',name:'Likely, cumulative',x:D.step,y:D.cum,line:{color:GOLD,width:3},marker:{size:6,color:GOLD},
 customdata:D.step.map(function(s,i){return [D.action[i],D.basis[i],D.s[i],D.lo[i],D.hi[i]];}),
 hovertemplate:'<b>Step %{x}: %{customdata[0]}</b><br>%{customdata[1]}<br>Adds $%{customdata[2]}M; total $%{y}M (range $%{customdata[3]}M to $%{customdata[4]}M)<extra></extra>'};
var layout=merge(base,{xaxis:{title:{text:'Step'},dtick:2}, yaxis:{title:{text:'Cumulative annual savings, $ millions'},tickprefix:'$',ticksuffix:'M',rangemode:'tozero'},
 shapes:[{type:'line',xref:'paper',x0:0,x1:1,y0:50,y1:50,line:{color:RED,width:2,dash:'dash'}}],
 annotations:[{xref:'paper',x:0.01,y:50,yshift:12,xanchor:'left',showarrow:false,text:'GMI target: $50M',font:{color:RED,size:12}}], legend:{y:-0.18}});
Plotly.newPlot('chart',band.concat([line]),layout,config);
"""
    write("calc", title, sub, js, d)


def fcast():
    r = read("f_revenue")
    act = r[r.kind == "Actual"]
    fc = r[r.kind == "Forecast"].iloc[0]
    title = f"FY{int(fc.fiscal_year)} General Fund revenue midpoint {money(fc.p50)}, indicative range {money(fc.p10)} to {money(fc.p90)}"
    sub = "General Fund revenue, budgetary basis, as reported (one-time items included). The range is indicative, from a log-linear trend; the wider dotted band is the calibrated range."
    d = {"fy": act.fiscal_year.tolist(), "v": (act.value / 1e9).round(3).tolist(), "fy2": int(fc.fiscal_year), "p10": round(fc.p10 / 1e9, 2), "p50": round(fc.p50 / 1e9, 2), "p90": round(fc.p90 / 1e9, 2),
         "c10": round(fc.p10_cal / 1e9, 2), "c90": round(fc.p90_cal / 1e9, 2), "last": float(act.value.iloc[-1] / 1e9), "lfy": int(act.fiscal_year.iloc[-1])}
    js = """
var a={type:'scatter',mode:'lines+markers',name:'Actual',x:D.fy,y:D.v,line:{color:GOLD,width:3},marker:{size:7,color:GOLD},hovertemplate:'<b>FY%{x}</b><br>$%{y:.1f}B actual<extra></extra>'};
var xs=[D.lfy,D.fy2];
var wide={type:'scatter',mode:'lines',name:'Calibrated range',x:[D.lfy,D.fy2,D.fy2,D.lfy],y:[D.last,D.c90,D.c10,D.last],fill:'toself',fillcolor:'rgba(100,116,139,0.12)',line:{color:'#64748b',width:1,dash:'dot'},hoverinfo:'skip'};
var rng={type:'scatter',mode:'lines',name:'Indicative range',x:[D.lfy,D.fy2,D.fy2,D.lfy],y:[D.last,D.p90,D.p10,D.last],fill:'toself',fillcolor:'rgba(6,182,212,0.22)',line:{width:0},hoverinfo:'skip'};
var mid={type:'scatter',mode:'lines+markers',name:'Forecast midpoint',x:xs,y:[D.last,D.p50],line:{color:CYAN,width:3,dash:'dash'},marker:{size:[0,10],color:CYAN},
 hovertemplate:'<b>FY%{x}</b><br>$%{y:.1f}B midpoint ($'+D.p10+'B to $'+D.p90+'B)<extra></extra>'};
var layout=merge(base,{xaxis:{dtick:1,tickprefix:'FY',tickangle:-45},yaxis:{title:{text:'$ billions'},tickprefix:'$',ticksuffix:'B',rangemode:'tozero'},legend:{y:-0.2}});
Plotly.newPlot('chart',[wide,rng,a,mid],layout,config);
"""
    write("fcast", title, sub, js, d)


def vend():
    m = read("d_multi")
    y = int(m.fiscal_year.max())
    v = m[m.fiscal_year == y].sort_values("spend", ascending=False)
    top = v.head(20).iloc[::-1]
    title = f"{len(v)} vendors were each paid by {int(v.agencies.min())}+ agencies buying separately: {money(v.spend.sum())} in FY{y}"
    sub = f"The 20 largest of {len(v)} by spend. Each is a candidate for one statewide contract. Hover for agencies and the number of names the vendor is paid under."
    d = {"v": top.vendor.str.title().tolist(), "m": (top.spend / 1e6).round(2).tolist(), "ag": top.agencies.tolist(), "pn": top.payee_names.tolist(), "area": top.area.tolist()}
    js = """
var areas=Array.from(new Set(D.area)); var traces=areas.map(function(a,k){var ix=D.area.map(function(x,i){return x===a?i:-1;}).filter(function(i){return i>=0;});
 return {type:'bar',orientation:'h',name:a,y:ix.map(function(i){return D.v[i];}),x:ix.map(function(i){return D.m[i];}),marker:{color:PALETTE[k%PALETTE.length]},
 customdata:ix.map(function(i){return [D.ag[i],D.pn[i]];}),hovertemplate:'<b>%{y}</b><br>$%{x}M in FY'+""" + str(y) + """+'<br>Paid by %{customdata[0]} agencies under %{customdata[1]} name(s)<extra>'+a+'</extra>'};});
var layout=merge(base,{barmode:'stack',xaxis:{title:{text:'$ millions'},tickprefix:'$',ticksuffix:'M'},yaxis:{automargin:true,dtick:1,tickfont:{size:10,color:'#cbd5e1'}},margin:{l:220,t:84,b:96},legend:{y:-0.2}});
Plotly.newPlot('chart',traces,layout,config);
"""
    write("vend", title, sub, js, d)


def agency():
    f = read("f_agency")
    fa = f[(f.stage == "Actual") & f.fte.notna() & (f.fte > 0)]
    g = fa.groupby("agency")[["controllable", "fte"]].sum()
    g = g[g.controllable >= 100e6]
    g["per"] = g.controllable / g.fte
    top = g.sort_values("per", ascending=False).head(12).iloc[::-1]
    y0, y1 = int(fa.fiscal_year.min()), int(fa.fiscal_year.max())
    best = top.iloc[-1]
    title = f"{top.index[-1]} has the highest controllable purchases per position: {best.per / 1e3:,.1f}K a year"
    title = title.replace(": ", ": $", 1)
    sub = f"Agencies with at least $100M of controllable purchases, FY{y0}-FY{y1} actuals, per budgeted position per year. Some agencies mostly pass money through, so a high figure is a place to ask, not a finding."
    d = {"a": top.index.tolist(), "k": (top.per / 1e3).round(1).tolist(), "c": (top.controllable / 1e6).round(1).tolist(), "f": top.fte.round(0).tolist()}
    js = """
var tr={type:'bar',orientation:'h',y:D.a,x:D.k,marker:{color:D.a.map(function(_,i){return i===D.a.length-1?GOLD:CYAN;})},
 customdata:D.a.map(function(_,i){return [D.c[i],D.f[i]];}),hovertemplate:'<b>%{y}</b><br>$%{x}K per position a year<br>$%{customdata[0]}M controllable over the period, %{customdata[1]:,} position-years<extra></extra>'};
var layout=merge(base,{xaxis:{title:{text:'Controllable purchases per position, $ thousands a year'},tickprefix:'$',ticksuffix:'K'},yaxis:{automargin:true,tickfont:{size:11,color:'#cbd5e1'}},margin:{l:260},showlegend:false});
Plotly.newPlot('chart',[tr],layout,config);
"""
    write("agency", title, sub, js, d)


def budget():
    f = read("f_function")
    x = f[f.stage == "Actual"].pivot_table(index="fiscal_year", columns="category_title", values="budget", aggfunc="sum").fillna(0)
    tot = x.sum(axis=1)
    order = x.loc[x.index.max()].sort_values(ascending=False).index.tolist()
    top = order[:6]
    other = [c for c in order if c not in top]
    series = {c: (x[c] / 1e9).round(3).tolist() for c in top}
    if other:
        series["All other functions"] = (x[other].sum(axis=1) / 1e9).round(3).tolist()
    y0, y1 = int(x.index.min()), int(x.index.max())
    lead = order[0]
    title = f"Actual spending rose from {money(tot[y0])} in FY{y0} to {money(tot[y1])} in FY{y1}; {lead} is {x.loc[y1, lead] / tot[y1]:.0%} of FY{y1}"
    sub = "Operating budget actuals by government function, all funds. Click a legend entry to hide or show a function."
    d = {"fy": x.index.tolist(), "s": series}
    js = """
var names=Object.keys(D.s);
var tr=names.map(function(n,i){return {type:'scatter',mode:'lines',stackgroup:'one',name:n,x:D.fy,y:D.s[n],line:{width:0.5,color:'#0a0e1a'},fillcolor:PALETTE[i%PALETTE.length],
 hovertemplate:'<b>'+n+'</b><br>FY%{x}: $%{y:.1f}B<extra></extra>'};});
var layout=merge(base,{xaxis:{dtick:1,tickprefix:'FY',tickangle:-45},yaxis:{title:{text:'$ billions'},tickprefix:'$',ticksuffix:'B'},legend:{y:-0.22}});
Plotly.newPlot('chart',tr,layout,config);
"""
    write("budget", title, sub, js, d)


def data():
    s = read("sources").copy().sort_values("rows_downloaded")
    total = int(s.rows_downloaded.sum())
    ok = int(s.reconciled.sum())
    title = f"{total:,} rows downloaded; {ok} of {len(s)} datasets match the portal on count and yearly totals"
    sub = "Rows per State dataset, downloaded in full through the SODA API and checked against the portal on every run (log scale). Nothing is built from a dataset that does not match."
    d = {"name": s.source.tolist(), "id": s.dataset_id.tolist(), "dl": s.rows_downloaded.tolist(), "pt": s.rows_portal.tolist(), "ok": s.reconciled.tolist(), "yrs": s.years.tolist(), "upd": s.portal_updated.astype(str).tolist()}
    js = """
var tr={type:'bar',orientation:'h',y:D.name,x:D.dl,text:D.dl.map(function(v){return v.toLocaleString();}),textposition:'outside',textfont:{color:'#f0f0f0'},cliponaxis:false,
 marker:{color:D.ok.map(function(v){return v?GOLD:RED;})},customdata:D.name.map(function(_,i){return [D.id[i],D.pt[i],D.yrs[i],D.upd[i]];}),
 hovertemplate:'<b>%{y}</b> (%{customdata[0]})<br>%{x:,} rows downloaded; portal: %{customdata[1]:,}<br>Years: %{customdata[2]}<br>Portal updated %{customdata[3]}<extra></extra>'};
var layout=merge(base,{xaxis:{type:'log',title:{text:'Rows (log scale)'},range:[3,6.6],tickvals:[1000,10000,100000,1000000],ticktext:['1K','10K','100K','1M']},yaxis:{automargin:true,tickfont:{size:12,color:'#cbd5e1'}},margin:{l:110,r:80},showlegend:false});
Plotly.newPlot('chart',[tr],layout,config);
"""
    write("data", title, sub, js, d)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for fn in (over, areas, track, opp, calc, fcast, vend, agency, budget, data):
        fn()
