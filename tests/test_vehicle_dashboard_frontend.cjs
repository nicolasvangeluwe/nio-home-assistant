const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const elements = new Map();
const source = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/nio-vehicle-card.js'), 'utf8');
const vehicleWindow = { customCards: [] };
const vehicleRuntime = {
  HTMLElement: class {},
  customElements: { get: name => elements.get(name), define: (name, cls) => elements.set(name, cls) },
  window: vehicleWindow,
};
vm.runInNewContext(source.replace(
  "await import(retry?`${url}${url.includes('?')?'&':'?'}retry=${Date.now()}`:url);",
  "await window.__loadHistory(retry?`${url}${url.includes('?')?'&':'?'}retry=${Date.now()}`:url);",
), vehicleRuntime);
const Dashboard = elements.get('nio-vehicle-dashboard');
const Vehicle = elements.get('nio-vehicle-card');
const ledgerElements = new Map();
const ledgerPath = path.join(__dirname, '../custom_components/nio_telematics/car_dashboard/car-ledger-card.js');
const ledgerSource = fs.readFileSync(ledgerPath, 'utf8')
  .replaceAll('new URL(import.meta.url)', `new URL("file:///${ledgerPath.replaceAll('\\', '/')}")`)
  .replace(/\bexport\s*\{\s*CarLedgerCard\s*\};?/g, '');
vm.runInNewContext(ledgerSource, {
  HTMLElement: class {},
  URL,
  customElements: { get: name => ledgerElements.get(name), define: (name, cls) => ledgerElements.set(name, cls) },
  window: { customCards: [] },
});
const Ledger = ledgerElements.get('car-ledger-card');

test('dashboard setup provides keyboard-accessible help and restore controls', () => {
  const card = Object.create(Vehicle.prototype);
  assert.match(card.fieldHelp('evcc_connected', 'en'), /<details class="field-help">/);
  assert.match(card.fieldHelp('evcc_connected', 'en'), /EVCC is not required/);
  assert.match(card.fieldHelp('battery_capacity_kwh', 'nl'), /Alleen nodig/);
  assert.match(Dashboard.styles, /\.field-help summary:focus-visible/);
  assert.match(Dashboard.styles, /\.backup button\[hidden\]/);
});

function display(chargingState, connection, power, powerUnit = 'kW') {
  const nodes = new Map();
  const makeNode = () => {
    const node = {textContent:'',style:{},setAttribute(name,value){this[name]=value;}};
    Object.defineProperty(node,'innerHTML',{get(){return this._html||'';},set(value){this._html=String(value);this.textContent=String(value).replace(/<[^>]*>/g,'');}});
    return node;
  };
  const root = {
    querySelector(selector) {
      if (selector === 'car-ledger-card') return null;
      if (selector === '[data-value="third-label"],[data-label="third"]') return nodes.get('[data-label="third"]');
      if (!nodes.has(selector)) nodes.set(selector, makeNode());
      return nodes.get(selector);
    },
  };
  nodes.set('[data-label="third"]', makeNode());
  const states = {
    soc: { state: '75' }, range: { state: '416' }, odo: { state: '6266' }, limit: { state: '90' },
    charging: { state: chargingState }, connected: { state: connection }, power: { state: power, attributes: {unit_of_measurement: powerUnit} },
  };
  const card = {
    vehicle: { entities: { battery_state_of_charge: 'soc', remaining_range: 'range', odometer: 'odo', maximum_soc: 'limit', charging_state: 'charging' }, preferences: { evcc_connected: 'connected', evcc_power: 'power' } },
    shadowRoot: { querySelector: selector => selector === '.dashboard[data-entry-id]' ? root : null },
    words: { charging: 'Laden', chargingUnknown: 'Laadstatus onbekend', connectedStatus: 'Verbonden', idle: 'Laadt niet', unavailable: 'Niet beschikbaar', power: 'Vermogen', limit: 'Laadlimiet' },
    state: id => states[id],
    number(id, digits = 0) { const value = Number(states[id]?.state); return Number.isFinite(value) ? value.toFixed(digits) : null; },
    powerKw: Dashboard.prototype.powerKw,
    connectedState: Dashboard.prototype.connectedState,
    formatNumber: Dashboard.prototype.formatNumber,
    esc: Vehicle.prototype.esc,
    locale: () => 'en',
    stamp: () => '',
    _hass: {},
  };
  Dashboard.prototype.updateDisplay.call(card);
  nodes.states=states;
  nodes.card=card;
  return nodes;
}

test('a connected but idle EVCC car is not labelled charging', () => {
  const nodes = display('unknown', 'on', '0');
  assert.equal(nodes.get('[data-value="status"]').textContent, 'Laadt niet · Verbonden');
  assert.equal(nodes.get('[data-value="soc"]').textContent, '75%');
  assert.equal(nodes.get('[data-value="range"]').textContent, '416 km');
});

test('positive power means charging even when native state is sparse', () => {
  assert.equal(display('unknown', 'on', '4.2').get('[data-value="status"]').textContent, 'Laden · Verbonden');
});

test('a non-EVCC charger with watts and textual connection is accepted', () => {
  const nodes = display('unknown', 'connected', '4200', 'W');
  assert.equal(nodes.get('[data-value="status"]').textContent, 'Laden · Verbonden');
  assert.equal(nodes.get('[data-value="third"]').textContent, '4.2 kW');
});

test('connected alone does not imply idle; unknown state stays explicit', () => {
  assert.equal(display('unknown', 'on', 'unknown').get('[data-value="status"]').textContent,
    'Laadstatus onbekend · Verbonden');
  assert.equal(display('unknown', 'off', 'unknown').get('[data-value="status"]').textContent,
    'Laadstatus onbekend');
  assert.equal(display('unknown', 'on', '-0.2').get('[data-value="status"]').textContent,
    'Laadstatus onbekend · Verbonden');
});

test('charger power threshold and explicit native states retain their meanings', () => {
  assert.equal(display('unknown', 'on', '0.1').get('[data-value="status"]').textContent,
    'Laadt niet · Verbonden');
  assert.equal(display('unknown', 'on', '0.1001').get('[data-value="status"]').textContent,
    'Laden · Verbonden');
  assert.equal(display('off', 'on', 'unknown').get('[data-value="status"]').textContent,
    'Laadt niet · Verbonden');
  assert.equal(display('on', 'off', 'unknown').get('[data-value="status"]').textContent,
    'Laden');
  assert.equal(display('3', 'on', 'unknown').get('[data-value="status"]').textContent,
    'Laadstatus onbekend · Verbonden');
});

test('simple NIO card also distinguishes unknown status from idle', () => {
  const card = Object.create(Vehicle.prototype);
  const states = {
    soc: {state:'75'}, range:{state:'416'}, odo:{state:'6266'}, limit:{state:'90'},
    charging:{state:'unknown'}, connected:{state:'on'}, power:{state:'unknown',attributes:{unit_of_measurement:'kW'}},
  };
  card._hass={language:'en',states};
  card.vehicles=[{entry_id:'example',name:'ET5 Touring',entities:{battery_state_of_charge:'soc',remaining_range:'range',odometer:'odo',maximum_soc:'limit',charging_state:'charging'},preferences:{language:'en',model:'ET5 Touring',evcc_connected:'connected',evcc_power:'power',ledger_enabled:false},ledger_available:false}];card.config={entry_id:'example'};
  card.shadowRoot={innerHTML:'',querySelector:()=>null};card.view='overview';card.openDetails=false;
  card.state=Vehicle.prototype.state;card.number=Vehicle.prototype.number;card.powerKw=Vehicle.prototype.powerKw;card.formatNumber=Vehicle.prototype.formatNumber;card.esc=Vehicle.prototype.esc;
  card.stamp=Vehicle.prototype.stamp;card.effectiveModel=Vehicle.prototype.effectiveModel;card.artwork=()=>'';
  card.render();
  assert.match(card.shadowRoot.innerHTML,/Charging status unknown · Connected/);
  assert.match(card.shadowRoot.innerHTML,/<strong>75(?:\.0)?<small>%<\/small><\/strong>/,'instantaneous SoC remains a percentage');
  assert.doesNotMatch(card.shadowRoot.innerHTML,/Battery equivalent/,'Parked battery equivalents do not replace instantaneous SoC');
});

test('charging status unknown is localized in all fourteen dashboard languages', () => {
  const languages=['en','nl','de','fr','nb','sv','da','cs','el','hu','lb','pl','pt','ro'];
  const card=Object.create(Vehicle.prototype);card._hass={language:'en'};
  const words=languages.map(language=>{
    card.vehicles=[{entry_id:'lang',preferences:{language}}];card.config={entry_id:'lang'};
    return card.words;
  });
  assert.equal(words.length,14);
  assert.ok(words.every(word=>typeof word.chargingUnknown==='string'&&word.chargingUnknown.length>0));
  assert.equal(words[0].chargingUnknown,'Charging status unknown');
  assert.equal(words[1].chargingUnknown,'Laadstatus onbekend');
  assert.ok(words.every(word=>typeof word.connectedStatus==='string'&&word.connectedStatus.length>0));
});

test('a selected external binary state updates the displayed NIO status', () => {
  const nodes=display('unknown','on','unknown');
  assert.equal(nodes.get('[data-value="status"]').textContent,'Laadstatus onbekend · Verbonden');
  nodes.states.charging.state='on';
  Dashboard.prototype.updateDisplay.call(nodes.card);
  assert.equal(nodes.get('[data-value="status"]').textContent,'Laden · Verbonden');
});

test('no configured EVCC source falls back to native charge limit', () => {
  const nodes = display('not_charging', undefined, undefined);
  assert.equal(nodes.get('[data-value="status"]').textContent, 'Laadt niet');
  assert.equal(nodes.get('[data-label="third"]').textContent, 'Laadlimiet');
  assert.equal(nodes.get('[data-value="third"]').textContent, '90%');
});

test('EVCC quick setup only offers chargers with matching connection and power', () => {
  const presets = Dashboard.prototype.evccPresets.call({ _hass: { states: {
    'binary_sensor.evcc_garage_connected': {},
    'sensor.evcc_garage_charge_power': {},
    'binary_sensor.evcc_driveway_connected': {},
    'sensor.other_charge_power': {},
  } } });
  assert.deepEqual(Array.from(presets, item => ({...item})), [{
    name: 'garage', connected: 'binary_sensor.evcc_garage_connected', power: 'sensor.evcc_garage_charge_power',
  }]);
});

test('history uses English outside Dutch HA and keeps Dutch for the owner', () => {
  const english = {config: {language: 'en'}, displayLocale: 'en'};
  const dutch = {config: {language: 'nl'}, displayLocale: 'nl'};
  assert.equal(Ledger.prototype.translate.call(english, 'Ritten'), 'Trips');
  assert.equal(Ledger.prototype.translate.call(english, 'Laden'), 'Charging');
  assert.equal(Ledger.prototype.translate.call(dutch, 'Ritten'), 'Ritten');
  assert.equal(Ledger.prototype.translate.call(english, 'Lopende sessie'), 'Ongoing session');
});

test('ongoing charge is not presented as a completed session', () => {
  const card = Object.create(Ledger.prototype);
  card.config = {language: 'nl'};
  const active = card.chargeCard({id:'home-114',kind:'home',category:'home',start:1700000000,end:1700000900,kwh:0.91,cost_eur:null,benefit_eur:null,confirmed:true,ongoing:true});
  assert.match(active, /Lopende sessie/);
  assert.match(active, /class="session active"/);
  assert.doesNotMatch(active, / → /);
  assert.doesNotMatch(active, /Prijs aanvullen/);
  const finished = card.chargeCard({id:'home-113',kind:'home',category:'home',start:1700000000,end:1700000900,kwh:1,cost_eur:0.1,confirmed:true});
  assert.match(finished, / → /);
  assert.doesNotMatch(finished, /Lopende sessie/);
});

test('history consumption pairs known energy with its distance and preserves raw gaps', () => {
  const card = Object.create(Ledger.prototype);
  card.snapshot = {settings: {capacity_kwh: 90}};
  const rows = [
    {start: 1, end: 2, km: 4, kwh: 0.9, complete: true, cost_eur: null},
    {start: 2, end: 3, km: 1, kwh: null, complete: false, invalid_reason: 'charging'},
    {start: 3, end: 4, km: 2, kwh: 0, complete: true, cost_eur: null},
    {start: 1, end: 2, km: 4, kwh: 0.9, complete: true, cost_eur: null},
  ];
  const before = JSON.stringify(rows);
  const stats = card.drivingStats(rows);
  assert.equal(stats.used_kwh, 0.9);
  assert.equal(stats.consumption_distance_km, 6);
  assert.equal(stats.consumption_kwh_100km, 15);
  assert.equal(stats.cost_eur_100km, null);
  assert.equal(JSON.stringify(rows), before);
  assert.equal(card.knownDriving(rows, 5).reduce((sum, row) => sum + row.km, 0), 5);
});

test('history card leaves missing energy unknown instead of deriving it from endpoints', () => {
  const card = Object.create(Ledger.prototype);
  const trip = {id: 'trip-1', start: 1, end: 3, start_energy: 50, end_energy: 48,
    start_odo: 100, end_odo: 105, distance_km: 5, complete: false, segments: [
      {start: 1, end: 2, km: 4, kwh: 0.9, complete: true, start_energy: 50, end_energy: 49.1},
      {start: 2, end: 3, km: 1, kwh: null, complete: false, start_energy: 49.1, end_energy: 48},
    ]};
  const raw = {settings: {capacity_kwh: 90}, statistics: {last_trip: {segments: []}},
    trips: [trip], charges: [], counters: [], preferences: {}, active_trip_id: null};
  const before = JSON.stringify(raw);
  const prepared = card.prepareSnapshot(raw);
  assert.equal(prepared.trips[0].segments[1].kwh, null);
  assert.equal(prepared.statistics.last_trip.distance_km, 5);
  assert.equal(prepared.statistics.last_trip.consumption_distance_km, 4);
  assert.equal(prepared.statistics.last_trip.consumption_kwh_100km, 22.5);
  assert.equal(JSON.stringify(raw), before);
});

test('rolling native 100 km reaches past gaps but excludes range-derived trips', () => {
  const card = Object.create(Ledger.prototype);
  const trip = (id, start, km, kwh, source, native_alignment_version) => ({
    id, start, end: start + 1, start_odo: start, end_odo: start + km,
    start_energy: 60, end_energy: 60 - (kwh || 0), distance_km: km,
    source, native_alignment_version, complete: kwh != null,
    segments: [{start, end: start + 1, km, kwh, complete: kwh != null}],
  });
  const raw = {settings: {capacity_kwh: 90}, statistics: {
    last_trip: {segments: []}, last_100km: {segments: [], remaining_kwh: 45},
  }, trips: [
    trip('native-old', 1, 80, 16, undefined, 2),
    trip('range-recovery', 3, 100, 10, 'recorder_recovery', undefined),
    trip('native-new', 5, 30, 6, undefined, 2),
    trip('native-gap', 7, 5, null, undefined, 2),
  ], charges: [], counters: [], preferences: {}, active_trip_id: null};
  const prepared = card.prepareSnapshot(raw);
  const rolling = prepared.statistics.last_100km;
  assert.equal(rolling.distance_km, 100);
  assert.equal(rolling.used_kwh, 20);
  assert.equal(rolling.consumption_kwh_100km, 20);
  assert.equal(rolling.projected_range_km, 225);
});

test('other NIO models keep their placeholder before local artwork arrives', () => {
  const card = Object.create(Dashboard.prototype);
  const html = card.carImage('EL6');
  assert.match(html, /class="car-placeholder"/);
  assert.doesNotMatch(html, /et5-touring-hero/);
  const range = Dashboard.prototype.rangeIcon.call({}, 'EL6');
  assert.match(range, /map-marker-distance/);
  assert.doesNotMatch(range, /range-nio-d/);
  assert.match(Dashboard.prototype.rangeIcon.call({}, 'ET5 Touring'), /range-nio-d/);
});

test('ET5 Touring uses the locally bundled studio render without stacked shadows', () => {
  const card = Object.create(Dashboard.prototype);
  const html = card.carImage('ET5 Touring');
  assert.match(html, /et5-touring-studio\.png/);
  assert.match(Dashboard.styles, /\.car-art:before\{display:none\}/);
  assert.match(Dashboard.styles, /\.car-photo\{filter:none\}/);
});

test('automatic model detection prefers ET5 Touring over the shorter ET5 name', () => {
  const card = Object.create(Dashboard.prototype);
  card.config = {};
  const model = card.modelFor({name: 'My ET5 Touring', preferences: {model: 'auto'}});
  assert.equal(model, 'ET5 Touring');
  const unknown = card.modelFor({name: 'My car', preferences: {model: 'auto'}});
  assert.equal(unknown, 'NIO');
});

test('paint images use bundled model paths and preserve the Touring default', () => {
  const catalogue = JSON.parse(fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/artwork/catalogue.json'), 'utf8'));
  const card = Object.create(Dashboard.prototype);
  card.artworkCatalogue = catalogue;
  card.vehicles = [];
  card.config = {};
  card._hass = {language: 'en'};
  assert.match(card.carImage('EL6', 'auto'), /\/nio_telematics\/artwork\/el6\//);
  assert.match(card.carImage('ES8', 'auto'), /\/nio_telematics\/artwork\/es8\//);
  assert.match(card.paintOptions('ES8'), /cloud-white/);
  assert.match(card.carImage('ET5 Touring', 'auto'), /et5-touring-studio\.png/);
  assert.match(card.carImage('ET5 Touring', 'sunlight-gold'), /\/nio_telematics\/artwork\/et5-touring\//);
  assert.doesNotMatch(card.carImage('ET7', 'sunlight-gold'), /\/nio_telematics\/artwork\//);
});

test('all offered dashboard languages translate the history tabs and empty state', () => {
  const card = Object.create(Dashboard.prototype);
  card._hass = {language: 'en'};
  card.vehicles = [{entry_id: 'car', preferences: {language: 'auto'}}];
  for(const language of ['nl','fr','de','nb','sv','da','cs','el','hu','lb','pl','pt','ro']){
    card.config = {language};
    assert.notEqual(card.words.vehicleHistory, 'Vehicle history', language);
    assert.notEqual(card.words.historyTabs[0], 'Charging', language);
    assert.notEqual(card.words.noData, 'Vehicle data unavailable', language);
  }
});

test('the dashboard has three persistent primary destinations and a module-owned history entry point', () => {
  assert.match(source, /data-screen-target="\$\{key\}"/);
  assert.match(source, /data-panel="history"/);
  assert.match(source, /data-panel="settings"/);
  assert.match(source, /this\.config\?\.history_url\|\|['"]\/nio_telematics\/nio-dashboard-history\.js['"]/);
  assert.match(source, /addEventListener\('nio-history-updated'/);
  assert.doesNotMatch(source.slice(source.lastIndexOf('const NIO_DASHBOARD_ICONS')), /car-ledger-card/);
});

test('primary navigation switches panels and retains its selected screen', () => {
  const panels = ['car','history','settings'].map(name => ({dataset:{panel:name},hidden:true}));
  const buttons = ['car','history','settings'].map(name => ({dataset:{screenTarget:name},setAttribute(key,value){this[key]=value;},removeAttribute(key){delete this[key];}}));
  const root = {dataset:{},querySelectorAll(selector){
    return selector === '[data-panel]' ? panels : buttons;
  }};
  const card = Object.create(Dashboard.prototype);
  card.shadowRoot = {querySelector:()=>root};
  card.selectScreen('history');
  assert.equal(card.screen,'history');
  assert.deepEqual(panels.map(panel=>panel.hidden),[true,false,true]);
  assert.deepEqual(buttons.map(button=>button['aria-current']||null),[null,'page',null]);
  card.selectScreen('settings');
  assert.equal(root.dataset.screen,'settings');
  card.selectScreen('history');
  assert.equal(root.dataset.screen,'history');
});

test('calculated range and current charging summary use only current snapshot fields', () => {
  const received={textContent:''},solar={textContent:''};
  const calculated={innerHTML:'',textContent:'',setAttribute(name,value){this[name]=value;},set innerHTML(value){this._html=value;this.textContent=String(value).replace(/<[^>]*>/g,'');},get innerHTML(){return this._html||'';}};
  const note={textContent:''};
  const details={innerHTML:''};
  const root={querySelector(selector){return ({'[data-details]':details,'[data-value="received"]':received,'[data-value="solar"]':solar,'[data-value="calculated-range"]':calculated,'[data-range-note]':note})[selector]||null;}};
  const card={shadowRoot:{querySelector:()=>root},vehicle:{preferences:{}},words:{unavailable:'Unavailable',dashboardUI:Array(12).fill('').concat(['Based on recorded driving consumption','Not available','Ongoing charge','Energy']),dashboardSolarShare:'Solar share'},
    _historySnapshot:{active_home_charge:{kwh:12.3,solar_pct:42,time:'must not be fabricated'},statistics:{month:{projected_range_km:320}}},
    state:()=>null,formatNumber:value=>String(value),esc:Vehicle.prototype.esc};
  Dashboard.prototype.updateDashboardDetails.call(card);
  assert.equal(received.textContent,'12.3 kWh');
  assert.equal(solar.textContent,'42%');
  assert.match(calculated.innerHTML,/320<small> km<\/small>/);
  assert.match(note.textContent,/recorded driving consumption/i);
});

test('successful History retry replaces the unavailable message and Retry button', async () => {
  let button;
  const host = {
    _html: '', isConnected: true, children: [],
    get innerHTML() { return this._html; },
    set innerHTML(value) { this._html = String(value); button = this._html.includes('<button') ? {onclick: null} : null; },
    querySelector(selector) { return selector === 'button' ? button : selector === 'nio-dashboard-history' ? this.children.find(child => child.tagName === selector) || null : null; },
    replaceChildren(history) { this.children = [history]; this.innerHTML = '<nio-dashboard-history></nio-dashboard-history>'; button = null; },
  };
  const card = Object.create(Dashboard.prototype);
  card.vehicles = [{entry_id: 'embedded-car', ledger_available: true}];
  card.config = {};
  card.words = {dashboardUI: Array(21).fill('').map((value, i) => i === 19 ? 'Set up' : i === 20 ? 'History is not available' : value), retry: 'Retry', historyOptional: 'History is optional'};
  card.locale = () => 'en';
  card._hass = {};
  card.shadowRoot = {querySelector: selector => selector === '[data-history]' ? host : null};
  vehicleRuntime.document = {
    createElement(name) {
      assert.equal(name, 'nio-dashboard-history');
      return {tagName: name, setConfig(config) {this.config = config;}, addEventListener() {}};
    },
  };
  let attempt = 0;
  vehicleWindow.__loadHistory = async () => {
    attempt++;
    if (attempt === 1) throw new Error('temporary asset failure');
    elements.set('nio-dashboard-history', class {});
  };

  await card.ensureLedger('embedded-car');
  assert.match(host.innerHTML, /History is unavailable/);
  assert.ok(button);
  await button.onclick();

  assert.equal(attempt, 2);
  assert.equal(host.children.length, 1);
  assert.equal(host.children[0].tagName, 'nio-dashboard-history');
  assert.doesNotMatch(host.innerHTML, /History is unavailable|Retry/);
  const loadedHistory = host.children[0];
  await card.ensureLedger('embedded-car');
  assert.equal(host.children[0], loadedHistory);
  assert.equal(host.children.length, 1);
});

test('explicit navigation reveals its destination without changing background rendering', () => {
  const seen=[];
  const panel={scrollIntoView:options=>seen.push(['history',options.block])};
  const root={querySelector:()=>panel,scrollIntoView:options=>seen.push(['car',options.block])};
  const card={shadowRoot:{querySelector:()=>root},selectScreen(screen){this.screen=screen;}};
  Dashboard.prototype.navigate.call(card,'history');
  Dashboard.prototype.navigate.call(card,'car');
  assert.deepEqual(seen,[['history','start'],['car','start']]);
});

test('calculated-range details use the same current-month basis as the car reading', async () => {
  let refreshed=false;
  const history={scope:'year',period:'last_trip',anchor:'2025-01-01',refresh:async()=>{refreshed=true;}};
  const card={navigate:screen=>assert.equal(screen,'history'),shadowRoot:{querySelector:()=>history}};
  await Dashboard.prototype.openCalculatedRange.call(card);
  assert.equal(history.tab,'insight');assert.equal(history.scope,'month');assert.equal(history.period,'month');assert.equal(history.anchor,null);assert.equal(refreshed,true);
});

test('all fourteen dashboard locales include the grouped menu and missing-range explanation', () => {
  const card=Object.create(Dashboard.prototype);card._hass={language:'en'};
  for(const language of ['en','nl','de','fr','nb','sv','da','cs','el','hu','lb','pl','pt','ro']){
    card.config={language};card.vehicles=[{entry_id:'lang',preferences:{language:'auto'}}];
    const words=card.words.dashboardUI;
    assert.equal(words.length,21,language);
    assert.ok(words[3]&&words[4]&&words[5]&&words[6],language);
    assert.ok(words[13].length>20,language);
    assert.ok(card.words.dashboardSolarShare.length>3,language);
    assert.ok(card.words.dashboardSettingsIntro.length>12,language);
    assert.ok(card.words.dashboardHistoryIntro.length>12,language);
  }
});

test('late artwork does not replace an open settings dialog', async () => {
  const catalogue = JSON.parse(fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/artwork/catalogue.json'), 'utf8'));
  const localElements = new Map();
  vm.runInNewContext(source, {
    HTMLElement: class {},
    customElements: {get: name => localElements.get(name), define: (name, cls) => localElements.set(name, cls)},
    window: {customCards: []},
    fetch: async () => ({ok: true, json: async () => catalogue}),
  });
  const card = Object.create(localElements.get('nio-vehicle-dashboard').prototype);
  card.vehicles = [{entry_id: 'car', name: 'My EL6', preferences: {model: 'EL6', paint: 'auto'}}];
  card.config = {};
  card._hass = {language: 'en'};
  card.isConnected = true;
  const picker = {value: 'auto', options: [{value: 'auto'}], innerHTML: ''};
  const dialog = {querySelector: selector => selector === '[name="paint"]' ? picker : selector === '[name="model"]' ? {value: 'EL6'} : null};
  const art = {innerHTML: ''};
  card.shadowRoot = {querySelector: selector => selector === 'dialog[open]' ? dialog : selector === '.car-art' ? art : null};
  let renders = 0;
  card.render = () => {renders++};
  card.refreshArtwork();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(renders, 0);
  assert.match(picker.innerHTML, /cloud-white/);
  assert.match(art.innerHTML, /\/nio_telematics\/artwork\/el6\//);
});

test('a failed artwork fetch can retry after the cooldown', async () => {
  const localElements = new Map();
  let now = 1000, calls = 0;
  const context = {
    HTMLElement: class {},
    customElements: {get: name => localElements.get(name), define: (name, cls) => localElements.set(name, cls)},
    window: {customCards: []},
    Date: class extends Date {static now(){return now;}},
    fetch: async () => {calls++; if(calls === 1)throw new Error('Temporary outage'); return {ok: true, json: async () => ({schema_version: 1, selection: 'model_and_paint', models: []})};},
  };
  vm.createContext(context);
  vm.runInContext(source + '\nglobalThis.loadArtwork = nioLoadArtworkCatalogue;', context);
  assert.equal(await context.loadArtwork(), null);
  assert.equal(await context.loadArtwork(), null);
  assert.equal(calls, 1);
  now += 30001;
  assert.equal((await context.loadArtwork()).schema_version, 1);
  assert.equal(calls, 2);
});
