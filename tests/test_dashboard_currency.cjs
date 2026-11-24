const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const component = path.join(__dirname, '../custom_components/nio_telematics');
const baseSource = fs.readFileSync(path.join(component, 'car_dashboard/car-ledger-card.js'), 'utf8');
const historySource = fs.readFileSync(path.join(component, 'nio-dashboard-history.js'), 'utf8');
const root = { querySelector() { return null; }, querySelectorAll() { return []; }, addEventListener() {} };
const context = {
  URL, Intl, Date, console, CustomEvent: class { constructor(type, options) { this.type = type; Object.assign(this, options); } },
  HTMLElement: class { constructor() { this.attributes = {}; } setAttribute(k, v) { this.attributes[k] = v; } addEventListener() {} attachShadow() { this.shadowRoot = root; } },
  window: { customCards: [] }, document: { hidden: false, addEventListener() {}, removeEventListener() {}, createElement() { return { children: [], append(child) { this.children.push(child); } }; } },
  customElements: { get() {}, define() {} },
};
vm.createContext(context);
vm.runInContext(baseSource.replaceAll('import.meta.url', JSON.stringify('https://ha.test/car-dashboard.js?nio_owned=1')).replace('export { CarLedgerCard };', '') + '\nglobalThis.__Base=CarLedgerCard;', context);
vm.runInContext(historySource.replaceAll('\r\n', '\n').replace(/const baseVersion=.*?\nconst \{CarLedgerCard\}=await import\([^\n]+\);/, '').replaceAll('import.meta.url', JSON.stringify('https://ha.test/nio-dashboard-history.js')).replace('export function periodLabel', 'function periodLabel').replace('export class NioDashboardHistory', 'class NioDashboardHistory') + '\nglobalThis.__History=NioDashboardHistory;', context);
const Car = context.__Base;
const History = context.__History;

function card(language = 'en') {
  const instance = new Car();
  instance.config = { entry_id: 'entry', language };
  instance.snapshot = { currency: 'DKK', preferences: { currency: 'DKK' }, settings: { capacity_kwh: 75 }, charges: [], trips: [], parked_periods: [], counters: [], charging_daily: [], statistics: {} };
  return instance;
}

test('charge entry keeps the amount in its explicit currency and does not convert', async () => {
  const c = card('en'); let form; let save;
  c.dialog = (_title, content, onSave) => { form = content; save = onSave; };
  c.update = async (action, values) => { c.lastUpdate = { action, values }; };
  c.snapshot.currency = 'EUR'; c.snapshot.preferences.currency = 'DKK';
  c.chargeDialog();
  assert.match(form, /<select name="currency">[\s\S]*<option value="EUR" selected>[\s\S]*<option value="DKK"/);
  await save({ get: key => ({ currency: 'DKK', price: '7.46', receipt: '', kwh: '10', category: 'other', start: '2026-11-24T10:00', end: '2026-11-24T11:00' })[key] ?? '' });
  assert.equal(c.lastUpdate.action, 'add_charge');
  assert.equal(c.lastUpdate.values.currency, 'DKK');
  assert.equal(c.lastUpdate.values.price, 7.46);
});

test('currency picker permits a new GBP receipt currency with an EUR-only snapshot', () => {
  const c = card('en'); c.snapshot.currency = 'EUR'; c.snapshot.preferences.currency = 'EUR'; c.snapshot.charges = [];
  let form; c.dialog = (_title, content) => { form = content; };
  c.chargeDialog();
  assert.match(form, /<option value="GBP"[^>]*>GBP<\/option>/);
  assert.match(form, /<option value="EUR" selected>EUR<\/option>/);
});

test('editing an untagged historic charge defaults to EUR and currency changes clear only money inputs', () => {
  const c = card('en'); c.snapshot.currency = 'DKK';
  let form, change;
  const inputs = { price: { value: '0.2', placeholder: '' }, receipt: { value: '', placeholder: '' }, kwh: { value: '10' } };
  const select = { value: 'EUR', addEventListener(_name, fn) { change = fn; } };
  const modal = { querySelector(selector) { if (selector === '[name="currency"]') return select; const key = selector.match(/\[name="(.*?)"\]/)?.[1]; if (key) return inputs[key]; return null; } };
  c.shadowRoot = { querySelector: () => modal };
  c.dialog = (_title, content) => { form = content; };
  c.chargeDialog({ id: 'legacy', start: 1, end: 2, kwh: 10, cost_eur: 2, price_eur_kwh: 0.2, confirmed: true, category: 'other' });
  assert.match(form, /<select name="currency"><option value="EUR" selected>/);
  assert.match(form, /value="0\.2"/);
  select.value = 'DKK'; change();
  assert.equal(inputs.price.value, '');
  assert.equal(inputs.receipt.value, '');
  assert.equal(inputs.kwh.value, '10');
  assert.equal(inputs.price.placeholder, 'DKK/kWh');
  assert.equal(inputs.receipt.placeholder, 'DKK');
});

test('ledger currency change exposes its input unit and submits explicit replacement prices', async () => {
  const c = card('en'); let form; let save;
  c.snapshot.currency = 'EUR'; c.snapshot.preferences = { currency: 'EUR', opening_price_eur_kwh: 0.2, petrol_eur_l: 1.8, petrol_l_100km: 6.5, rated_kwh_100km: 18 };
  c.dialog = (_title, content, onSave) => { form = content; save = onSave; };
  c.update = async (action, values) => { c.lastUpdate = { action, values }; };
  c.settingsDialog();
  assert.match(form, /<select name="currency">[\s\S]*<option value="EUR" selected>/);
  assert.match(form, /€\/kWh/);
  assert.match(form, /does not convert saved prices/);
  await save({ get: key => ({ currency: 'DKK', opening_price_eur_kwh: '', petrol_eur_l: '14.2', petrol_l_100km: '6.5', rated_kwh_100km: '18' })[key] ?? '' });
  assert.equal(c.lastUpdate.action, 'preferences');
  assert.equal(c.lastUpdate.values.currency, 'DKK');
  assert.equal(c.lastUpdate.values.opening_price_eur_kwh, null);
  assert.equal(c.lastUpdate.values.petrol_eur_l, 14.2);
  assert.equal(c.lastUpdate.values.petrol_l_100km, 6.5);
});

test('legacy untagged charge stays EUR while a DKK session renders its own amount unit', () => {
  const c = card('en');
  assert.equal(c.moneyUnit(c.currencyCode(undefined)), '€');
  const legacy = c.chargeCard({ id: 'legacy', start: 1, end: 2, kwh: 10, cost_eur: 10, category: 'other' });
  assert.match(legacy, /10\.00<small>€<\/small>/);
  const row = c.chargeCard({ id: 'dkk', start: 1, end: 2, kwh: 10, cost_eur: 74.6, currency: 'DKK', category: 'other' });
  assert.match(row, /74\.60<small>DKK<\/small>/);
  assert.match(row, /7\.46<small>DKK\/kWh<\/small>/);
  assert.doesNotMatch(row, /7\.46<small>€<\/small>/);
});

test('managed history monthly summary and daily graph preserve DKK units', () => {
  const h = new History(); h.config = { language: 'en' }; h.graphUnit = 'eur'; h.snapshot = { currency: 'DKK', charging_daily: [{ date: '2026-11-23', kwh: 10, known_cost_eur: 74.6 }], statistics: { selected: { currency_mismatch_count: 0 } } };
  const summary = { textContent: '10.00 kWh · 74.60 DKK charging cost', classList: { contains: () => false }, replaceWith(node) { this.replacement = node; } };
  const notice = { textContent: 'Costs in different currencies are kept separate', classList: { contains: name => name === 'currency-notice' }, replaceWith(node) { this.replacement = node; } };
  h.shadowRoot = { querySelectorAll: () => [summary, notice] };
  h.tab = 'charging'; h.moneyUnit = Car.prototype.moneyUnit; h.currencyCode = Car.prototype.currencyCode; h.translate = Car.prototype.translate; h.config.language = 'en';
  // The actual month-summary renderer parses the source money unit into the value cell.
  const created = [];
  context.document.createElement = () => { const node = { children: [], append(...children) { this.children.push(...children); } }; created.push(node); return node; };
  h.summaryGrids();
  assert.equal(created.some(node => node.className?.startsWith('period-summary')), true);
  assert.ok(created.some(node => node.className === 'unit' && node.textContent === ' DKK'));
  assert.equal(notice.replacement, undefined, 'the currency notice is not parsed as a fifth summary metric');
  const graph = History.prototype.chargingGraph.call(h);
  assert.match(graph, />DKK<\/button>/);
  assert.match(graph, /74\.60 DKK/);
  h.snapshot.statistics.selected.currency_mismatch_count = 1;
  const mixedGraph = History.prototype.chargingGraph.call(h);
  assert.match(mixedGraph, /Costs in different currencies are kept separate/);
  assert.match(mixedGraph, /2026-11-23: — DKK/);
  assert.doesNotMatch(mixedGraph, /2026-11-23: 74\.60 DKK/);
});

test('managed counter popup uses the statistic unit and hides mixed-currency costs', async () => {
  const h = new History(); let content;
  h.config = { language: 'en' }; h.snapshot = { currency: 'EUR', counters: [{ id: 'counter', name: 'Commute', statistics: { distance_km: 100, consumption_kwh_100km: 20, cost_eur_100km: 12, currency: 'DKK', currency_mismatch_count: 0 } }] };
  h.translate = Car.prototype.translate; h.currencyCode = Car.prototype.currencyCode; h.moneyUnit = Car.prototype.moneyUnit; h.value = Car.prototype.value; h.esc = Car.prototype.esc; h.currencyNotice = Car.prototype.currencyNotice;
  h.dialog = (_title, body) => { content = body; };
  const button = { dataset: { showCounter: 'counter' }, hasAttribute: () => false };
  await History.prototype.click.call(h, { target: { closest: () => button } });
  assert.match(content, /12\.00<small>DKK\/100 km<\/small>/);
  h.snapshot.counters[0].statistics.currency_mismatch_count = 1;
  await History.prototype.click.call(h, { target: { closest: () => button } });
  assert.match(content, /—<small>DKK\/100 km<\/small>/);
  assert.match(content, /Costs in different currencies are kept separate/);
});

test('mixed currencies stay unknown in the managed cost graph and totals', () => {
  const c = card(); c.tab = 'charging'; c.full = true; c.pageSize = 20;
  c.snapshot.charges = [
    { id: 'eur', start: 1795428000, end: 1795429000, kwh: 10, cost_eur: 10, currency: 'EUR', confirmed: true, category: 'other' },
    { id: 'dkk', start: 1795430000, end: 1795431000, kwh: 10, cost_eur: 74.6, currency: 'DKK', confirmed: true, category: 'other' },
  ];
  const html = c.history();
  assert.match(html, /Costs in different currencies are kept separate/);
  assert.match(html, /— DKK/);
  assert.doesNotMatch(html, /84\.60/);
  const translated = c.translate('20.00 kWh · — DKK laadkosten · — DKK vergoeding · — DKK laadvoordeel');
  assert.match(translated, /charging cost/);
  assert.match(translated, /DKK reimbursement/);
  assert.doesNotMatch(translated, /laadkosten|vergoeding|laadvoordeel/);
});

test('currency controls and conflict copy are localized for every supported UI language', () => {
  for (const language of ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro']) {
    const c = card(language);
    assert.ok(c.currencyLabel(), `${language} currency label`);
    assert.ok(c.currencyHelp(), `${language} currency help`);
    assert.ok(c.currencyNotice('mixed'), `${language} mixed currency explanation`);
    assert.ok(c.currencyNotice('conflict'), `${language} retained amount explanation`);
  }
});

test('unaccounted usage detail separates signed battery change from blank manual energy', () => {
  const c = card('en'), gap = { id: 'g1', fingerprint: 'fp1', trip_id: 'trip1', start: 1, end: 2, km: 41, battery_change_kwh: -11.25, resolution: 'open' };
  c.snapshot.unaccounted_intervals = [gap];
  const section = c.unaccountedUsage({ unaccounted_distance_km: 41, unaccounted_battery_change_kwh: -11.25, unaccounted_intervals: 1 });
  assert.match(section, /Unaccounted usage/);
  assert.match(section, /41\.0<small>km<\/small>/);
  assert.match(section, /[-−]11\.25<small>kWh<\/small>/);
  assert.match(section, /name="energy_kwh"[^>]*required><\/label>/);
  assert.doesNotMatch(section, /name="energy_kwh"[^>]*value=/);
  assert.match(section, /data-gap-status="ignored"/);
  assert.match(section, /Complete manually/);
});

test('manual gap form sends user energy, optional signed cost and chosen currency only', async () => {
  const c = card('en'); let update;
  c.update = async (action, values) => { update = { action, values }; };
  const form = { dataset: { gapIdent: 'g1', gapFingerprint: 'fp1' }, elements: { energy_kwh: { value: '16.05' }, cost: { value: '-4.815' }, currency: { value: 'GBP' } }, closest: () => form };
  let prevented = false;
  await c.submitGap({ target: form, preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(update.action, 'resolve_gap');
  assert.equal(JSON.stringify(update.values), JSON.stringify({ ident: 'g1', fingerprint: 'fp1', status: 'manual', energy_kwh: 16.05, cost: -4.815, currency: 'GBP' }));
});

test('blank manual cost clears it explicitly, while ignore and undo send no energy or currency', async () => {
  const c = card('en'); let update;
  c.update = async (action, values) => { update = { action, values }; };
  const form = { dataset: { gapIdent: 'g1', gapFingerprint: 'fp2' }, elements: { energy_kwh: { value: '0' }, cost: { value: '' }, currency: { value: 'DKK' } }, closest: () => form };
  await c.submitGap({ target: form, preventDefault() {} });
  assert.equal(update.values.cost, null);
  const button = { dataset: { gapIdent: 'g1', gapFingerprint: 'fp2', gapStatus: 'ignored' } };
  await c.setGapResolution(button);
  assert.equal(JSON.stringify(update.values), JSON.stringify({ ident: 'g1', fingerprint: 'fp2', status: 'ignored' }));
  button.dataset.gapStatus = 'open';
  await c.setGapResolution(button);
  assert.equal(JSON.stringify(update.values), JSON.stringify({ ident: 'g1', fingerprint: 'fp2', status: 'open' }));
});

test('unaccounted intervals follow the selected period, including gaps spanning into it', () => {
  const c = card('en'); c.snapshot.selected_period = { start: 100, end: 200, effective_end: 190 };
  c.snapshot.unaccounted_intervals = [
    { id: 'old', start: 10, end: 99, resolution: 'ignored' },
    { id: 'inside', start: 90, end: 120, resolution: 'ignored' },
    { id: 'future', start: 190, end: 210, resolution: 'open' },
  ];
  assert.deepEqual(Array.from(c.gapIntervals(), row => row.id), ['inside']);
  assert.equal(c.unaccountedUsage({ unaccounted_distance_km: 0, unaccounted_battery_change_kwh: 0, unaccounted_intervals: 0 }).includes('data-gap-ident="inside"'), true);
  c.snapshot.unaccounted_intervals = c.snapshot.unaccounted_intervals.filter(row => row.id === 'old');
  assert.equal(c.unaccountedUsage({ unaccounted_distance_km: 0 }).includes('Unaccounted usage'), false);
});

test('trip details show cross-period gap history and stale overlays can be cleared with the current fingerprint', async () => {
  const c = card('en'); let content, update;
  c.snapshot.selected_period = { start: 100, end: 200, effective_end: 190 };
  c.snapshot.unaccounted_intervals = [];
  c.fullSnapshot = { unaccounted_intervals: [{ id: 'g1', fingerprint: 'new-fingerprint', trip_id: 'trip1', start: 10, end: 99, km: 41, battery_change_kwh: -11.25, resolution: 'stale' }] };
  c.dialog = (_title, body) => { content = body; };
  c.tripDialog({ id: 'trip1', start: 10, end: 120, distance_km: 41, start_energy: 50, end_energy: 44, start_odo: 1, end_odo: 42, segments: [{ gap_fingerprint: 'new-fingerprint' }] });
  assert.match(content, /Unaccounted usage/);
  assert.match(content, /data-gap-status="open"/);
  assert.match(content, /new-fingerprint/);
  assert.doesNotMatch(content, /name="energy_kwh"/);
  c.update = async (action, values) => { update = { action, values }; };
  await c.setGapResolution({ dataset: { gapIdent: 'g1', gapFingerprint: 'new-fingerprint', gapStatus: 'open' } });
  assert.equal(update.action, 'resolve_gap');
  assert.equal(JSON.stringify(update.values), JSON.stringify({ ident: 'g1', fingerprint: 'new-fingerprint', status: 'open' }));
});

test('all fourteen dashboard languages localize every new gap action and status', () => {
  for (const language of ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro']) {
    const c = card(language);
    for (const key of ['title', 'complete', 'ignore', 'undo', 'battery', 'manual', 'ignored', 'stale', 'noConvert', 'matched', 'usageHelp', 'savedRefresh']) assert.ok(c.gapCopy(key), `${language} ${key}`);
  }
});

test('known-cost notice localizes the dynamic amount while preserving its ISO currency', () => {
  for (const language of ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro']) {
    const c = card(language), source = c.missingNoticeText({ missing_prices: 2, known_spend_eur: 74.6, currency: 'DKK' });
    const rendered = c.translate(source);
    assert.match(rendered, /DKK/, language);
    if (language !== 'nl') assert.doesNotMatch(rendered, /Bekende kosten/, language);
  }
});

test('dynamic usernames containing euro text remain unchanged', () => {
  const c = card('fr');
  assert.equal(c.translate('Trip € 20'), 'Trip € 20');
});

test('Ignore and Undo acknowledge success by closing the old trip dialog', async () => {
  for (const status of ['ignored', 'open']) {
    const c = card(); let finish; let closes = 0; let writes = 0;
    const dialog = { close() { closes++; } };
    const panel = { querySelector() { return null; } };
    const button = { disabled: false, dataset: { gapIdent: 'gap', gapFingerprint: 'fingerprint', gapStatus: status }, closest(selector) { return selector === 'dialog' ? dialog : panel; } };
    c.update = async (action, values) => { writes++; assert.equal(action, 'resolve_gap'); assert.equal(values.status, status); await new Promise(resolve => { finish = resolve; }); return { saved: true, refreshed: true }; };
    const pending = c.setGapResolution(button);
    assert.equal(button.disabled, true);
    assert.equal(closes, 0);
    finish(); await pending;
    assert.equal(closes, 1);
    assert.equal(writes, 1);
  }
});

test('rejected Ignore keeps the dialog open and shows an inline localized error', async () => {
  const c = card(); let closes = 0; let message;
  const dialog = { close() { closes++; } };
  const panel = { querySelector() { return message; }, append(node) { message = node; } };
  const button = { disabled: false, dataset: { gapIdent: 'gap', gapFingerprint: 'fingerprint', gapStatus: 'ignored' }, closest(selector) { return selector === 'dialog' ? dialog : panel; } };
  const previousCreate = context.document.createElement;
  context.document.createElement = () => ({ setAttribute(key, value) { this[key] = value; } });
  c.localizeError = () => 'Could not save. Try again.';
  c.update = async () => { throw new Error('private backend detail'); };
  try { await c.setGapResolution(button); } finally { context.document.createElement = previousCreate; }
  assert.equal(closes, 0);
  assert.equal(button.disabled, false);
  assert.equal(message.role, 'alert');
  assert.equal(message.textContent, 'Could not save. Try again.');
  assert.doesNotMatch(message.textContent, /backend detail/);
});

test('trip with an unresolved gap keeps energy from its valid matched segments', () => {
  const c = card('en'); c.snapshot.settings.capacity_kwh = 75;
  const trip = { id: 'trip', start: 1, end: 4, distance_km: 61, start_energy: 60, end_energy: 55, segments: [
    { start: 1, end: 2, km: 20, kwh: 3.6 },
    { start: 2, end: 3, km: 41, kwh: 11.25, invalid_reason: 'gap' },
  ] };
  c.snapshot.unaccounted_intervals = [{ id: 'gap', fingerprint: 'fp', trip_id: 'trip', start: 2, end: 3, km: 41, battery_change_kwh: -11.25, resolution: 'open' }];
  const row = c.tripCard(trip);
  assert.match(row, /18\.0<small>kWh\/100 km<\/small>/);
  assert.match(row, /4\.8<small>%<\/small>/);
  assert.match(row, /gap-status/);
  let details; c.dialog = (_title, body) => { details = body; };
  c.tripDialog(trip);
  assert.match(details, /3\.60<small>kWh<\/small>/);
  assert.match(details, /Trip energy includes matched readings and manually entered intervals/);
  assert.doesNotMatch(details, /Kilometerstand|Afname zonder kilometerverandering|Tijden volgen de ontvangen metingen/);
});

test('unknown-energy trips render safely with or without a gap marker', () => {
  const c = card('en'); c.snapshot.settings.capacity_kwh = 75;
  const base = { id: 'unknown', start: 1, end: 2, distance_km: 10, start_energy: 50, end_energy: 49, segments: [] };
  assert.doesNotThrow(() => c.tripCard(base));
  assert.match(c.tripCard(base), /Meting ontbreekt/);
  c.snapshot.unaccounted_intervals = [{ id: 'gap', fingerprint: 'fp', trip_id: 'unknown', start: 1, end: 2, km: 10, battery_change_kwh: -1, resolution: 'open' }];
  assert.doesNotThrow(() => c.tripCard(base));
  assert.match(c.tripCard(base), /gap-status/);
});

test('whole trip detail message is localized as a complete sentence in every dashboard language', () => {
  for (const language of ['en', 'nl', 'fr', 'de', 'nb', 'sv', 'da', 'cs', 'el', 'hu', 'lb', 'pl', 'pt', 'ro']) {
    const c = card(language); let content;
    c.dialog = (_title, body) => { content = body; };
    c.snapshot.unaccounted_intervals = [{ id: 'gap', fingerprint: 'fp', trip_id: 't', start: 1, end: 2, km: 5, battery_change_kwh: -2, resolution: 'open' }];
    c.tripDialog({ id: 't', start: 1, end: 2, distance_km: 20, start_energy: 50, end_energy: 45, start_odo: 10, end_odo: 30, segments: [{ gap_id: 'g' }] });
    assert.match(content, /10/);
    assert.match(content, /20/);
    if (language === 'en') assert.match(content, /Odometer .* Times follow the received measurements\. Trip energy includes matched readings/);
    if (language === 'nl') assert.match(content, /Kilometerstand .* Tijden volgen de ontvangen metingen\. Ritenergie omvat/);
    if (language !== 'en') assert.doesNotMatch(content, /Odometer|Trip energy includes matched readings/);
  }
});

test('changing manual gap currency clears cost only and explains charging receipts belong in Charging', () => {
  const c = card('en'), cost = { value: '3.60' }, energy = { value: '12' };
  const form = { dataset: { currency: 'EUR' }, elements: { cost, energy_kwh: energy } };
  const select = { value: 'GBP', closest: () => form };
  c.change({ target: { closest: () => select } });
  assert.equal(cost.value, '');
  assert.equal(energy.value, '12');
  const gap = c.gapEntry({ id: 'g', fingerprint: 'fp', start: 1, end: 2, km: 10, battery_change_kwh: -1, resolution: 'open' });
  assert.match(gap, /These fields complete missing driving usage/);
  assert.match(gap, /charging receipts under Add charge in Charging/);
});

test('petrol comparison stays unknown when the input unit differs from accounting currency or its price is blank', () => {
  const c = card('en');
  const segment = { start: 1, end: 2, km: 100, kwh: 20, cost_eur: 2 };
  const makeSnapshot = (accounting, prefCurrency, fuelPrice) => ({
    currency: accounting, settings: { capacity_kwh: 75 }, preferences: { currency: prefCurrency, petrol_l_100km: 6, petrol_eur_l: fuelPrice },
    charges: [], trips: [{ id: 't', start: 1, end: 2, distance_km: 100, start_odo: 0, end_odo: 100, start_energy: 60, end_energy: 40, segments: [segment] }],
    counters: [{ id: 'counter', statistics: { segments: [segment] } }], parked_periods: [], active_trip_id: null, driving_segments: [segment],
    statistics: Object.fromEntries(['month','day','week','year','selected','current_trip','last_trip'].map(key => [key, { segments: [segment], projected_range_km: null, consumption_kwh_100km: 20 }]))
  });
  let result = c.prepareSnapshot(makeSnapshot('DKK', 'EUR', 2));
  assert.equal(result.statistics.month.petrol_comparison_eur, null);
  assert.equal(result.counters[0].statistics.petrol_comparison_eur, null);
  result = c.prepareSnapshot(makeSnapshot('DKK', 'DKK', null));
  assert.equal(result.statistics.month.petrol_comparison_eur, null, 'explicit blank price stays unknown');
  result = c.prepareSnapshot(makeSnapshot('DKK', 'DKK', 2));
  assert.equal(result.statistics.month.petrol_comparison_eur, 12);
  assert.equal(result.counters[0].statistics.petrol_comparison_eur, 12);
});

test('rejected manual gap save keeps entered values and displays the inline error', async () => {
  const c = card('en'); let rendered = false;
  const error = { textContent: '' };
  const form = { dataset: { gapIdent: 'g1', gapFingerprint: 'stale' }, elements: { energy_kwh: { value: '12' }, cost: { value: '3.60' }, currency: { value: 'EUR' } }, closest: () => form, querySelector: () => error };
  c.update = async () => { throw new Error('stale fingerprint'); };
  c.render = () => { rendered = true; };
  let prevented = false;
  await c.submitGap({ target: form, preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(form.elements.energy_kwh.value, '12');
  assert.equal(form.elements.cost.value, '3.60');
  assert.notEqual(error.textContent, '');
  assert.doesNotMatch(error.textContent, /stale fingerprint/);
  assert.equal(rendered, false);
});

test('saved gap with failed readback is disabled and cannot be accidentally resubmitted', async () => {
  const c = card('en'), energy = { value: '12' }, cost = { value: '3.60' }, currency = { value: 'GBP' };
  const controls = [energy, cost, currency, {}], status = { textContent: '' }, error = { textContent: '' }, ignore = { disabled: false };
  const form = { dataset: { gapIdent: 'g', gapFingerprint: 'fp' }, elements: { energy_kwh: energy, cost, currency }, closest: () => form, querySelectorAll: () => controls, querySelector: selector => selector === '.form-saved' ? status : error, parentElement: { querySelector: () => ignore } };
  c.update = async () => ({ saved: true, refreshed: false });
  await c.submitGap({ target: form, preventDefault() {} });
  assert.match(status.textContent, /Saved\. Refresh history/);
  assert.equal(error.textContent, '');
  assert.deepEqual(controls.map(control => control.disabled), [true, true, true, true]);
  assert.equal(ignore.disabled, true);
  assert.equal(energy.value, '12');
  assert.equal(cost.value, '3.60');
  assert.equal(currency.value, 'GBP');
});
