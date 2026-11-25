const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const component = path.join(__dirname, '../custom_components/nio_telematics');
const root = { querySelector() { return null; }, querySelectorAll() { return []; }, addEventListener() {} };
const context = {
  URL, Intl, Date, console,
  CustomEvent: class { constructor(type, options) { this.type = type; Object.assign(this, options); } },
  HTMLElement: class {
    constructor() { this.attributes = {}; }
    setAttribute(key, value) { this.attributes[key] = value; }
    addEventListener() {}
    attachShadow() { this.shadowRoot = root; }
  },
  window: { customCards: [] }, document: { hidden: false, addEventListener() {}, removeEventListener() {} },
  customElements: { get() {}, define() {} },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(component, 'car_dashboard/car-ledger-card.js'), 'utf8')
  .replaceAll('import.meta.url', JSON.stringify('https://ha.test/car-dashboard.js?nio_owned=1'))
  .replace('export { CarLedgerCard };', ''), context);
vm.runInContext(fs.readFileSync(path.join(component, 'nio-dashboard-history.js'), 'utf8')
  .replaceAll('\r\n', '\n')
  .replace(/const baseVersion=.*?\nconst \{CarLedgerCard\}=await import\([^\n]+\);/, '')
  .replaceAll('import.meta.url', JSON.stringify('https://ha.test/nio-dashboard-history.js'))
  .replace('export function periodLabel', 'function periodLabel')
  .replace('export class NioDashboardHistory', 'class NioDashboardHistory')
  + '\nglobalThis.__History=NioDashboardHistory;', context);
const History = context.__History;

// UPDATE's real contract is an ordinary ledger snapshot: no selected calendar
// and no statistics.selected. GET adds those only for a period query.
function ordinary(revision = 1) {
  const statistics = Object.fromEntries(['day', 'month', 'year', 'since_charge', 'last_trip', 'last_100km']
    .map(key => [key, { segments: [], categories: {}, charged_kwh: 0, spend_eur: 0, currency: 'DKK' }]));
  return { revision, currency: 'DKK', settings: { capacity_kwh: 90 }, preferences: { currency: 'DKK' },
    statistics, charges: [], trips: [], parked_periods: [], counters: [], charging_daily: [],
    unaccounted_intervals: [], driving_segments: [], active_trip_id: null };
}
function selected(revision = 2, scope = 'month') {
  const result = ordinary(revision);
  result.selected_period = { scope, date: '2026-11-24', start_date: '2026-11-01',
    end_date: '2026-12-01', start: 100, end: 200, effective_end: 190 };
  result.statistics.selected = { segments: [], categories: {}, currency: 'DKK' };
  return result;
}
function instance(language = 'en') {
  const h = new History(); h.config = { entry_id: 'one', language };
  h.renderCount = 0; h.render = () => { h.renderCount++; }; h.refreshState = () => {};
  h.events = []; h.dispatchEvent = event => { h.events.push(event); };
  return h;
}
function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; }
const tick = () => new Promise(resolve => setImmediate(resolve));

test('ordinary mutation response is followed by the current selected GET and parent notifications', async () => {
  const h = instance(), calls = []; h.scope = 'week'; h.anchor = '2026-11-23';
  const read = selected(2, 'week');
  read.charges = [{ id: 'inside', start: 110, end: 150, category: 'other', confirmed: true, kwh: 1 },
    { id: 'outside', start: 210, end: 250, category: 'other', confirmed: true, kwh: 1 }];
  h._hass = { callWS: async query => { calls.push(query); return query.type.endsWith('/update') ? ordinary(2) : read; } };
  const result = await h.update('add_charge', { kwh: 1, receipt: 7.46 });
  assert.equal(result.saved, true); assert.equal(result.refreshed, true);
  assert.deepEqual(calls.map(q => q.type), ['nio_telematics/car_dashboard/update', 'nio_telematics/car_dashboard/get']);
  assert.equal(calls[1].period, 'week'); assert.equal(calls[1].date, '2026-11-23');
  assert.equal(h.fullSnapshot.selected_period.scope, 'week');
  assert.deepEqual(Array.from(h.snapshot.charges, row => row.id), ['inside']);
  assert.equal(h.events[0].detail.snapshot.selected_period, undefined);
  assert.equal(h.events.at(-1).detail.snapshot.selected_period.scope, 'week');
  assert.equal(h.events.at(-1).detail.entry_id, 'one');
  assert.equal(h.events.at(-1).bubbles, true); assert.equal(h.events.at(-1).composed, true);
});

test('measurement-error exclusion posts exact raw identity then re-reads the selected period', async () => {
  const h = instance(), calls = [], values = { ident: 'loss-raw-id', fingerprint: 'loss-current-fingerprint', excluded: true };
  h.scope = 'week'; h.anchor = '2026-11-23';
  const read = selected(2, 'week');
  read.measurement_errors = [{ id: 'loss-raw-id', fingerprint: 'loss-current-fingerprint', start: 110, end: 150, kwh: 1.55, state: 'excluded' },
    { id: 'outside', fingerprint: 'outside-fingerprint', start: 210, end: 250, kwh: 2, state: 'stale' }];
  read.parked_intervals = [{ id: 'loss-raw-id', fingerprint: 'loss-current-fingerprint', start: 110, end: 150, kwh: 1.55, state: 'excluded' },
    { id: 'outside', fingerprint: 'outside-fingerprint', start: 210, end: 250, kwh: 2, state: 'stale' }];
  h._hass = { callWS: async query => { calls.push(query); return query.type.endsWith('/update') ? ordinary(2) : read; } };

  const result = await h.update('set_measurement_error', values);

  assert.equal(result.saved, true); assert.equal(result.refreshed, true);
  assert.deepEqual(calls.map(query => query.type), ['nio_telematics/car_dashboard/update', 'nio_telematics/car_dashboard/get']);
  assert.deepEqual(calls[0].values, values); assert.equal(calls[0].action, 'set_measurement_error');
  assert.equal(calls[1].period, 'week'); assert.equal(calls[1].date, '2026-11-23');
  assert.deepEqual(Array.from(h.snapshot.measurement_errors, row => row.id), ['loss-raw-id']);
  assert.equal(h.fullSnapshot.measurement_errors[1].fingerprint, 'outside-fingerprint');

  const cleared = selected(3, 'week'); cleared.measurement_errors = []; cleared.parked_intervals = [];
  h._hass = { callWS: async query => query.type.endsWith('/update') ? ordinary(3) : cleared };
  const undo = await h.update('set_measurement_error', { ident: 'orphan-id', fingerprint: 'saved-orphan-fingerprint', excluded: false });
  assert.equal(undo.saved, true); assert.equal(undo.refreshed, true);
  assert.deepEqual(Array.from(h.snapshot.measurement_errors), []);
});

test('failed follow-up reports saved in every locale and never repeats the mutation', async () => {
  for (const language of ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro']) {
    const h = instance(language), calls = []; h.fullSnapshot = selected(1); h.applyView(); const before = h.snapshot;
    h._hass = { callWS: async query => { calls.push(query); if (query.type.endsWith('/update')) return ordinary(2); throw new Error('GET failed'); } };
    const result = await h.update('add_charge', { kwh: 1, receipt: 7.46 });
    assert.equal(result.saved, true); assert.equal(result.refreshed, false);
    assert.equal(h.error, h.savedRefreshCopy(), language);
    assert.equal(calls.filter(q => q.type.endsWith('/update')).length, 1);
    assert.equal(calls.filter(q => q.type.endsWith('/get')).length, 1);
    assert.equal(h.snapshot, before); assert.equal(h.loading, false);
    assert.equal(h.events.length, 1); assert.equal(h.events[0].detail.snapshot.revision, 2);
    h._hass.callWS = async query => { calls.push(query); return selected(2); };
    await h.refresh(); assert.equal(h.error, ''); assert.equal(h._savedRefreshPending, false);
    assert.equal(calls.filter(q => q.type.endsWith('/update')).length, 1);
  }
});

test('mutation failure preserves the current form/view and does not issue a GET', async () => {
  const h = instance(), values = { energy_kwh: 12, cost: 3.6 }, calls = [];
  h.fullSnapshot = selected(1); h.applyView(); const before = h.snapshot;
  h._hass = { callWS: async query => { calls.push(query); throw new Error('write rejected'); } };
  await assert.rejects(h.update('resolve_gap', values), /write rejected/);
  assert.equal(calls.length, 1); assert.equal(calls[0].values, values);
  assert.equal(values.energy_kwh, 12); assert.equal(values.cost, 3.6);
  assert.equal(h.snapshot, before); assert.equal(h.renderCount, 0); assert.equal(h.events.length, 0);
  assert.equal(h._pendingWrites, 0);
});

test('a pre-mutation read cannot overwrite the selected post-save snapshot', async () => {
  const h = instance(), old = deferred(); let reads = 0;
  h._hass = { callWS: query => query.type.endsWith('/update') ? Promise.resolve(ordinary(2))
    : ++reads === 1 ? old.promise : Promise.resolve(selected(2)) };
  const stale = h.refresh(); await h.update('resolve_gap', { status: 'ignored' });
  old.resolve(selected(1)); assert.equal(await stale, 'superseded');
  assert.equal(h.fullSnapshot.revision, 2);
  assert.equal(h.events.some(event => event.detail.snapshot.revision === 1), false);
});

test('a newer period wins over the save follow-up even when the old read rejects', async () => {
  const h = instance(), reads = [];
  h._hass = { callWS: query => { if (query.type.endsWith('/update')) return Promise.resolve(ordinary(2));
    const pending = deferred(); reads.push({ ...pending, query }); return pending.promise; } };
  const saving = h.update('resolve_gap', { status: 'manual', energy_kwh: 12 }); await tick();
  h.scope = 'year'; h.anchor = '2025-06-01'; const newest = h.refresh();
  reads[1].resolve(selected(3, 'year')); await newest;
  reads[0].reject(new Error('old period failed')); await saving;
  assert.equal(h.fullSnapshot.revision, 3); assert.equal(h.fullSnapshot.selected_period.scope, 'year');
  assert.equal(reads[1].query.date, '2025-06-01'); assert.equal(h.error, ''); assert.equal(h.loading, false);
});

test('a superseding read failure still reports that the mutation was saved', async () => {
  const h = instance('fr'), reads = [];
  h._hass = { callWS: query => { if (query.type.endsWith('/update')) return Promise.resolve(ordinary(2));
    const pending = deferred(); reads.push(pending); return pending.promise; } };
  const saving = h.update('add_charge', { kwh: 1 }); await tick();
  const newest = h.refresh(); reads[1].reject(new Error('new read failed')); await newest;
  reads[0].resolve(selected(2)); await saving;
  assert.equal(h.error, h.savedRefreshCopy()); assert.equal(h._savedRefreshPending, true);
  assert.equal(h.events.length, 1);
});

test('switching vehicles while saving cannot fetch or broadcast the old car into the new view', async () => {
  const h = instance(), write = deferred(), calls = [];
  h._hass = { callWS: query => { calls.push(query); return write.promise; } };
  const saving = h.update('add_charge', { kwh: 1 }); h.setConfig({ entry_id: 'two', language: 'en' });
  write.resolve(ordinary(2)); const result = await saving;
  assert.equal(result.saved, true); assert.equal(result.refreshed, false);
  assert.equal(calls.length, 1); assert.equal(h.fullSnapshot, null); assert.equal(h.events.length, 0);
});

test('empty arrays are valid selected-period reads, but an ordinary GET reply is not', async () => {
  const h = instance(); h._hass = { callWS: async () => selected(1) };
  assert.equal(await h.refresh(), 'updated'); assert.equal(h.snapshot.charges.length, 0); assert.equal(h.snapshot.trips.length, 0);
  const before = h.fullSnapshot;
  h._hass.callWS = async query => query.type.endsWith('/update') ? ordinary(2) : ordinary(2);
  const result = await h.update('counter', { name: 'A' });
  assert.equal(result.saved, true); assert.equal(result.refreshed, false);
  assert.equal(h.fullSnapshot, before); assert.equal(h.error, h.savedRefreshCopy());
});

test('out-of-order mutation replies never broadcast an older ordinary snapshot after a newer write', async () => {
  const h = instance(), writes = [];
  h._hass = { callWS: query => { if (query.type.endsWith('/get')) return Promise.resolve(selected(2));
    const pending = deferred(); writes.push(pending); return pending.promise; } };
  const first = h.update('counter', { name: 'A' }), second = h.update('counter', { name: 'B' });
  writes[1].resolve(ordinary(2)); await second;
  writes[0].resolve(ordinary(1)); await first;
  assert.equal(h.events.some(event => event.detail.snapshot.revision === 1), false);
  assert.equal(h.fullSnapshot.revision, 2);
});

test('automatic HA state refresh waits for a pending mutation instead of replacing its form', async () => {
  const h = instance(), write = deferred(), calls = []; h.isConnected = true;
  h._hass = { callWS: query => { calls.push(query); return write.promise; } };
  const saving = h.update('add_charge', { kwh: 1 });
  h.hass = { callWS: async query => { calls.push(query); return selected(2); } };
  assert.equal(calls.length, 1);
  write.resolve(ordinary(2)); await saving;
  assert.equal(calls.filter(query => query.type.endsWith('/update')).length, 1);
  assert.equal(calls.filter(query => query.type.endsWith('/get')).length, 1);
});
