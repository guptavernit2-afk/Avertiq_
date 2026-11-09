/* Exercise the report's own filtering script against a minimal DOM.
 * This is a JavaScript smoke check, not a browser layout or accessibility audit.
 * Usage: node tools/check_report.cjs path/to/report.html
 */
"use strict";
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const filename = process.argv[2];
if (!filename) throw new Error("Pass a generated report.html path");
const html = fs.readFileSync(filename, "utf8");
const embedded = html.match(/<script id="study-data" type="application\/json">([\s\S]*?)<\/script>/);
assert.ok(embedded, "embedded study JSON");
const study = JSON.parse(embedded[1]);
const rows = [...html.matchAll(/<tr data-index="(\d+)">/g)].map(m => ({dataset:{index:m[1]},hidden:false}));
const panels = [...html.matchAll(/<section class="scenario" data-index="(\d+)">/g)].map(m => ({dataset:{index:m[1]},hidden:false}));
assert.equal(rows.length, study.paths.reduce((n,p)=>n+p.points.length,0));
assert.equal(panels.length,study.paths.length);
const chooser = {value:"all", options:Array(study.paths.length+1), addEventListener(name, callback){
  assert.equal(name,"change"); this.onchange=callback;
}};
const caption = {textContent:""};
const document = {
  getElementById(id){if(id==="scenario")return chooser;if(id==="table-caption")return caption;throw new Error(id);},
  querySelectorAll(selector){
    if(selector==="[data-index]") return [...panels,...rows];
    if(selector==="tbody tr:not([hidden])") return rows.filter(row=>!row.hidden);
    throw new Error(selector);
  }
};
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,1);
vm.runInNewContext(scripts[0][1],{document},{timeout:1000});
for(let i=0;i<study.paths.length;i++){
  chooser.value=String(i);chooser.onchange();
  assert.equal(rows.filter(r=>!r.hidden).length,study.paths[i].points.length);
  assert.equal(panels.filter(p=>!p.hidden).length,1);
  assert.equal(panels.find(p=>!p.hidden).dataset.index,String(i));
}
chooser.value="all";chooser.onchange();
assert.ok(rows.every(r=>!r.hidden)&&panels.every(p=>!p.hidden));
assert.ok(caption.textContent.startsWith(String(rows.length)));
console.log("PASS: report script filters all "+study.paths.length+" scenarios and restores all "+rows.length+" states.");
