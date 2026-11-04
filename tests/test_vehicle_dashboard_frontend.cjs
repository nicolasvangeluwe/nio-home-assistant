const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const elements = new Map();
const source = fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/nio-vehicle-card.js'), 'utf8');
vm.runInNewContext(source, {
  HTMLElement: class {},
  customElements: { get: name => elements.get(name), define: (name, cls) => elements.set(name, cls) },
  window: { customCards: [] },
});
const Dashboard = elements.get('nio-vehicle-dashboard');
const Vehicle = elements.get('nio-vehicle-card');
const ledgerElements = new Map();
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../custom_components/nio_telematics/car_dashboard/car-ledger-card.js'), 'utf8'), {
  HTMLElement: class {},
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
  const root = {
    querySelector(selector) {
      if (selector === 'car-ledger-card') return null;
      if (!nodes.has(selector)) nodes.set(selector, { textContent: '', style: {}, setAttribute(name, value) { this[name] = value; } });
      return nodes.get(selector);
    },
  };
  const states = {
    soc: { state: '75' }, range: { state: '416' }, odo: { state: '6266' }, limit: { state: '90' },
    charging: { state: chargingState }, connected: { state: connection }, power: { state: power, attributes: {unit_of_measurement: powerUnit} },
  };
  const card = {
    vehicle: { entities: { battery_state_of_charge: 'soc', remaining_range: 'range', odometer: 'odo', maximum_soc: 'limit', charging_state: 'charging' }, preferences: { evcc_connected: 'connected', evcc_power: 'power' } },
    shadowRoot: { querySelector: selector => selector === '.dashboard[data-entry-id]' ? root : null },
    words: { charging: 'Laden', connectedStatus: 'Verbonden', idle: 'Laadt niet', unavailable: 'Niet beschikbaar', power: 'Vermogen', limit: 'Laadlimiet' },
    state: id => states[id],
    number(id, digits = 0) { const value = Number(states[id]?.state); return Number.isFinite(value) ? value.toFixed(digits) : null; },
    powerKw: Dashboard.prototype.powerKw,
    connectedState: Dashboard.prototype.connectedState,
    formatNumber: Dashboard.prototype.formatNumber,
    locale: () => 'en',
    stamp: () => '',
    _hass: {},
  };
  Dashboard.prototype.updateDisplay.call(card);
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
