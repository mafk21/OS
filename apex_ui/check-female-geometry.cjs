// Fast numerical regression for the original sculpture; no browser/GPU required.
const fs=require('node:fs'),assert=require('node:assert/strict'),ts=require('typescript'),THREE=require('three');
const source=fs.readFileSync('components/ApexFemaleHumanoid.tsx','utf8');
const code=source.slice(source.indexOf('const gaussian'),source.indexOf('const vertex'));
const js=ts.transpileModule(code,{compilerOptions:{target:ts.ScriptTarget.ES2020}}).outputText;
const out={exports:{}};new Function('THREE','module',js+';module.exports={sculpture,faceVolume};')(THREE,out);
const a=out.exports.sculpture(),b=out.exports.sculpture();
assert(a.position.length>90000&&a.position.length<180000);
assert.equal(a.position.length,a.color.length);assert.equal(a.region.length*3,a.position.length);
for(const values of Object.values(a))assert(values.every(Number.isFinite));
assert.deepEqual(a.position,b.position,'Stable seed avoids remount flicker');
assert(new Set(a.region).has(4));assert(new Set(a.region).has(5));
const g=out.exports.faceVolume();
for(const name of ['position','normal'])assert(g.getAttribute(name).array.every(Number.isFinite));
g.computeBoundingBox();assert(g.boundingBox.max.z>.70,'Nose projects into real depth');
g.dispose();console.log(`Female sculpture: ${a.region.length} finite, deterministic 3D particles; surface normals and depth valid.`);
