// Exercise the ACTUAL shared particle builder and its appearance-isolated cache.
const fs=require('node:fs'),assert=require('node:assert/strict'),ts=require('typescript'),THREE=require('three');
const source=fs.readFileSync('components/ApexMaleHumanoid.tsx','utf8');
const code=source.slice(source.indexOf('const PORTRAIT_URL'),source.indexOf('const VERTEX_SHADER'));
const js=ts.transpileModule(code,{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText;
const mod={exports:{}};
new Function('THREE','module','exports',js+';module.exports={buildHumanoidParticles};')(THREE,mod,mod.exports);
function asset(rgb){
 const width=48,height=30,portrait=new Uint8ClampedArray(width*height*4),depth=new Uint8ClampedArray(width*height*4);
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
  const i=(y*width+x)*4;
  portrait.set([...rgb,255],i);
  depth.set([Math.round(170+65*Math.exp(-(((x-width/2)/9)**2))),y<height*.66?255:0,y<height*.66?178:102,255],i);
 }return {width,height,portrait,depth};
}
const build=mod.exports.buildHumanoidParticles;
const male=build(asset([30,180,220]),'low','male');
const female=build(asset([230,100,170]),'low','female');
assert.notEqual(male,female,'Male/female must never share cached geometry/color data');
assert.equal(build(asset([1,2,3]),'low','female'),female,'Repeated female builds reuse their own cache');
for(const d of [male,female]){
 assert(d.count>1000);
 for(const k of ['positions','colors','normals','traits','assemblySource','meta','rig'])assert(d[k].every(Number.isFinite),k);
 assert.equal(d.positions.length,d.count*3);
 assert.equal(d.rig.length,d.count*2);
}
assert.notDeepEqual(male.colors,female.colors,'Female source colors must survive geometry caching');
console.log(`Shared renderer geometry/cache regression passed: ${male.count} male / ${female.count} female particles.`);
