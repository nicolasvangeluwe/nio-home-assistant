const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),test=require('node:test');
const component=path.join(__dirname,'../custom_components/nio_telematics');
const root={querySelector(){return null;},querySelectorAll(){return [];},addEventListener(){}};
const context={URL,console,Intl,Date,CustomEvent:class{constructor(type,init){this.type=type;Object.assign(this,init);}},HTMLElement:class{constructor(){this.attributes={};}setAttribute(k,v){this.attributes[k]=v;}addEventListener(){}attachShadow(){this.shadowRoot=root;}dispatchEvent(event){this.event=event;}},window:{customCards:[]},document:{hidden:false,addEventListener(){},removeEventListener(){}},customElements:{get(){},define(){}}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(component,'car_dashboard/car-ledger-card.js'),'utf8').replaceAll('import.meta.url',JSON.stringify('https://ha.test/car-dashboard.js?nio_owned=1')).replace('export { CarLedgerCard };','')+'\nglobalThis.__Base=CarLedgerCard;',context);
let source=fs.readFileSync(path.join(component,'nio-dashboard-history.js'),'utf8').replaceAll('\r\n','\n');
source=source.replace(/const baseVersion=.*?\nconst \{CarLedgerCard\}=await import\([^\n]+\);/,'').replace('export function periodLabel','function periodLabel').replace('export class NioDashboardHistory','class NioDashboardHistory');
vm.runInContext(source+'\nglobalThis.__History=NioDashboardHistory;globalThis.__label=periodLabel;globalThis.__uiRows=UI_ROWS;globalThis.__emptyPeriod=EMPTY_PERIOD;globalThis.__emptyFilters=EMPTY_FILTERS;',context);
const History=context.__History;
function instance(){const h=new History();h.config={entry_id:'one',language:'en'};h.render=()=>{};h.refreshState=()=>{};return h;}
function renderRoot(){
  const root={children:[],_html:'',currencyWarning:null,addEventListener(){},append(node){this.children.push(node);},set innerHTML(value){this._html=value;this.currencyWarning=null;},get innerHTML(){return this._html;},querySelector(selector){return ({'.top':top,'.refresh':refresh,'.insight':insight,'.heading':heading,'ha-card':card})[selector]||null;},querySelectorAll(selector){return selector==='.month p'?[summary]:[];}};
  const node=(tag='div')=>({tagName:tag,children:[],style:{setProperty(){}},classList:{contains:()=>false,toggle(){}},setAttribute(name,value){this[name]=value;},addEventListener(){},append(...items){this.children.push(...items);},before(){},after(item){root.currencyWarning=item;},querySelector(selector){return selector==='.date-tools'?dateTools:null;},replaceWith(item){this.replacedWith=item;}});
  const top=node(),refresh=node('button'),insight=node(),heading=node(),card=node('ha-card'),dateTools=node(),summary=node('p');summary.textContent='1.00 kWh · 30%';
  return {root,document:{hidden:false,addEventListener(){},removeEventListener(){},createElement:node},summary};
}
test('history categories and calendar scopes remain visible while loading or failed',()=>{const h=instance();for(const error of ['', 'History is temporarily unavailable']){h.error=error;History.prototype.render.call(h);assert.equal((root.innerHTML.match(/data-tab=/g)||[]).length,4);assert.equal((root.innerHTML.match(/data-scope=/g)||[]).length,4);for(const label of ['Charging','Trips','Energy','Parked','Day','Week','Month','Year'])assert.ok(root.innerHTML.includes('>'+label+'</button>'),label);}});
function snapshot(){return {selected_period:{scope:'day',date:'2026-11-23',start_date:'2026-11-23',end_date:'2026-11-24',start:100,end:200,effective_end:180},statistics:{selected:{distance_km:10},month:{projected_range_km:172}},charges:[{id:'previous',end:99},{id:'first',end:100},{id:'now',end:180},{id:'future',end:181},{id:'next',end:200}],trips:[],parked_periods:[],charging_daily:[]};}
test('calendar filters use half-open HA window and preserve the complete current snapshot',()=>{const h=instance();h.fullSnapshot=snapshot();const before=JSON.stringify(h.fullSnapshot);h.applyView();assert.deepEqual(Array.from(h.snapshot.charges,x=>x.id),['first','now']);assert.equal(JSON.stringify(h.fullSnapshot),before);assert.equal(h.fullSnapshot.statistics.month.projected_range_km,172);assert.equal(h.snapshot.statistics.month.distance_km,10);});
test('parked losses are calendar-filtered before canonical grouping and actual Parked rendering',async()=>{
  const h=instance(),tz='Europe/Brussels',toSec=value=>Date.parse(value)/1000;
  h._hass={config:{time_zone:tz}};h.filters={location:'all',price:false,basis:'all'};h.full=true;h.pageSize=36;
  const first={id:'loss-one',fingerprint:'fp-one',start:toSec('2026-11-22T22:50:00Z'),end:toSec('2026-11-22T22:55:00Z'),kwh:.45,state:'open'},second={id:'loss-two',fingerprint:'fp-two',start:toSec('2026-11-22T22:55:00Z'),end:toSec('2026-11-22T23:05:00Z'),kwh:.45,state:'open'};
  const originalGroup={id:`parked-${first.start.toFixed(6)}`,start:first.start,end:second.end,kwh:.9,soc_used_pct:1,intervals:[first,second]};
  const makeSnapshot=(start,end)=>({selected_period:{start,end,effective_end:end},statistics:{selected:{distance_km:0},day:{},month:{},year:{}},settings:{capacity_kwh:90},parked_periods:[structuredClone(originalGroup)],parked_intervals:[structuredClone(first),structuredClone(second)],charges:[],trips:[],unaccounted_intervals:[],measurement_errors:[],charging_daily:[]});
  // The two losses end on opposite Brussels calendar dates despite sharing
  // one canonical same-month backend group.
  h.fullSnapshot=makeSnapshot(toSec('2026-11-21T23:00:00Z'),toSec('2026-11-22T23:00:00Z'));h.applyView();
  assert.equal(h.snapshot.parked_periods.length,1);assert.equal(h.snapshot.parked_periods[0].kwh,.45);assert.deepEqual(Array.from(h.snapshot.parked_periods[0].intervals,row=>row.id),['loss-one']);
  assert.equal(h.snapshot.parked_periods[0].id,originalGroup.id);assert.equal(h.snapshot.parked_intervals[0].id,'loss-one');
  const firstDay=h.parkedHistory();assert.match(firstDay,/0\.45 kWh/);assert.match(firstDay,/data-parked="parked-[^"]+"/);
  h.fullSnapshot=makeSnapshot(toSec('2026-11-22T23:00:00Z'),toSec('2026-11-23T23:00:00Z'));h.applyView();
  assert.equal(h.snapshot.parked_periods.length,1);assert.equal(h.snapshot.parked_periods[0].kwh,.45);assert.deepEqual(Array.from(h.snapshot.parked_periods[0].intervals,row=>row.id),['loss-two']);
  h.dialog=(...args)=>{h.lastDialog=args;return {querySelector:()=>null};};await h.click(clickButton({dataset:{parked:h.snapshot.parked_periods[0].id}}));assert.match(h.lastDialog[1],/data-measurement-preview="loss-two" data-measurement-fingerprint="fp-two"/);assert.doesNotMatch(h.lastDialog[1],/data-measurement-preview="loss-one"/);
  // A wider month view restores both raw readings to the same .90 kWh group.
  h.fullSnapshot=makeSnapshot(toSec('2026-10-31T23:00:00Z'),toSec('2026-11-30T23:00:00Z'));h.applyView();
  assert.equal(h.snapshot.parked_periods.length,1);assert.equal(h.snapshot.parked_periods[0].kwh,.9);assert.deepEqual(Array.from(h.snapshot.parked_periods[0].intervals,row=>row.id),['loss-one','loss-two']);
  assert.equal(h.parkedHistory().match(/0\.90 kWh/g)?.length,1);
  h.fullSnapshot=makeSnapshot(toSec('2026-11-15T23:00:00Z'),toSec('2026-11-22T23:00:00Z'));h.applyView();assert.equal(h.snapshot.parked_periods[0].kwh,.45);
  h.fullSnapshot=makeSnapshot(toSec('2026-11-22T23:00:00Z'),toSec('2026-11-29T23:00:00Z'));h.applyView();assert.equal(h.snapshot.parked_periods[0].kwh,.45);
  h.fullSnapshot=makeSnapshot(toSec('2025-12-31T23:00:00Z'),toSec('2026-12-31T23:00:00Z'));h.applyView();assert.equal(h.snapshot.parked_periods[0].kwh,.9);
  // Both epochs of the Brussels autumn clock change remain one local-month
  // group when raw intervals touch across the repeated hour.
  const dst=[{id:'dst-one',start:toSec('2026-10-25T00:20:00Z'),end:toSec('2026-10-25T00:30:00Z'),kwh:.45},{id:'dst-two',start:toSec('2026-10-25T00:30:00Z'),end:toSec('2026-10-25T00:40:00Z'),kwh:.45}];
  h.fullSnapshot=makeSnapshot(toSec('2026-10-24T22:00:00Z'),toSec('2026-10-25T23:00:00Z'));h.fullSnapshot.parked_intervals=structuredClone(dst);h.fullSnapshot.parked_periods=[{id:`parked-${dst[0].start.toFixed(6)}`,start:dst[0].start,end:dst[1].end,kwh:.9,intervals:structuredClone(dst)}];h.applyView();assert.equal(h.snapshot.parked_periods[0].kwh,.9);assert.deepEqual(Array.from(h.snapshot.parked_periods[0].intervals,row=>row.id),['dst-one','dst-two']);
});
test('calendar shift uses local dates without month overflow',()=>{const h=instance();h.scope='month';h._calendar={start_date:'2026-01-01'};h.shift(1);assert.equal(h.anchor,'2026-02-01');h.scope='week';h._calendar.start_date='2025-12-29';h.shift(1);assert.equal(h.anchor,'2026-01-05');});
test('period labels are localized calendar dates',()=>{const p=snapshot().selected_period;assert.match(context.__label(p,'en-GB'),/23 November 2026/);assert.match(context.__label({...p,scope:'month'},'nl-BE'),/november 2026/);});
test('older request cannot overwrite a newer period or broadcast stale range',async()=>{const h=instance(),pending=[];h.prepareSnapshot=x=>x;h._hass={callWS:query=>new Promise(resolve=>pending.push({resolve,query}))};h.scope='day';const first=h.refresh();h.scope='week';const second=h.refresh();const fresh=snapshot();fresh.selected_period.scope='week';pending[1].resolve(fresh);await second;pending[0].resolve({...snapshot(),marker:'old'});await first;assert.equal(h.fullSnapshot.marker,undefined);assert.equal(h.event.detail.snapshot.selected_period.scope,'week');assert.equal(pending[1].query.period,'week');});
test('switching vehicle invalidates prior responses and filters',async()=>{const h=instance();let resolve;h.prepareSnapshot=x=>x;h._hass={callWS:()=>new Promise(r=>resolve=r)};const request=h.refresh();h.setConfig({entry_id:'two',language:'en'});resolve(snapshot());await request;assert.equal(h.fullSnapshot,null);assert.equal(h.config.entry_id,'two');});
test('all supported locales provide complete calendar controls',()=>{for(const language of ['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro']){const h=instance();h.config.language=language;assert.equal(Object.values(h.ui).filter(Boolean).length,23,language);}});
test('history navigation and ledger headings use the same charging and trip names',()=>{for(const language of ['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro']){const h=instance();h.config.language=language;assert.equal(h.ui.charging,h.translate('Laden'),language+' charging label');assert.equal(h.ui.trips,h.translate('Ritten'),language+' trips label');}});
test('history host owns localization and opts out of the household DOM translator',()=>{const h=instance();h.connectedCallback();assert.equal(h.attributes['data-i18n-ignore'],'');assert.equal(h.attributes.translate,'no');assert.equal(h.attributes.lang,'en');});
test('every history locale has a full row and empty-state dictionary',()=>{const locales=['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro'];for(const locale of locales){assert.equal(context.__uiRows[locale].length,23,locale+' control rows');assert.equal(typeof context.__emptyPeriod[locale],'string',locale+' period empty state');assert.equal(typeof context.__emptyFilters[locale],'string',locale+' filtered empty state');assert.ok(context.__emptyPeriod[locale]);assert.ok(context.__emptyFilters[locale]);}});
test('parked consumption translates a complete dynamic metric without replacing inside words',()=>{const h=instance();assert.equal(h.translate('Verbruikt'),'Consumption');assert.equal(h.translate('Verbruikt 0.45 kWh'),'Consumption 0.45 kWh');assert.equal(h.translate('Verbruiktin'), 'Verbruiktin');assert.equal(h.translate('Home'), 'Home');h.config.language='fr';assert.equal(h.translate('Verbruikt 0,45 kWh'),'Consommation 0,45 kWh');h.config.language='nl';assert.equal(h.translate('Verbruikt'),'Verbruikt');});
test('visible record dates follow HA timezone',()=>{const h=instance();h._hass={config:{time_zone:'Europe/Brussels'}};const t=Date.parse('2026-11-22T23:30Z')/1000;assert.match(h.date(t,{day:'numeric',month:'long'}),/23/);});
test('English history uses 24-hour time and localized selected-period empty copy',()=>{const h=instance();h._hass={config:{time_zone:'Europe/Brussels'}};const t=Date.parse('2026-11-22T17:30Z')/1000;assert.match(h.date(t,{hour:'2-digit',minute:'2-digit'}),/18:30/);assert.doesNotMatch(h.date(t),/AM|PM/);assert.match(h.emptyPeriodLabel,/this period/);h.config.language='nl-BE';assert.equal(h.emptyPeriodLabel,'Geen registraties in deze periode.');});
test('a record excluded by a filter is not reported as a genuinely empty period',()=>{const h=instance();h.fullSnapshot=snapshot();h.fullSnapshot.charges=[{id:'home',category:'home',end:150}];h.filters.location='work';h.applyView();assert.equal(h.snapshot.charges.length,0);assert.match(h.emptyPeriodLabel,/match these filters/);assert.equal(h.fullSnapshot.charges.length,1);h.filters.location='all';h.applyView();assert.equal(h.snapshot.charges.length,1);assert.equal(h.emptyPeriodLabel,'No records in this period.');});

test('history currency warning is fully localized and renders outside every summary grid',()=>{
  const locales=['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro'];
  const source='Amina € <img src=x onerror=alert(1)> Home';
  let englishWarning='';for(const locale of locales){const h=instance();h.config.language=locale;const message=h.historyCurrencyWarning({code:'history_currency_assumed',source,currency:'DKK',previous_currencies:['EUR','SEK']});assert.ok(message.length>100,locale);assert.ok(message.includes(source),locale);assert.ok(message.includes('DKK')&&message.includes('EUR, SEK'),locale);assert.doesNotMatch(message,/\{(?:source|current|previous)\}/,locale);if(locale==='en')englishWarning=message;else assert.notEqual(message,englishWarning,locale);}
  const savedDocument=context.document,full=snapshot();full.currency='DKK';full.settings={capacity_kwh:90};full.preferences={};full.counters=[];full.parked_intervals=[];full.measurement_errors=[];full.unaccounted_intervals=[];full.charging_daily=[];full.history_currency_warning={code:'history_currency_assumed',source,currency:'DKK',previous_currencies:['EUR']};
  context.document=renderRoot().document;
  for(const tab of ['charging','trips','insight','parked']){
    const h=new History(),render=renderRoot();context.document=render.document;h.shadowRoot=render.root;h.config={entry_id:'embedded',language:'en'};h._hass={language:'en',config:{time_zone:'UTC'}};h.fullSnapshot=structuredClone(full);h.snapshot=structuredClone(full);h._calendar=full.selected_period;h.scope='day';h.anchor=full.selected_period.date;h.tab=tab;h.filters={location:'all',price:false,basis:'all'};h.localize=()=>{};h.refreshState=()=>{};h.history=()=>'<section class="history-content"></section>';h.insight=()=>'<section class="insight"></section>';h.parkedHistory=()=>'<section class="parked-history"></section>';h.render();
    const notice=render.root.currencyWarning;assert.ok(notice,tab);assert.equal(notice.className,'notice currency-notice');assert.equal(notice.translate,'no');assert.match(notice.textContent,/Amina € <img src=x onerror=alert\(1\)> Home/,tab);assert.equal(render.root.querySelectorAll('.month p').includes(notice),false,tab);
    h.fullSnapshot.history_currency_warning=null;h.render();assert.equal(render.root.currencyWarning,null,tab);
  }
  context.document=savedDocument;
});

function measurementHistory(){
  const h=instance(),save={textContent:'',disabled:false};h.tab='parked';h.full=true;h.snapshot={settings:{capacity_kwh:90},parked_periods:[],parked_intervals:[],measurement_errors:[]};h._hass={config:{time_zone:'UTC'}};h.dialog=(...args)=>{h.lastDialog=args;return {querySelector:()=>save};};h.shadowRoot={querySelector:()=>save};h.saveButton=save;return h;
}
const clickButton=button=>{button.hasAttribute||=()=>false;return {target:{closest:selector=>selector==='button'?button:null}};};
test('measurement-error copy covers all fourteen locales and a grouped-period click shows exact raw intervals',async()=>{
  const locales=['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro'],keys=['intervals','mark','review','reviewQueue','chargingBoundary','decrease','recorded','reviewSummary','confirmTitle','preview','kept','linked','exclude','decisions','excluded','stale','undo','restored'];
  const english={};for(const language of locales){const h=measurementHistory();h.config.language=language;for(const key of keys){const value=h.measurementErrorCopy(key);assert.ok(value.length>3,`${language} ${key}`);if(language==='en')english[key]=value;else assert.notEqual(value,english[key],`${language} ${key}`);}}
  const h=measurementHistory(),first={id:'loss-one',fingerprint:'raw-fingerprint-one',start:120,end:150,kwh:1.55,state:'open',paired_candidate_id:'charge-estimate',paired_candidate_kwh:3.6,paired_candidate_excluded:false},second={id:'loss-two',fingerprint:'raw-fingerprint-two',start:150,end:180,kwh:2,state:'open',paired_candidate_id:null,paired_candidate_kwh:null,paired_candidate_excluded:false};
  const period={id:'parked-group',start:120,end:180,kwh:3.55,soc_used_pct:3.94,intervals:[first,second]};h.snapshot.parked_periods=[period];h.snapshot.parked_intervals=[first,second];
  await h.click(clickButton({dataset:{parked:'parked-group'}}));
  assert.match(h.lastDialog[1],/data-measurement-preview="loss-one" data-measurement-fingerprint="raw-fingerprint-one"/);
  assert.match(h.lastDialog[1],/data-measurement-preview="loss-two" data-measurement-fingerprint="raw-fingerprint-two"/);
  await h.click(clickButton({dataset:{measurementPreview:'loss-one',measurementFingerprint:'raw-fingerprint-one'}}));
  assert.match(h.lastDialog[1],/1\.55 kWh/);assert.match(h.lastDialog[1],/3\.60 kWh/);assert.match(h.lastDialog[1],/original readings/i);assert.match(h.lastDialog[1],/battery-value allocation/i);
  assert.equal(h.lastDialog[0],'Review this interval');assert.equal(h.saveButton.textContent,'Exclude interval');
  let payload;h.update=async(action,values)=>{payload={action,values};return {saved:true,refreshed:true};};
  await h.lastDialog[2]();
  assert.equal(JSON.stringify(payload),JSON.stringify({action:'set_measurement_error',values:{ident:'loss-one',fingerprint:'raw-fingerprint-one',excluded:true}}));
  assert.equal(h._measurementFeedback,'Excluded from totals');
});

test('Parked summary, month total, group and detail use localized battery equivalents without changing kWh',()=>{
  const locales=['en','nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro'],savedDocument=context.document;
  for(const language of locales){
    const h=instance(),render=renderRoot(),period={id:'parked-label',start:100,end:160,kwh:210.6,soc_used_pct:234,intervals:[]};context.document=render.document;h.shadowRoot=render.root;h.tab='parked';h.config.language=language;h.snapshot={currency:'EUR',settings:{capacity_kwh:90},parked_periods:[period]};h.full=true;h.pageSize=36;
    const expectedEquivalent=h.n(2.34,2),summary=h.parkedSummary({parked_loss_estimate_kwh:210.6});assert.ok(summary.includes(`${h.measurementErrorCopy('equivalent')} ${expectedEquivalent}×`),`${language} parked summary`);assert.ok(summary.includes(`${h.n(210.6,2)} kWh`));
    render.summary.textContent=`${h.n(210.6,2)} kWh · ${expectedEquivalent}×`;h.summaryGrids();const summaryCells=render.summary.replacedWith.children;assert.equal(summaryCells[0].children[0].textContent,h.measurementErrorCopy('decrease'),`${language} period kWh label`);assert.equal(summaryCells[1].children[0].textContent,h.measurementErrorCopy('equivalent'),`${language} period equivalent label`);assert.equal(summaryCells[1].children[1].textContent,expectedEquivalent);
    const html=h.parkedHistory();assert.ok(html.includes(h.measurementErrorCopy('decrease')),`${language} card kWh label`);assert.ok(html.includes(h.measurementErrorCopy('equivalent')),`${language} card equivalent label`);assert.ok(html.includes(`${expectedEquivalent}×`),`${language} >100% equivalent`);assert.doesNotMatch(html,/234%/);
    h.dialog=(...args)=>{h.lastDialog=args;return null;};h.parkedDialog(period);assert.ok(h.lastDialog[1].includes(h.measurementErrorCopy('equivalent')),`${language} detail label`);assert.ok(h.lastDialog[1].includes(expectedEquivalent),`${language} detail equivalent`);assert.match(h.lastDialog[1],/×/);assert.ok(h.lastDialog[1].includes(h.n(210.6,2)));assert.match(h.lastDialog[1],/kWh/);
    assert.ok(h.parkedSummary({parked_loss_estimate_kwh:45}).includes(`${h.n(.5,2)}×`),`${language} fraction`);
    assert.equal(h.parkedEquivalentPrecision(.45),3,`${language} small fraction precision`);assert.ok(h.parkedSummary({parked_loss_estimate_kwh:.45}).includes(`${h.n(.005,3)}×`),`${language} small fraction`);
    assert.ok(h.measurementErrorCopy('equivalent').length>3,`${language} label copy`);
  }
  context.document=savedDocument;
});

test('historical zero-refill review reuses the fingerprinted preview and preserves raw plus paired evidence',async()=>{
  const h=measurementHistory(),start=Date.parse('2026-11-22T22:50:00Z')/1000,end=Date.parse('2026-11-22T22:55:00Z')/1000,candidateStart=Date.parse('2026-11-23T00:00:00Z')/1000,candidateEnd=Date.parse('2026-11-23T01:46:00Z')/1000;
  h._hass={config:{time_zone:'Europe/Brussels'}};h.snapshot.settings={capacity_kwh:90};
  const row={id:'loss-history',fingerprint:'loss-fingerprint',start,end,kwh:0,recorded_kwh:.45,state:'open',review_required:true,review_reason:'zero_refill_pair',evidence_basis:'archived_pair_only',paired_candidate_id:'charge-candidate',paired_candidate_start:candidateStart,paired_candidate_end:candidateEnd,paired_candidate_duration_seconds:6341,paired_candidate_kwh:.45,paired_candidate_excluded:false};
  h.snapshot.parked_periods=[];h.snapshot.parked_intervals=[row];
  h.dialog=(...args)=>{h.lastDialog=args;return {querySelector:()=>({textContent:'',disabled:false})};};
  const html=h.parkedHistory();assert.match(html,/Historical review/);assert.match(html,/0\.45 kWh/);assert.match(html,/Review archived pair/);assert.doesNotMatch(html,/original source readings are no longer available/i);assert.doesNotMatch(html,/data-parked="/);
  await h.click(clickButton({dataset:{measurementPreview:'loss-history',measurementFingerprint:'loss-fingerprint'}}));
  assert.equal(h.lastDialog[0],'Review this interval');assert.equal((h.lastDialog[1].match(/0\.45 kWh/g)||[]).length,2);assert.match(h.lastDialog[1],/Nov 23, 2026/);assert.match(h.lastDialog[1],/1 h 46 min/);assert.match(h.lastDialog[1],/both archived records stay unchanged/i);assert.match(h.lastDialog[1],/not proof of a measurement error/i);assert.doesNotMatch(h.lastDialog[1],/original source readings are no longer available/i);assert.doesNotMatch(h.lastDialog[1],/linked inferred charge/);
  let payload;h.update=async(action,values)=>{payload={action,values};return {saved:true,refreshed:true};};await h.lastDialog[2]();
  assert.deepEqual(JSON.parse(JSON.stringify(payload)),{action:'set_measurement_error',values:{ident:'loss-history',fingerprint:'loss-fingerprint',excluded:true}});
});

test('connection and charge boundary rows stay outside Parked totals and show read-only unaccounted evidence',()=>{
  const h=measurementHistory(),start=Date.parse('2026-11-22T22:50:00Z')/1000,end=Date.parse('2026-11-22T23:05:00Z')/1000;h._hass={config:{time_zone:'Europe/Brussels'}};h.full=true;h.pageSize=36;
  const row={id:'connection-boundary',fingerprint:'boundary-fingerprint',start,end,kwh:0,recorded_kwh:.45,state:'open',accounting_basis:'connection_boundary',evidence_basis:'source_samples'},excludedBoundary={id:'excluded-boundary',fingerprint:'excluded-boundary-fingerprint',start,end,kwh:0,recorded_kwh:9.9,state:'excluded',accounting_basis:'charging_boundary',evidence_basis:'source_samples'};
  h.fullSnapshot={...snapshot(),selected_period:{...snapshot().selected_period,start:start-100,end:end+100,effective_end:end+100},settings:{capacity_kwh:90},parked_periods:[],parked_intervals:[row,excludedBoundary],unaccounted_intervals:[],measurement_errors:[],charging_daily:[]};h.applyView();
  assert.equal(h.snapshot.parked_periods.length,0);assert.equal(h.snapshot.parked_intervals.length,2);
  const html=h.parkedHistory();assert.match(html,/Unaccounted usage/);assert.match(html,/0\.45 kWh/);assert.doesNotMatch(html,/9\.90 kWh/);assert.match(html,/This battery change crosses a connection or charging boundary\./);assert.doesNotMatch(html,/data-measurement-preview=/);assert.doesNotMatch(html,/data-parked="/);
});

test('connection boundary cannot bridge a parked group but remains in Unaccounted evidence',()=>{
  const h=measurementHistory(),boundary={id:'boundary-before',fingerprint:'boundary-fp',start:100,end:120,kwh:0,recorded_kwh:.45,state:'open',accounting_basis:'connection_boundary'},loss={id:'real-loss',fingerprint:'real-fp',start:120,end:150,kwh:.45,state:'open'};
  h._hass={config:{time_zone:'UTC'}};h.fullSnapshot={...snapshot(),settings:{capacity_kwh:90},parked_periods:[{id:'parked-120.000000',start:120,end:150,kwh:.45,soc_used_pct:.5,intervals:[loss]}],parked_intervals:[boundary,loss],measurement_errors:[],unaccounted_intervals:[],charging_daily:[]};h.applyView();
  assert.equal(h.snapshot.parked_periods.length,1);assert.equal(h.snapshot.parked_periods[0].start,120);assert.equal(h.snapshot.parked_periods[0].kwh,.45);assert.deepEqual(Array.from(h.snapshot.parked_periods[0].intervals,row=>row.id),['real-loss']);
  const html=h.parkedHistory();assert.match(html,/Unaccounted usage/);assert.match(html,/0\.45 kWh/);assert.match(html,/data-parked="parked-120\.000000"/);
});

test('Parked shows Undo for excluded and stale decisions even when all loss groups disappear',()=>{
  const h=measurementHistory();h.snapshot.parked_periods=[];h.snapshot.measurement_errors=[
    {id:'loss-excluded',fingerprint:'excluded-fingerprint',start:120,end:150,kwh:1.55,state:'excluded'},
    {id:'loss-stale',fingerprint:'current-stale-fingerprint',start:150,end:180,kwh:2,state:'stale'},
  ];
  const html=h.parkedHistory();assert.match(html,/measurement-decisions/);assert.match(html,/data-measurement-undo="loss-excluded" data-measurement-fingerprint="excluded-fingerprint"/);assert.match(html,/data-measurement-undo="loss-stale" data-measurement-fingerprint="current-stale-fingerprint"/);assert.match(html,/Source changed/);assert.equal(h.snapshot.parked_periods.length,0);
});

test('measurement-error Undo preserves current stale and saved orphan fingerprints and keeps retryable errors inline',async()=>{
  for(const [ident,fingerprint] of [['stale-present','current-stale-fingerprint'],['orphan','saved-fingerprint']]){
    const h=measurementHistory(),error={textContent:''},target={querySelector:()=>error};let payload;
    const button={dataset:{measurementUndo:ident,measurementFingerprint:fingerprint},disabled:false,hasAttribute:()=>false,closest:selector=>selector==='.measurement-decision'?target:null};
    h.update=async(action,values)=>{payload={action,values};return {saved:true,refreshed:true};};
    await h.click(clickButton(button));
    assert.equal(JSON.stringify(payload),JSON.stringify({action:'set_measurement_error',values:{ident,fingerprint,excluded:false}}));assert.equal(h._measurementFeedback,'Parked interval decision undone.');
  }
  const h=measurementHistory(),error={textContent:''},target={querySelector:()=>error},button={dataset:{measurementUndo:'stale',measurementFingerprint:'current'},disabled:false,hasAttribute:()=>false,closest:selector=>selector==='.measurement-decision'?target:null};h.update=async()=>{throw new Error('The parked interval changed; refresh before saving');};
  await h.click(clickButton(button));assert.equal(button.disabled,false);assert.ok(error.textContent.length>0);
});

test('measurement-error decisions follow the selected period without changing full identity records',()=>{
  const h=measurementHistory();h.fullSnapshot=snapshot();h.fullSnapshot.settings={capacity_kwh:90};h.fullSnapshot.parked_intervals=[{id:'raw-inside',fingerprint:'raw-in',start:110,end:150,kwh:1,state:'open'},{id:'raw-out',fingerprint:'raw-out',start:190,end:210,kwh:2,state:'open'}];h.fullSnapshot.measurement_errors=[{id:'inside',fingerprint:'fp-in',start:110,end:150,kwh:1,state:'excluded'},{id:'outside',fingerprint:'fp-out',start:190,end:210,kwh:2,state:'stale'}];h.fullSnapshot.parked_periods=[{id:'inside-period',end:150},{id:'outside-period',end:210}];const before=structuredClone(h.fullSnapshot);h.applyView();assert.deepEqual(Array.from(h.snapshot.measurement_errors,row=>row.id),['inside']);assert.deepEqual(Array.from(h.snapshot.parked_periods,row=>row.id),['parked-110.000000']);assert.deepEqual(Array.from(h.snapshot.parked_intervals,row=>row.id),['raw-inside']);assert.deepEqual(h.fullSnapshot,before);
});

test('saved exclusion is removed from selected GET grouping while raw audit stays visible and Undo restores the card',async()=>{
  const h=measurementHistory(),start=120,end=150,record={id:'loss-excluded',fingerprint:'excluded-fingerprint',start,end,kwh:73.8,state:'open'};let excluded=false;const mutations=[];
  const selectedSnapshot=()=>({selected_period:{scope:'day',date:'1970-01-01',start_date:'1970-01-01',end_date:'1970-01-02',start:100,end:200,effective_end:200},statistics:{selected:{distance_km:0}},settings:{capacity_kwh:90},currency:'EUR',charges:[],trips:[],parked_periods:excluded?[]:[{id:`parked-${start.toFixed(6)}`,start,end,kwh:73.8,soc_used_pct:82,intervals:[{...record,state:'open'}]}],parked_intervals:[{...record,state:excluded?'excluded':'open'},{id:'boundary-excluded',fingerprint:'boundary-fp',start,end,kwh:0,recorded_kwh:6.4,state:excluded?'excluded':'open',accounting_basis:'connection_boundary'}],measurement_errors:excluded?[{...record,state:'excluded'}]:[],unaccounted_intervals:[],charging_daily:[]});
  h._hass={config:{time_zone:'UTC'},async callWS(query){if(query.type.endsWith('/update')){mutations.push(query);excluded=query.values.excluded;return selectedSnapshot();}if(query.type.endsWith('/get')){mutations.push(query);return selectedSnapshot();}throw new Error(`Unexpected request ${query.type}`);}};
  h.scope='day';h.anchor='1970-01-01';h.prepareSnapshot=raw=>raw;h.full=true;h.pageSize=36;h.dialog=(...args)=>{h.lastDialog=args;return {querySelector:()=>({textContent:'',disabled:false})};};
  h.fullSnapshot=selectedSnapshot();h.applyView();const current=h.snapshot.parked_intervals[0];h.measurementErrorDialog(current);await h.lastDialog[2]();
  assert.deepEqual(mutations.map(query=>query.type),['nio_telematics/car_dashboard/update','nio_telematics/car_dashboard/get']);assert.equal(excluded,true);
  assert.equal(h.fullSnapshot.parked_intervals[0].kwh,73.8);assert.equal(h.fullSnapshot.parked_intervals[0].state,'excluded');assert.equal(h.snapshot.parked_periods.length,0);
  let html=h.parkedHistory();assert.match(html,/class="empty"/);assert.match(html,/data-measurement-undo="loss-excluded" data-measurement-fingerprint="excluded-fingerprint"/);assert.doesNotMatch(html,/data-parked="/);assert.doesNotMatch(html,/6\.40 kWh/);
  const error={textContent:''},target={querySelector:()=>error},button={dataset:{measurementUndo:'loss-excluded',measurementFingerprint:'excluded-fingerprint'},disabled:false,hasAttribute:()=>false,closest:selector=>selector==='.measurement-decision'?target:null};await h.click(clickButton(button));
  assert.deepEqual(mutations.slice(-2).map(query=>query.type),['nio_telematics/car_dashboard/update','nio_telematics/car_dashboard/get']);assert.equal(excluded,false);assert.equal(h.snapshot.parked_periods.length,1);assert.equal(h.snapshot.parked_periods[0].kwh,73.8);html=h.parkedHistory();assert.match(html,/data-parked="parked-120\.000000"/);assert.doesNotMatch(html,/measurement-decisions/);
});

test('successful measurement-error save closes preview and stale Parked detail after refresh',async()=>{
  const savedDocument=context.document,savedFormData=context.FormData,openDialogs=[];
  const root={openDialogs,append(dialog){openDialogs.push(dialog);},querySelector(selector){return selector==='dialog[open]'?openDialogs.find(dialog=>dialog.open)||null:null;},querySelectorAll(){return[];},addEventListener(){},set innerHTML(_value){for(const dialog of openDialogs)dialog.removed=true;openDialogs.length=0;}};
  context.document={...savedDocument,createElement(){const listeners={},closeButton={},saveButton={disabled:false,textContent:''},error={textContent:''},form={};const dialog={open:false,removed:false,querySelector(selector){return ({'[data-close]':closeButton,'[data-dialog-save]':form,'.save':saveButton,'.form-error':error})[selector]||null;},addEventListener(type,callback){(listeners[type]||=[]).push(callback);},showModal(){this.open=true;},close(){this.open=false;for(const callback of listeners.close||[])callback();},remove(){this.removed=true;const index=openDialogs.indexOf(this);if(index>=0)openDialogs.splice(index,1);}};return dialog;}};
  context.FormData=class {constructor(){}};
  const h=measurementHistory();delete h.dialog;h.shadowRoot=root;h.localize=()=>{};h.refreshState=()=>{};h.renderCount=0;h.render=()=>{h.renderCount++;root.innerHTML='fresh selected history';};
  const parent=h.dialog('Parked details','<p>56 kWh before review</p>'),row={id:'loss-one',fingerprint:'fp-one',start:120,end:150,kwh:1.55,state:'open',paired_candidate_id:null,paired_candidate_kwh:null,paired_candidate_excluded:false};h.snapshot.parked_intervals=[row];
  h.update=async()=>{h._deferredRender=true;return {saved:true,refreshed:true};};h.measurementErrorDialog(row);const confirmation=openDialogs[1],form=confirmation.querySelector('[data-dialog-save]');
  await form.onsubmit({preventDefault(){},target:{}});
  assert.equal(confirmation.open,false);assert.equal(parent.removed,true);assert.equal(root.openDialogs.length,0);assert.equal(h.renderCount,1);assert.equal(h._measurementFeedback,'Excluded from totals');
  context.document=savedDocument;context.FormData=savedFormData;
});

test('saved measurement-error with failed read stays open, shows acknowledgement and cannot resubmit',async()=>{
  const savedDocument=context.document,savedFormData=context.FormData,openDialogs=[];
  const root={openDialogs,append(dialog){openDialogs.push(dialog);},querySelector(selector){return selector==='dialog[open]'?openDialogs.find(dialog=>dialog.open)||null:null;},querySelectorAll(){return[];},addEventListener(){},set innerHTML(_value){for(const dialog of openDialogs)dialog.removed=true;openDialogs.length=0;}};
  context.document={...savedDocument,createElement(){const listeners={},closeButton={},saveButton={disabled:false,textContent:''},error={textContent:''},form={};const dialog={open:false,removed:false,querySelector(selector){return ({'[data-close]':closeButton,'[data-dialog-save]':form,'.save':saveButton,'.form-error':error})[selector]||null;},addEventListener(type,callback){(listeners[type]||=[]).push(callback);},showModal(){this.open=true;},close(){this.open=false;for(const callback of listeners.close||[])callback();},remove(){this.removed=true;const index=openDialogs.indexOf(this);if(index>=0)openDialogs.splice(index,1);}};return dialog;}};
  context.FormData=class {constructor(){}};
  const h=measurementHistory();delete h.dialog;h.shadowRoot=root;h.localize=()=>{};h.refreshState=()=>{};h.render=()=>{root.innerHTML='refreshed selected view';};const parent=h.dialog('Parked details','<p>Original interval detail</p>'),row={id:'loss-one',fingerprint:'fp-one',start:120,end:150,kwh:1.55,state:'open',paired_candidate_id:null,paired_candidate_kwh:null,paired_candidate_excluded:false};
  h.update=async()=>({saved:true,refreshed:false});h.measurementErrorDialog(row);const confirmation=openDialogs[1],form=confirmation.querySelector('[data-dialog-save]'),save=confirmation.querySelector('.save'),error=confirmation.querySelector('.form-error');
  await form.onsubmit({preventDefault(){},target:{}});
  assert.equal(confirmation.open,true);assert.equal(parent.open,true);assert.equal(save.disabled,true);assert.equal(error.textContent,h.savedRefreshCopy());assert.equal(h._measurementPending.has('loss-one/fp-one'),true);
  const close=confirmation.querySelector('[data-close]');close.onclick();assert.equal(parent.removed,true);assert.equal(openDialogs.length,0);
  context.document=savedDocument;context.FormData=savedFormData;
});

test('trip endpoint battery SoC keeps missing readings unknown in row and detail while preserving real zero',()=>{
  const h=instance();h.snapshot={settings:{capacity_kwh:90},active_trip_id:null};h.config.language='en';h.gapsForTrip=()=>[];h.tripEnergy=()=>null;h.tripAverage=()=>null;h.date=()=> 'time';h.value=(label,value,unit)=>`${label}: ${value==null?'—':h.n(value,1)}${unit}`;
  h.dialog=(...args)=>{h.lastDialog=args;};
  for(const [start,end,expected] of [[null,0,'—% → 0.0%'],[0,null,'0.0% → —%']]){
    const trip={id:'pending-trip',start:1,end:2,start_energy:start,end_energy:end,start_odo:10,end_odo:11,distance_km:1,segments:[]};
    const row=h.tripCard(trip);assert.ok(row.includes(expected),`row preserves endpoint values ${expected}`);assert.doesNotMatch(row,/NaN/);
    h.tripDialog(trip);const detail=h.lastDialog[1];assert.ok(detail.includes(start==null?'—':'0.0'),`detail start ${start}`);assert.ok(detail.includes(end==null?'—':'0.0'),`detail end ${end}`);assert.match(detail,/Batterij bij (vertrek|aankomst)/);
  }
});

test('successful Parked decisions scroll feedback once after deferred close render; failures do not scroll',async()=>{
  const originalDialog=context.__Base.prototype.dialog,originalFrame=context.requestAnimationFrame,frames=[],scrolls=[];
  context.requestAnimationFrame=callback=>{frames.push(callback);return frames.length;};
  context.__Base.prototype.dialog=function(...args){const listeners={},closeButton={},saveButton={disabled:false,textContent:''},dialog={open:true,querySelector(selector){return selector==='[data-close]'?closeButton:selector==='.save'?saveButton:null;},addEventListener(type,callback){(listeners[type]||=[]).push(callback);},close(){this.open=false;for(const callback of listeners.close||[])callback();}};this.lastDialog=args;this._testDialog=dialog;return dialog;};
  try{
    const h=measurementHistory(),row={id:'loss-scroll',fingerprint:'scroll-fingerprint',start:120,end:150,kwh:1,state:'open',paired_candidate_id:null,paired_candidate_kwh:null};delete h.dialog;let renderCount=0;
    h.tab='parked';h.scope='day';h.anchor='2026-11-23';h.filters={location:'all',basis:'all',price:false};h.shadowRoot={querySelector(selector){return selector==='.measurement-feedback'?{scrollIntoView:options=>scrolls.push(options)}:null;}};
    h.render=()=>{renderCount++;h.scrollMeasurementFeedbackAfterRender();};h.update=async()=>{h._deferredRender=true;return {saved:true,refreshed:true};};
    h.measurementErrorDialog(row);await h.lastDialog[2]();assert.equal(frames.length,0);assert.equal(h._measurementFeedbackScrollPending,true);
    h._testDialog.close();assert.equal(renderCount,1);assert.equal(frames.length,1);assert.deepEqual([h.tab,h.scope,h.anchor],['parked','day','2026-11-23']);
    frames.shift()();assert.equal(scrolls.length,1);assert.equal(JSON.stringify(scrolls[0]),JSON.stringify({behavior:'smooth',block:'center'}));h.render();assert.equal(frames.length,0);
    const error={textContent:''},target={querySelector:()=>error},button={dataset:{measurementUndo:'loss-scroll',measurementFingerprint:'scroll-fingerprint'},disabled:false,hasAttribute:()=>false,closest:selector=>selector==='.measurement-decision'?target:null};
    h.update=async()=>({saved:true,refreshed:true});await h.undoMeasurementError(button);assert.equal(renderCount,3);assert.equal(frames.length,1);frames.shift()();assert.equal(scrolls.length,2);
    h.update=async()=>({saved:true,refreshed:false});h.measurementErrorDialog(row);await h.lastDialog[2]();assert.equal(h._measurementFeedbackScrollPending,false);assert.equal(frames.length,0);
    h.update=async()=>{throw new Error('write rejected');};h.measurementErrorDialog(row);await assert.rejects(h.lastDialog[2](),/write rejected/);assert.equal(h._measurementFeedbackScrollPending,false);assert.equal(frames.length,0);assert.equal(scrolls.length,2);
  }finally{context.__Base.prototype.dialog=originalDialog;if(originalFrame===undefined)delete context.requestAnimationFrame;else context.requestAnimationFrame=originalFrame;}
});
