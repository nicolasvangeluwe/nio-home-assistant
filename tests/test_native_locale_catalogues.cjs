const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const test=require('node:test');
const root=path.join(__dirname,'../custom_components/nio_telematics');
const locales=['en','nl','de','fr','nb','sv','da','cs','el','hu','lb','pl','pt','ro'];
const read=locale=>JSON.parse(fs.readFileSync(path.join(root,'translations',locale+'.json'),'utf8'));
const base=JSON.parse(fs.readFileSync(path.join(root,'strings.json'),'utf8'));
const flatten=(obj,prefix='',out={})=>{for(const [key,value]of Object.entries(obj)){const full=prefix?prefix+'.'+key:key;if(value&&typeof value==='object')flatten(value,full,out);else out[full]=value;}return out;};
const leaves=flatten(base);
const slots=text=>(text.match(/\{[^{}]+\}/g)||[]).sort();

test('the English HA catalogue is exactly the native source catalogue',()=>assert.deepEqual(read('en'),base));

test('all native locale messages are complete with valid variables, links and encoding',()=>{
 for(const locale of locales){
  const translated=flatten(read(locale));
  assert.deepEqual(Object.keys(translated).sort(),Object.keys(leaves).sort(),locale+' keys');
  for(const [key,value]of Object.entries(translated)){
   assert.equal(typeof value,'string',locale+' '+key);
   assert.ok(value.trim(),locale+' '+key+' must not be empty');
   assert.deepEqual(slots(value),slots(leaves[key]),locale+' '+key+' variables');
   assert.doesNotMatch(value,/\]\s+\(/,locale+' '+key+' broken Markdown link');
   assert.doesNotMatch(value,/\uFFFD|Ã©|Ã¤|â€™|Â\u00a0/,locale+' '+key+' encoding');
  }
 }
});

test('native model and language pickers have readable labels without changing saved identifiers',()=>{
 const models=['auto','ET5','ET5 Touring','ET7','EL6','EL7','EL8','ES8','other'];
 for(const locale of locales){
  const catalogue=read(locale);
  assert.deepEqual(Object.keys(catalogue.selector.model.options).sort(),models.sort(),locale+' model ids');
  assert.deepEqual(Object.keys(catalogue.selector.language.options).sort(),['auto',...locales].sort(),locale+' language ids');
  assert.equal(catalogue.selector.language.options.auto,catalogue.selector.paint.options.auto,locale+' automatic');
  for(const model of models.filter(id=>!['auto','other'].includes(id)))assert.equal(catalogue.selector.model.options[model],model);
  for(const code of locales)assert.notEqual(catalogue.selector.language.options[code],code,locale+' readable '+code);
 }
});

test('product names retain their identity in every native message, not only sample labels',()=>{
 const failures=[];
 for(const locale of locales){
  const translated=flatten(read(locale));
  for(const [key,source]of Object.entries(leaves)){
   for(const brand of ['Direct NIO','Companion','Home Assistant','EVCC']){
    const pattern=brand==='Home Assistant'?/Home[ -]Assistant/:new RegExp(brand);
    if(source.includes(brand)&&!pattern.test(translated[key]))failures.push(locale+' '+key+' must retain '+brand);
   }
  }
 }
 assert.deepEqual(failures,[]);
});

test('reviewed native technical terms preserve product identity and charging semantics',()=>{
 const de=JSON.stringify(read('de')),fr=JSON.stringify(read('fr')),nl=JSON.stringify(read('nl'));
 assert.doesNotMatch(de,/Begleitkonto|Connect Companion|Beweistoken|Gebührenbegrenzungseinheit|lokale Kunstwerke|Verbleibender Bereich/);
 assert.doesNotMatch(fr,/Compte compagnon|Connecter le compagnon|Titre d.assistant|commutateur est tombé|état de facturation|œuvres d.art locales|Entité de plage|Portée restante/);
 assert.doesNotMatch(nl,/oplopende valuta|entiteit voor aangesloten en/);
});
